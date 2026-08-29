import { request } from "./client";


export function getCEOExecutions({
  limit = 50,
  offset = 0,
} = {}) {
  const searchParams =
    new URLSearchParams();

  searchParams.set(
    "limit",
    String(limit),
  );

  searchParams.set(
    "offset",
    String(offset),
  );

  return request(
    `/ceo-executions?${searchParams.toString()}`,
  );
}


export function getCEOExecution(
  executionUid,
) {
  return request(
    `/ceo-executions/${executionUid}`,
  );
}


export function getCEOExecutionByApproval(
  approvalUid,
) {
  return request(
    `/ceo-executions/approval/${approvalUid}`,
  );
}
