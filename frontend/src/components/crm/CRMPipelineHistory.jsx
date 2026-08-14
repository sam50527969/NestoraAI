import PropTypes from "prop-types";
import {
  useCallback,
  useEffect,
  useState,
} from "react";

import {
  getPipelineActivities,
} from "../../api";

import Card from "../ui/Card";

import "./CRMPipelineHistory.css";


function formatDate(value) {
  if (!value) {
    return "Unknown date";
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


export default function CRMPipelineHistory({
  refreshKey = 0,
}) {
  const [activities, setActivities] =
    useState([]);

  const [isLoading, setIsLoading] =
    useState(true);

  const [
    errorMessage,
    setErrorMessage,
  ] = useState("");

  const loadActivities = useCallback(
    async () => {
      setIsLoading(true);
      setErrorMessage("");

      try {
        const response =
          await getPipelineActivities({
            limit: 100,
          });

        setActivities(
          Array.isArray(response)
            ? response
            : [],
        );
      } catch (error) {
        console.error(
          "Unable to load pipeline history:",
          error,
        );

        setErrorMessage(
          error?.message ||
            "Unable to load pipeline history.",
        );
      } finally {
        setIsLoading(false);
      }
    },
    [],
  );

  useEffect(() => {
    loadActivities();
  }, [
    loadActivities,
    refreshKey,
  ]);

  return (
    <Card className="crm-pipeline-history">
      <div className="crm-pipeline-history-header">
        <div>
          <p className="eyebrow">
            CRM Activity
          </p>

          <h2>
            Pipeline Stage History
          </h2>

          <p>
            Review recorded movements
            between CRM pipeline stages.
          </p>
        </div>

        <div className="crm-pipeline-history-actions">
          <span>
            {activities.length}
          </span>

          <button
            type="button"
            onClick={loadActivities}
            disabled={isLoading}
          >
            {isLoading
              ? "Refreshing..."
              : "Refresh"}
          </button>
        </div>
      </div>

      {errorMessage && (
        <div className="crm-pipeline-history-error">
          {errorMessage}
        </div>
      )}

      {isLoading ? (
        <div className="crm-pipeline-history-state">
          Loading pipeline history...
        </div>
      ) : activities.length ? (
        <div className="crm-pipeline-history-list">
          {activities.map(
            (activity) => (
              <article
                className="crm-pipeline-history-item"
                key={
                  activity.activity_uid
                }
              >
                <div className="crm-pipeline-history-item-header">
                  <div>
                    <h3>
                      {activity.lead_name}
                    </h3>

                    <span>
                      {formatDate(
                        activity.created_at,
                      )}
                    </span>
                  </div>

                  <span className="crm-pipeline-history-source">
                    {activity.source ||
                      "CRM Pipeline"}
                  </span>
                </div>

                <div className="crm-pipeline-history-transition">
                  <span>
                    {activity.previous_status}
                  </span>

                  <strong aria-hidden="true">
                    →
                  </strong>

                  <span className="current">
                    {activity.new_status}
                  </span>
                </div>

                <div className="crm-pipeline-history-footer">
                  Changed by{" "}
                  <strong>
                    {activity.changed_by ||
                      "CRM User"}
                  </strong>
                </div>

                {activity.notes && (
                  <p className="crm-pipeline-history-notes">
                    {activity.notes}
                  </p>
                )}
              </article>
            ),
          )}
        </div>
      ) : (
        <div className="crm-pipeline-history-state success">
          No pipeline stage changes have
          been recorded yet.
        </div>
      )}
    </Card>
  );
}


CRMPipelineHistory.propTypes = {
  refreshKey: PropTypes.number,
};