import { useEffect, useState } from 'react'
import api from '../api/client'
import ProductCard from '../components/ProductCard'

export default function HomePage() {
  const [products, setProducts] = useState([])
  const [query, setQuery] = useState('')
  const [loading, setLoading] = useState(true)
  const [searching, setSearching] = useState(false)

  useEffect(() => {
    loadAllProducts()
  }, [])

  function loadAllProducts() {
    setLoading(true)
    api.get('/api/products/products/')
      .then((res) => setProducts(res.data.results ?? res.data))
      .finally(() => setLoading(false))
  }

  function handleSearch(e) {
    e.preventDefault()
    if (!query.trim()) {
      loadAllProducts()
      return
    }
    setSearching(true)
    api.get('/api/ai/search/', { params: { q: query } })
      .then((res) => setProducts(res.data.results))
      .finally(() => setSearching(false))
  }

  return (
    <div className="page">
      <h1>Browse Products</h1>

      <form onSubmit={handleSearch} className="search-bar">
        <input
          type="text"
          placeholder="Try 'warm jacket for winter'..."
          value={query}
          onChange={(e) => setQuery(e.target.value)}
        />
        <button type="submit" disabled={searching}>
          {searching ? 'Searching…' : 'AI Search'}
        </button>
      </form>

      {loading ? (
        <p>Loading products…</p>
      ) : products.length === 0 ? (
        <p>No products found.</p>
      ) : (
        <div className="product-grid">
          {products.map((p) => (
            <ProductCard key={p.id} product={p} />
          ))}
        </div>
      )}
    </div>
  )
}