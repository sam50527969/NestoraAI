import {
  useEffect,
  useState,
} from "react";
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

import {
  createObjectiveMission,
  executePersistedMission,
} from "../api";
import useWorkspace from "../workspace/useWorkspace";
import "./AIMissionCreator.css";


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
  const { activeWorkspace } = useWorkspace();

  const [objective, setObjective] = useState("");

  const [mission, setMission] = useState(null);
  const [isGenerating, setIsGenerating] = useState(false);
  const [isExecuting, setIsExecuting] = useState(false);
  const [error, setError] = useState("");
  const [executionResult, setExecutionResult] = useState(null);

  useEffect(() => {
    setMission(null);
    setExecutionResult(null);
    setError("");
  }, [activeWorkspace?.business_uid]);


  async function handleGenerateMission(event) {
    event.preventDefault();

    const cleanObjective = objective.trim();

    if (!activeWorkspace) {
      setError("Please select an active workspace.");
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
    setExecutionResult(null);
    setIsGenerating(true);

    try {
      const response = await createObjectiveMission({
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


  async function handleExecuteMission() {
    const missionUid = mission?.mission_uid;

    if (!missionUid) {
      setError(
        "Mission ID is missing. Please generate the mission again.",
      );
      return;
    }

    setError("");
    setExecutionResult(null);
    setIsExecuting(true);

    try {
      const responseData = await executePersistedMission(
        missionUid,
      );

      setExecutionResult(responseData);

      setMission((currentMission) => ({
        ...currentMission,
        mission_status:
          responseData?.status || "completed",
      }));
    } catch (requestError) {
      console.error(
        "Mission execution failed:",
        requestError,
      );

      setError(
        requestError?.message ||
          "Nestora could not execute the mission. Please check the backend and try again.",
      );
    } finally {
      setIsExecuting(false);
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

            <input
              value={activeWorkspace?.name || ""}
              readOnly
              disabled={isGenerating}
            />

            <small>
              Active workspace: {activeWorkspace?.name || "None"}
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
                onClick={handleExecuteMission}
                disabled={
                  isExecuting ||
                  !mission?.mission_uid ||
                  mission?.mission_status === "completed"
                }
              >
                {isExecuting ? (
                  <>
                    <Loader2
                      className="spin"
                      size={19}
                    />

                    Executing Mission...
                  </>
                ) : mission?.mission_status === "completed" ? (
                  <>
                    <CheckCircle2 size={19} />

                    Mission Completed
                  </>
                ) : (
                  <>
                    <Rocket size={19} />

                    Execute Mission
                  </>
                )}
              </button>

              <p className="execution-note">
                {isExecuting
                  ? "Nestora's executives are processing the mission."
                  : executionResult?.message ||
                    "The mission is ready for execution."}
              </p>
            </section>
          </div>
        </>
      )}
    </div>
  );
}


export default AIMissionCreator;
