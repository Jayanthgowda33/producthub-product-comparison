from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

from products.models import Product


def _product_text(p):
    return f"{p.title} {p.description or ''} {p.category.name if p.category else ''}"


def build_index():
    products = list(Product.objects.filter(is_active=True).select_related('category'))
    if not products:
        return None, None, []
    texts = [_product_text(p) for p in products]
    vectorizer = TfidfVectorizer(stop_words='english')
    matrix = vectorizer.fit_transform(texts)
    return vectorizer, matrix, [p.id for p in products]


def search(query, top_k=10):
    vectorizer, matrix, product_ids = build_index()
    if vectorizer is None:
        return []
    query_vec = vectorizer.transform([query])
    scores = cosine_similarity(query_vec, matrix).flatten()
    ranked = sorted(zip(product_ids, scores), key=lambda x: x[1], reverse=True)
    return [(pid, float(score)) for pid, score in ranked[:top_k] if score > 0]


def similar_products(product_id, top_k=5):
    vectorizer, matrix, product_ids = build_index()
    if vectorizer is None or product_id not in product_ids:
        return []
    idx = product_ids.index(product_id)
    scores = cosine_similarity(matrix[idx], matrix).flatten()
    ranked = sorted(zip(product_ids, scores), key=lambda x: x[1], reverse=True)
    return [(pid, float(score)) for pid, score in ranked if pid != product_id][:top_k]