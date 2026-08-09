import { useMemo, useState } from "react";
import { Link } from "react-router-dom";
import {
  Activity,
  BarChart3,
  Brain,
  Building2,
  CalendarDays,
  CheckCircle2,
  ChevronDown,
  ChevronUp,
  CircleDollarSign,
  Globe2,
  Loader2,
  Mail,
  Megaphone,
  Search,
  ShieldCheck,
  Sparkles,
  Target,
  TrendingUp,
  Rocket,
} from "lucide-react";

import { createObjectiveMission } from "../api";
import { executePersistedMission } from "../api/mission";

import "./BusinessAnalysis.css";

const API_BASE_URL = "http://127.0.0.1:8000";
const DEFAULT_MISSION_BUSINESS_ID = "biz_5d86879387a7";

const STRATEGY_TABS = [
  { id: "strategy", label: "Strategy", icon: Target },
  { id: "seo", label: "SEO", icon: Globe2 },
  { id: "ads", label: "Ads", icon: Megaphone },
  { id: "content", label: "Content", icon: CalendarDays },
  { id: "crm", label: "CRM", icon: Mail },
];

function BusinessAnalysis() {
  const [form, setForm] = useState({
    business_name: "Reem Medical Center",
    industry: "Medical Center",
    location: "Doha, Qatar",
    objective: "Increase patient enquiries and appointments",
    timeline_days: 90,
    monthly_budget: 5000,
    currency: "QAR",
    average_sale_value: 500,
    competitor_limit: 5,
  });

  const [report, setReport] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");
  const [activeTab, setActiveTab] = useState("strategy");
  const [missionBusinessId, setMissionBusinessId] = useState(
    DEFAULT_MISSION_BUSINESS_ID
  );
  const [missionCreating, setMissionCreating] = useState("");
  const [missionExecuting, setMissionExecuting] = useState(false);
  const [missionError, setMissionError] = useState("");
  const [createdMission, setCreatedMission] = useState(null);
  const [missionExecutionResult, setMissionExecutionResult] = useState(null);

  const marketSummary = report?.market_summary || {};
  const strategy = report?.growth_strategy || {};
  const roi = strategy?.roi_forecast || {};
  const competitors = report?.competitors || [];

  const averageStrength = Number(
    marketSummary?.average_profile_strength || 0
  );
  const confidence = Number(report?.confidence || 0);

  const marketLabel = useMemo(() => {
    if (!competitors.length) return "Unknown";
    if (averageStrength >= 70) return "Highly Competitive";
    if (averageStrength >= 50) return "Competitive";
    return "Opportunity Rich";
  }, [competitors.length, averageStrength]);

  const competitorBreakdown = useMemo(() => {
    const strong = Number(marketSummary?.strong_competitors || 0);
    const moderate = Number(marketSummary?.moderate_competitors || 0);
    const weak = Number(marketSummary?.weak_competitors || 0);
    const total = Math.max(1, strong + moderate + weak);

    return {
      strong,
      moderate,
      weak,
      total,
      strongPct: (strong / total) * 100,
      moderatePct: (moderate / total) * 100,
      weakPct: (weak / total) * 100,
    };
  }, [marketSummary]);

  function updateField(event) {
    const { name, value, type } = event.target;
    setForm((current) => ({
      ...current,
      [name]: type === "number" ? Number(value) : value,
    }));
  }

  async function runAnalysis(event) {
    event.preventDefault();
    setLoading(true);
    setError("");

    try {
      const response = await fetch(
        `${API_BASE_URL}/business-analysis/analyze`,
        {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify({ ...form, additional_context: {} }),
        }
      );

      const data = await response.json();
      if (!response.ok) {
        throw new Error(data?.detail || "Business analysis failed.");
      }

      setReport(data);
      setActiveTab("strategy");
    } catch (err) {
      setError(err?.message || "Unable to complete analysis.");
    } finally {
      setLoading(false);
    }
  }

  function buildMissionObjective(type) {
    const businessName = report?.business_name || form.business_name;
    const location = report?.location || form.location;
    const priorities = strategy?.priorities || [];
    const seoActions = strategy?.seo_plan?.actions || [];
    const campaigns = strategy?.ad_campaigns || [];
    const emails = strategy?.email_sequence || [];
    const timeline = strategy?.timeline || [];

    if (type === "seo") {
      const actionText = seoActions
        .slice(0, 5)
        .map((item) => item.title)
        .join(", ");

      return (
        `Create and execute an SEO growth mission for ${businessName} in ${location}. ` +
        `Use the Business Analysis findings and prioritize: ${actionText || "local SEO, service pages, on-page SEO, and reputation signals"}. ` +
        `The mission should produce measurable SEO tasks, assign the appropriate executives, and focus on increasing qualified enquiries.`
      );
    }

    if (type === "ads") {
      const campaignText = campaigns
        .slice(0, 4)
        .map((item) => `${item.channel}: ${item.name}`)
        .join("; ");

      return (
        `Create and execute a paid acquisition mission for ${businessName} in ${location}. ` +
        `Use these recommended campaigns: ${campaignText || "Google Ads and Meta Ads"}. ` +
        `Work within a monthly budget of ${form.monthly_budget} ${form.currency}, define tracking requirements, create campaign tasks, and optimize for enquiries and appointments.`
      );
    }

    if (type === "crm") {
      const followUpText = emails
        .slice(0, 5)
        .map((item) => `Day ${item.day}: ${item.subject}`)
        .join("; ");

      return (
        `Create and execute a CRM follow-up mission for ${businessName}. ` +
        `Build a lead nurturing and follow-up workflow based on this sequence: ${followUpText || "immediate acknowledgement, service education, objection handling, conversion follow-up, and re-engagement"}. ` +
        `Assign the appropriate sales and CRM executives and define measurable follow-up tasks.`
      );
    }

    const priorityText = priorities.slice(0, 6).join("; ");
    const timelineText = timeline
      .slice(0, 8)
      .map((item) => `${item.period}: ${item.title}`)
      .join("; ");

    return (
      `Create and execute a coordinated growth mission for ${businessName} in ${location}. ` +
      `Primary objective: ${form.objective}. ` +
      `Business Analysis priorities: ${priorityText || "improve conversion, local visibility, reputation, and acquisition"}. ` +
      `Recommended execution roadmap: ${timelineText || `${form.timeline_days}-day coordinated growth plan`}. ` +
      `Coordinate the CEO, Marketing, Sales, CRM, and other relevant executives, create concrete tasks, and track execution against the objective.`
    );
  }

  function limitMissionObjective(value, maxLength = 500) {
    const cleaned = String(value || "")
      .replace(/\s+/g, " ")
      .trim();

    if (cleaned.length <= maxLength) {
      return cleaned;
    }

    const shortened = cleaned.slice(0, maxLength - 3);
    const lastSentence = shortened.lastIndexOf(".");
    const lastSeparator = Math.max(
      shortened.lastIndexOf(";"),
      shortened.lastIndexOf(",")
    );

    const safeCut =
      lastSentence >= 320
        ? lastSentence + 1
        : lastSeparator >= 320
          ? lastSeparator
          : shortened.length;

    return `${shortened.slice(0, safeCut).trim()}...`;
  }

  async function createMissionFromAnalysis(type) {
    const businessId = missionBusinessId.trim();

    if (!businessId) {
      setMissionError(
        "Enter the saved Business ID that should own this mission."
      );
      return;
    }

    setMissionCreating(type);
    setMissionError("");
    setCreatedMission(null);
    setMissionExecutionResult(null);

    try {
      const mission = await createObjectiveMission({
        businessId,
        objective: limitMissionObjective(
          buildMissionObjective(type)
        ),
      });

      setCreatedMission({
        ...mission,
        sourceType: type,
      });
    } catch (requestError) {
      setMissionError(
        requestError?.message ||
          "Nestora could not create the mission from this analysis."
      );
    } finally {
      setMissionCreating("");
    }
  }

  async function executeCreatedMission() {
    const missionUid = createdMission?.mission_uid;

    if (!missionUid) {
      setMissionError(
        "Mission ID is missing. Please create the mission again."
      );
      return;
    }

    setMissionExecuting(true);
    setMissionError("");
    setMissionExecutionResult(null);

    try {
      const response = await executePersistedMission(missionUid);

      setMissionExecutionResult(response);

      setCreatedMission((currentMission) => ({
        ...currentMission,
        mission_status:
          response?.status ||
          response?.mission_status ||
          "completed",
      }));
    } catch (requestError) {
      setMissionError(
        requestError?.message ||
          "Nestora could not execute this mission."
      );
    } finally {
      setMissionExecuting(false);
    }
  }

  return (
    <div className="business-analysis-page">
      <section className="analysis-hero">
        <div>
          <div className="analysis-eyebrow">
            <Sparkles size={16} /> AI Business Intelligence
          </div>
          <h1>Business Analysis</h1>
          <p>
            Analyze a business, discover competitors, identify market gaps,
            and generate a complete growth strategy.
          </p>
        </div>

        <div className="analysis-hero-badge">
          <Brain size={20} />
          <div>
            <span>Powered by</span>
            <strong>Nestora Intelligence</strong>
          </div>
        </div>
      </section>

      <section className="analysis-input-card">
        <div className="analysis-section-heading">
          <div>
            <span className="analysis-section-icon"><Search size={18} /></span>
            <div>
              <h2>Analyze a Business</h2>
              <p>Enter the business context and Nestora will build an executive intelligence report.</p>
            </div>
          </div>
        </div>

        <form className="analysis-form" onSubmit={runAnalysis}>
          <label>Business Name<input name="business_name" value={form.business_name} onChange={updateField} required /></label>
          <label>Industry<input name="industry" value={form.industry} onChange={updateField} required /></label>
          <label>Location<input name="location" value={form.location} onChange={updateField} required /></label>
          <label className="analysis-form-wide">Business Objective<input name="objective" value={form.objective} onChange={updateField} required /></label>
          <label>Timeline<div className="analysis-input-suffix"><input type="number" name="timeline_days" value={form.timeline_days} onChange={updateField} min="1" /><span>days</span></div></label>
          <label>Monthly Budget<div className="analysis-input-suffix"><input type="number" name="monthly_budget" value={form.monthly_budget} onChange={updateField} min="0" /><span>{form.currency}</span></div></label>
          <label>Average Sale Value<div className="analysis-input-suffix"><input type="number" name="average_sale_value" value={form.average_sale_value} onChange={updateField} min="0" /><span>{form.currency}</span></div></label>
          <label>Competitors<input type="number" name="competitor_limit" value={form.competitor_limit} onChange={updateField} min="1" max="10" /></label>

          <div className="analysis-form-action">
            <button type="submit" className="analysis-primary-button" disabled={loading}>
              {loading ? <><Loader2 size={18} className="analysis-spin" />Analyzing Market...</> : <><Sparkles size={18} />Run AI Analysis</>}
            </button>
          </div>
        </form>

        {error && <div className="analysis-error">{error}</div>}
      </section>

      {!report && !loading && (
        <section className="analysis-empty-state">
          <Brain size={38} />
          <h2>Your intelligence report will appear here</h2>
          <p>Run an analysis to discover competitors, market opportunities, growth priorities, and estimated business performance.</p>
        </section>
      )}

      {report && (
        <>
          <nav className="analysis-sticky-nav">
            <a href="#overview">Overview</a>
            <a href="#competitors">Competitors</a>
            <a href="#market">Market</a>
            <a href="#strategy-hub">Strategy</a>
            <a href="#actions">Actions</a>
            <a href="#roadmap">Roadmap</a>
          </nav>

          <section id="overview" className="analysis-report-header">
            <div>
              <div className="analysis-status"><CheckCircle2 size={16} />Analysis Complete</div>
              <h2>{report.business_name}</h2>
              <p>{report.industry} • {report.location} • {report.timeline_days}-day strategy</p>
            </div>
            <div className="analysis-confidence"><span>AI Confidence</span><strong>{confidence}%</strong></div>
          </section>

          <section className="analysis-kpi-grid">
            <MetricCard icon={Building2} label="Competitors" value={marketSummary.competitor_count || competitors.length} detail="Relevant competitors analyzed" />
            <MetricCard icon={BarChart3} label="Average Strength" value={`${averageStrength}%`} detail="Competitor digital strength" />
            <MetricCard icon={Target} label="Market" value={marketLabel} detail="Competitive environment" />
            <MetricCard icon={TrendingUp} label="Forecast ROI" value={`${roi.estimated_roi_percent || 0}%`} detail="Planning estimate" />
            <MetricCard icon={CircleDollarSign} label="Revenue Forecast" value={`${Number(roi.estimated_revenue || 0).toLocaleString()} ${roi.currency || form.currency}`} detail="Estimated monthly revenue" />
            <MetricCard icon={Activity} label="Expected Leads" value={roi.estimated_leads || 0} detail="Estimated lead generation" />
          </section>

          <section className="analysis-visual-grid">
            <div className="analysis-chart-card">
              <div className="chart-card-header"><div><h3>Competitor Strength</h3><p>Digital profile strength by competitor</p></div><BarChart3 size={18} /></div>
              <div className="strength-chart">
                {competitors.map((competitor) => {
                  const score = Number(competitor.profile_strength || 0);
                  return <div className="strength-row" key={competitor.name}><div className="strength-row-label"><span>{competitor.name}</span><strong>{score}%</strong></div><div className="strength-row-track"><span style={{ width: `${Math.min(100, score)}%` }} /></div></div>;
                })}
              </div>
            </div>

            <div className="analysis-chart-card">
              <div className="chart-card-header"><div><h3>Market Mix</h3><p>Strong, moderate and weak competitors</p></div><Target size={18} /></div>
              <div className="market-mix-wrap">
                <div className="market-donut" style={{ background: `conic-gradient(#5f63e8 0 ${competitorBreakdown.strongPct}%, #8c91a0 ${competitorBreakdown.strongPct}% ${competitorBreakdown.strongPct + competitorBreakdown.moderatePct}%, #3d4655 ${competitorBreakdown.strongPct + competitorBreakdown.moderatePct}% 100%)` }}>
                  <div className="market-donut-center"><strong>{competitorBreakdown.total}</strong><span>Total</span></div>
                </div>
                <div className="market-legend">
                  <LegendRow label="Strong" value={competitorBreakdown.strong} className="legend-strong" />
                  <LegendRow label="Moderate" value={competitorBreakdown.moderate} className="legend-moderate" />
                  <LegendRow label="Weak" value={competitorBreakdown.weak} className="legend-weak" />
                </div>
              </div>
            </div>

            <div className="analysis-chart-card">
              <div className="chart-card-header"><div><h3>ROI Snapshot</h3><p>Investment versus projected return</p></div><CircleDollarSign size={18} /></div>
              <div className="roi-visual">
                <div><span>Investment</span><strong>{Number(roi.monthly_investment || 0).toLocaleString()} {roi.currency || form.currency}</strong></div>
                <div className="roi-arrow">→</div>
                <div><span>Revenue</span><strong>{Number(roi.estimated_revenue || 0).toLocaleString()} {roi.currency || form.currency}</strong></div>
                <div className="roi-badge">+{roi.estimated_roi_percent || 0}%</div>
              </div>
            </div>
          </section>

          <ReportSection icon={Brain} title="Executive Summary" subtitle="CEO-level interpretation of the current market">
            <div className="executive-summary">{report.executive_summary}</div>
          </ReportSection>

          <section id="actions" className="analysis-action-center">
            <div className="action-center-heading">
              <div>
                <div className="analysis-eyebrow">
                  <Rocket size={16} />
                  From Intelligence to Execution
                </div>

                <h2>Launch AI Missions</h2>

                <p>
                  Turn this analysis into coordinated work for Nestora's AI
                  workforce. Each button creates a real persisted mission using
                  the existing CEO objective engine.
                </p>
              </div>
            </div>

            <div className="mission-business-row">
              <label>
                Mission Business ID
                <input
                  value={missionBusinessId}
                  onChange={(event) =>
                    setMissionBusinessId(event.target.value)
                  }
                  placeholder="biz_..."
                />
              </label>

              <p>
                Development note: this must be the saved business ID that owns
                the mission. Later, Nestora can populate it automatically when
                Business Analysis is opened from a saved business.
              </p>
            </div>

            <div className="analysis-action-grid">
              <MissionActionButton
                title="Full Growth Mission"
                description="Coordinate the recommended 90-day strategy across the AI workforce."
                loading={missionCreating === "growth"}
                disabled={Boolean(missionCreating)}
                onClick={() => createMissionFromAnalysis("growth")}
              />

              <MissionActionButton
                title="SEO Mission"
                description="Convert the SEO recommendations into executable optimization tasks."
                loading={missionCreating === "seo"}
                disabled={Boolean(missionCreating)}
                onClick={() => createMissionFromAnalysis("seo")}
              />

              <MissionActionButton
                title="Paid Acquisition Mission"
                description="Create an execution mission from the recommended Google and Meta campaigns."
                loading={missionCreating === "ads"}
                disabled={Boolean(missionCreating)}
                onClick={() => createMissionFromAnalysis("ads")}
              />

              <MissionActionButton
                title="CRM Follow-up Mission"
                description="Turn the nurturing sequence into structured sales and CRM follow-up work."
                loading={missionCreating === "crm"}
                disabled={Boolean(missionCreating)}
                onClick={() => createMissionFromAnalysis("crm")}
              />
            </div>

            {missionError && (
              <div className="analysis-error">{missionError}</div>
            )}

            {createdMission && (
              <div className="mission-created-card">
                <div>
                  <div className="analysis-status">
                    <CheckCircle2 size={16} />
                    Mission Created
                  </div>

                  <h3>
                    {createdMission.strategy?.title ||
                      "AI Mission ready for execution"}
                  </h3>

                  <p>
                    Mission ID:{" "}
                    <strong>{createdMission.mission_uid || "Created"}</strong>
                  </p>

                  <small>
                    Status: {createdMission.mission_status || "planned"}
                  </small>
                </div>

                <div className="mission-created-actions">
                  <button
                    type="button"
                    className="mission-execute-button"
                    onClick={executeCreatedMission}
                    disabled={
                      missionExecuting ||
                      !createdMission?.mission_uid ||
                      createdMission?.mission_status === "completed"
                    }
                  >
                    {missionExecuting ? (
                      <>
                        <Loader2 size={15} className="analysis-spin" />
                        Executing...
                      </>
                    ) : createdMission?.mission_status === "completed" ? (
                      <>
                        <CheckCircle2 size={15} />
                        Mission Completed
                      </>
                    ) : (
                      <>
                        <Rocket size={15} />
                        Execute Mission
                      </>
                    )}
                  </button>

                  <Link className="mission-dashboard-link" to="/missions">
                    Open Mission Dashboard
                  </Link>
                </div>
              </div>
            )}

            {missionExecutionResult && (
              <div className="mission-execution-result">
                <CheckCircle2 size={16} />

                <div>
                  <strong>
                    {missionExecutionResult?.message ||
                      "Mission execution completed."}
                  </strong>

                  <span>
                    Status:{" "}
                    {missionExecutionResult?.status ||
                      missionExecutionResult?.mission_status ||
                      createdMission?.mission_status ||
                      "completed"}
                  </span>
                </div>
              </div>
            )}
          </section>

          <section id="competitors">
            <ReportSection icon={Building2} title="Competitor Intelligence" subtitle={`${competitors.length} relevant competitors selected by Nestora`}>
              <div className="competitor-grid">{competitors.map((competitor, index) => <CompetitorCard key={`${competitor.name}-${index}`} competitor={competitor} />)}</div>
            </ReportSection>
          </section>

          <section id="market">
            <ReportSection icon={BarChart3} title="Market Summary" subtitle="Competitive strength and market opportunity">
              <div className="market-summary-grid">
                <InfoCard label="Strongest Competitor" value={marketSummary.strongest_competitor || "Not available"} />
                <InfoCard label="Weakest Competitor" value={marketSummary.weakest_competitor || "Not available"} />
                <InfoCard label="Strong Competitors" value={marketSummary.strong_competitors || 0} />
                <InfoCard label="Moderate Competitors" value={marketSummary.moderate_competitors || 0} />
                <InfoCard label="Weak Competitors" value={marketSummary.weak_competitors || 0} />
              </div>
              {!!marketSummary.common_opportunities?.length && <div className="opportunity-strip"><h3>Common Market Opportunities</h3><div className="analysis-tags">{marketSummary.common_opportunities.map((item) => <span key={item}>{item}</span>)}</div></div>}
            </ReportSection>
          </section>

          <section id="strategy-hub" className="analysis-strategy-hub">
            <div className="analysis-tabs">
              {STRATEGY_TABS.map((tab) => {
                const Icon = tab.icon;
                return <button type="button" key={tab.id} className={activeTab === tab.id ? "analysis-tab active" : "analysis-tab"} onClick={() => setActiveTab(tab.id)}><Icon size={16} />{tab.label}</button>;
              })}
            </div>

            <div className="analysis-tab-panel">
              {activeTab === "strategy" && <StrategyOverview strategy={strategy} />}
              {activeTab === "seo" && <SeoPlan strategy={strategy} />}
              {activeTab === "ads" && <AdvertisingPlan strategy={strategy} currency={form.currency} />}
              {activeTab === "content" && <ContentPlan strategy={strategy} />}
              {activeTab === "crm" && <CrmPlan strategy={strategy} />}
            </div>
          </section>

          <ReportSection icon={CircleDollarSign} title="ROI Forecast" subtitle="Planning estimates based on the current strategy">
            <div className="roi-grid">
              <InfoCard label="Monthly Investment" value={`${Number(roi.monthly_investment || 0).toLocaleString()} ${roi.currency || form.currency}`} />
              <InfoCard label="Estimated Leads" value={roi.estimated_leads || 0} />
              <InfoCard label="Estimated Customers" value={roi.estimated_customers || 0} />
              <InfoCard label="Estimated Revenue" value={`${Number(roi.estimated_revenue || 0).toLocaleString()} ${roi.currency || form.currency}`} />
              <InfoCard label="Estimated ROI" value={`${roi.estimated_roi_percent || 0}%`} />
            </div>
          </ReportSection>

          <section id="roadmap">
            <ReportSection icon={CalendarDays} title="90-Day Execution Roadmap" subtitle="Recommended implementation sequence">
              <div className="timeline-list">{(strategy.timeline || []).map((item, index) => <div className="timeline-item" key={`${item.period}-${index}`}><div className="timeline-marker">{index + 1}</div><div className="timeline-body"><div className="timeline-top"><span>{item.period}</span><strong>{item.priority}</strong></div><h3>{item.title}</h3><p>{item.description}</p><small>Owner: {item.owner}</small></div></div>)}</div>
            </ReportSection>
          </section>
        </>
      )}
    </div>
  );
}

function MetricCard({ icon: Icon, label, value, detail }) {
  return <article className="analysis-metric-card"><div className="analysis-metric-icon"><Icon size={20} /></div><div><span>{label}</span><strong>{value}</strong><small>{detail}</small></div></article>;
}

function ReportSection({ icon: Icon, title, subtitle, children }) {
  return <section className="analysis-report-section"><div className="analysis-section-heading"><div><span className="analysis-section-icon"><Icon size={18} /></span><div><h2>{title}</h2><p>{subtitle}</p></div></div></div>{children}</section>;
}

function InfoCard({ label, value }) {
  return <div className="analysis-info-card"><span>{label}</span><strong>{value}</strong></div>;
}

function LegendRow({ label, value, className }) {
  return <div className="legend-row"><span className={`legend-dot ${className}`} /><span>{label}</span><strong>{value}</strong></div>;
}

function CompetitorCard({ competitor }) {
  const [expanded, setExpanded] = useState(false);
  const intelligence = competitor.competitor_intelligence || {};
  const opportunities = intelligence.opportunities || [];
  const recommendations = intelligence.recommendations || [];
  const swot = intelligence.swot || {};
  const score = Number(competitor.profile_strength || 0);

  return (
    <article className="competitor-card">
      <div className="competitor-card-top"><div><span className="competitor-category">{competitor.category || "Business"}</span><h3>{competitor.name}</h3><p>{competitor.location || "Location unavailable"}</p></div><div className="competitor-score"><strong>{score}%</strong><span>{competitor.profile_strength_label || "Unrated"}</span></div></div>
      <div className="competitor-progress"><span style={{ width: `${Math.min(100, score)}%` }} /></div>
      <div className="competitor-facts"><div><span>Market Position</span><strong>{competitor.market_position || "Unknown"}</strong></div><div><span>Digital Maturity</span><strong>{competitor.digital_maturity || "Unknown"}</strong></div><div><span>AI Confidence</span><strong>{competitor.intelligence_confidence || 0}%</strong></div></div>
      <div className="competitor-contact-row"><span className={competitor.website && competitor.website !== "Not found" ? "available" : ""}>Website</span><span className={competitor.phone && competitor.phone !== "Not found" ? "available" : ""}>Phone</span><span className={competitor.email && competitor.email !== "Not found" ? "available" : ""}>Email</span></div>
      {!!opportunities.length && <div className="competitor-opportunity"><span>Top Opportunity</span><strong>{opportunities[0].title}</strong><p>{opportunities[0].description}</p></div>}
      <button type="button" className="competitor-toggle" onClick={() => setExpanded((value) => !value)}>{expanded ? "Hide intelligence" : "View full intelligence"}{expanded ? <ChevronUp size={15} /> : <ChevronDown size={15} />}</button>
      {expanded && <div className="competitor-expanded"><SwotColumn title="Strengths" items={swot.strengths || []} /><SwotColumn title="Weaknesses" items={swot.weaknesses || []} /><SwotColumn title="Opportunities" items={swot.opportunities || []} /><SwotColumn title="Threats" items={swot.threats || []} />{!!recommendations.length && <div className="competitor-recommendations"><h4>Recommendations</h4>{recommendations.map((item, index) => <div key={`${item.title}-${index}`}><strong>{item.title}</strong><p>{item.action}</p></div>)}</div>}</div>}
    </article>
  );
}

function SwotColumn({ title, items }) {
  return <div className="swot-column"><h4>{title}</h4>{items.length ? <ul>{items.map((item, index) => <li key={`${title}-${index}`}>{item}</li>)}</ul> : <p>No major signals detected.</p>}</div>;
}

function StrategyOverview({ strategy }) {
  return <><div className="tab-section-header"><Target size={18} /><div><h3>Strategic Priorities</h3><p>Recommended areas of immediate executive focus</p></div></div><div className="priority-list">{(strategy.priorities || []).map((priority, index) => <div className="priority-item" key={priority}><span>{String(index + 1).padStart(2, "0")}</span><p>{priority}</p></div>)}</div></>;
}

function SeoPlan({ strategy }) {
  return <><div className="tab-section-header"><Globe2 size={18} /><div><h3>SEO Growth Plan</h3><p>Organic visibility and local search opportunities</p></div></div><div className="strategy-card-grid">{(strategy?.seo_plan?.actions || []).map((action, index) => <StrategyCard key={`${action.title}-${index}`} title={action.title} description={action.description} priority={action.priority} footer={action.target_keywords} />)}</div></>;
}

function AdvertisingPlan({ strategy, currency }) {
  return <><div className="tab-section-header"><Megaphone size={18} /><div><h3>Advertising Strategy</h3><p>Recommended paid acquisition campaigns</p></div></div><div className="campaign-grid">{(strategy.ad_campaigns || []).map((campaign, index) => <div className="campaign-card" key={`${campaign.name}-${index}`}><div className="campaign-card-header"><span>{campaign.channel}</span><strong>{campaign.daily_budget} {currency}/day</strong></div><h3>{campaign.name}</h3><p>{campaign.objective}</p>{campaign.message && <blockquote>{campaign.message}</blockquote>}{!!campaign.keywords?.length && <div className="analysis-tags">{campaign.keywords.map((keyword) => <span key={keyword}>{keyword}</span>)}</div>}</div>)}</div></>;
}

function ContentPlan({ strategy }) {
  const [showAll, setShowAll] = useState(false);
  const items = strategy.content_calendar || [];
  const visibleItems = showAll ? items : items.slice(0, 9);

  return <><div className="tab-section-header"><CalendarDays size={18} /><div><h3>Content Calendar</h3><p>AI-generated content execution plan</p></div></div><div className="content-calendar-grid">{visibleItems.map((item, index) => <div className="content-calendar-card" key={`${item.day}-${index}`}><span className="calendar-day">Day {item.day}</span><strong>{item.channel}</strong><small>{item.content_type}</small><h3>{item.topic}</h3><p>{item.objective}</p></div>)}</div>{items.length > 9 && <button type="button" className="show-more-button" onClick={() => setShowAll((value) => !value)}>{showAll ? "Show less" : `Show all ${items.length} items`}</button>}</>;
}

function CrmPlan({ strategy }) {
  return <><div className="tab-section-header"><ShieldCheck size={18} /><div><h3>Lead Nurturing Sequence</h3><p>Recommended automated follow-up journey</p></div></div><div className="email-sequence">{(strategy.email_sequence || []).map((email, index) => <div className="email-sequence-item" key={`${email.day}-${index}`}><span>Day {email.day}</span><div><h3>{email.subject}</h3><p>{email.purpose}</p><small>CTA: {email.call_to_action}</small></div></div>)}</div></>;
}

function MissionActionButton({
  title,
  description,
  loading,
  disabled,
  onClick,
}) {
  return (
    <button
      type="button"
      className="mission-action-card"
      onClick={onClick}
      disabled={disabled}
    >
      <div className="mission-action-icon">
        {loading ? (
          <Loader2 size={18} className="analysis-spin" />
        ) : (
          <Rocket size={18} />
        )}
      </div>

      <div>
        <strong>{loading ? "Creating mission..." : title}</strong>
        <p>{description}</p>
      </div>
    </button>
  );
}

function StrategyCard({ title, description, priority, footer }) {
  return <article className="strategy-card"><div className="strategy-card-top"><h3>{title}</h3><span>{priority || "Medium"}</span></div><p>{description}</p>{!!footer?.length && <div className="analysis-tags">{footer.map((item) => <span key={item}>{item}</span>)}</div>}</article>;
}

export default BusinessAnalysis;