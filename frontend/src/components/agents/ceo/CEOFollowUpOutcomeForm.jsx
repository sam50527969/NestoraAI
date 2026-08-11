import {
  useState,
} from "react";
import PropTypes from "prop-types";

import {
  recordFollowUpOutcome,
} from "../../../api";

import "./CEOFollowUpOutcomeForm.css";


const OUTCOME_OPTIONS = [
  {
    value: "contacted",
    label: "Contacted",
  },
  {
    value: "qualified",
    label: "Qualified",
  },
  {
    value: "won",
    label: "Won",
  },
  {
    value: "lost",
    label: "Lost",
  },
  {
    value: "no_response",
    label: "No Response",
  },
  {
    value: "rescheduled",
    label: "Rescheduled",
  },
];


function getDefaultFollowUpValue() {
  const date = new Date();

  date.setDate(
    date.getDate() + 2,
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


export default function CEOFollowUpOutcomeForm({
  lead,
  onRecorded,
  onCancel,
}) {
  const [outcome, setOutcome] =
    useState("contacted");

  const [notes, setNotes] =
    useState("");

  const [
    nextFollowUp,
    setNextFollowUp,
  ] = useState(
    getDefaultFollowUpValue(),
  );

  const [isSaving, setIsSaving] =
    useState(false);

  const [errorMessage, setErrorMessage] =
    useState("");


  const requiresFollowUp =
    outcome === "rescheduled" ||
    outcome === "no_response";


  async function handleSubmit(event) {
    event.preventDefault();
    setErrorMessage("");

    let nextFollowUpValue = null;

    if (requiresFollowUp) {
      const selectedDate =
        new Date(nextFollowUp);

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
          "The follow-up date must be in the future.",
        );

        return;
      }

      nextFollowUpValue =
        selectedDate.toISOString();
    }

    setIsSaving(true);

    try {
      const activity =
        await recordFollowUpOutcome(
          lead.id,
          {
            outcome,
            notes:
              notes.trim() || null,
            next_follow_up:
              nextFollowUpValue,
            completed_by: "CEO",
          },
        );

      onRecorded(activity);
    } catch (error) {
      console.error(
        "Unable to record follow-up outcome:",
        error,
      );

      setErrorMessage(
        error?.message ||
          "Unable to record the follow-up outcome.",
      );
    } finally {
      setIsSaving(false);
    }
  }


  return (
    <form
      className="ceo-follow-up-outcome-form"
      onSubmit={handleSubmit}
    >
      <div className="ceo-follow-up-outcome-heading">
        <div>
          <span>Record Outcome</span>
          <strong>{lead.name}</strong>
        </div>

        <button
          type="button"
          className="ceo-follow-up-outcome-close"
          onClick={onCancel}
          disabled={isSaving}
          aria-label="Close outcome form"
        >
          ×
        </button>
      </div>

      <div className="ceo-follow-up-outcome-fields">
        <label>
          <span>Outcome</span>

          <select
            value={outcome}
            disabled={isSaving}
            onChange={(event) =>
              setOutcome(
                event.target.value,
              )
            }
          >
            {OUTCOME_OPTIONS.map(
              (option) => (
                <option
                  value={option.value}
                  key={option.value}
                >
                  {option.label}
                </option>
              ),
            )}
          </select>
        </label>

        {requiresFollowUp && (
          <label>
            <span>Next Follow-up</span>

            <input
              type="datetime-local"
              value={nextFollowUp}
              disabled={isSaving}
              onChange={(event) =>
                setNextFollowUp(
                  event.target.value,
                )
              }
              required
            />
          </label>
        )}

        <label className="ceo-follow-up-outcome-notes">
          <span>Notes</span>

          <textarea
            value={notes}
            disabled={isSaving}
            placeholder="Add the result of the conversation or next action..."
            rows={3}
            onChange={(event) =>
              setNotes(
                event.target.value,
              )
            }
          />
        </label>
      </div>

      {errorMessage && (
        <div className="ceo-follow-up-outcome-error">
          {errorMessage}
        </div>
      )}

      <div className="ceo-follow-up-outcome-actions">
        <button
          type="button"
          className="secondary"
          onClick={onCancel}
          disabled={isSaving}
        >
          Cancel
        </button>

        <button
          type="submit"
          className="primary"
          disabled={isSaving}
        >
          {isSaving
            ? "Saving..."
            : "Save Outcome"}
        </button>
      </div>
    </form>
  );
}


CEOFollowUpOutcomeForm.propTypes = {
  lead: PropTypes.shape({
    id: PropTypes.number.isRequired,
    name: PropTypes.string.isRequired,
  }).isRequired,
  onRecorded: PropTypes.func.isRequired,
  onCancel: PropTypes.func.isRequired,
};