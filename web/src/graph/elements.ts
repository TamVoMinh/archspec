import type { GraphModel } from "@archspec/model";

/** A Cytoscape element (node or edge). Kept structural so it's testable without cytoscape. */
export interface CyElement {
  data: Record<string, unknown>;
}

export type EdgeKind = "depends_on" | "affects" | "addresses" | "contains";

/**
 * Convert the knowledge-graph model into Cytoscape elements:
 * - a node per graph node, typed by `ntype`
 * - partition boundaries via compound `sys:<system>` parent nodes
 * - edges: service→service `depends_on`, problem→adr `addresses`,
 *   problem/adr→service `affects`, group→child `contains`
 */
export function toElements(model: GraphModel): CyElement[] {
  const els: CyElement[] = [];
  const present = new Set(Object.keys(model.graph));

  // Partition compound parents.
  const systems = new Set<string>();
  for (const node of Object.values(model.graph)) {
    if (node.system) systems.add(node.system);
  }
  for (const sys of [...systems].sort()) {
    els.push({ data: { id: `sys:${sys}`, label: sys, kind: "system" } });
  }

  // Nodes.
  for (const [id, node] of Object.entries(model.graph)) {
    const data: Record<string, unknown> = { id, label: id, ntype: node.type };
    if (node.system) data.parent = `sys:${node.system}`;
    els.push({ data });
  }

  // Edges (deduped; only between present nodes).
  const seen = new Set<string>();
  const addEdge = (source: string, target: string, kind: EdgeKind) => {
    if (!present.has(source) || !present.has(target) || source === target) return;
    const id = `${source}|${kind}|${target}`;
    if (seen.has(id)) return;
    seen.add(id);
    els.push({ data: { id, source, target, kind } });
  };

  for (const [id, node] of Object.entries(model.graph)) {
    switch (node.type) {
      case "problem":
        node.linked_adrs.forEach((a) => addEdge(id, a, "addresses"));
        node.services.forEach((s) => addEdge(id, s, "affects"));
        break;
      case "adr":
        node.linked_problems.forEach((p) => addEdge(p, id, "addresses"));
        node.linked_services.forEach((s) => addEdge(id, s, "affects"));
        break;
      case "service":
        node.depends_on.forEach((d) => addEdge(id, d, "depends_on"));
        break;
      case "group":
        node.children.forEach((c) => addEdge(id, c, "contains"));
        break;
    }
  }

  return els;
}
