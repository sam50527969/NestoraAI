import {
  useCallback,
  useEffect,
  useState,
} from "react";

import {
  approveCEOApproval,
  getCEOApprovals,
  rejectCEOApproval,
} from "../../../api";

import Badge from "../../ui/Badge";
import Card from "../../ui/Card";

import "./CEOApprovalQueue.css";

function formatDate(value) {
  if (!value) {
    return "—";
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

function getStatusVariant(status) {
  if (status === "approved") {
    return "success";
  }

  if (status === "rejected") {
    return "danger";
  }

  return "primary";
}

export default function CEOApprovalQueue() {
  const [approvals, setApprovals] =
    useState([]);

  const [isLoading, setIsLoading] =
    useState(true);

  const [activeApprovalUid, setActiveApprovalUid] =
    useState("");

  const [errorMessage, setErrorMessage] =
    useState("");

  const loadApprovals = useCallback(
    async () => {
      setIsLoading(true);
      setErrorMessage("");

      try {
        const response =
          await getCEOApprovals({
            limit: 100,
          });

        setApprovals(
          Array.isArray(response)
            ? response
            : [],
        );
      } catch (error) {
        console.error(
          "Unable to load CEO approvals:",
          error,
        );

        setErrorMessage(
          "Unable to load CEO approval requests.",
        );
      } finally {
        setIsLoading(false);
      }
    },
    [],
  );

  useEffect(() => {
    loadApprovals();
  }, [loadApprovals]);

  async function handleDecision(
    approval,
    decision,
  ) {
    setActiveApprovalUid(
      approval.approval_uid,
    );

    setErrorMessage("");

    try {
      const decide =
        decision === "approved"
          ? approveCEOApproval
          : rejectCEOApproval;

      const updatedApproval =
        await decide(
          approval.approval_uid,
          {
            reviewed_by: "CEO",
          },
        );

      setApprovals((current) =>
        current.map((item) =>
          item.approval_uid ===
          updatedApproval.approval_uid
            ? updatedApproval
            : item,
        ),
      );
    } catch (error) {
      console.error(
        "Unable to update CEO approval:",
        error,
      );

      setErrorMessage(
        error?.message ||
          "Unable to update the approval request.",
      );
    } finally {
      setActiveApprovalUid("");
    }
  }

  const pendingCount = approvals.filter(
    (approval) =>
      approval.status === "pending",
  ).length;

  return (
    <Card className="ceo-approval-queue">
      <div className="ceo-approval-header">
        <div>
          <p className="eyebrow">
            CEO Governance
          </p>

          <h2>Approval Queue</h2>

          <p>
            Review actions proposed by the
            CEO Agent before execution.
          </p>
        </div>

        <div className="ceo-approval-header-actions">
          <Badge
            variant={
              pendingCount
                ? "primary"
                : "success"
            }
          >
            {pendingCount} Pending
          </Badge>

          <button
            type="button"
            className="ceo-approval-refresh-button"
            onClick={loadApprovals}
            disabled={isLoading}
          >
            Refresh
          </button>
        </div>
      </div>

      {errorMessage && (
        <div className="ceo-approval-error">
          {errorMessage}
        </div>
      )}

      {isLoading ? (
        <div className="ceo-approval-state">
          Loading approval requests...
        </div>
      ) : approvals.length ? (
        <div className="ceo-approval-list">
          {approvals.map((approval) => {
            const isUpdating =
              activeApprovalUid ===
              approval.approval_uid;

            return (
              <article
                className={`ceo-approval-item status-${approval.status}`}
                key={approval.approval_uid}
              >
                <div className="ceo-approval-item-header">
                  <div>
                    <span className="ceo-approval-type">
                      {approval.decision_type
                        .replaceAll("_", " ")}
                    </span>

                    <h3>
                      {approval.title}
                    </h3>
                  </div>

                  <Badge
                    variant={getStatusVariant(
                      approval.status,
                    )}
                  >
                    {approval.status}
                  </Badge>
                </div>

                {approval.description && (
                  <p className="ceo-approval-description">
                    {approval.description}
                  </p>
                )}

                <div className="ceo-approval-meta">
                  <span>
                    Requested by{" "}
                    {approval.requested_by}
                  </span>

                  <span>
                    {formatDate(
                      approval.created_at,
                    )}
                  </span>
                </div>

                {approval.status ===
                "pending" ? (
                  <div className="ceo-approval-actions">
                    <button
                      type="button"
                      className="ceo-approval-button approve"
                      disabled={isUpdating}
                      onClick={() =>
                        handleDecision(
                          approval,
                          "approved",
                        )
                      }
                    >
                      {isUpdating
                        ? "Updating..."
                        : "Approve"}
                    </button>

                    <button
                      type="button"
                      className="ceo-approval-button reject"
                      disabled={isUpdating}
                      onClick={() =>
                        handleDecision(
                          approval,
                          "rejected",
                        )
                      }
                    >
                      Reject
                    </button>
                  </div>
                ) : (
                  <div className="ceo-approval-reviewed">
                    Reviewed by{" "}
                    {approval.reviewed_by ||
                      "CEO"}{" "}
                    on{" "}
                    {formatDate(
                      approval.reviewed_at,
                    )}
                  </div>
                )}
              </article>
            );
          })}
        </div>
      ) : (
        <div className="ceo-approval-state">
          No approval requests are waiting.
        </div>
      )}
    </Card>
  );
}