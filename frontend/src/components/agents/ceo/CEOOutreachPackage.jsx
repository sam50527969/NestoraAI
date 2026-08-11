import {
  useState,
} from "react";
import PropTypes from "prop-types";

import "./CEOOutreachPackage.css";

function formatDate(value) {
  if (!value) {
    return "";
  }

  const date = new Date(value);

  if (Number.isNaN(date.getTime())) {
    return value;
  }

  return new Intl.DateTimeFormat(
    "en-US",
    {
      dateStyle: "medium",
      timeStyle: "short",
    },
  ).format(date);
}

function OutreachSection({
  label,
  value,
  onCopy,
  copiedField,
  field,
}) {
  if (!value) {
    return null;
  }

  return (
    <section className="ceo-outreach-section">
      <div className="ceo-outreach-section-header">
        <h4>{label}</h4>

        <button
          type="button"
          onClick={() =>
            onCopy(field, value)
          }
        >
          {copiedField === field
            ? "Copied"
            : "Copy"}
        </button>
      </div>

      <p>{value}</p>
    </section>
  );
}

OutreachSection.propTypes = {
  label: PropTypes.string.isRequired,
  value: PropTypes.string,
  onCopy: PropTypes.func.isRequired,
  copiedField: PropTypes.string,
  field: PropTypes.string.isRequired,
};

export default function CEOOutreachPackage({
  outreach,
  onMarkSent,
  isUpdating = false,
}) {
  const [isExpanded, setIsExpanded] =
    useState(false);

  const [copiedField, setCopiedField] =
    useState("");

  async function handleCopy(
    field,
    value,
  ) {
    try {
      await navigator.clipboard.writeText(
        value,
      );

      setCopiedField(field);

      window.setTimeout(() => {
        setCopiedField("");
      }, 1600);
    } catch (error) {
      console.error(
        "Unable to copy outreach content:",
        error,
      );
    }
  }

  const hasScore =
    outreach.score != null;

  const hasEstimatedValue =
    outreach.estimated_value != null;

  const status =
    outreach.status || "prepared";

  const canMarkSent =
    Boolean(
      outreach.activity_uid &&
      status === "prepared" &&
      onMarkSent,
    );

  return (
    <article
      className={`ceo-outreach-package ${
        isExpanded ? "expanded" : ""
      } status-${status}`}
    >
      <button
        type="button"
        className="ceo-outreach-package-summary"
        onClick={() =>
          setIsExpanded(
            (current) => !current,
          )
        }
        aria-expanded={isExpanded}
      >
        <div>
          <strong>
            {outreach.lead_name}
          </strong>

          <span>
            {outreach.priority ||
              outreach.prepared_by ||
              "CEO Agent"}

            {hasScore &&
              ` - Score ${outreach.score}`}
          </span>
        </div>

        <div className="ceo-outreach-package-controls">
          <span
            className={`ceo-outreach-package-status status-${status}`}
          >
            {status}
          </span>

          <span className="ceo-outreach-package-toggle">
            {isExpanded ? "-" : "+"}
          </span>
        </div>
      </button>

      {isExpanded && (
        <div className="ceo-outreach-package-details">
          <div className="ceo-outreach-contact-grid">
            <div>
              <span>Phone</span>

              <strong>
                {outreach.phone ||
                  "Not available"}
              </strong>
            </div>

            <div>
              <span>Website</span>

              {outreach.website ? (
                <a
                  href={outreach.website}
                  target="_blank"
                  rel="noreferrer"
                >
                  Open website
                </a>
              ) : (
                <strong>
                  Not available
                </strong>
              )}
            </div>

            {hasEstimatedValue && (
              <div>
                <span>
                  Estimated Value
                </span>

                <strong>
                  QAR{" "}
                  {Number(
                    outreach.estimated_value,
                  ).toLocaleString(
                    "en-US",
                  )}
                </strong>
              </div>
            )}
          </div>

          {status === "sent" &&
            outreach.sent_at && (
              <div className="ceo-outreach-sent-notice">
                Marked as sent on{" "}
                {formatDate(
                  outreach.sent_at,
                )}
              </div>
            )}

          <OutreachSection
            label="Email Subject"
            value={outreach.email_subject}
            field="email_subject"
            onCopy={handleCopy}
            copiedField={copiedField}
          />

          <OutreachSection
            label="Email Body"
            value={outreach.email_body}
            field="email_body"
            onCopy={handleCopy}
            copiedField={copiedField}
          />

          <OutreachSection
            label="WhatsApp Message"
            value={
              outreach.whatsapp_message
            }
            field="whatsapp_message"
            onCopy={handleCopy}
            copiedField={copiedField}
          />

          <OutreachSection
            label="Cold Call Script"
            value={
              outreach.cold_call_script
            }
            field="cold_call_script"
            onCopy={handleCopy}
            copiedField={copiedField}
          />

          <OutreachSection
            label="Proposal Summary"
            value={
              outreach.proposal_summary
            }
            field="proposal_summary"
            onCopy={handleCopy}
            copiedField={copiedField}
          />

          {canMarkSent && (
            <div className="ceo-outreach-lifecycle-actions">
              <button
                type="button"
                className="ceo-outreach-mark-sent-button"
                disabled={isUpdating}
                onClick={() =>
                  onMarkSent(outreach)
                }
              >
                {isUpdating
                  ? "Updating..."
                  : "Mark as Sent"}
              </button>
            </div>
          )}
        </div>
      )}
    </article>
  );
}

CEOOutreachPackage.propTypes = {
  outreach: PropTypes.shape({
    activity_uid: PropTypes.string,
    lead_name: PropTypes.string.isRequired,
    phone: PropTypes.string,
    website: PropTypes.string,
    priority: PropTypes.string,
    prepared_by: PropTypes.string,
    status: PropTypes.string,
    score: PropTypes.number,
    estimated_value: PropTypes.number,
    email_subject: PropTypes.string,
    email_body: PropTypes.string,
    whatsapp_message: PropTypes.string,
    cold_call_script: PropTypes.string,
    proposal_summary: PropTypes.string,
    sent_at: PropTypes.string,
  }).isRequired,
  onMarkSent: PropTypes.func,
  isUpdating: PropTypes.bool,
};