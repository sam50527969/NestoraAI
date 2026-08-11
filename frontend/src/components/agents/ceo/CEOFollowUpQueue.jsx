import {
  useCallback,
  useEffect,
  useState,
} from "react";

import {
  getDueFollowUps,
  updateLead,
} from "../../../api";

import Badge from "../../ui/Badge";
import Card from "../../ui/Card";

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


function getDefaultRescheduleValue() {
  const date = new Date();

  date.setDate(
    date.getDate() + 1,
  );

  date.setHours(
    9,
    0,
    0,
    0,
  );

  const offset =
    date.getTimezoneOffset() * 60000;

  return new Date(
    date.getTime() - offset,
  )
    .toISOString()
    .slice(0, 16);
}


export default function CEOFollowUpQueue() {
  const [followUps, setFollowUps] =
    useState([]);

  const [isLoading, setIsLoading] =
    useState(true);

  const [
    activeLeadId,
    setActiveLeadId,
  ] = useState(null);

  const [
    rescheduleValues,
    setRescheduleValues,
  ] = useState({});

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
  }, [loadFollowUps]);


  function removeLead(
    leadId,
  ) {
    setFollowUps((current) =>
      current.filter(
        (lead) =>
          lead.id !== leadId,
      ),
    );
  }


  async function handleComplete(
    lead,
  ) {
    setActiveLeadId(lead.id);
    setErrorMessage("");

    try {
      await updateLead(
        lead.id,
        {
          next_follow_up: null,
        },
      );

      removeLead(lead.id);
    } catch (error) {
      console.error(
        "Unable to complete follow-up:",
        error,
      );

      setErrorMessage(
        error?.message ||
          "Unable to complete the follow-up.",
      );
    } finally {
      setActiveLeadId(null);
    }
  }


  async function handleReschedule(
    lead,
  ) {
    const selectedValue =
      rescheduleValues[lead.id] ||
      getDefaultRescheduleValue();

    const selectedDate =
      new Date(selectedValue);

    if (
      Number.isNaN(
        selectedDate.getTime(),
      )
    ) {
      setErrorMessage(
        "Choose a valid follow-up date.",
      );

      return;
    }

    if (
      selectedDate.getTime() <=
      Date.now()
    ) {
      setErrorMessage(
        "The new follow-up date must be in the future.",
      );

      return;
    }

    setActiveLeadId(lead.id);
    setErrorMessage("");

    try {
      await updateLead(
        lead.id,
        {
          next_follow_up:
            selectedDate.toISOString(),
        },
      );

      removeLead(lead.id);
    } catch (error) {
      console.error(
        "Unable to reschedule follow-up:",
        error,
      );

      setErrorMessage(
        error?.message ||
          "Unable to reschedule the follow-up.",
      );
    } finally {
      setActiveLeadId(null);
    }
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
            Complete overdue CRM tasks or
            reschedule them for a future
            date.
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
            const isUpdating =
              activeLeadId === lead.id;

            const rescheduleValue =
              rescheduleValues[lead.id] ||
              getDefaultRescheduleValue();

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
                    <span>Last Contacted</span>
                    <strong>
                      {formatDate(
                        lead.last_contacted,
                      )}
                    </strong>
                  </div>
                </div>

                <div className="ceo-follow-up-actions">
                  <button
                    type="button"
                    className="ceo-follow-up-complete"
                    disabled={isUpdating}
                    onClick={() =>
                      handleComplete(lead)
                    }
                  >
                    {isUpdating
                      ? "Updating..."
                      : "Complete"}
                  </button>

                  <div className="ceo-follow-up-reschedule">
                    <input
                      type="datetime-local"
                      value={
                        rescheduleValue
                      }
                      disabled={isUpdating}
                      onChange={(event) =>
                        setRescheduleValues(
                          (current) => ({
                            ...current,
                            [lead.id]:
                              event.target.value,
                          }),
                        )
                      }
                    />

                    <button
                      type="button"
                      disabled={isUpdating}
                      onClick={() =>
                        handleReschedule(
                          lead,
                        )
                      }
                    >
                      Reschedule
                    </button>
                  </div>
                </div>
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