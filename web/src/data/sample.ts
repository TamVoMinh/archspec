import type { GraphModel } from "@archspec/model";
import type { EmbeddedData } from "./source";

/**
 * Demo data used until the Python `serve`/`view` data path lands (§5). Exercises
 * depends_on edges, two partitions, and a service group so the panels have
 * something real to render. Mirrors the shape of `sda graph` output.
 */
const model: GraphModel = {
  schemaVersion: 1,
  systems: ["payments", "platform"],
  graph: {
    "PROB-001": {
      type: "problem",
      system: "payments",
      services: ["api-gateway", "billing"],
      status: "active",
      linked_adrs: ["ADR-001"],
    },
    "ADR-001": {
      type: "adr",
      system: "payments",
      status: "accepted",
      linked_problems: ["PROB-001"],
      linked_services: ["billing"],
    },
    "api-gateway": { type: "service", system: "payments", problems: ["PROB-001"], adrs: [], depends_on: ["auth", "billing"] },
    billing: { type: "service", system: "payments", problems: ["PROB-001"], adrs: ["ADR-001"], depends_on: ["database"] },
    auth: { type: "service", system: "platform", problems: [], adrs: [], depends_on: [], group: "infra" },
    database: { type: "service", system: "platform", problems: [], adrs: [], depends_on: [], group: "infra" },
    infra: { type: "group", children: ["auth", "database"] },
  },
};

export const SAMPLE_DATA: EmbeddedData = {
  model,
  documents: {
    "ADR-001": {
      id: "ADR-001",
      contentType: "markdown",
      text: [
        "# ADR-001: Cache billing reads in Redis",
        "",
        "## Metadata",
        "- status: accepted",
        "",
        "## Decision",
        "Introduce a Redis cache in front of `billing` reads to cut p95 latency.",
        "",
        "```yaml",
        "cache:",
        "  ttl: 60s",
        "  backend: redis",
        "```",
        "",
        "## Diagram",
        "",
        "```mermaid",
        "graph LR",
        "  api_gateway --> billing --> database",
        "```",
        "",
        "## Affected Services",
        "- billing",
      ].join("\n"),
    },
    "PROB-001": {
      id: "PROB-001",
      contentType: "markdown",
      text: [
        "# PROB-001: API latency spike on billing",
        "",
        "- source: slack",
        "- type: performance",
        "- status: active",
        "",
        "p95 latency > 2s on checkout under load.",
      ].join("\n"),
    },
    "api-gateway": { id: "api-gateway", contentType: "service-detail", text: "service: api-gateway\ntype: api\ndepends_on: [auth, billing]\nsystem: payments" },
    billing: { id: "billing", contentType: "service-detail", text: "service: billing\ntype: api\ndepends_on: [database]\nsystem: payments" },
    auth: { id: "auth", contentType: "service-detail", text: "service: auth\ntype: api\ngroup: infra\nsystem: platform" },
    database: { id: "database", contentType: "service-detail", text: "service: database\ntype: postgres\ngroup: infra\nsystem: platform" },
  },
};
