import {
  getAccessToken,
} from "../auth/session";
import {
  getActiveBusinessUid,
} from "../workspace/session";

const API_BASE_URL =
  import.meta.env.VITE_API_BASE_URL || "http://127.0.0.1:8000";


export class MarketingApiError extends Error {
  constructor(message, status = null, details = null) {
    super(message);

    this.name = "MarketingApiError";
    this.status = status;
    this.details = details;
  }
}


async function parseResponse(response) {
  const contentType = response.headers.get("content-type") || "";

  if (contentType.includes("application/json")) {
    return response.json();
  }

  const text = await response.text();

  return text || null;
}


function getErrorMessage(data, fallbackMessage) {
  if (!data) {
    return fallbackMessage;
  }

  if (typeof data === "string") {
    return data;
  }

  if (typeof data.detail === "string") {
    return data.detail;
  }

  if (Array.isArray(data.detail)) {
    return data.detail
      .map((item) => {
        const location = Array.isArray(item.loc)
          ? item.loc.join(" → ")
          : "request";

        return `${location}: ${item.msg || "Invalid value"}`;
      })
      .join("\n");
  }

  if (typeof data.message === "string") {
    return data.message;
  }

  return fallbackMessage;
}


function formatIndustry(value) {
  return String(value || "")
    .replaceAll("_", " ")
    .replace(/\b\w/g, (letter) =>
      letter.toUpperCase(),
    );
}


function workspaceLocation(workspace) {
  return [
    workspace?.city,
    workspace?.region,
    workspace?.country,
  ]
    .map((value) =>
      String(value || "").trim(),
    )
    .filter(Boolean)
    .filter(
      (value, index, values) =>
        values.indexOf(value) === index,
    )
    .join(", ");
}


function metadataList(
  workspace,
  field,
) {
  const value =
    workspace?.metadata?.[field];

  return Array.isArray(value)
    ? value
    : [];
}


export function createDefaultMarketingRequest() {
  return {
    business: {
      business_id: "",
      business_name: "",
      industry: "",
      location: "",
      description: "",
      products_or_services: [],
      target_audience: [],
      differentiators: [],
      current_channels: [],
      preferred_languages: [],
      brand_voice: "",
    },

    goal: {
      objective: "",
      timeline_days: 30,
      monthly_budget: 0,
      currency: "",
      preferred_channels: [],
      approval_required: true,
    },

    additional_instructions: "",
  };
}


export function createMarketingRequestFromWorkspace(
  workspace,
) {
  const request =
    createDefaultMarketingRequest();

  if (!workspace) {
    return request;
  }

  const configuredIndustry =
    formatIndustry(
      workspace.industry,
    );

  const businessType = String(
    workspace.metadata?.business_type
    || "",
  ).trim();

  return {
    ...request,
    business: {
      ...request.business,
      business_id:
        workspace.business_uid,
      business_name:
        workspace.name,
      industry: [
        configuredIndustry,
        businessType,
      ]
        .filter(Boolean)
        .join(" / "),
      location:
        workspaceLocation(
          workspace,
        ),
      description:
        workspace.description || "",
      products_or_services:
        metadataList(
          workspace,
          "products_services",
        ),
      target_audience:
        metadataList(
          workspace,
          "target_audience",
        ),
      differentiators:
        metadataList(
          workspace,
          "differentiators",
        ),
      current_channels:
        metadataList(
          workspace,
          "marketing_channels",
        ),
      preferred_languages:
        metadataList(
          workspace,
          "preferred_languages",
        ),
      brand_voice:
        workspace.metadata
          ?.brand_voice || "",
    },
    goal: {
      ...request.goal,
      currency:
        workspace.finances
          ?.currency || "",
    },
  };
}


export function mergeMarketingRequestWithWorkspace(
  current,
  workspace,
) {
  const authoritative =
    createMarketingRequestFromWorkspace(
      workspace,
    );

  return {
    ...current,
    business: {
      ...authoritative.business,
      target_audience:
        current.business
          ?.target_audience || [],
      differentiators:
        current.business
          ?.differentiators || [],
      current_channels:
        current.business
          ?.current_channels || [],
      brand_voice:
        current.business
          ?.brand_voice || "",
    },
    goal: {
      ...current.goal,
      currency:
        authoritative.goal.currency,
    },
  };
}


export function createMarketingBusinessView(
  workspace,
) {
  if (!workspace) {
    return null;
  }

  return {
    id: workspace.business_uid,
    name: workspace.name,
    category:
      formatIndustry(
        workspace.industry,
      ),
    industry:
      workspace.industry,
    address:
      workspaceLocation(
        workspace,
      ),
    location:
      workspaceLocation(
        workspace,
      ),
    website:
      workspace.metadata?.website
      || "Not found",
    description:
      workspace.description || "",
    products:
      metadataList(
        workspace,
        "products_services",
      ),
    source: "Workspace",
  };
}


export async function runMarketingDirector(
  request,
  options = {},
) {
  const controller = new AbortController();

  const timeoutMs =
    typeof options.timeoutMs === "number"
      ? options.timeoutMs
      : 120000;

  const timeoutId = window.setTimeout(() => {
    controller.abort();
  }, timeoutMs);

  const accessToken =
    getAccessToken();

  const activeBusinessUid =
    getActiveBusinessUid();

  try {
    const response = await fetch(
      `${API_BASE_URL}/marketing/director`,
      {
        method: "POST",

        headers: {
          Accept: "application/json",
          "Content-Type": "application/json",
          ...(accessToken
            ? {
                Authorization:
                  `Bearer ${accessToken}`,
              }
            : {}),
          ...(activeBusinessUid
            ? {
                "X-Business-Uid":
                  activeBusinessUid,
              }
            : {}),
        },

        body: JSON.stringify(request),

        signal: options.signal || controller.signal,
      },
    );

    const data = await parseResponse(response);

    if (!response.ok) {
      throw new MarketingApiError(
        getErrorMessage(
          data,
          "The Marketing Director could not complete the request.",
        ),
        response.status,
        data,
      );
    }

    return data;
  } catch (error) {
    if (error instanceof MarketingApiError) {
      throw error;
    }

    if (error?.name === "AbortError") {
      throw new MarketingApiError(
        "The Marketing Director request took too long and was stopped.",
        408,
      );
    }

    throw new MarketingApiError(
      "Could not connect to the Nestora backend. Make sure the backend is running on port 8000.",
      null,
      error,
    );
  } finally {
    window.clearTimeout(timeoutId);
  }
}


export const MARKETING_CHANNELS = [
  {
    value: "instagram",
    label: "Instagram",
  },
  {
    value: "facebook",
    label: "Facebook",
  },
  {
    value: "linkedin",
    label: "LinkedIn",
  },
  {
    value: "tiktok",
    label: "TikTok",
  },
  {
    value: "x",
    label: "X",
  },
  {
    value: "email",
    label: "Email",
  },
  {
    value: "whatsapp",
    label: "WhatsApp",
  },
  {
    value: "google_business",
    label: "Google Business",
  },
  {
    value: "google_ads",
    label: "Google Ads",
  },
];


export default {
  runMarketingDirector,
  createDefaultMarketingRequest,
  createMarketingRequestFromWorkspace,
  mergeMarketingRequestWithWorkspace,
  createMarketingBusinessView,
  MARKETING_CHANNELS,
};
