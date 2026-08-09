import {
  useEffect,
  useMemo,
  useState,
} from "react";

import {
  AlertCircle,
  Building2,
  Globe2,
  Loader2,
  MapPin,
  Phone,
  RefreshCw,
  Sparkles,
} from "lucide-react";

import competitorsApi from "../../api/competitors";

import "./CompetitorIntelligence.css";


function normalizeName(value) {
  return String(value || "")
    .trim()
    .toLowerCase()
    .replaceAll("&", "and")
    .replace(/\s+/g, " ");
}


function formatCategory(value) {
  return String(value || "Business")
    .replaceAll("_", " ")
    .replace(/\b\w/g, (letter) =>
      letter.toUpperCase(),
    );
}


function hasValue(value) {
  return Boolean(
    value
    && String(value).trim()
    && String(value).trim().toLowerCase()
      !== "not found",
  );
}


function extractCompetitors(response) {
  if (Array.isArray(response)) {
    return response;
  }

  const possibleLists = [
    response?.businesses,
    response?.results,
    response?.items,
    response?.data,
    response?.leads,
  ];

  return (
    possibleLists.find(Array.isArray)
    || []
  );
}

function hasRealValue(value) {
  if (
    value === null ||
    value === undefined
  ) {
    return false;
  }

  const cleaned = String(value)
    .trim()
    .toLowerCase();

  return (
    cleaned !== "" &&
    cleaned !== "not found" &&
    cleaned !== "website missing" &&
    cleaned !== "phone missing" &&
    cleaned !== "email missing" &&
    cleaned !== "missing" &&
    cleaned !== "none" &&
    cleaned !== "null" &&
    cleaned !== "undefined" &&
    cleaned !== "n/a"
  );
}


function calculateProfileStrength(item) {
  let score = 10;

  const website =
    item?.website
    ?? item?.contact_website;

  const phone =
    item?.phone
    ?? item?.contact_phone;

  const email =
    item?.email
    ?? item?.contact_email;

  const location =
    item?.location
    ?? item?.address;

  const category =
    item?.category
    ?? item?.industry;

  if (hasRealValue(website)) {
    score += 25;
  }

  if (hasRealValue(phone)) {
    score += 20;
  }

  if (hasRealValue(email)) {
    score += 10;
  }

  if (hasRealValue(location)) {
    score += 15;
  }

  if (hasRealValue(category)) {
    score += 10;
  }

  if (
    item?.opening_hours
    || item?.openingHours
  ) {
    score += 10;
  }

  if (
    item?.nameMatchScore >= 70
    || item?.name_match_score >= 70
  ) {
    score += 10;
  }

  return Math.min(score, 100);
}

function normalizeCompetitor(item, index) {
  return {
    id:
      item?.id
      ?? item?.source_id
      ?? `competitor-${index}`,

    name:
      item?.businessName
      ?? item?.business_name
      ?? item?.name
      ?? "Unnamed business",

    category:
      item?.category
      ?? "Business",

    location:
      item?.location
      ?? item?.address
      ?? "Location unavailable",

    phone:
      item?.phone
      ?? "Not found",

    website:
      item?.website
      ?? "Not found",

    priority:
      item?.priority
      ?? "Medium",

    opportunityScore:
  calculateProfileStrength(item),

    contactQuality:
      Number(
        item?.contactQuality
        ?? item?.contact_quality
        ?? 0,
      ),

    source:
      item?.source
      ?? "Business Search",
  };
}


export default function CompetitorIntelligence({
  business,
}) {
  const [
    competitors,
    setCompetitors,
  ] = useState([]);

  const [
    isLoading,
    setIsLoading,
  ] = useState(false);

  const [
    errorMessage,
    setErrorMessage,
  ] = useState("");

  const [
    refreshKey,
    setRefreshKey,
  ] = useState(0);


  useEffect(() => {
    if (!business) {
      setCompetitors([]);
      setErrorMessage("");
      return;
    }

    let isMounted = true;

    async function loadCompetitors() {
      setIsLoading(true);
      setErrorMessage("");

      try {
        const category =
          business.category
          || business.industry
          || "medical center";

        const location =
          business.location
          || business.address
          || "Doha";

        const response =
          await competitorsApi.getCompetitors(
            category,
            location,
            12,
          );

        const currentBusinessName =
          normalizeName(
            business.name
            || business.businessName,
          );

        const normalizedResults =
          extractCompetitors(response)
            .map(normalizeCompetitor)
            .filter(
              (competitor) =>
                normalizeName(competitor.name)
                !== currentBusinessName,
            )
            .slice(0, 8);

        if (isMounted) {
          setCompetitors(normalizedResults);
        }
      } catch (error) {
        console.error(
          "Competitor discovery failed:",
          error,
        );

        if (isMounted) {
          setCompetitors([]);
          setErrorMessage(
            error?.message
            || "Unable to discover competitors.",
          );
        }
      } finally {
        if (isMounted) {
          setIsLoading(false);
        }
      }
    }

    loadCompetitors();

    return () => {
      isMounted = false;
    };
  }, [business, refreshKey]);


  const marketSummary = useMemo(() => {
    if (!competitors.length) {
      return {
        websites: 0,
        phones: 0,
        averageScore: 0,
      };
    }

    const websites = competitors.filter(
      (competitor) =>
        hasValue(competitor.website),
    ).length;

    const phones = competitors.filter(
      (competitor) =>
        hasValue(competitor.phone),
    ).length;

    const totalScore = competitors.reduce(
      (total, competitor) =>
        total
        + competitor.opportunityScore,
      0,
    );

    return {
      websites,
      phones,
      averageScore: Math.round(
        totalScore / competitors.length,
      ),
    };
  }, [competitors]);


  if (!business) {
    return null;
  }


  return (
    <section className="competitor-panel">
      <header className="competitor-header">
        <div>
          <p className="section-label">
            <Sparkles size={15} />
            AI Competitor Intelligence
          </p>

          <h2>Nearby Competitors</h2>

          <p>
            Live competitor discovery for{" "}
            <strong>
              {business.name
                || business.businessName}
            </strong>
            .
          </p>
        </div>

        <button
          type="button"
          className="competitor-refresh-button"
          onClick={() =>
            setRefreshKey((current) =>
              current + 1
            )
          }
          disabled={isLoading}
        >
          <RefreshCw
            size={15}
            className={
              isLoading
                ? "competitor-spin"
                : ""
            }
          />

          Refresh
        </button>
      </header>

      {isLoading ? (
        <div className="competitor-state">
          <Loader2
            size={30}
            className="competitor-spin"
          />

          <strong>
            Discovering nearby competitors...
          </strong>

          <span>
            Searching for{" "}
            {formatCategory(
              business.category
              || business.industry,
            )}
            {" "}businesses.
          </span>
        </div>
      ) : null}

      {!isLoading && errorMessage ? (
        <div className="competitor-error">
          <AlertCircle size={18} />

          <div>
            <strong>
              Competitor search failed
            </strong>

            <span>{errorMessage}</span>
          </div>
        </div>
      ) : null}

      {!isLoading
        && !errorMessage
        && competitors.length === 0 ? (
          <div className="competitor-state">
            <Building2 size={30} />

            <strong>
              No competitors found
            </strong>

            <span>
              Try refreshing or use a broader
              category in the CRM profile.
            </span>
          </div>
        ) : null}

      {!isLoading
        && competitors.length > 0 ? (
          <>
            <div className="competitor-summary">
              <article>
                <span>Competitors Found</span>
                <strong>
                  {competitors.length}
                </strong>
              </article>

              <article>
                <span>With Websites</span>
                <strong>
                  {marketSummary.websites}
                </strong>
              </article>

              <article>
                <span>With Phones</span>
                <strong>
                  {marketSummary.phones}
                </strong>
              </article>

              <article>
                <span>Average Profile Strength</span>
                <strong>
                  {marketSummary.averageScore}%
                </strong>
              </article>
            </div>

            <div className="competitor-list">
              {competitors.map(
                (competitor) => (
                  <article
                    className="competitor-card"
                    key={competitor.id}
                  >
                    <div className="competitor-card-header">
                      <div className="competitor-card-icon">
                        <Building2 size={18} />
                      </div>

                      <div>
                        <h3>
                          {competitor.name}
                        </h3>

                        <span>
                          {formatCategory(
                            competitor.category,
                          )}
                        </span>
                      </div>

                      <strong
  className="competitor-score"
  title="Profile strength based on available public business data"
>
  {competitor.opportunityScore}%
</strong>
                    </div>

                    <div className="competitor-card-details">
                      <span>
                        <MapPin size={13} />
                        {competitor.location}
                      </span>

                      <span>
                        <Phone size={13} />
                        {hasValue(
                          competitor.phone,
                        )
                          ? competitor.phone
                          : "Phone missing"}
                      </span>

                      <span>
                        <Globe2 size={13} />
                        {hasValue(
                          competitor.website,
                        )
                          ? "Website available"
                          : "Website missing"}
                      </span>
                    </div>
                  </article>
                ),
              )}
            </div>

            <div className="competitor-insight">
              <Sparkles size={18} />

              <div>
                <strong>
                  Initial market insight
                </strong>

                <p>
                  {marketSummary.websites} of{" "}
                  {competitors.length} nearby
                  competitors have websites, while{" "}
                  {marketSummary.phones} provide direct
                  phone contact. Nestora recommends
                  strengthening local SEO, reputation,
                  online booking, and patient follow-up
                  to improve competitive positioning.
                </p>
              </div>
            </div>
          </>
        ) : null}
    </section>
  );
}