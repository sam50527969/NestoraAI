import {
  Activity,
  CheckCircle2,
  Globe2,
  Mail,
  Phone,
  Sparkles,
  TrendingUp,
} from "lucide-react";
import "./BusinessHealthCard.css";


function hasValue(value) {
  return Boolean(
    value
    && String(value).trim()
    && String(value).trim().toLowerCase() !== "not found",
  );
}


function clampScore(value) {
  return Math.min(
    Math.max(
      Math.round(Number(value) || 0),
      0,
    ),
    100,
  );
}


function calculateBusinessHealth(business) {
  if (!business) {
    return {
      overall: 0,
      contact: 0,
      crm: 0,
      marketingReadiness: 0,
      growthPotential: 0,
    };
  }

  const hasPhone = hasValue(business.phone);
  const hasWebsite = hasValue(business.website);
  const hasEmail = hasValue(business.email);
  const hasAddress = hasValue(
    business.address || business.location,
  );
  const hasCategory = hasValue(business.category);
  const hasNotes = hasValue(business.notes);
  const hasAiRecommendation = hasValue(
    business.aiRecommendation,
  );

  const contactScore = clampScore(
    (hasPhone ? 35 : 0)
    + (hasWebsite ? 35 : 0)
    + (hasEmail ? 20 : 0)
    + (hasAddress ? 10 : 0),
  );

  const crmScore = clampScore(
    25
    + (hasCategory ? 20 : 0)
    + (hasAddress ? 15 : 0)
    + (hasNotes ? 15 : 0)
    + (business.priority ? 10 : 0)
    + (business.status ? 10 : 0)
    + (hasAiRecommendation ? 5 : 0),
  );

  const marketingReadiness = clampScore(
    (hasWebsite ? 30 : 0)
    + (hasPhone ? 20 : 0)
    + (hasEmail ? 15 : 0)
    + (hasCategory ? 15 : 0)
    + (hasAddress ? 10 : 0)
    + (hasAiRecommendation ? 10 : 0),
  );

  const sourceScore =
    business.opportunityScore
    ?? business.aiScore
    ?? 70;

  const growthPotential = clampScore(
    sourceScore,
  );

  const overall = clampScore(
    (
      contactScore
      + crmScore
      + marketingReadiness
      + growthPotential
    ) / 4,
  );

  return {
    overall,
    contact: contactScore,
    crm: crmScore,
    marketingReadiness,
    growthPotential,
  };
}


function HealthMetric({
  icon,
  label,
  value,
}) {
  return (
    <article className="business-health-metric">
      <div className="business-health-metric-icon">
        {icon}
      </div>

      <div>
        <span>{label}</span>
        <strong>{value}%</strong>
      </div>
    </article>
  );
}


export default function BusinessHealthCard({
  business,
}) {
  if (!business) {
    return (
      <section className="panel business-health-card business-health-empty">
        <Sparkles
          size={24}
          strokeWidth={1.8}
        />

        <h2>Business Health</h2>

        <p>
          Select a CRM business to generate an instant
          business health assessment.
        </p>
      </section>
    );
  }

  const health = calculateBusinessHealth(
    business,
  );

  const websiteAvailable = hasValue(
    business.website,
  );

  const phoneAvailable = hasValue(
    business.phone,
  );

  const emailAvailable = hasValue(
    business.email,
  );

  return (
    <section className="panel business-health-card">
      <header className="business-health-header">
        <div>
          <p className="page-eyebrow">
            AI Business Assessment
          </p>

          <h2>Business Health</h2>

          <p>
            Instant readiness analysis based on CRM
            completeness, contact quality, and growth
            potential.
          </p>
        </div>

        <div className="business-health-score">
          <strong>{health.overall}%</strong>
          <span>Overall</span>
        </div>
      </header>

      <div className="business-health-progress">
        <div
          className="business-health-progress-fill"
          style={{
            width: `${health.overall}%`,
          }}
        />
      </div>

      <div className="business-health-metrics">
        <HealthMetric
          icon={
            <Phone
              size={17}
              strokeWidth={2.2}
            />
          }
          label="Contact Quality"
          value={health.contact}
        />

        <HealthMetric
          icon={
            <CheckCircle2
              size={17}
              strokeWidth={2.2}
            />
          }
          label="CRM Completeness"
          value={health.crm}
        />

        <HealthMetric
          icon={
            <Activity
              size={17}
              strokeWidth={2.2}
            />
          }
          label="Marketing Readiness"
          value={health.marketingReadiness}
        />

        <HealthMetric
          icon={
            <TrendingUp
              size={17}
              strokeWidth={2.2}
            />
          }
          label="Growth Potential"
          value={health.growthPotential}
        />
      </div>

      <div className="business-health-checks">
        <span
          className={
            websiteAvailable
              ? "available"
              : "missing"
          }
        >
          <Globe2 size={14} />
          Website
          {websiteAvailable ? " available" : " missing"}
        </span>

        <span
          className={
            phoneAvailable
              ? "available"
              : "missing"
          }
        >
          <Phone size={14} />
          Phone
          {phoneAvailable ? " available" : " missing"}
        </span>

        <span
          className={
            emailAvailable
              ? "available"
              : "missing"
          }
        >
          <Mail size={14} />
          Email
          {emailAvailable ? " available" : " missing"}
        </span>
      </div>
    </section>
  );
}