import "./button.css";

function Button({
  children,
  variant = "primary",
  size = "md",
  type = "button",
  disabled = false,
  loading = false,
  fullWidth = false,
  onClick,
  className = "",
}) {
  return (
    <button
      type={type}
      disabled={disabled || loading}
      onClick={onClick}
      className={`
        ui-button
        ui-button-${variant}
        ui-button-${size}
        ${fullWidth ? "ui-button-full" : ""}
        ${loading ? "ui-button-loading" : ""}
        ${className}
      `}
    >
      {loading ? "Loading..." : children}
    </button>
  );
}

export default Button;