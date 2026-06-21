import type { GraphNode } from "@archspec/model";
import type { ContentType } from "../bus/events";

/**
 * Map a graph node to the content the viewer opens when it's activated.
 * - ADR  → its Markdown file
 * - problem → its record (rendered as Markdown)
 * - service → a detail derived from its services.yaml entry (no standalone file)
 * - group → null: focus/filter the graph instead of opening a document
 */
export function nodeToContent(node: GraphNode): { contentType: ContentType } | null {
  switch (node.type) {
    case "adr":
      return { contentType: "markdown" };
    case "problem":
      return { contentType: "markdown" };
    case "service":
      return { contentType: "service-detail" };
    case "group":
      return null;
  }
}
