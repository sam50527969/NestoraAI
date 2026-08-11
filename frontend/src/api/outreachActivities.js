import { request } from "./client";

export function getOutreachActivities({
  status,
  approvalUid,
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

  if (approvalUid) {
    searchParams.set(
      "approval_uid",
      approvalUid,
    );
  }

  searchParams.set(
    "limit",
    String(limit),
  );

  return request(
    `/outreach-activities?${searchParams.toString()}`,
  );
}

export function getOutreachActivity(
  activityUid,
) {
  return request(
    `/outreach-activities/${activityUid}`,
  );
}

export function markOutreachActivitySent(
  activityUid,
) {
  return request(
    `/outreach-activities/${activityUid}/mark-sent`,
    {
      method: "POST",
    },
  );
}