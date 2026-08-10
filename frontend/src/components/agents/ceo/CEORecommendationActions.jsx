import {
  useState,
} from "react";
import PropTypes from "prop-types";

import {
  createCEOApproval,
} from "../../../api";

import Card from "../../ui/Card";

import "./CEORecommendationActions.css";


function isOutreachRecommendation(
  recommendation,
) {
  const value = String(
    recommendation || "",
  ).toLowerCase();

  return (
    value.includes("outreach")
    || value.includes("high-priority")
    || value.includes("high priority")
  );
}


function buildApprovalRequest(
  recommendation,
  highPriorityCount,
) {
  return {
    title: "Approve priority lead outreach",
    description: recommendation,
    decision_type: "crm_outreach",
    source_type: "ceo_recommendation",
    requested_by: "CEO Agent",
    payload: {
      high_priority_count:
        Math.max(
          1,
          Number(highPriorityCount) || 1,
        ),
    },
  };
}


export default function CEORecommendationActions({
  recommendations = [],
  highPriorityCount = 0,
  onApprovalCreated,
}) {
  const [
    activeRecommendation,
    setActiveRecommendation,
  ] = useState("");

  const [
    submittedRecommendations,
    setSubmittedRecommendations,
  ] = useState([]);

  const [
    errorMessage,
    setErrorMessage,
  ] = useState("");


  async function handleRequestApproval(
    recommendation,
  ) {
    setActiveRecommendation(
      recommendation,
    );

    setErrorMessage("");

    try {
      const approval =
        await createCEOApproval(
          buildApprovalRequest(
            recommendation,
            highPriorityCount,
          ),
        );

      setSubmittedRecommendations(
        (current) => [
          ...current,
          recommendation,
        ],
      );

      if (onApprovalCreated) {
        onApprovalCreated(approval);
      }
    } catch (error) {
      console.error(
        "Unable to create CEO approval:",
        error,
      );

      setErrorMessage(
        error?.message
        || "Unable to submit the recommendation for approval.",
      );
    } finally {
      setActiveRecommendation("");
    }
  }


  return (
    <Card className="ceo-decisions-card">
      <p className="eyebrow">
        Recommended Decisions
      </p>

      <h2>What to Do Next</h2>

      {errorMessage && (
        <div className="ceo-recommendation-error">
          {errorMessage}
        </div>
      )}

      {recommendations.length ? (
        <div className="ceo-recommendation-list">
          {recommendations.map(
            (
              recommendation,
              index,
            ) => {
              const supportsApproval =
                isOutreachRecommendation(
                  recommendation,
                );

              const isSubmitting =
                activeRecommendation ===
                recommendation;

              const wasSubmitted =
                submittedRecommendations.includes(
                  recommendation,
                );

              return (
                <div
                  className="ceo-recommendation-item"
                  key={`${index}-${recommendation}`}
                >
                  <span>
                    {index + 1}
                  </span>

                  <div className="ceo-recommendation-content">
                    <p>
                      {recommendation}
                    </p>

                    {supportsApproval && (
                      <button
                        type="button"
                        className="ceo-recommendation-approval-button"
                        disabled={
                          isSubmitting
                          || wasSubmitted
                        }
                        onClick={() =>
                          handleRequestApproval(
                            recommendation,
                          )
                        }
                      >
                        {isSubmitting
                          ? "Submitting..."
                          : wasSubmitted
                            ? "Sent for Approval"
                            : "Request CEO Approval"}
                      </button>
                    )}
                  </div>
                </div>
              );
            },
          )}
        </div>
      ) : (
        <p className="ceo-empty-state">
          No recommended decisions are
          available.
        </p>
      )}
    </Card>
  );
}


CEORecommendationActions.propTypes = {
  recommendations: PropTypes.arrayOf(
    PropTypes.string,
  ),
  highPriorityCount: PropTypes.number,
  onApprovalCreated: PropTypes.func,
};