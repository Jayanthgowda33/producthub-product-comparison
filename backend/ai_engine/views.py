import json


from django.conf import settings
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from products.models import Product
from products.serializers import ProductListSerializer
from .search import search as tfidf_search, similar_products as tfidf_similar


class SearchView(APIView):
    permission_classes = [AllowAny]

    def get(self, request):
        query = request.query_params.get('q', '').strip()
        if not query:
            return Response({'detail': 'Missing ?q= parameter.'}, status=400)

        ranked = tfidf_search(query)
        products_by_id = {p.id: p for p in Product.objects.filter(id__in=[r[0] for r in ranked])}
        results = []
        for pid, score in ranked:
            if pid in products_by_id:
                data = ProductListSerializer(products_by_id[pid]).data
                data['relevance'] = round(score, 4)
                results.append(data)
        return Response({'query': query, 'results': results})


class SimilarProductsView(APIView):
    permission_classes = [AllowAny]

    def get(self, request, product_id):
        ranked = tfidf_similar(product_id)
        products_by_id = {p.id: p for p in Product.objects.filter(id__in=[r[0] for r in ranked])}
        results = []
        for pid, score in ranked:
            if pid in products_by_id:
                data = ProductListSerializer(products_by_id[pid]).data
                data['similarity'] = round(score, 4)
                results.append(data)
        return Response({'results': results})


PRODUCT_SEARCH_TOOL = {
    "type": "function",
    "function": {
        "name": "search_products",
        "description": "Search the real product catalog by a text query. Returns actual in-stock products with prices.",
        "parameters": {
            "type": "object",
            "properties": {
                "query": {"type": "string", "description": "What the customer is looking for"},
            },
            "required": ["query"],
        },
    },
}


class AssistantView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        try:
            return self._handle(request)
        except Exception as exc:
            return Response({'detail': f'Assistant error: {exc}'}, status=500)

    def _handle(self, request):
        message = request.data.get('message', '').strip()
        history = request.data.get('history', [])
        if not message:
            return Response({'detail': 'message is required.'}, status=400)

        api_key = getattr(settings, 'GROQ_API_KEY', '')
        if not api_key:
            return Response(
                {'detail': 'GROQ_API_KEY is not set on the server. Add it to your .env file.'},
                status=503,
            )

        from openai import OpenAI
        client = OpenAI(api_key=api_key, base_url="https://api.groq.com/openai/v1")

        system_prompt = (
            "You are ProductHub's shopping assistant. Help customers find products. "
            "Always use the search_products tool to look up real inventory before "
            "recommending anything — never invent product names or prices. "
            "Keep responses short and friendly."
        )
        messages = [{"role": "system", "content": system_prompt}] + history + [
            {"role": "user", "content": message}
        ]

        response = client.chat.completions.create(
            model="openai/gpt-oss-20b",
            messages=messages,
            tools=[PRODUCT_SEARCH_TOOL],
            tool_choice="auto",
        )
        reply = response.choices[0].message

        if reply.tool_calls:
            messages.append({
                "role": "assistant",
                "content": reply.content,
                "tool_calls": [
                    {
                        "id": call.id,
                        "type": "function",
                        "function": {"name": call.function.name, "arguments": call.function.arguments},
                    }
                    for call in reply.tool_calls
                ],
            })

            for call in reply.tool_calls:
                args = json.loads(call.function.arguments)
                ranked = tfidf_search(args.get('query', ''))[:5]
                products_by_id = {p.id: p for p in Product.objects.filter(id__in=[r[0] for r in ranked])}
                results = [
                    {'title': products_by_id[pid].title, 'price': str(products_by_id[pid].base_price), 'id': pid}
                    for pid, _ in ranked if pid in products_by_id
                ]
                
                tool_payload = {'results': results} if results else {'results': [], 'note': 'No matching products found in the catalog for this query.'}
                messages.append({"role": "tool", "tool_call_id": call.id, "content": json.dumps(tool_payload)})
            second_response = client.chat.completions.create(
                model="openai/gpt-oss-20b",
                messages=messages,
                tools=[PRODUCT_SEARCH_TOOL],
                tool_choice="none",
            )
            final_text = second_response.choices[0].message.content
        else:
            final_text = reply.content

        return Response({'reply': final_text})