import {
  useCallback,
  useEffect,
  useState,
} from "react";

import {
  getOutreachActivities,
} from "../../../api";

import Badge from "../../ui/Badge";
import Card from "../../ui/Card";
import CEOOutreachPackage from "./CEOOutreachPackage";

import "./CEOOutreachHistory.css";


export default function CEOOutreachHistory() {
  const [activities, setActivities] =
    useState([]);

  const [isLoading, setIsLoading] =
    useState(true);

  const [errorMessage, setErrorMessage] =
    useState("");


  const loadActivities = useCallback(
    async () => {
      setIsLoading(true);
      setErrorMessage("");

      try {
        const response =
          await getOutreachActivities({
            limit: 100,
          });

        setActivities(
          Array.isArray(response)
            ? response
            : [],
        );
      } catch (error) {
        console.error(
          "Unable to load outreach history:",
          error,
        );

        setErrorMessage(
          error?.message ||
            "Unable to load outreach history.",
        );
      } finally {
        setIsLoading(false);
      }
    },
    [],
  );


  useEffect(() => {
    loadActivities();
  }, [loadActivities]);


  return (
    <Card className="ceo-outreach-history">
      <div className="ceo-outreach-history-header">
        <div>
          <p className="eyebrow">
            CRM Outreach
          </p>

          <h2>
            Prepared Outreach History
          </h2>

          <p>
            Review outreach assets saved
            from approved CEO actions.
          </p>
        </div>

        <div className="ceo-outreach-history-actions">
          <Badge variant="primary">
            {activities.length}
          </Badge>

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
        <div className="ceo-outreach-history-error">
          {errorMessage}
        </div>
      )}

      {isLoading ? (
        <div className="ceo-outreach-history-state">
          Loading outreach history...
        </div>
      ) : activities.length ? (
        <div className="ceo-outreach-history-list">
          {activities.map((activity) => (
            <CEOOutreachPackage
              key={activity.activity_uid}
              outreach={activity}
            />
          ))}
        </div>
      ) : (
        <div className="ceo-outreach-history-state">
          No saved outreach activities
          are available yet.
        </div>
      )}
    </Card>
  );
}