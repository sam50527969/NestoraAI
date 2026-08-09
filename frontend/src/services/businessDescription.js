function hasValue(value) {
  return Boolean(
    value &&
    String(value).trim() &&
    String(value).trim().toLowerCase() !== "not found",
  );
}

function formatCategory(category) {
  return String(category || "business")
    .replaceAll("_", " ")
    .replace(/\b\w/g, (c) => c.toUpperCase());
}

export function generateBusinessDescription(business) {
  if (!business) {
    return "";
  }

  const category = formatCategory(
    business.category,
  );

  const location =
    business.location ||
    business.address ||
    "Qatar";

  const hasWebsiteAvailable = hasValue(
    business.website,
  );

  const hasPhoneAvailable = hasValue(
    business.phone,
  );

  const strengths = [];

  if (hasWebsiteAvailable) {
    strengths.push("an active business website");
  }

  if (hasPhoneAvailable) {
    strengths.push("a verified phone number");
  }

  const strengthsText =
    strengths.length > 0
      ? strengths.join(" and ")
      : "basic business information";

  return (
    `${business.businessName || business.name} is a `
    + `${category.toLowerCase()} located in ${location}. `
    + `The business currently has ${strengthsText}, `
    + `making it a strong candidate for AI-driven `
    + `marketing, customer acquisition, and business `
    + `growth initiatives.`
  );
}

export default generateBusinessDescription;