import type { GraphModel, GraphNode, NodeType } from "@archspec/model";

// Structural groupings, plus dynamic label dimensions encoded as `label:<dimension>`.
export type GroupBy = "system" | "type" | "group" | `label:${string}`;

/** Distinct label dimensions present across the model's nodes (for the Group-by menu). */
export function labelDimensions(model: GraphModel): string[] {
  const dims = new Set<string>();
  for (const node of Object.values(model.graph)) {
    for (const dim of Object.keys(node.labels ?? {})) dims.add(dim);
  }
  return [...dims].sort();
}

/** A node in the Explorer tree: a logical folder or an artifact leaf. */
export interface TreeNode {
  id: string;
  name: string;
  kind: "folder" | "artifact";
  ntype?: NodeType; // artifact leaves only
  artifactId?: string; // artifact leaves only — the model node id to open
  count?: number; // folders only — recursive leaf count
  children?: TreeNode[];
}

interface Artifact {
  id: string;
  node: GraphNode;
}

const TYPE_ORDER: NodeType[] = ["problem", "adr", "service"];
const TYPE_LABEL: Record<NodeType, string> = {
  problem: "Problems",
  adr: "ADRs",
  service: "Services",
  group: "Groups",
};

function leaf(a: Artifact): TreeNode {
  return { id: `leaf:${a.id}`, name: a.id, kind: "artifact", ntype: a.node.type, artifactId: a.id };
}

function countLeaves(n: TreeNode): number {
  return n.kind === "artifact" ? 1 : (n.children ?? []).reduce((s, c) => s + countLeaves(c), 0);
}

function folder(id: string, name: string, children: TreeNode[]): TreeNode {
  return { id, name, kind: "folder", children, count: children.reduce((s, c) => s + countLeaves(c), 0) };
}

/** Problems/ADRs/Services subfolders (non-empty only); leaves sorted by id. */
function byType(prefix: string, arts: Artifact[]): TreeNode[] {
  const out: TreeNode[] = [];
  for (const t of TYPE_ORDER) {
    const items = arts
      .filter((a) => a.node.type === t)
      .sort((x, y) => x.id.localeCompare(y.id))
      .map(leaf);
    if (items.length) out.push(folder(`${prefix}/type:${t}`, TYPE_LABEL[t], items));
  }
  return out;
}

const groupOf = (a: Artifact): string | undefined =>
  a.node.type === "service" ? a.node.group : undefined;

/**
 * Build the Explorer tree for a grouping. Folders are logical; leaves are
 * artifacts (problems, ADRs, services — group nodes are structure, not leaves).
 * Artifacts with no value for the active grouping land in an explicit leftover
 * folder rather than being dropped. Ordering is deterministic.
 */
export function buildTree(model: GraphModel, groupBy: GroupBy): TreeNode[] {
  const arts: Artifact[] = Object.entries(model.graph)
    .filter(([, n]) => n.type === "problem" || n.type === "adr" || n.type === "service")
    .map(([id, node]) => ({ id, node }));

  if (groupBy === "type") {
    return byType("type", arts);
  }

  if (groupBy.startsWith("label:")) {
    const dim = groupBy.slice("label:".length);
    const values = [...new Set(arts.map((a) => a.node.labels?.[dim]).filter((v): v is string => !!v))].sort();
    const folders = values.map((v) =>
      folder(`label:${dim}:${v}`, v, arts
        .filter((a) => a.node.labels?.[dim] === v)
        .sort((x, y) => x.id.localeCompare(y.id))
        .map(leaf)),
    );
    const unlabeled = arts.filter((a) => !a.node.labels?.[dim]);
    if (unlabeled.length) folders.push(folder(`label:${dim}:__unlabeled`, "Unlabeled", byType(`label:${dim}:__unlabeled`, unlabeled)));
    return folders;
  }

  if (groupBy === "system") {
    const systems = [...new Set(arts.map((a) => a.node.system).filter((s): s is string => !!s))].sort();
    const folders = systems.map((sys) =>
      folder(`sys:${sys}`, sys, byType(`sys:${sys}`, arts.filter((a) => a.node.system === sys))),
    );
    const unscoped = arts.filter((a) => !a.node.system);
    if (unscoped.length) folders.push(folder("sys:__unscoped", "Unscoped", byType("sys:__unscoped", unscoped)));
    return folders;
  }

  // groupBy === "group"
  const groups = [...new Set(arts.map(groupOf).filter((g): g is string => !!g))].sort();
  const folders = groups.map((g) => {
    const items = arts
      .filter((a) => groupOf(a) === g)
      .sort((x, y) => x.id.localeCompare(y.id))
      .map(leaf);
    return folder(`grp:${g}`, g, items);
  });
  // Leftover: group-less services + all problems + all ADRs.
  const leftover = arts.filter((a) => a.node.type !== "service" || !groupOf(a));
  if (leftover.length) folders.push(folder("grp:__ungrouped", "Ungrouped", byType("grp:__ungrouped", leftover)));
  return folders;
}
