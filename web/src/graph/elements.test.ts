import { describe, it, expect } from "vitest";
import { toElements } from "./elements";
import type { GraphModel } from "@archspec/model";

const model: GraphModel = {
  schemaVersion: 1,
  systems: ["payments", "platform"],
  graph: {
    "PROB-001": { type: "problem", system: "payments", services: ["billing"], status: "active", linked_adrs: ["ADR-001"] },
    "ADR-001": { type: "adr", system: "payments", status: "accepted", linked_problems: ["PROB-001"], linked_services: ["billing"] },
    billing: { type: "service", system: "payments", problems: ["PROB-001"], adrs: ["ADR-001"], depends_on: ["database"] },
    database: { type: "service", system: "platform", problems: [], adrs: [], depends_on: [], group: "infra" },
    infra: { type: "group", children: ["database"] },
  },
};

function edges(els: ReturnType<typeof toElements>) {
  return els.filter((e) => "source" in e.data).map((e) => e.data);
}

describe("toElements", () => {
  it("emits a depends_on edge between services", () => {
    expect(edges(toElements(model))).toContainEqual(
      expect.objectContaining({ source: "billing", target: "database", kind: "depends_on" }),
    );
  });

  it("creates partition compound parents and assigns nodes to them", () => {
    const els = toElements(model);
    expect(els).toContainEqual({ data: { id: "sys:payments", label: "payments", kind: "system" } });
    const billing = els.find((e) => e.data.id === "billing");
    expect(billing?.data.parent).toBe("sys:payments");
  });

  it("represents group membership via contains edges", () => {
    expect(edges(toElements(model))).toContainEqual(
      expect.objectContaining({ source: "infra", target: "database", kind: "contains" }),
    );
  });

  it("does not emit edges to absent nodes", () => {
    const m: GraphModel = {
      schemaVersion: 1,
      graph: { api: { type: "service", problems: [], adrs: [], depends_on: ["ghost"] } },
    };
    expect(edges(toElements(m))).toHaveLength(0);
  });
});
