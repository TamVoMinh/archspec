import { describe, it, expect, vi } from "vitest";
import { createEventBus } from "./bus";

describe("event bus", () => {
  it("delivers an emitted event to subscribers", () => {
    const bus = createEventBus();
    const handler = vi.fn();
    bus.on("selection.changed", handler);
    bus.emit("selection.changed", { nodeId: "ADR-001" });
    expect(handler).toHaveBeenCalledWith({ nodeId: "ADR-001" });
  });

  it("supports multiple subscribers for the same event", () => {
    const bus = createEventBus();
    const a = vi.fn();
    const b = vi.fn();
    bus.on("graph.highlight", a);
    bus.on("graph.highlight", b);
    bus.emit("graph.highlight", { nodeIds: ["billing"] });
    expect(a).toHaveBeenCalledOnce();
    expect(b).toHaveBeenCalledOnce();
  });

  it("stops delivering after unsubscribe", () => {
    const bus = createEventBus();
    const handler = vi.fn();
    const off = bus.on("selection.changed", handler);
    off();
    bus.emit("selection.changed", { nodeId: "x" });
    expect(handler).not.toHaveBeenCalled();
  });
});
