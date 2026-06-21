import type { GraphModel } from "@archspec/model";

/** Content types a panel can render / a node can resolve to. */
export type ContentType = "graph" | "markdown" | "mermaid" | "yaml" | "service-detail";

/**
 * The v1 event vocabulary. Together with the panel manifest this is the plugin
 * contract — panels coordinate only through these fire-and-forget events.
 */
export interface EventMap {
  "model.loaded": { model: GraphModel };
  "selection.changed": { nodeId: string | null };
  "document.open": { id: string; contentType: ContentType };
  "graph.highlight": { nodeIds: string[] };
  "panel.mounted": { panelId: string };
  "panel.disposed": { panelId: string };
}

export type EventName = keyof EventMap;
