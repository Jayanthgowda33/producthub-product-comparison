import { Link } from 'react-router-dom'
import { formatPrice } from '../utils/currency'

export default function ProductCard({ product }) {
  return (
    <Link to={`/products/${product.id}`} className="product-card">
      <div className="product-image-placeholder">
        {product.primary_image ? (
          <img src={product.primary_image} alt={product.title} />
        ) : (
          <span>{product.title[0]}</span>
        )}
      </div>
      <h3>{product.title}</h3>
      <p className="product-vendor">{product.vendor_name}</p>
      <p className="product-price">{formatPrice(product.base_price)}</p>
    </Link>
  )
}