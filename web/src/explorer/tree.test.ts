import { describe, it, expect } from "vitest";
import { buildTree, type TreeNode } from "./tree";
import type { GraphModel } from "@archspec/model";

const model: GraphModel = {
  schemaVersion: 1,
  systems: ["payments", "platform"],
  graph: {
    "PROB-001": { type: "problem", system: "payments", services: ["billing"], status: "active", linked_adrs: ["ADR-001"] },
    "PROB-099": { type: "problem", services: [], status: "active", linked_adrs: [] }, // no system
    "ADR-001": { type: "adr", system: "payments", status: "accepted", linked_problems: ["PROB-001"], linked_services: ["billing"] },
    billing: { type: "service", system: "payments", problems: ["PROB-001"], adrs: ["ADR-001"], depends_on: ["database"] },
    auth: { type: "service", system: "platform", problems: [], adrs: [], depends_on: [], group: "infra" },
    database: { type: "service", system: "platform", problems: [], adrs: [], depends_on: [], group: "infra" },
    standalone: { type: "service", problems: [], adrs: [], depends_on: [] }, // no system, no group
    infra: { type: "group", children: ["auth", "database"] },
  },
};

const names = (nodes: TreeNode[]) => nodes.map((n) => n.name);
function findFolder(nodes: TreeNode[], name: string): TreeNode | undefined {
  for (const n of nodes) {
    if (n.kind === "folder" && n.name === name) return n;
    const inner = n.children ? findFolder(n.children, name) : undefined;
    if (inner) return inner;
  }
  return undefined;
}
function leafIds(nodes: TreeNode[]): string[] {
  const out: string[] = [];
  const walk = (ns: TreeNode[]) => ns.forEach((n) => (n.kind === "artifact" ? out.push(n.artifactId!) : walk(n.children ?? [])));
  walk(nodes);
  return out;
}

describe("buildTree", () => {
  it("group by type → Problems/ADRs/Services, services as individual leaves", () => {
    const tree = buildTree(model, "type");
    expect(names(tree)).toEqual(["Problems", "ADRs", "Services"]);
    const services = findFolder(tree, "Services")!;
    expect(leafIds([services]).sort()).toEqual(["auth", "billing", "database", "standalone"]);
  });

  it("group by system → partitions as folders + Unscoped for system-less artifacts", () => {
    const tree = buildTree(model, "system");
    expect(names(tree)).toEqual(["payments", "platform", "Unscoped"]);
    // PROB-099 and standalone have no system → Unscoped
    expect(leafIds([findFolder(tree, "Unscoped")!]).sort()).toEqual(["PROB-099", "standalone"]);
  });

  it("group by service group → groups + Ungrouped (group-less services, problems, ADRs)", () => {
    const tree = buildTree(model, "group");
    expect(names(tree)).toContain("infra");
    expect(leafIds([findFolder(tree, "infra")!]).sort()).toEqual(["auth", "database"]);
    const ungrouped = leafIds([findFolder(tree, "Ungrouped")!]).sort();
    expect(ungrouped).toEqual(["ADR-001", "PROB-001", "PROB-099", "billing", "standalone"]);
  });

  it("folder counts are recursive leaf counts", () => {
    const tree = buildTree(model, "system");
    // payments: PROB-001, ADR-001, billing = 3
    expect(findFolder(tree, "payments")!.count).toBe(3);
  });

  it("group by a label dimension → folder per value + Unlabeled leftover", () => {
    const m: GraphModel = {
      schemaVersion: 1,
      graph: {
        a: { type: "service", problems: [], adrs: [], depends_on: [], labels: { criticality: "core" } },
        b: { type: "service", problems: [], adrs: [], depends_on: [], labels: { criticality: "generic" } },
        c: { type: "service", problems: [], adrs: [], depends_on: [] }, // no label
      },
    };
    const tree = buildTree(m, "label:criticality");
    expect(names(tree)).toEqual(["core", "generic", "Unlabeled"]);
    expect(leafIds([findFolder(tree, "core")!])).toEqual(["a"]);
    expect(leafIds([findFolder(tree, "Unlabeled")!])).toEqual(["c"]);
  });

  it("ordering is deterministic across builds", () => {
    const a = JSON.stringify(buildTree(model, "system"));
    const b = JSON.stringify(buildTree(model, "system"));
    expect(a).toBe(b);
  });
});
