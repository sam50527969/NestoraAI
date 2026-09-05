import {
  useCallback,
  useEffect,
  useState,
} from "react";

import PropTypes from "prop-types";

import {
  getCEOExecution,
  getCEOExecutions,
} from "../../../api";

import Badge from "../../ui/Badge";
import Card from "../../ui/Card";

import "./CEOExecutionHistory.css";


function formatDate(value) {
  if (!value) {
    return "-";
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


function getStatusVariant(execution) {
  if (execution.success) {
    return "success";
  }

  if (
    execution.status === "failed"
    || execution.error
  ) {
    return "danger";
  }

  return "primary";
}


export default function CEOExecutionHistory({
  businessUid,
}) {
  const [executions, setExecutions] =
    useState([]);

  const [selectedExecution, setSelectedExecution] =
    useState(null);

  const [isLoading, setIsLoading] =
    useState(true);

  const [activeExecutionUid, setActiveExecutionUid] =
    useState("");

  const [errorMessage, setErrorMessage] =
    useState("");


  const loadExecutions = useCallback(
    async () => {
      setIsLoading(true);
      setErrorMessage("");

      try {
        const response =
          await getCEOExecutions({
            limit: 20,
            offset: 0,
          });

        setExecutions(
          Array.isArray(response?.executions)
            ? response.executions
            : [],
        );
      } catch (error) {
        console.error(
          "Unable to load CEO execution history:",
          error,
        );

        setErrorMessage(
          error?.message
          || "Unable to load CEO execution history.",
        );
      } finally {
        setIsLoading(false);
      }
    },
    [],
  );


  useEffect(() => {
    setSelectedExecution(null);
    setActiveExecutionUid("");
    loadExecutions();
  }, [loadExecutions, businessUid]);


  async function handleViewExecution(
    executionUid,
  ) {
    if (
      selectedExecution?.execution_uid
      === executionUid
    ) {
      setSelectedExecution(null);
      return;
    }

    setActiveExecutionUid(executionUid);
    setErrorMessage("");

    try {
      const response =
        await getCEOExecution(
          executionUid,
        );

      setSelectedExecution(response);
    } catch (error) {
      console.error(
        "Unable to load CEO execution:",
        error,
      );

      setErrorMessage(
        error?.message
        || "Unable to load execution details.",
      );
    } finally {
      setActiveExecutionUid("");
    }
  }


  const successfulCount =
    executions.filter(
      (execution) => execution.success,
    ).length;

  const failedCount =
    executions.filter(
      (execution) => !execution.success,
    ).length;


  return (
    <Card className="ceo-execution-history">
      <div className="ceo-execution-history-header">
        <div>
          <p className="eyebrow">
            Executive Audit Trail
          </p>

          <h2>Execution History</h2>

          <p>
            Review persistent results from
            CEO-approved executive actions.
          </p>
        </div>

        <div className="ceo-execution-history-actions">
          <Badge variant="success">
            {successfulCount} Successful
          </Badge>

          {failedCount > 0 && (
            <Badge variant="danger">
              {failedCount} Failed
            </Badge>
          )}

          <button
            type="button"
            className="ceo-execution-refresh-button"
            onClick={loadExecutions}
            disabled={isLoading}
          >
            {isLoading
              ? "Refreshing..."
              : "Refresh"}
          </button>
        </div>
      </div>

      {errorMessage && (
        <div className="ceo-execution-error">
          {errorMessage}
        </div>
      )}

      {isLoading ? (
        <div className="ceo-execution-state">
          Loading execution history...
        </div>
      ) : executions.length ? (
        <div className="ceo-execution-list">
          {executions.map((execution) => {
            const isActive =
              activeExecutionUid
              === execution.execution_uid;

            const isSelected =
              selectedExecution?.execution_uid
              === execution.execution_uid;

            return (
              <article
                className={`ceo-execution-item status-${execution.status}`}
                key={execution.execution_uid}
              >
                <div className="ceo-execution-item-header">
                  <div>
                    <span className="ceo-execution-uid">
                      {execution.execution_uid}
                    </span>

                    <h3>
                      {execution.objective}
                    </h3>
                  </div>

                  <Badge
                    variant={getStatusVariant(
                      execution,
                    )}
                  >
                    {execution.status}
                  </Badge>
                </div>

                <div className="ceo-execution-meta">
                  <span>
                    Approval:{" "}
                    {execution.approval_uid}
                  </span>

                  {execution.mission_id && (
                    <span>
                      Mission:{" "}
                      {execution.mission_id}
                    </span>
                  )}

                  {execution.workflow_id && (
                    <span>
                      Workflow:{" "}
                      {execution.workflow_id}
                    </span>
                  )}

                  <span>
                    {formatDate(
                      execution.completed_at
                      || execution.created_at,
                    )}
                  </span>
                </div>

                <div className="ceo-execution-counts">
                  <span>
                    {execution.completed_task_count}
                    {" "}completed
                  </span>

                  <span>
                    {execution.failed_task_count}
                    {" "}failed
                  </span>
                </div>

                {execution.error && (
                  <div className="ceo-execution-record-error">
                    {execution.error}
                  </div>
                )}

                <button
                  type="button"
                  className="ceo-execution-detail-button"
                  disabled={isActive}
                  onClick={() =>
                    handleViewExecution(
                      execution.execution_uid,
                    )
                  }
                >
                  {isActive
                    ? "Loading..."
                    : isSelected
                      ? "Hide Details"
                      : "View Details"}
                </button>

                {isSelected && (
                  <div className="ceo-execution-details">
                    <div className="ceo-execution-details-heading">
                      Execution Result
                    </div>

                    {selectedExecution.result ? (
                      <pre>
                        {JSON.stringify(
                          selectedExecution.result,
                          null,
                          2,
                        )}
                      </pre>
                    ) : (
                      <p>
                        No detailed execution result
                        is available.
                      </p>
                    )}
                  </div>
                )}
              </article>
            );
          })}
        </div>
      ) : (
        <div className="ceo-execution-state">
          No CEO executions have been recorded yet.
        </div>
      )}
    </Card>
  );
}


CEOExecutionHistory.propTypes = {
  businessUid: PropTypes.string,
};
