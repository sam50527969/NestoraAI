const ACTIVE_BUSINESS_KEY =
  "nestora.active_business_uid";

export function getActiveBusinessUid() {
  return (
    window.sessionStorage.getItem(
      ACTIVE_BUSINESS_KEY,
    )
  );
}

export function setActiveBusinessUid(
  businessUid,
) {
  const cleanBusinessUid =
    String(businessUid || "").trim();

  if (!cleanBusinessUid) {
    window.sessionStorage.removeItem(
      ACTIVE_BUSINESS_KEY,
    );
    return;
  }

  window.sessionStorage.setItem(
    ACTIVE_BUSINESS_KEY,
    cleanBusinessUid,
  );
}

export function clearActiveBusinessUid() {
  window.sessionStorage.removeItem(
    ACTIVE_BUSINESS_KEY,
  );
}
