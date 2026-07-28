import { useState } from "react";
import {
  AlertCircle,
  CheckCircle2,
  Loader2,
  Rocket,
  Sparkles,
  Target,
  TrendingUp,
  Users,
} from "lucide-react";

import { createObjectiveMission } from "../api";


const DEFAULT_BUSINESS_ID = "biz_5d86879387a7";


function formatPercentage(value) {
  const number = Number(value);

  if (!Number.isFinite(number)) {
    return "—";
  }

  return `${Math.round(number * 100)}%`;
}


function formatROI(value) {
  const number = Number(value);

  if (!Number.isFinite(number)) {
    return "—";
  }

  return `${number.toFixed(1)}x`;
}


function AIMissionCreator() {
  const [businessId, setBusinessId] = useState(
    DEFAULT_BUSINESS_ID,
  );

  const [objective, setObjective] = useState(
    "Increase monthly revenue by 20% by improving patient follow-up, reducing appointment cancellations, and increasing repeat visits.",
  );

  const [mission, setMission] = useState(null);
  const [isGenerating, setIsGenerating] = useState(false);
  const [error, setError] = useState("");


  async function handleGenerateMission(event) {
    event.preventDefault();

    const cleanBusinessId = businessId.trim();
    const cleanObjective = objective.trim();

    if (!cleanBusinessId) {
      setError("Please select a business.");
      return;
    }

    if (cleanObjective.length < 3) {
      setError(
        "Please enter a business objective of at least 3 characters.",
      );
      return;
    }

    setError("");
    setMission(null);
    setIsGenerating(true);

    try {
      const response = await createObjectiveMission({
        businessId: cleanBusinessId,
        objective: cleanObjective,
      });

      setMission(response);
    } catch (requestError) {
      console.error(
        "Mission generation failed:",
        requestError,
      );

      setError(
        requestError?.message ||
          "Nestora could not generate the mission. Please check that the backend is running and try again.",
      );
    } finally {
      setIsGenerating(false);
    }
  }


  return (
    <div className="ai-mission-page">
      <section className="panel ai-mission-hero">
        <div>
          <p className="eyebrow">
            AI Workforce
          </p>

          <h1>AI Mission Creator</h1>

          <p className="page-description">
            Give Nestora a business objective. The AI CEO will
            analyze the business, identify opportunities and
            generate a coordinated mission for its executive
            workforce.
          </p>
        </div>

        <div className="ai-mission-hero-icon">
          <Rocket size={32} />
        </div>
      </section>

      <section className="panel">
        <div className="section-heading">
          <div>
            <p className="eyebrow">
              Mission Brief
            </p>

            <h2>Define the business objective</h2>
          </div>

          <Target size={24} />
        </div>

        <form
          className="ai-mission-form"
          onSubmit={handleGenerateMission}
        >
          <label className="form-field">
            <span>Business</span>

            <select
              value={businessId}
              onChange={(event) =>
                setBusinessId(event.target.value)
              }
              disabled={isGenerating}
            >
              <option value={DEFAULT_BUSINESS_ID}>
                Nestora Dental Clinic
              </option>
            </select>

            <small>
              Business ID: {businessId}
            </small>
          </label>

          <label className="form-field">
            <span>Business Objective</span>

            <textarea
              value={objective}
              onChange={(event) =>
                setObjective(event.target.value)
              }
              rows={6}
              maxLength={500}
              disabled={isGenerating}
              placeholder="Example: Increase monthly revenue by improving customer retention and reducing cancellations."
            />

            <small>
              {objective.length}/500 characters
            </small>
          </label>

          {error && (
            <div className="mission-error">
              <AlertCircle size={20} />

              <span>{error}</span>
            </div>
          )}

          <button
            type="submit"
            className="primary-button mission-generate-button"
            disabled={isGenerating}
          >
            {isGenerating ? (
              <>
                <Loader2
                  className="spin"
                  size={19}
                />

                AI CEO is planning...
              </>
            ) : (
              <>
                <Sparkles size={19} />

                Generate AI Mission
              </>
            )}
          </button>
        </form>
      </section>

      {mission && (
        <>
          <section className="mission-result-header">
            <div>
              <p className="eyebrow">
                Mission Generated
              </p>

              <h2>{mission.strategy?.title}</h2>

              <p>
                {mission.strategy?.summary}
              </p>
            </div>

            <div className="mission-status-badge">
              <CheckCircle2 size={18} />

              {mission.mission_status}
            </div>
          </section>

          <section className="mission-metrics-grid">
            <article className="panel mission-metric-card">
              <div className="mission-metric-icon">
                <Rocket size={21} />
              </div>

              <div>
                <span>Mission ID</span>

                <strong>
                  {mission.mission_uid}
                </strong>
              </div>
            </article>

            <article className="panel mission-metric-card">
              <div className="mission-metric-icon">
                <TrendingUp size={21} />
              </div>

              <div>
                <span>Estimated ROI</span>

                <strong>
                  {formatROI(
                    mission.strategy?.estimated_roi,
                  )}
                </strong>
              </div>
            </article>

            <article className="panel mission-metric-card">
              <div className="mission-metric-icon">
                <Target size={21} />
              </div>

              <div>
                <span>Confidence</span>

                <strong>
                  {formatPercentage(
                    mission.strategy?.confidence,
                  )}
                </strong>
              </div>
            </article>

            <article className="panel mission-metric-card">
              <div className="mission-metric-icon">
                <Users size={21} />
              </div>

              <div>
                <span>Executives</span>

                <strong>
                  {
                    mission.strategy?.executives
                      ?.length
                  }
                </strong>
              </div>
            </article>
          </section>

          <div className="mission-result-grid">
            <section className="panel">
              <div className="section-heading">
                <div>
                  <p className="eyebrow">
                    Opportunity Engine
                  </p>

                  <h2>Identified opportunities</h2>
                </div>

                <Sparkles size={23} />
              </div>

              <div className="opportunity-list">
                {mission.opportunities?.map(
                  (opportunity, index) => (
                    <article
                      className="opportunity-card"
                      key={`${opportunity.title}-${index}`}
                    >
                      <div className="opportunity-card-header">
                        <div>
                          <span className="opportunity-number">
                            {index + 1}
                          </span>

                          <h3>
                            {opportunity.title}
                          </h3>
                        </div>

                        <strong>
                          {formatPercentage(
                            opportunity.confidence,
                          )}
                        </strong>
                      </div>

                      <p>
                        {opportunity.description}
                      </p>

                      <div className="executive-chip-list">
                        {opportunity.executives?.map(
                          (executive) => (
                            <span
                              className="executive-chip"
                              key={executive}
                            >
                              {executive}
                            </span>
                          ),
                        )}
                      </div>
                    </article>
                  ),
                )}
              </div>
            </section>

            <section className="panel">
              <div className="section-heading">
                <div>
                  <p className="eyebrow">
                    Executive Team
                  </p>

                  <h2>Mission workforce</h2>
                </div>

                <Users size={23} />
              </div>

              <div className="executive-list">
                {mission.strategy?.executives?.map(
                  (executive, index) => (
                    <div
                      className="executive-row"
                      key={executive}
                    >
                      <div className="executive-row-number">
                        {index + 1}
                      </div>

                      <div>
                        <strong>{executive}</strong>

                        <span>
                          Assigned to mission
                        </span>
                      </div>

                      <CheckCircle2 size={19} />
                    </div>
                  ),
                )}
              </div>

              <button
                type="button"
                className="primary-button execute-mission-button"
                disabled
                title="Mission execution will be connected in the next step."
              >
                <Rocket size={19} />

                Execute Mission
              </button>

              <p className="execution-note">
                The mission has been saved as planned.
                Execution will be connected in the next step.
              </p>
            </section>
          </div>
        </>
      )}
    </div>
  );
}


export default AIMissionCreator;