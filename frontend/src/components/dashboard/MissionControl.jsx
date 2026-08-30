import { useEffect, useState } from "react";

import { getMissionStatus, startMission } from "../../api";
import Badge from "../ui/Badge";
import Button from "../ui/Button";
import Card from "../ui/Card";
import useWorkspace from "../../workspace/useWorkspace";

const PRIORITY_FILTERS = [
  { value: "all", label: "All Priorities" },
  { value: "high", label: "High Priority Only" },
  { value: "medium", label: "Medium and Above" },
  { value: "low", label: "Low and Above" },
];

function MissionControl({ onMissionChange }) {
  const { activeWorkspace } = useWorkspace();
  const [mission, setMission] = useState(null);
  const [isStarting, setIsStarting] = useState(false);
  const [errorMessage, setErrorMessage] = useState("");

  const [businessType, setBusinessType] = useState("");
  const [location, setLocation] = useState("");
  const [quantity, setQuantity] = useState(5);
  const [analyzeWebsites, setAnalyzeWebsites] = useState(true);
  const [generateOutreach, setGenerateOutreach] = useState(true);
  const [minimumQuality, setMinimumQuality] = useState(60);
  const [priorityFilter, setPriorityFilter] = useState("all");

  useEffect(() => {
    if (!activeWorkspace) {
      setBusinessType("");
      setLocation("");
      setMission(null);
      onMissionChange?.(null);
      return;
    }

    setMission(null);
    setErrorMessage("");
    onMissionChange?.(null);

    setBusinessType(
      String(
        activeWorkspace.industry || "",
      ).replaceAll("_", " "),
    );

    setLocation(
      [
        activeWorkspace.city,
        activeWorkspace.region,
        activeWorkspace.country,
      ].filter(Boolean).join(", "),
    );
  }, [activeWorkspace, onMissionChange]);

  useEffect(() => {
    if (!mission?.mission_id) {
      return undefined;
    }

    if (["completed", "failed"].includes(mission.status)) {
      return undefined;
    }

    const intervalId = window.setInterval(async () => {
      try {
        const latestMission = await getMissionStatus(
          mission.mission_id
        );

        setMission(latestMission);
        onMissionChange?.(latestMission);
      } catch (error) {
        console.error(
          "Failed to refresh mission status:",
          error
        );

        setErrorMessage(
          "Unable to refresh mission progress."
        );
      }
    }, 3000);

    return () => window.clearInterval(intervalId);
  }, [
    mission?.mission_id,
    mission?.status,
    onMissionChange,
  ]);

  async function handleStartMission() {
    const cleanedLocation = location.trim();

    const safeQuantity = Math.min(
      Math.max(Number(quantity) || 1, 1),
      100
    );

    const safeMinimumQuality = Math.min(
      Math.max(Number(minimumQuality) || 0, 0),
      100
    );

    if (!businessType) {
      setErrorMessage(
        "Please select a business type."
      );
      return;
    }

    if (!cleanedLocation) {
      setErrorMessage(
        "Please enter a location."
      );
      return;
    }

    try {
      setIsStarting(true);
      setErrorMessage("");

      const startedMission = await startMission({
        business_type: businessType,
        location: cleanedLocation,
        quantity: safeQuantity,
        analyze_websites: analyzeWebsites,
        generate_outreach: generateOutreach,
        minimum_quality: safeMinimumQuality,
        priority_filter: priorityFilter,
      });

      setMission(startedMission);
      onMissionChange?.(startedMission);
    } catch (error) {
      console.error(
        "Unable to start mission:",
        error
      );

      setErrorMessage(
        "Unable to start the AI mission."
      );
    } finally {
      setIsStarting(false);
    }
  }

  const missionProgress = Math.min(
    Math.max(Number(mission?.progress || 0), 0),
    100
  );

  const missionIsActive =
    mission?.status === "running" ||
    mission?.status === "queued";

  const statusVariant =
    mission?.status === "completed"
      ? "success"
      : mission?.status === "failed"
        ? "danger"
        : mission?.status === "running"
          ? "primary"
          : "warning";

  return (
    <Card className="mission-control">
      <div className="mission-control-header">
        <div>
          <p className="eyebrow">AI Workforce</p>

          <h2>Mission Control</h2>

          <p className="mission-description">
            Choose an industry and location, then let Nestora search,
            analyze, save, and prepare outreach automatically.
          </p>
        </div>

        <span className="mission-control-icon">
          🤖
        </span>
      </div>

      <div className="mission-builder">
        <div className="mission-field">
          <label htmlFor="mission-business-type">
            Business Type
          </label>

          <input
            id="mission-business-type"
            type="text"
            value={businessType}
            onChange={(event) =>
              setBusinessType(event.target.value)
            }
            placeholder="Example: Professional services"
            disabled={missionIsActive}
          />
        </div>

        <div className="mission-field">
          <label htmlFor="mission-location">
            Location
          </label>

          <input
            id="mission-location"
            type="text"
            value={location}
            onChange={(event) =>
              setLocation(event.target.value)
            }
            placeholder="Example: Sydney, Australia"
            disabled={missionIsActive}
          />
        </div>

        <div className="mission-field">
          <label htmlFor="mission-quantity">
            Number of Businesses
          </label>

          <input
            id="mission-quantity"
            type="number"
            min="1"
            max="100"
            value={quantity}
            onChange={(event) =>
              setQuantity(event.target.value)
            }
            disabled={missionIsActive}
          />
        </div>

        <div className="mission-field">
          <label htmlFor="mission-minimum-quality">
            Minimum Quality
          </label>

          <input
            id="mission-minimum-quality"
            type="number"
            min="0"
            max="100"
            value={minimumQuality}
            onChange={(event) =>
              setMinimumQuality(event.target.value)
            }
            disabled={missionIsActive}
          />
        </div>

        <div className="mission-field">
          <label htmlFor="mission-priority-filter">
            Priority Filter
          </label>

          <select
            id="mission-priority-filter"
            value={priorityFilter}
            onChange={(event) =>
              setPriorityFilter(event.target.value)
            }
            disabled={missionIsActive}
          >
            {PRIORITY_FILTERS.map((filter) => (
              <option
                key={filter.value}
                value={filter.value}
              >
                {filter.label}
              </option>
            ))}
          </select>
        </div>
      </div>

      <div className="mission-option-grid">
        <label className="mission-option">
          <input
            type="checkbox"
            checked={analyzeWebsites}
            onChange={(event) =>
              setAnalyzeWebsites(event.target.checked)
            }
            disabled={missionIsActive}
          />

          <span>
            <strong>Analyze Websites</strong>

            <small>
              Check websites when a valid URL is available.
            </small>
          </span>
        </label>

        <label className="mission-option">
          <input
            type="checkbox"
            checked={generateOutreach}
            onChange={(event) =>
              setGenerateOutreach(event.target.checked)
            }
            disabled={missionIsActive}
          />

          <span>
            <strong>Generate Outreach</strong>

            <small>
              Prepare a personalized sales message for each lead.
            </small>
          </span>
        </label>
      </div>

      <div className="mission-control-actions">
        <Button
          onClick={handleStartMission}
          loading={isStarting}
          disabled={missionIsActive}
        >
          Start AI Mission
        </Button>

        {mission && (
          <Badge variant={statusVariant}>
            {mission.status || "queued"}
          </Badge>
        )}
      </div>

      {errorMessage && (
        <div className="mission-control-error">
          {errorMessage}
        </div>
      )}

      {mission && (
        <div className="mission-status-card">
          <div className="mission-progress-header">
            <div>
              <span>Current Step</span>

              <strong>
                {mission.current_step ||
                  "Preparing mission"}
              </strong>
            </div>

            <strong>
              {missionProgress}%
            </strong>
          </div>

          <div className="mission-progress-track">
            <div
              className="mission-progress-fill"
              style={{
                width: `${missionProgress}%`,
              }}
            />
          </div>

          <div className="mission-stat-grid">
            <div className="mission-stat">
              <span>Searched</span>
              <strong>
                {mission.searched ?? 0}
              </strong>
            </div>

            <div className="mission-stat">
              <span>Analyzed</span>
              <strong>
                {mission.analyzed ?? 0}
              </strong>
            </div>

            <div className="mission-stat">
              <span>Outreach</span>
              <strong>
                {mission.outreach_generated ?? 0}
              </strong>
            </div>

            <div className="mission-stat">
              <span>Mission ID</span>

              <strong className="mission-id">
                {mission.mission_id || "Pending"}
              </strong>
            </div>
          </div>
        </div>
      )}
    </Card>
  );
}

export default MissionControl;
