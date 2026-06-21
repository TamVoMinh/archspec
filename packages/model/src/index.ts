/**
 * The graph-model contract shared by the Python engine and the viewer FE.
 *
 * Source of truth for the model *shape*. The Python side emits data matching this
 * (embedded in `sda graph view`, served by `sda graph serve`); panels consume it.
 * `SCHEMA_VERSION` lets a frozen `view` export detect an incompatible model.
 */

export const SCHEMA_VERSION = 1;

export type NodeType = "problem" | "adr" | "service" | "group";

export interface BaseNode {
  type: NodeType;
  /** Partition this node belongs to, when the workspace is partitioned. */
  system?: string;
  /** Classification labels (dimension → value), e.g. { area: "payments", criticality: "core" }. */
  labels?: Record<string, string>;
}

export interface ProblemNode extends BaseNode {
  type: "problem";
  services: string[];
  status: string;
  linked_adrs: string[];
}

export interface AdrNode extends BaseNode {
  type: "adr";
  status: string;
  linked_problems: string[];
  linked_services: string[];
  superseded_by?: string | null;
}

export interface ServiceNode extends BaseNode {
  type: "service";
  problems: string[];
  adrs: string[];
  depends_on: string[];
  group?: string;
}

export interface GroupNode extends BaseNode {
  type: "group";
  children: string[];
}

export type GraphNode = ProblemNode | AdrNode | ServiceNode | GroupNode;

/** The full model the viewer loads (embedded in `view`, fetched in `serve`). */
export interface GraphModel {
  schemaVersion: number;
  /** Present only for partitioned workspaces. */
  systems?: string[];
  graph: Record<string, GraphNode>;
}
