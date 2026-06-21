import { describe, it, expect, vi } from "vitest";
import { createEventBus } from "../bus/bus";
import { PanelRegistry } from "../panels/registry";
import { createOpenRouter, type Mounter } from "./router";

function makeMounter(): Mounter & { open: ReturnType<typeof vi.fn>; notifyNoHandler: ReturnType<typeof vi.fn> } {
  return { open: vi.fn(), notifyNoHandler: vi.fn() };
}

describe("open router", () => {
  it("routes document.open to a panel handling the content type", () => {
    const bus = createEventBus();
    const registry = new PanelRegistry();
    registry.register({ id: "markdown", title: "Doc", handles: ["markdown"], capability: "view" });
    const mounter = makeMounter();
    createOpenRouter(bus, registry, "view", mounter);

    bus.emit("document.open", { id: "ADR-001", contentType: "markdown" });

    expect(mounter.open).toHaveBeenCalledOnce();
    expect(mounter.open.mock.calls[0][0].id).toBe("markdown");
    expect(mounter.open.mock.calls[0][1]).toEqual({ documentId: "ADR-001", contentType: "markdown" });
  });

  it("picks deterministically when multiple panels are eligible", () => {
    const bus = createEventBus();
    const registry = new PanelRegistry();
    registry.register({ id: "zeta", title: "Z", handles: ["markdown"], capability: "view" });
    registry.register({ id: "alpha", title: "A", handles: ["markdown"], capability: "view" });
    const mounter = makeMounter();
    createOpenRouter(bus, registry, "view", mounter);

    bus.emit("document.open", { id: "x", contentType: "markdown" });
    expect(mounter.open.mock.calls[0][0].id).toBe("alpha"); // sorted by id
  });

  it("surfaces a clear message when no panel is eligible", () => {
    const bus = createEventBus();
    const registry = new PanelRegistry();
    const mounter = makeMounter();
    createOpenRouter(bus, registry, "view", mounter);

    bus.emit("document.open", { id: "x", contentType: "mermaid" });
    expect(mounter.notifyNoHandler).toHaveBeenCalledWith("mermaid");
    expect(mounter.open).not.toHaveBeenCalled();
  });

  it("excludes a serve-only panel when in view mode", () => {
    const bus = createEventBus();
    const registry = new PanelRegistry();
    registry.register({ id: "plantuml", title: "PlantUML", handles: ["mermaid"], capability: "serve" });
    const mounter = makeMounter();
    createOpenRouter(bus, registry, "view", mounter);

    bus.emit("document.open", { id: "x", contentType: "mermaid" });
    expect(mounter.notifyNoHandler).toHaveBeenCalledWith("mermaid");
  });
});
