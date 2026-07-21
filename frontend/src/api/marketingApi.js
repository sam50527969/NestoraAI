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

  try {
    const response = await fetch(
      `${API_BASE_URL}/marketing/director`,
      {
        method: "POST",

        headers: {
          Accept: "application/json",
          "Content-Type": "application/json",
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


export function createDefaultMarketingRequest() {
  return {
    business: {
      business_id: "",
      business_name: "",
      industry: "",
      location: "Doha",
      description: "",
      products_or_services: [],
      target_audience: [],
      differentiators: [],
      current_channels: [],
      preferred_languages: ["English"],
      brand_voice: "Professional and friendly",
    },

    goal: {
      objective: "",
      timeline_days: 30,
      monthly_budget: 0,
      currency: "QAR",
      preferred_channels: [],
      approval_required: true,
    },

    additional_instructions: "",
  };
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
  MARKETING_CHANNELS,
};