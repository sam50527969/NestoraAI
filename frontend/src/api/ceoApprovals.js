import { request } from "./client";


export function getCEOApprovals({
  status,
  limit = 100,
} = {}) {
  const searchParams =
    new URLSearchParams();

  if (status) {
    searchParams.set(
      "status",
      status,
    );
  }

  searchParams.set(
    "limit",
    String(limit),
  );

  return request(
    `/ceo-approvals?${searchParams.toString()}`,
  );
}


export function createCEOApproval(data) {
  return request("/ceo-approvals", {
    method: "POST",
    body: JSON.stringify(data),
  });
}


export function approveCEOApproval(
  approvalUid,
  data = {},
) {
  return request(
    `/ceo-approvals/${approvalUid}/approve`,
    {
      method: "POST",
      body: JSON.stringify({
        reviewed_by:
          data.reviewed_by || "CEO",
        decision_note:
          data.decision_note || null,
      }),
    },
  );
}


export function rejectCEOApproval(
  approvalUid,
  data = {},
) {
  return request(
    `/ceo-approvals/${approvalUid}/reject`,
    {
      method: "POST",
      body: JSON.stringify({
        reviewed_by:
          data.reviewed_by || "CEO",
        decision_note:
          data.decision_note || null,
      }),
    },
  );
}


export function executeCEOApproval(
  approvalUid,
) {
  return request(
    `/ceo-approvals/${approvalUid}/execute`,
    {
      method: "POST",
    },
  );
}