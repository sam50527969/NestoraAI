import { useEffect, useMemo, useState } from "react";

import {
  MARKETING_CHANNELS,
  createMarketingBusinessView,
  createMarketingRequestFromWorkspace,
  mergeMarketingRequestWithWorkspace,
  runMarketingDirector,
} from "../api/marketingApi";

import ExecutiveAssessment from "../components/marketing/ExecutiveAssessment";
import CompetitorIntelligence from "../components/competitors/CompetitorIntelligence";
import useWorkspace from "../workspace/useWorkspace";

function splitCommaSeparated(value) {
  return value
    .split(",")
    .map((item) => item.trim())
    .filter(Boolean);
}


function joinCommaSeparated(values) {
  return Array.isArray(values)
    ? values.join(", ")
    : "";
}


function SectionCard({
  title,
  children,
}) {
  return (
    <section className="panel">
      <div className="marketing-section-header">
        <h2>{title}</h2>
      </div>

      {children}
    </section>
  );
}


function ListBlock({
  title,
  items,
}) {
  if (!Array.isArray(items) || items.length === 0) {
    return null;
  }

  return (
    <div className="marketing-list-block">
      <h3>{title}</h3>

      <ul>
        {items.map((item, index) => (
          <li key={`${title}-${index}`}>
            {item}
          </li>
        ))}
      </ul>
    </div>
  );
}


function MetricCard({
  label,
  value,
}) {
  return (
    <div className="marketing-metric-card">
      <span>{label}</span>
      <strong>{value}</strong>
    </div>
  );
}


export default function MarketingDirector() {
  const {
    activeWorkspace,
  } = useWorkspace();

  const [request, setRequest] = useState(
    () => createMarketingRequestFromWorkspace(
      activeWorkspace,
    ),
  );

  const [result, setResult] = useState(null);
  const [error, setError] = useState("");
  const [isLoading, setIsLoading] = useState(false);

  const selectedCurrentChannels = useMemo(
    () => request.business.current_channels || [],
    [request.business.current_channels],
  );

  const selectedPreferredChannels = useMemo(
    () => request.goal.preferred_channels || [],
    [request.goal.preferred_channels],
  );

  const selectedBusiness = useMemo(
    () => createMarketingBusinessView(
      activeWorkspace,
    ),
    [activeWorkspace],
  );

  useEffect(() => {
    setRequest(
      createMarketingRequestFromWorkspace(
        activeWorkspace,
      ),
    );
    setResult(null);
    setError("");
  }, [
    activeWorkspace,
  ]);

  function updateBusinessField(
    field,
    value,
  ) {
    setRequest((current) => ({
      ...current,

      business: {
        ...current.business,
        [field]: value,
      },
    }));
  }

  function updateGoalField(
    field,
    value,
  ) {
    setRequest((current) => ({
      ...current,

      goal: {
        ...current.goal,
        [field]: value,
      },
    }));
  }

  function toggleBusinessChannel(
    channel,
  ) {
    setRequest((current) => {
      const channels =
        current.business.current_channels || [];

      const exists = channels.includes(channel);

      return {
        ...current,

        business: {
          ...current.business,

          current_channels: exists
            ? channels.filter(
                (item) => item !== channel,
              )
            : [...channels, channel],
        },
      };
    });
  }

  function togglePreferredChannel(
    channel,
  ) {
    setRequest((current) => {
      const channels =
        current.goal.preferred_channels || [];

      const exists = channels.includes(channel);

      return {
        ...current,

        goal: {
          ...current.goal,

          preferred_channels: exists
            ? channels.filter(
                (item) => item !== channel,
              )
            : [...channels, channel],
        },
      };
    });
  }

  async function handleSubmit(event) {
    event.preventDefault();

    setError("");
    setResult(null);
    setIsLoading(true);

    try {
      const authoritativeRequest =
        mergeMarketingRequestWithWorkspace(
          request,
          activeWorkspace,
        );

      const response = await runMarketingDirector(
        authoritativeRequest,
      );

      setResult(response);
    } catch (requestError) {
      setError(
        requestError?.message
          || "Marketing Director request failed.",
      );
    } finally {
      setIsLoading(false);
    }
  }

  function handleReset() {
    setRequest(
      createMarketingRequestFromWorkspace(
        activeWorkspace,
      ),
    );
    setResult(null);
    setError("");
  }

  return (
    <div className="page marketing-director-page">
      <div className="page-header">
        <div>
          <p className="page-eyebrow">
            AI Executive
          </p>

          <h1>Marketing Director</h1>

          <p className="page-description">
            Generate a complete marketing strategy,
            campaign plan, budget allocation, and
            performance forecast.
          </p>
        </div>
      </div>

      <form
        className="marketing-director-layout"
        onSubmit={handleSubmit}
      >
        <div className="marketing-form-column">
          <SectionCard title="Business Profile">
            <div className="marketing-form-grid">
              <label className="lead-field">
                <span>Business ID</span>

                <input
                  type="text"
                  value={request.business.business_id}
                  onChange={(event) => {
                    updateBusinessField(
                      "business_id",
                      event.target.value,
                    );
                  }}
                  placeholder="Authoritative workspace ID"
                  readOnly
                  required
                />
              </label>

              <label className="lead-field">
                <span>Business Name</span>

                <input
                  type="text"
                  value={request.business.business_name}
                  onChange={(event) => {
                    updateBusinessField(
                      "business_name",
                      event.target.value,
                    );
                  }}
                  placeholder="Business name"
                  readOnly
                  required
                />
              </label>

              <label className="lead-field">
                <span>Industry</span>

                <input
                  type="text"
                  value={request.business.industry}
                  onChange={(event) => {
                    updateBusinessField(
                      "industry",
                      event.target.value,
                    );
                  }}
                  placeholder="Configured industry"
                  readOnly
                  required
                />
              </label>

              <label className="lead-field">
                <span>Location</span>

                <input
                  type="text"
                  value={request.business.location || ""}
                  onChange={(event) => {
                    updateBusinessField(
                      "location",
                      event.target.value,
                    );
                  }}
                  placeholder="Configured location"
                  readOnly
                />
              </label>
            </div>

            <label className="lead-field">
              <span>Description</span>

              <textarea
                rows="4"
                value={request.business.description || ""}
                onChange={(event) => {
                  updateBusinessField(
                    "description",
                    event.target.value,
                  );
                }}
                placeholder="Describe the business, its services, and current market position."
              />
            </label>

            <div className="marketing-form-grid">
              <label className="lead-field">
                <span>Products or Services</span>

                <input
                  type="text"
                  value={joinCommaSeparated(
                    request.business.products_or_services,
                  )}
                  onChange={(event) => {
                    updateBusinessField(
                      "products_or_services",
                      splitCommaSeparated(
                        event.target.value,
                      ),
                    );
                  }}
                  placeholder="Configured products and services"
                  readOnly
                />
              </label>

              <label className="lead-field">
                <span>Target Audience</span>

                <input
                  type="text"
                  value={joinCommaSeparated(
                    request.business.target_audience,
                  )}
                  onChange={(event) => {
                    updateBusinessField(
                      "target_audience",
                      splitCommaSeparated(
                        event.target.value,
                      ),
                    );
                  }}
                  placeholder="Families, professionals"
                />
              </label>

              <label className="lead-field">
                <span>Differentiators</span>

                <input
                  type="text"
                  value={joinCommaSeparated(
                    request.business.differentiators,
                  )}
                  onChange={(event) => {
                    updateBusinessField(
                      "differentiators",
                      splitCommaSeparated(
                        event.target.value,
                      ),
                    );
                  }}
                  placeholder="Modern equipment, experienced team"
                />
              </label>

              <label className="lead-field">
                <span>Preferred Languages</span>

                <input
                  type="text"
                  value={joinCommaSeparated(
                    request.business.preferred_languages,
                  )}
                  readOnly
                  placeholder="English, Arabic"
                />
              </label>
            </div>

            <label className="lead-field">
              <span>Brand Voice</span>

              <input
                type="text"
                value={request.business.brand_voice || ""}
                onChange={(event) => {
                  updateBusinessField(
                    "brand_voice",
                    event.target.value,
                  );
                }}
                placeholder="Professional and friendly"
              />
            </label>

            <div className="lead-field">
              <span>Current Channels</span>

              <div className="marketing-channel-grid">
                {MARKETING_CHANNELS.map((channel) => {
                  const active =
                    selectedCurrentChannels.includes(
                      channel.value,
                    );

                  return (
                    <button
                      key={channel.value}
                      type="button"
                      className={
                        active
                          ? "marketing-channel-chip active"
                          : "marketing-channel-chip"
                      }
                      onClick={() => {
                        toggleBusinessChannel(
                          channel.value,
                        );
                      }}
                    >
                      {channel.label}
                    </button>
                  );
                })}
              </div>
            </div>
          </SectionCard>

          <SectionCard title="Marketing Goal">
            <label className="lead-field">
              <span>Objective</span>

              <textarea
                rows="3"
                value={request.goal.objective}
                onChange={(event) => {
                  updateGoalField(
                    "objective",
                    event.target.value,
                  );
                }}
                placeholder="Increase qualified leads or revenue"
                required
              />
            </label>

            <div className="marketing-form-grid">
              <label className="lead-field">
                <span>Timeline</span>

                <input
                  type="number"
                  min="1"
                  max="365"
                  value={request.goal.timeline_days}
                  onChange={(event) => {
                    updateGoalField(
                      "timeline_days",
                      Number(event.target.value),
                    );
                  }}
                />
              </label>

              <label className="lead-field">
                <span>Monthly Budget</span>

                <input
                  type="number"
                  min="0"
                  step="0.01"
                  value={request.goal.monthly_budget}
                  onChange={(event) => {
                    updateGoalField(
                      "monthly_budget",
                      Number(event.target.value),
                    );
                  }}
                />
              </label>

              <label className="lead-field">
                <span>Currency</span>

                <input
                  type="text"
                  maxLength="3"
                  value={request.goal.currency}
                  readOnly
                />
              </label>

              <label className="lead-field marketing-checkbox-field">
                <span>Approval Required</span>

                <input
                  type="checkbox"
                  checked={
                    request.goal.approval_required
                  }
                  onChange={(event) => {
                    updateGoalField(
                      "approval_required",
                      event.target.checked,
                    );
                  }}
                />
              </label>
            </div>

            <div className="lead-field">
              <span>Preferred Channels</span>

              <div className="marketing-channel-grid">
                {MARKETING_CHANNELS.map((channel) => {
                  const active =
                    selectedPreferredChannels.includes(
                      channel.value,
                    );

                  return (
                    <button
                      key={channel.value}
                      type="button"
                      className={
                        active
                          ? "marketing-channel-chip active"
                          : "marketing-channel-chip"
                      }
                      onClick={() => {
                        togglePreferredChannel(
                          channel.value,
                        );
                      }}
                    >
                      {channel.label}
                    </button>
                  );
                })}
              </div>
            </div>

            <label className="lead-field">
              <span>Additional Instructions</span>

              <textarea
                rows="3"
                value={
                  request.additional_instructions || ""
                }
                onChange={(event) => {
                  setRequest((current) => ({
                    ...current,
                    additional_instructions:
                      event.target.value,
                  }));
                }}
                placeholder="Add campaign-specific guidance."
              />
            </label>

            <div className="marketing-form-actions">
              <button
                type="button"
                className="button secondary"
                onClick={handleReset}
                disabled={isLoading}
              >
                Reset
              </button>

              <button
                type="submit"
                className="button primary"
                disabled={isLoading}
              >
                {isLoading
                  ? "Generating..."
                  : "Generate Marketing Plan"}
              </button>
            </div>

            {error ? (
              <div className="marketing-error">
                {error}
              </div>
            ) : null}
          </SectionCard>
        </div>

        <div className="marketing-results-column">
          {!result && !isLoading ? (
  <>
    <ExecutiveAssessment
      business={selectedBusiness}
    />

    <CompetitorIntelligence
      business={selectedBusiness}
    />
  </>
) : null}

          {isLoading ? (
            <section className="panel marketing-loading-state">
              <div className="marketing-loading-spinner" />

              <h2>Marketing Director is working</h2>

              <p>
                Analyzing the business, building the
                strategy, allocating budget, and
                predicting results.
              </p>
            </section>
          ) : null}

          {result ? (
            <>
              <SectionCard title="Executive Summary">
                <p>
                  {
                    result.strategy
                      ?.executive_summary
                  }
                </p>

                <div className="marketing-metrics-grid">
                  <MetricCard
                    label="Estimated Reach"
                    value={
                      result.prediction
                        ?.estimated_reach
                        ?.toLocaleString?.()
                      || 0
                    }
                  />

                  <MetricCard
                    label="Estimated Leads"
                    value={
                      result.prediction
                        ?.estimated_leads
                        ?.toLocaleString?.()
                      || 0
                    }
                  />

                  <MetricCard
                    label="Conversions"
                    value={
                      result.prediction
                        ?.estimated_conversions
                        ?.toLocaleString?.()
                      || 0
                    }
                  />

                  <MetricCard
                    label="Estimated ROI"
                    value={`${result.prediction?.estimated_roi_percentage || 0}%`}
                  />
                </div>
              </SectionCard>

              <SectionCard title="Business Analysis">
                <p>
                  {
                    result.analysis
                      ?.business_summary
                  }
                </p>

                <p>
                  {
                    result.analysis
                      ?.audience_summary
                  }
                </p>

                <div className="marketing-analysis-grid">
                  <ListBlock
                    title="Strengths"
                    items={
                      result.analysis
                        ?.strengths
                    }
                  />

                  <ListBlock
                    title="Weaknesses"
                    items={
                      result.analysis
                        ?.weaknesses
                    }
                  />

                  <ListBlock
                    title="Opportunities"
                    items={
                      result.analysis
                        ?.opportunities
                    }
                  />

                  <ListBlock
                    title="Risks"
                    items={
                      result.analysis
                        ?.risks
                    }
                  />
                </div>

                <div className="marketing-highlight">
                  <strong>
                    Recommended Positioning
                  </strong>

                  <p>
                    {
                      result.analysis
                        ?.recommended_positioning
                    }
                  </p>
                </div>
              </SectionCard>

              <SectionCard title="Marketing Strategy">
                <h3>
                  {result.strategy?.strategy_name}
                </h3>

                <p>
                  {result.strategy?.primary_objective}
                </p>

                <ListBlock
                  title="Target Segments"
                  items={
                    result.strategy
                      ?.target_segments
                  }
                />

                <ListBlock
                  title="Key Messages"
                  items={
                    result.strategy
                      ?.key_messages
                  }
                />

                <div className="marketing-channel-strategy-list">
                  {result.strategy?.channels?.map(
                    (channel) => (
                      <article
                        key={channel.channel}
                        className="marketing-channel-strategy-card"
                      >
                        <div>
                          <h3>
                            {channel.channel}
                          </h3>

                          <p>
                            {channel.objective}
                          </p>
                        </div>

                        <strong>
                          {
                            channel.budget_percentage
                          }
                          %
                        </strong>
                      </article>
                    ),
                  )}
                </div>
              </SectionCard>

              <SectionCard title="Budget Plan">
                <div className="marketing-budget-summary">
                  <MetricCard
                    label="Total Budget"
                    value={`${result.budget?.total_budget || 0} ${result.budget?.currency || ""}`}
                  />

                  <MetricCard
                    label="Reserve"
                    value={`${result.budget?.reserve_amount || 0} ${result.budget?.currency || ""}`}
                  />
                </div>

                <div className="marketing-budget-list">
                  {result.budget?.allocations?.map(
                    (item) => (
                      <article
                        key={item.channel}
                        className="marketing-budget-row"
                      >
                        <div>
                          <strong>
                            {item.channel}
                          </strong>

                          <p>
                            {item.rationale}
                          </p>
                        </div>

                        <div>
                          <strong>
                            {item.amount}{" "}
                            {
                              result.budget
                                ?.currency
                            }
                          </strong>

                          <span>
                            {item.percentage}%
                          </span>
                        </div>
                      </article>
                    ),
                  )}
                </div>
              </SectionCard>

              <SectionCard title="Campaign Timeline">
                <div className="marketing-week-list">
                  {result.campaign?.weeks?.map(
                    (week) => (
                      <article
                        key={week.week_number}
                        className="marketing-week-card"
                      >
                        <div className="marketing-week-number">
                          Week {week.week_number}
                        </div>

                        <h3>{week.theme}</h3>

                        <p>{week.objective}</p>

                        <ListBlock
                          title="Activities"
                          items={week.activities}
                        />
                      </article>
                    ),
                  )}
                </div>
              </SectionCard>

              <SectionCard title="Prediction">
                <div className="marketing-metrics-grid">
                  <MetricCard
                    label="Reach"
                    value={
                      result.prediction
                        ?.estimated_reach
                        ?.toLocaleString?.()
                      || 0
                    }
                  />

                  <MetricCard
                    label="Engagements"
                    value={
                      result.prediction
                        ?.estimated_engagements
                        ?.toLocaleString?.()
                      || 0
                    }
                  />

                  <MetricCard
                    label="Leads"
                    value={
                      result.prediction
                        ?.estimated_leads
                        ?.toLocaleString?.()
                      || 0
                    }
                  />

                  <MetricCard
                    label="Revenue"
                    value={`${result.prediction?.estimated_revenue || 0} ${result.budget?.currency || ""}`}
                  />
                </div>

                <ListBlock
                  title="Assumptions"
                  items={
                    result.prediction
                      ?.assumptions
                  }
                />
              </SectionCard>
            </>
          ) : null}
        </div>
      </form>
    </div>
  );
}