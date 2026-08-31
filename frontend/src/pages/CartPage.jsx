import { useEffect, useState } from 'react'
import { useNavigate } from 'react-router-dom'
import api from '../api/client'
import { useAuth } from '../context/AuthContext'
import { formatPrice } from '../utils/currency'

export default function CartPage() {
  const { user } = useAuth()
  const navigate = useNavigate()
  const [cart, setCart] = useState(null)
  const [address, setAddress] = useState('')
  const [placing, setPlacing] = useState(false)
  const [error, setError] = useState('')

  useEffect(() => {
    if (!user) return
    loadCart()
  }, [user])

  function loadCart() {
    api.get('/api/orders/cart/').then((res) => setCart(res.data))
  }

  async function updateQuantity(itemId, quantity) {
    if (quantity < 1) return
    await api.patch(`/api/orders/cart/items/${itemId}/`, { quantity })
    loadCart()
  }

  async function removeItem(itemId) {
    await api.delete(`/api/orders/cart/items/${itemId}/`)
    loadCart()
  }

  async function checkout() {
    setError('')
    setPlacing(true)
    try {
      const { data } = await api.post('/api/orders/checkout/', { shipping_address: address })
      navigate('/orders', { state: { justPlacedOrderId: data.id } })
    } catch (err) {
      setError(err.response?.data?.detail || 'Checkout failed.')
    } finally {
      setPlacing(false)
    }
  }

  if (!user) {
    return (
      <div className="page">
        <h1>Your Cart</h1>
        <p>Please <a href="/login">log in</a> to view your cart.</p>
      </div>
    )
  }

  if (!cart) return <div className="page">Loading cart…</div>

  return (
    <div className="page">
      <h1>Your Cart</h1>
      {cart.items.length === 0 ? (
        <p>Your cart is empty.</p>
      ) : (
        <>
          <table className="cart-table">
            <thead>
              <tr><th>Product</th><th>Qty</th><th>Unit Price</th><th>Total</th><th></th></tr>
            </thead>
            <tbody>
              {cart.items.map((item) => (
                <tr key={item.id}>
                  <td>{item.product_title}</td>
                  <td>
                    <input
                      type="number"
                      min="1"
                      value={item.quantity}
                      onChange={(e) => updateQuantity(item.id, Number(e.target.value))}
                    />
                  </td>
                  <td>{formatPrice(item.unit_price)}</td>
                  <td>{formatPrice(item.line_total)}</td>
                  <td><button onClick={() => removeItem(item.id)}>Remove</button></td>
                </tr>
              ))}
            </tbody>
          </table>
          <h2>Total: {formatPrice(cart.total)}</h2>

          <div className="checkout-form">
            <label>Shipping address</label>
            <textarea value={address} onChange={(e) => setAddress(e.target.value)} rows={3} />
            {error && <p className="status-message error">{error}</p>}
            <button onClick={checkout} disabled={placing || !address.trim()}>
              {placing ? 'Placing order…' : 'Place Order'}
            </button>
          </div>
        </>
      )}
    </div>
  )
}