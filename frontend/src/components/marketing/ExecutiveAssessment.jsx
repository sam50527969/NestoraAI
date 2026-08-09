import {
  AlertTriangle,
  CheckCircle2,
  Lightbulb,
  Sparkles,
  TrendingUp,
} from "lucide-react";
import "./ExecutiveAssessment.css";


function hasValue(value) {
  return Boolean(
    value
    && String(value).trim()
    && String(value).trim().toLowerCase() !== "not found",
  );
}


function formatCategory(value) {
  return String(value || "Business")
    .replaceAll("_", " ")
    .replace(/\b\w/g, (letter) =>
      letter.toUpperCase(),
    );
}


function buildAssessment(business) {
  if (!business) {
    return {
      strengths: [],
      weaknesses: [],
      actions: [],
      potentialScore: 0,
      potentialLabel: "Not Available",
      summary: "",
    };
  }

  const hasPhone = hasValue(business.phone);
  const hasWebsite = hasValue(business.website);
  const hasEmail = hasValue(business.email);
  const hasAddress = hasValue(
    business.address || business.location,
  );
  const hasNotes = hasValue(business.notes);
  const hasRecommendation = hasValue(
    business.aiRecommendation,
  );

  const category = formatCategory(
    business.category,
  );

  const strengths = [];
  const weaknesses = [];
  const actions = [];

  if (hasWebsite) {
    strengths.push(
      "A business website is available for digital campaigns.",
    );
  } else {
    weaknesses.push(
      "No website is currently available in the CRM profile.",
    );

    actions.push(
      "Create or improve the business website and online booking journey.",
    );
  }

  if (hasPhone) {
    strengths.push(
      "A direct phone number is available for customer outreach.",
    );
  } else {
    weaknesses.push(
      "A direct phone number is missing.",
    );

    actions.push(
      "Research and add a verified customer contact number.",
    );
  }

  if (hasEmail) {
    strengths.push(
      "Email contact information is available.",
    );
  } else {
    weaknesses.push(
      "The CRM profile does not contain an email address.",
    );

    actions.push(
      "Add a verified business email for campaign and follow-up use.",
    );
  }

  if (hasAddress) {
    strengths.push(
      "The location is available for local marketing and geographic targeting.",
    );
  } else {
    weaknesses.push(
      "The business location is incomplete.",
    );

    actions.push(
      "Complete the business address before launching local campaigns.",
    );
  }

  if (hasNotes || hasRecommendation) {
    strengths.push(
      "The CRM contains additional context for AI recommendations.",
    );
  } else {
    weaknesses.push(
      "The CRM profile lacks detailed business notes and market context.",
    );

    actions.push(
      "Add services, target audience, differentiators, and current challenges.",
    );
  }

  const normalizedCategory = String(
    business.category || "",
  ).toLowerCase();

  if (
    normalizedCategory.includes("clinic")
    || normalizedCategory.includes("medical")
    || normalizedCategory.includes("health")
  ) {
    actions.push(
      "Launch a Google review campaign to strengthen local trust.",
      "Use WhatsApp reminders and follow-ups to improve appointment attendance.",
      "Create family-focused and preventive healthcare campaigns.",
      "Improve local SEO for healthcare searches in Doha.",
    );
  } else {
    actions.push(
      "Strengthen Google Business visibility and customer reviews.",
      "Launch a targeted local awareness campaign.",
      "Create an automated lead follow-up workflow.",
    );
  }

  const sourceScore =
    business.opportunityScore
    ?? business.aiScore
    ?? 70;

  const profileBonus =
    (hasWebsite ? 6 : 0)
    + (hasPhone ? 6 : 0)
    + (hasEmail ? 4 : 0)
    + (hasAddress ? 4 : 0)
    + (hasNotes ? 4 : 0);

  const potentialScore = Math.min(
    100,
    Math.max(
      0,
      Math.round(
        Number(sourceScore || 0)
        + profileBonus,
      ),
    ),
  );

  let potentialLabel = "Moderate Opportunity";

  if (potentialScore >= 85) {
    potentialLabel = "Excellent Opportunity";
  } else if (potentialScore >= 70) {
    potentialLabel = "High Opportunity";
  } else if (potentialScore < 50) {
    potentialLabel = "Needs Enrichment";
  }

  return {
    strengths: strengths.slice(0, 5),
    weaknesses: weaknesses.slice(0, 5),
    actions: [...new Set(actions)].slice(0, 6),
    potentialScore,
    potentialLabel,
    summary:
      `${business.name} is a ${category.toLowerCase()} `
      + "with measurable growth potential. Nestora recommends "
      + "prioritizing digital visibility, customer follow-up, "
      + "and reputation-building activities.",
  };
}


function AssessmentList({
  title,
  items,
  icon,
  className,
}) {
  if (!items.length) {
    return null;
  }

  return (
    <section
      className={`executive-assessment-list ${className}`}
    >
      <header>
        {icon}
        <h3>{title}</h3>
      </header>

      <ul>
        {items.map((item, index) => (
          <li key={`${title}-${index}`}>
            {item}
          </li>
        ))}
      </ul>
    </section>
  );
}


export default function ExecutiveAssessment({
  business,
}) {
  if (!business) {
    return (
      <section className="panel executive-assessment executive-assessment-empty">
        <Sparkles
          size={25}
          strokeWidth={1.8}
        />

        <h2>AI Executive Assessment</h2>

        <p>
          Select a CRM business to receive an instant
          assessment and recommended actions.
        </p>
      </section>
    );
  }

  const assessment = buildAssessment(
    business,
  );

  return (
    <section className="panel executive-assessment">
      <header className="executive-assessment-header">
        <div>
          <p className="page-eyebrow">
            AI Executive Insight
          </p>

          <h2>Executive Assessment</h2>

          <p>{assessment.summary}</p>
        </div>

        <div className="executive-potential-score">
          <strong>
            {assessment.potentialScore}%
          </strong>

          <span>
            {assessment.potentialLabel}
          </span>
        </div>
      </header>

      <div className="executive-assessment-grid">
        <AssessmentList
          title="Strengths"
          items={assessment.strengths}
          className="strengths"
          icon={
            <CheckCircle2
              size={17}
              strokeWidth={2.2}
            />
          }
        />

        <AssessmentList
          title="Weaknesses"
          items={assessment.weaknesses}
          className="weaknesses"
          icon={
            <AlertTriangle
              size={17}
              strokeWidth={2.2}
            />
          }
        />
      </div>

      <section className="executive-actions">
        <header>
          <Lightbulb
            size={18}
            strokeWidth={2.2}
          />

          <div>
            <h3>Immediate Actions</h3>

            <p>
              Recommended next steps based on the current
              business profile.
            </p>
          </div>
        </header>

        <ol>
          {assessment.actions.map(
            (action, index) => (
              <li key={`action-${index}`}>
                <span>{index + 1}</span>
                <p>{action}</p>
              </li>
            ),
          )}
        </ol>
      </section>

      <footer className="executive-assessment-footer">
        <TrendingUp
          size={16}
          strokeWidth={2.2}
        />

        <span>
          Growth potential:
          <strong>
            {assessment.potentialLabel}
          </strong>
        </span>
      </footer>
    </section>
  );
}