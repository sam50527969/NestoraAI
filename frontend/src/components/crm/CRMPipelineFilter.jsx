import PropTypes from "prop-types";

import "./CRMPipelineFilter.css";

const PIPELINE_STAGES = [
  {
    value: "All",
    label: "All Leads",
  },
  {
    value: "New",
    label: "New",
  },
  {
    value: "Contacted",
    label: "Contacted",
  },
  {
    value: "Qualified",
    label: "Qualified",
  },
  {
    value: "Won",
    label: "Won",
  },
  {
    value: "Lost",
    label: "Lost",
  },
];

export default function CRMPipelineFilter({
  leads,
  selectedStage,
  onStageChange,
}) {
  function getCount(stage) {
    if (stage === "All") {
      return leads.length;
    }

    return leads.filter(
      (lead) =>
        (lead.status || "New") === stage,
    ).length;
  }

  return (
    <section className="crm-pipeline-filter">
      <div className="crm-pipeline-filter-heading">
        <div>
          <p>Pipeline Stages</p>

          <h2>
            Filter CRM Opportunities
          </h2>
        </div>

        <span>
          Select a stage to inspect its
          leads.
        </span>
      </div>

      <div className="crm-pipeline-filter-list">
        {PIPELINE_STAGES.map(
          ({ value, label }) => {
            const isActive =
              selectedStage === value;

            return (
              <button
                type="button"
                className={
                  isActive
                    ? "active"
                    : ""
                }
                aria-pressed={isActive}
                onClick={() =>
                  onStageChange(value)
                }
                key={value}
              >
                <span>{label}</span>

                <strong>
                  {getCount(value)}
                </strong>
              </button>
            );
          },
        )}
      </div>
    </section>
  );
}

CRMPipelineFilter.propTypes = {
  leads: PropTypes.arrayOf(
    PropTypes.shape({
      status: PropTypes.string,
    }),
  ).isRequired,
  selectedStage: PropTypes.string.isRequired,
  onStageChange: PropTypes.func.isRequired,
};