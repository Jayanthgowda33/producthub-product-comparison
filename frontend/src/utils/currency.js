// Fixed approximate rate — not live. Update this constant periodically,
// or swap in a real forex API call later if you need live rates.
const USD_TO_INR = 95.5

export function formatPrice(usdAmount) {
  const usd = Number(usdAmount)
  const inr = usd * USD_TO_INR
  return `$${usd.toFixed(2)} · ₹${inr.toLocaleString('en-IN', { maximumFractionDigits: 0 })}`
}