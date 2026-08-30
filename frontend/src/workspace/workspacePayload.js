export const INDUSTRY_OPTIONS = [
  ["healthcare", "Healthcare"],
  ["dental", "Dental"],
  ["beauty", "Beauty"],
  ["retail", "Retail"],
  ["ecommerce", "E-commerce"],
  [
    "professional_services",
    "Professional services",
  ],
  ["home_services", "Home services"],
  ["hospitality", "Hospitality"],
  ["other", "Other"],
];

export const SIZE_OPTIONS = [
  ["solo", "Solo"],
  ["micro", "Micro"],
  ["small", "Small"],
  ["medium", "Medium"],
  ["large", "Large"],
];

function listValue(value) {
  if (Array.isArray(value)) {
    return value.join(", ");
  }

  return "";
}

export function workspaceToForm(
  workspace,
) {
  return {
    name: workspace?.name || "",
    industry:
      workspace?.industry || "other",
    country:
      workspace?.country || "",
    city: workspace?.city || "",
    region: workspace?.region || "",
    timezone:
      workspace?.timezone || "",
    locale: workspace?.locale || "",
    size: workspace?.size || "small",
    currency:
      workspace?.finances?.currency
      || "",
    description:
      workspace?.description || "",
    employee_count: String(
      workspace?.team?.employee_count
      ?? 0,
    ),
    locations_count: String(
      workspace?.operations
        ?.locations_count
      ?? 1,
    ),
    business_type:
      workspace?.metadata
        ?.business_type
      || "",
    products_services: listValue(
      workspace?.metadata
        ?.products_services,
    ),
    preferred_languages: listValue(
      workspace?.metadata
        ?.preferred_languages,
    ),
  };
}

function splitList(value) {
  return String(value || "")
    .split(",")
    .map((item) => item.trim())
    .filter(Boolean);
}

export function formToWorkspace(
  form,
  current = null,
) {
  return {
    name: form.name.trim(),
    industry: form.industry,
    country: form.country.trim(),
    city: form.city.trim() || null,
    region:
      form.region.trim() || null,
    timezone:
      form.timezone.trim() || null,
    locale:
      form.locale.trim() || null,
    size: form.size,
    description:
      form.description.trim(),
    team: {
      employee_count: Number(
        form.employee_count || 0,
      ),
      departments:
        current?.team?.departments || [],
      roles:
        current?.team?.roles || {},
    },
    customers: {
      total_customers:
        current?.customers
          ?.total_customers || 0,
      active_customers:
        current?.customers
          ?.active_customers || 0,
      inactive_customers:
        current?.customers
          ?.inactive_customers || 0,
      average_monthly_customers:
        current?.customers
          ?.average_monthly_customers
        || 0,
      returning_customer_rate:
        current?.customers
          ?.returning_customer_rate
        ?? null,
      average_customer_value:
        current?.customers
          ?.average_customer_value
        ?? null,
    },
    finances: {
      ...(current?.finances || {}),
      currency:
        form.currency.trim()
          .toUpperCase(),
    },
    operations: {
      daily_capacity:
        current?.operations
          ?.daily_capacity
        ?? null,
      average_daily_volume:
        current?.operations
          ?.average_daily_volume
        ?? null,
      cancellation_rate:
        current?.operations
          ?.cancellation_rate
        ?? null,
      utilization_rate:
        current?.operations
          ?.utilization_rate
        ?? null,
      locations_count: Number(
        form.locations_count || 1,
      ),
      working_hours:
        current?.operations
          ?.working_hours || [],
    },
    goals: current?.goals || [],
    metadata: {
      ...(current?.metadata || {}),
      business_type:
        form.business_type.trim(),
      products_services:
        splitList(
          form.products_services,
        ),
      preferred_languages:
        splitList(
          form.preferred_languages,
        ),
    },
  };
}
