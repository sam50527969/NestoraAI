import {
  useCallback,
  useEffect,
  useState,
} from "react";

import {
  getOutreachActivities,
  markOutreachActivitySent,
} from "../../../api/outreachActivities";

import Badge from "../../ui/Badge";
import Card from "../../ui/Card";
import CEOOutreachPackage from "./CEOOutreachPackage";

import "./CEOOutreachHistory.css";

export default function CEOOutreachHistory() {
  const [activities, setActivities] =
    useState([]);

  const [isLoading, setIsLoading] =
    useState(true);

  const [
    activeActivityUid,
    setActiveActivityUid,
  ] = useState("");

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

  async function handleMarkSent(
    activity,
  ) {
    setActiveActivityUid(
      activity.activity_uid,
    );

    setErrorMessage("");

    try {
      const updatedActivity =
        await markOutreachActivitySent(
          activity.activity_uid,
        );

      setActivities((current) =>
        current.map((item) =>
          item.activity_uid ===
          updatedActivity.activity_uid
            ? updatedActivity
            : item,
        ),
      );
    } catch (error) {
      console.error(
        "Unable to mark outreach as sent:",
        error,
      );

      setErrorMessage(
        error?.message ||
          "Unable to update outreach status.",
      );
    } finally {
      setActiveActivityUid("");
    }
  }

  const preparedCount = activities.filter(
    (activity) =>
      activity.status === "prepared",
  ).length;

  const sentCount = activities.filter(
    (activity) =>
      activity.status === "sent",
  ).length;

  return (
    <Card className="ceo-outreach-history">
      <div className="ceo-outreach-history-header">
        <div>
          <p className="eyebrow">
            CRM Outreach
          </p>

          <h2>
            Outreach Activity History
          </h2>

          <p>
            Review prepared outreach and
            record when each package is sent.
          </p>
        </div>

        <div className="ceo-outreach-history-actions">
          <Badge variant="primary">
            {preparedCount} Prepared
          </Badge>

          <Badge variant="success">
            {sentCount} Sent
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
              onMarkSent={handleMarkSent}
              isUpdating={
                activeActivityUid ===
                activity.activity_uid
              }
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