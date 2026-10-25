import { ReplitConnectors } from "@replit/connectors-sdk";
import { GetSalesforceDemoDataResponse } from "@workspace/api-zod";

// Public demo access is pinned to this approved Developer Edition and these
// synthetic records. Never broaden this into an arbitrary-SOQL public endpoint.
const DEMO_ORG_ID = "00Dak00001Lzxo9EAB";
const PARTNER_ACCOUNTS: Record<string, string> = {
  "001ak000040hoabAAA": "p-red-valley",
  "001ak000040hoacAAA": "p-bluewater",
};
const REGISTRATION_IDS = [
  "a00ak00003i74GvAAI",
  "a00ak00003i74GwAAI",
  "a00ak00003i74GxAAI",
];
const connectors = new ReplitConnectors();
type Snapshot = ReturnType<typeof GetSalesforceDemoDataResponse.parse>;
type SfRegistration = {
  Id: string;
  Name: string;
  Partner_Account__c: string;
  Opportunity__r: { Name: string; StageName: string };
  Status__c: string;
  Submitted_At__c: string | null;
  Expected_Close_Date__c: string | null;
  Next_Step__c: string | null;
  LastModifiedDate: string;
};
let cache: { at: number; data: Snapshot } | undefined;
let pending: Promise<Snapshot> | undefined;

export function isSalesforceDemoPartner(partnerId: string): boolean {
  return Object.values(PARTNER_ACCOUNTS).includes(partnerId);
}

async function query<T>(soql: string): Promise<T[]> {
  const response = await connectors.proxy(
    "salesforce",
    `/services/data/v66.0/query?q=${encodeURIComponent(soql)}`,
    { method: "GET" },
  );
  if (!response.ok) throw new Error("Salesforce query unavailable.");
  const body = (await response.json()) as { records?: T[]; done?: boolean };
  if (!Array.isArray(body.records) || body.done !== true) {
    throw new Error("Unexpected Salesforce response.");
  }
  return body.records;
}

async function readSnapshot(): Promise<Snapshot> {
  const orgs = await query<{ Id: string; OrganizationType: string }>(
    "SELECT Id, OrganizationType FROM Organization",
  );
  if (orgs[0]?.Id !== DEMO_ORG_ID || orgs[0]?.OrganizationType !== "Developer Edition") {
    throw new Error("The connected org is not the approved public demo org.");
  }
  const ids = REGISTRATION_IDS.map(id => `'${id}'`).join(",");
  const partners = Object.keys(PARTNER_ACCOUNTS).map(id => `'${id}'`).join(",");
  const records = await query<SfRegistration>(
    "SELECT Id, Name, Partner_Account__c, Opportunity__r.Name, Opportunity__r.StageName, " +
    "Status__c, Submitted_At__c, Expected_Close_Date__c, Next_Step__c, LastModifiedDate " +
    `FROM Deal_Registration__c WHERE Id IN (${ids}) AND Partner_Account__c IN (${partners}) ORDER BY Name`,
  );
  const quote = await connectors.proxy("salesforce", "/services/data/v66.0/sobjects/Quote/describe", { method: "GET" });
  if (!quote.ok && quote.status !== 404) throw new Error("Cannot verify native Quote availability.");
  return GetSalesforceDemoDataResponse.parse({
    fetchedAt: new Date().toISOString(),
    quoteAvailability: quote.ok ? "available_not_configured" : "unavailable",
    registrations: records.map(record => ({
      id: record.Name,
      salesforceId: record.Id,
      partnerId: PARTNER_ACCOUNTS[record.Partner_Account__c],
      title: record.Opportunity__r.Name,
      status: record.Status__c,
      opportunityStage: record.Opportunity__r.StageName,
      submittedAt: record.Submitted_At__c ?? "",
      expectedClose: record.Expected_Close_Date__c ?? "",
      lastModifiedAt: record.LastModifiedDate,
      owner: "Hidden in public demo",
      nextStep: record.Next_Step__c ?? "No next step recorded in Salesforce.",
      sourceLabel: "Salesforce · Deal_Registration__c · demo-only record",
    })),
  });
}

export async function getSalesforceDemoData(fresh = false): Promise<Snapshot> {
  if (!fresh && cache && Date.now() - cache.at < 30_000) return cache.data;
  if (pending) return pending;
  pending = readSnapshot().then(data => {
    cache = { at: Date.now(), data };
    return data;
  }).finally(() => { pending = undefined; });
  return pending;
}
