import {
  Building2,
  CheckCircle2,
  Globe2,
  Loader2,
  MapPin,
  Phone,
  Sparkles,
} from "lucide-react";

import "./BusinessSelector.css";


function hasValue(value) {
  return Boolean(
    value
    && String(value).trim()
    && String(value).toLowerCase() !== "not found",
  );
}


export default function BusinessSelector({
  businesses = [],
  selectedBusinessId = "",
  isLoading = false,
  errorMessage = "",
  onSelect,
}) {
  const selectedBusiness = businesses.find(
    (business) =>
      String(business.id)
      === String(selectedBusinessId),
  );

  return (
    <section className="business-selector-panel">
      <header className="business-selector-header">
        <div>
          <p className="business-selector-eyebrow">
            <Sparkles size={15} strokeWidth={2.2} />
            Business Context
          </p>

          <h2>Select a CRM Business</h2>

          <p>
            Choose a saved lead and Nestora will populate
            the Marketing Director automatically.
          </p>
        </div>

        <div className="business-selector-count">
          <Building2 size={16} />
          {businesses.length} saved
        </div>
      </header>

      <label className="business-selector-field">
        <span>Current Business</span>

        <div className="business-selector-control">
          {isLoading ? (
            <Loader2
              className="business-selector-spin"
              size={18}
            />
          ) : (
            <Building2 size={18} />
          )}

          <select
            value={selectedBusinessId}
            onChange={(event) =>
              onSelect?.(event.target.value)
            }
            disabled={isLoading}
          >
            <option value="">
              Select a business from CRM
            </option>

            {businesses.map((business) => (
              <option
                key={business.id}
                value={business.id}
              >
                {business.name}
                {business.category
                  ? ` · ${business.category}`
                  : ""}
              </option>
            ))}
          </select>
        </div>
      </label>

      {errorMessage ? (
        <div className="business-selector-error">
          {errorMessage}
        </div>
      ) : null}

      {selectedBusiness ? (
        <div className="business-selector-card">
          <div className="business-selector-card-main">
            <div className="business-selector-icon">
              <Building2 size={22} />
            </div>

            <div>
              <div className="business-selector-title-row">
                <h3>{selectedBusiness.name}</h3>

                <span
                  className={`business-priority priority-${String(
                    selectedBusiness.priority || "medium",
                  ).toLowerCase()}`}
                >
                  {selectedBusiness.priority || "Medium"}
                </span>
              </div>

              <p>
                {selectedBusiness.category || "Business"}
              </p>
            </div>
          </div>

          <div className="business-selector-details">
            <span>
              <MapPin size={14} />
              {selectedBusiness.address
                || "Location not available"}
            </span>

            <span>
              <Phone size={14} />
              {selectedBusiness.phone
                || "Phone not available"}
            </span>

            <span>
              <Globe2 size={14} />
              {selectedBusiness.website
                || "Website not available"}
            </span>
          </div>

          <div className="business-selector-health">
            <span>
              <CheckCircle2 size={14} />
              CRM {selectedBusiness.status || "Saved"}
            </span>

            <span>
              Phone {hasValue(selectedBusiness.phone)
                ? "✓"
                : "Missing"}
            </span>

            <span>
              Website {hasValue(selectedBusiness.website)
                ? "✓"
                : "Missing"}
            </span>

            {selectedBusiness.aiScore !== null ? (
              <span>
                AI Score {selectedBusiness.aiScore}%
              </span>
            ) : null}
          </div>
        </div>
      ) : null}
    </section>
  );
}
