import { describe, it, expect } from "vitest";
import { nodeToContent } from "./nodeContent";

describe("nodeToContent", () => {
  it("maps ADR and problem nodes to markdown", () => {
    expect(nodeToContent({ type: "adr", status: "accepted", linked_problems: [], linked_services: [] }))
      .toEqual({ contentType: "markdown" });
    expect(nodeToContent({ type: "problem", services: [], status: "active", linked_adrs: [] }))
      .toEqual({ contentType: "markdown" });
  });

  it("maps a service node to service-detail", () => {
    expect(nodeToContent({ type: "service", problems: [], adrs: [], depends_on: [] }))
      .toEqual({ contentType: "service-detail" });
  });

  it("returns null for a group node (focus, not a document)", () => {
    expect(nodeToContent({ type: "group", children: [] })).toBeNull();
  });
});
