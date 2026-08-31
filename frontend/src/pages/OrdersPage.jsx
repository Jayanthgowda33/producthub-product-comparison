import { useEffect, useState } from 'react'
import { useLocation } from 'react-router-dom'
import api from '../api/client'
import { useAuth } from '../context/AuthContext'
import { formatPrice } from '../utils/currency'

export default function OrdersPage() {
  const { user } = useAuth()
  const location = useLocation()
  const [orders, setOrders] = useState([])
  const justPlacedId = location.state?.justPlacedOrderId

  useEffect(() => {
    if (!user) return
    api.get('/api/orders/my-orders/').then((res) => setOrders(res.data.results ?? res.data))
  }, [user])

  if (!user) return <div className="page">Please log in to view your orders.</div>

  return (
    <div className="page">
      <h1>Your Orders</h1>
      {justPlacedId && <p className="status-message success">Order #{justPlacedId} placed successfully!</p>}
      {orders.length === 0 ? (
        <p>No orders yet.</p>
      ) : (
        orders.map((order) => (
          <div key={order.id} className="order-card">
            <div className="order-header">
              <strong>Order #{order.id}</strong>
              <span className={`status-badge status-${order.status}`}>{order.status}</span>
            </div>
            <p>Total: {formatPrice(order.total_amount)}</p>
            <p>Shipping to: {order.shipping_address}</p>
            <ul>
              {order.items.map((item) => (
                <li key={item.id}>{item.quantity} × {item.product_title} ({formatPrice(item.price_at_purchase)})</li>
              ))}
            </ul>
          </div>
        ))
      )}
    </div>
  )
}