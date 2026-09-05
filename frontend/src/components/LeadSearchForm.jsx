import { useState } from "react";

function LeadSearchForm({ onSearch }) {
  const [businessType, setBusinessType] = useState("");
  const [location, setLocation] = useState("");
  const [quantity, setQuantity] = useState("");
  const [validationError, setValidationError] = useState("");

  function handleSubmit(event) {
    event.preventDefault();

    const cleanedBusinessType =
      businessType.trim();
    const cleanedLocation =
      location.trim();

    if (!cleanedBusinessType) {
      setValidationError(
        "Please enter a business type."
      );
      return;
    }

    if (!cleanedLocation) {
      setValidationError(
        "Please enter a location."
      );
      return;
    }

    setValidationError("");

    onSearch({
      businessType: cleanedBusinessType,
      location: cleanedLocation,
      quantity: quantity.trim(),
    });
  }

  return (
    <div className="panel">
      <div>
        <p className="eyebrow">Research Agent</p>
        <h2>Find New Leads</h2>
      </div>

      <form className="lead-form" onSubmit={handleSubmit}>
        <input
          placeholder="Business type, e.g. Coffee Shop"
          value={businessType}
          onChange={(event) => setBusinessType(event.target.value)}
        />

        <input
          placeholder="Location, e.g. Doha"
          value={location}
          onChange={(event) => setLocation(event.target.value)}
        />

        <input
          placeholder="Number of leads, e.g. 50"
          value={quantity}
          onChange={(event) => setQuantity(event.target.value)}
        />

        <button className="secondary" type="submit">
          Find Leads
        </button>

        {validationError ? (
          <p
            className="dashboard-v2-error"
            role="alert"
          >
            {validationError}
          </p>
        ) : null}
      </form>
    </div>
  );
}

export default LeadSearchForm;