import {
  useCallback,
  useEffect,
  useState,
} from "react";
import PropTypes from "prop-types";

import {
  approveCEOApproval,
  executeCEOApproval,
  getCEOApprovals,
  rejectCEOApproval,
} from "../../../api";

import CEOOutreachPackage from "./CEOOutreachPackage";
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
  if (
    status === "approved"
    || status === "executed"
  ) {
    return "success";
  }

  if (status === "rejected") {
    return "danger";
  }

  return "primary";
}


function getExecutionResult(approval) {
  return (
    approval?.payload?.execution_result
    || null
  );
}


function getOutreachPackages(approval) {
  const result = getExecutionResult(
    approval,
  );

  return Array.isArray(
    result?.outreach_packages,
  )
    ? result.outreach_packages
    : [];
}


export default function CEOApprovalQueue({
  businessUid,
  currency = "",
}) {
  const [approvals, setApprovals] =
    useState([]);

  const [isLoading, setIsLoading] =
    useState(true);

  const [
    activeApprovalUid,
    setActiveApprovalUid,
  ] = useState("");

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
  }, [loadApprovals, businessUid]);


  function updateApproval(
    updatedApproval,
  ) {
    setApprovals((current) =>
      current.map((item) =>
        item.approval_uid ===
        updatedApproval.approval_uid
          ? updatedApproval
          : item,
      ),
    );
  }


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

      updateApproval(
        updatedApproval,
      );
    } catch (error) {
      console.error(
        "Unable to update CEO approval:",
        error,
      );

      setErrorMessage(
        error?.message
        || "Unable to update the approval request.",
      );
    } finally {
      setActiveApprovalUid("");
    }
  }


  async function handleExecute(
    approval,
  ) {
    setActiveApprovalUid(
      approval.approval_uid,
    );

    setErrorMessage("");

    try {
      const updatedApproval =
        await executeCEOApproval(
          approval.approval_uid,
        );

      updateApproval(
        updatedApproval,
      );
    } catch (error) {
      console.error(
        "Unable to execute approved action:",
        error,
      );

      setErrorMessage(
        error?.message
        || "Unable to execute the approved action.",
      );
    } finally {
      setActiveApprovalUid("");
    }
  }


  const pendingCount = approvals.filter(
    (approval) =>
      approval.status === "pending",
  ).length;

  const approvedCount = approvals.filter(
    (approval) =>
      approval.status === "approved",
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

          {approvedCount > 0 && (
            <Badge variant="success">
              {approvedCount} Ready
            </Badge>
          )}

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

            const executionResult =
              getExecutionResult(
                approval,
              );

            const outreachPackages =
              getOutreachPackages(
                approval,
              );

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
                "pending" && (
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
                )}

                {approval.status ===
                "approved" && (
                  <>
                    <div className="ceo-approval-reviewed">
                      Approved by{" "}
                      {approval.reviewed_by
                        || "CEO"}{" "}
                      on{" "}
                      {formatDate(
                        approval.reviewed_at,
                      )}
                    </div>

                    <div className="ceo-approval-actions">
                      <button
                        type="button"
                        className="ceo-approval-button execute"
                        disabled={isUpdating}
                        onClick={() =>
                          handleExecute(
                            approval,
                          )
                        }
                      >
                        {isUpdating
                          ? "Executing..."
                          : "Execute Approved Action"}
                      </button>
                    </div>
                  </>
                )}

                {approval.status ===
                "rejected" && (
                  <div className="ceo-approval-reviewed">
                    Rejected by{" "}
                    {approval.reviewed_by
                      || "CEO"}{" "}
                    on{" "}
                    {formatDate(
                      approval.reviewed_at,
                    )}
                  </div>
                )}

                {approval.status ===
                "executed" && (
                  <div className="ceo-approval-execution">
                    <div className="ceo-approval-execution-header">
                      <div>
                        <span className="ceo-approval-type">
                          Execution Result
                        </span>

                        <h4>
                          {executionResult?.message
                            || "Approved action executed successfully."}
                        </h4>
                      </div>

                      <span className="ceo-approval-executed-at">
                        {formatDate(
                          approval.executed_at,
                        )}
                      </span>
                    </div>

                    {outreachPackages.length > 0 && (
                      <div className="ceo-approval-outreach-list">
                        {outreachPackages.map(
                          (
                            outreach,
                            index,
                          ) => (
                            <CEOOutreachPackage
                              key={
                                outreach.lead_id
                                || `${outreach.lead_name}-${index}`
                              }
                              outreach={
                                outreach
                              }
                              currency={
                                currency
                              }
                            />
                          ),
                        )}
                      </div>
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

CEOApprovalQueue.propTypes = {
  businessUid: PropTypes.string,
  currency: PropTypes.string,
};
