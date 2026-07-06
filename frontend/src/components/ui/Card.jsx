function Card({ children, className = "" }) {
  return <section className={`ui-card ${className}`}>{children}</section>;
}

export default Card;