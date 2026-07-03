import { useState } from "react";

function LeadSearchForm({ onSearch }) {
  const [businessType, setBusinessType] = useState("");
  const [location, setLocation] = useState("");
  const [quantity, setQuantity] = useState("");

  function handleSubmit(event) {
    event.preventDefault();

    onSearch({
      businessType,
      location,
      quantity,
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
      </form>
    </div>
  );
}

export default LeadSearchForm;