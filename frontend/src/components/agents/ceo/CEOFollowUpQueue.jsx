import {
  useCallback,
  useEffect,
  useState,
} from "react";
import PropTypes from "prop-types";

import {
  getDueFollowUps,
} from "../../../api";

import Badge from "../../ui/Badge";
import Card from "../../ui/Card";
import CEOFollowUpOutcomeForm from "./CEOFollowUpOutcomeForm";

import "./CEOFollowUpQueue.css";


function formatDate(value) {
  if (!value) {
    return "Not scheduled";
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


export default function CEOFollowUpQueue({
  businessUid,
  onOutcomeRecorded = () => {},
}) {
  const [followUps, setFollowUps] =
    useState([]);

  const [isLoading, setIsLoading] =
    useState(true);

  const [
    activeLeadId,
    setActiveLeadId,
  ] = useState(null);

  const [
    errorMessage,
    setErrorMessage,
  ] = useState("");


  const loadFollowUps = useCallback(
    async () => {
      setIsLoading(true);
      setErrorMessage("");

      try {
        const response =
          await getDueFollowUps({
            limit: 100,
          });

        setFollowUps(
          Array.isArray(response)
            ? response
            : [],
        );
      } catch (error) {
        console.error(
          "Unable to load CRM follow-ups:",
          error,
        );

        setErrorMessage(
          error?.message ||
            "Unable to load CRM follow-ups.",
        );
      } finally {
        setIsLoading(false);
      }
    },
    [],
  );


  useEffect(() => {
    loadFollowUps();
  }, [loadFollowUps, businessUid]);


  function handleOutcomeRecorded(
    activity,
  ) {
    setFollowUps((current) =>
      current.filter(
        (lead) =>
          lead.id !== activity.lead_id,
      ),
    );

    setActiveLeadId(null);

    onOutcomeRecorded(activity);
  }


  return (
    <Card className="ceo-follow-up-queue">
      <div className="ceo-follow-up-header">
        <div>
          <p className="eyebrow">
            CRM Follow-ups
          </p>

          <h2>Due Follow-up Queue</h2>

          <p>
            Record each follow-up result,
            update the CRM stage, or
            schedule the next action.
          </p>
        </div>

        <div className="ceo-follow-up-header-actions">
          <Badge
            variant={
              followUps.length
                ? "primary"
                : "success"
            }
          >
            {followUps.length} Due
          </Badge>

          <button
            type="button"
            className="ceo-follow-up-refresh"
            onClick={loadFollowUps}
            disabled={isLoading}
          >
            {isLoading
              ? "Refreshing..."
              : "Refresh"}
          </button>
        </div>
      </div>

      {errorMessage && (
        <div className="ceo-follow-up-error">
          {errorMessage}
        </div>
      )}

      {isLoading ? (
        <div className="ceo-follow-up-state">
          Loading due follow-ups...
        </div>
      ) : followUps.length ? (
        <div className="ceo-follow-up-list">
          {followUps.map((lead) => {
            const isOutcomeOpen =
              activeLeadId === lead.id;

            return (
              <article
                className="ceo-follow-up-item"
                key={lead.id}
              >
                <div className="ceo-follow-up-item-heading">
                  <div>
                    <span>
                      {lead.category ||
                        "CRM Lead"}
                    </span>

                    <h3>{lead.name}</h3>
                  </div>

                  <Badge variant="primary">
                    {lead.priority}
                  </Badge>
                </div>

                <div className="ceo-follow-up-details">
                  <div>
                    <span>Status</span>

                    <strong>
                      {lead.status}
                    </strong>
                  </div>

                  <div>
                    <span>Due</span>

                    <strong>
                      {formatDate(
                        lead.next_follow_up,
                      )}
                    </strong>
                  </div>

                  <div>
                    <span>
                      Last Contacted
                    </span>

                    <strong>
                      {formatDate(
                        lead.last_contacted,
                      )}
                    </strong>
                  </div>
                </div>

                {!isOutcomeOpen && (
                  <div className="ceo-follow-up-actions">
                    <button
                      type="button"
                      className="ceo-follow-up-complete"
                      onClick={() =>
                        setActiveLeadId(
                          lead.id,
                        )
                      }
                    >
                      Record Outcome
                    </button>
                  </div>
                )}

                {isOutcomeOpen && (
                  <CEOFollowUpOutcomeForm
                    lead={lead}
                    onRecorded={
                      handleOutcomeRecorded
                    }
                    onCancel={() =>
                      setActiveLeadId(null)
                    }
                  />
                )}
              </article>
            );
          })}
        </div>
      ) : (
        <div className="ceo-follow-up-state success">
          No CRM follow-ups are currently
          overdue.
        </div>
      )}
    </Card>
  );
}


CEOFollowUpQueue.propTypes = {
  businessUid: PropTypes.string,
  onOutcomeRecorded: PropTypes.func,
};
