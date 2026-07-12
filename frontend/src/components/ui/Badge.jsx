import "./badge.css";

function Badge({
  children,
  variant = "default",
  size = "md",
  rounded = true,
  className = "",
}) {
  return (
    <span
      className={`
        ui-badge
        ui-badge-${variant}
        ui-badge-${size}
        ${rounded ? "ui-badge-rounded" : ""}
        ${className}
      `}
    >
      {children}
    </span>
  );
}

export default Badge;