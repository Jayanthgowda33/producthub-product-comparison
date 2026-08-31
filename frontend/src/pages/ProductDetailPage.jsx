import { useEffect, useState } from 'react'
import { useParams, useNavigate } from 'react-router-dom'
import api from '../api/client'
import ProductCard from '../components/ProductCard'
import { useAuth } from '../context/AuthContext'
import { formatPrice } from '../utils/currency'

export default function ProductDetailPage() {
  const { id } = useParams()
  const navigate = useNavigate()
  const { user } = useAuth()
  const [product, setProduct] = useState(null)
  const [similar, setSimilar] = useState([])
  const [selectedVariant, setSelectedVariant] = useState(null)
  const [message, setMessage] = useState('')

  useEffect(() => {
    api.get(`/api/products/products/${id}/`).then((res) => {
      setProduct(res.data)
      setSelectedVariant(res.data.variants?.[0]?.id ?? null)
    })
    api.get(`/api/ai/similar/${id}/`).then((res) => setSimilar(res.data.results))
  }, [id])

  async function addToCart() {
    if (!user) {
      navigate('/login')
      return
    }
    if (!selectedVariant) {
      setMessage('This product has no purchasable variant yet.')
      return
    }
    try {
      await api.post('/api/orders/cart/', { variant_id: selectedVariant, quantity: 1 })
      setMessage('Added to cart!')
    } catch {
      setMessage('Could not add to cart.')
    }
  }

  if (!product) return <div className="page">Loading…</div>

  return (
    <div className="page">
      <h1>{product.title}</h1>
      <p className="product-vendor">Sold by {product.vendor_name}</p>
      <p>{product.description}</p>
      <p className="product-price">{formatPrice(product.base_price)}</p>

      {product.variants?.length > 0 && (
        <div className="variant-picker">
          <label>Options:</label>
          <select value={selectedVariant ?? ''} onChange={(e) => setSelectedVariant(Number(e.target.value))}>
            {product.variants.map((v) => (
              <option key={v.id} value={v.id}>
                {[v.size, v.color].filter(Boolean).join(' / ') || v.sku} — {v.stock_quantity} in stock
              </option>
            ))}
          </select>
        </div>
      )}

      <button onClick={addToCart}>Add to Cart</button>
      {message && <p className="status-message">{message}</p>}

      {similar.length > 0 && (
        <>
          <h2>You might also like</h2>
          <div className="product-grid">
            {similar.map((p) => (
              <ProductCard key={p.id} product={p} />
            ))}
          </div>
        </>
      )}
    </div>
  )
}