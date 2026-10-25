import { useQuery } from "@tanstack/react-query";
import { getSalesforceDemoData } from "@workspace/api-client-react";

export function useSalesforceDemoRecords() {
  return useQuery({
    queryKey: ["salesforce-demo-registrations"],
    queryFn: ({ signal }) => getSalesforceDemoData({ signal }),
    staleTime: 30_000,
    refetchInterval: 60_000,
    retry: 1,
  });
}

export function SalesforceDataNotice() {
  const source = useSalesforceDemoRecords();
  return (
    <div className={`notice ${source.isError ? "caution" : "info"}`} role="status" style={{ marginTop: 12 }}>
      <div>
        {source.isError
          ? "Salesforce is unavailable. Previously fetched records may be stale; no local examples are substituted for Salesforce records."
          : source.isLoading
            ? "Reading the approved demo registrations from Salesforce…"
            : `Live Salesforce lookup · demo-only records · fetched ${new Date(source.data!.fetchedAt).toLocaleString()}. Registration status and Opportunity stage are separate.`}
      </div>
      <button className="button secondary small" style={{ marginLeft: "auto", flexShrink: 0 }} disabled={source.isFetching} onClick={() => void source.refetch()}>
        {source.isFetching ? "Refreshing…" : "Refresh"}
      </button>
    </div>
  );
}
