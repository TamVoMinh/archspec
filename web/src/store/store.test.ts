import { describe, it, expect } from "vitest";
import { createEventBus } from "../bus/bus";
import { createStore } from "./store";
import type { GraphModel } from "@archspec/model";

const model: GraphModel = { schemaVersion: 1, graph: {} };

describe("workbench store", () => {
  it("updates from model.loaded and selection.changed", () => {
    const bus = createEventBus();
    const store = createStore(bus);
    bus.emit("model.loaded", { model });
    bus.emit("selection.changed", { nodeId: "ADR-001" });
    expect(store.getState().model).toBe(model);
    expect(store.getState().selection).toBe("ADR-001");
  });

  it("exposes current state to a late reader (cold-start)", () => {
    const bus = createEventBus();
    const store = createStore(bus);
    bus.emit("selection.changed", { nodeId: "billing" });
    // a panel that mounts now reads current state, despite missing the event
    expect(store.getState().selection).toBe("billing");
  });

  it("notifies subscribers on change", () => {
    const bus = createEventBus();
    const store = createStore(bus);
    let calls = 0;
    store.subscribe(() => {
      calls++;
    });
    bus.emit("selection.changed", { nodeId: "a" });
    expect(calls).toBe(1);
  });
});
