import type { GraphModel } from "@archspec/model";
import type { EventBus } from "../bus/bus";

/** Current workbench state. Events announce changes; the store holds the value. */
export interface WorkbenchState {
  model: GraphModel | null;
  selection: string | null;
  /** Set when the model fails to load or its schema version is unsupported. */
  loadError: string | null;
}

export interface WorkbenchStore {
  getState(): WorkbenchState;
  subscribe(listener: () => void): () => void;
}

/**
 * Holds current state so a late-mounting panel can read it on mount rather than
 * having missed the announcing event. Updated from bus events.
 */
export function createStore(bus: EventBus): WorkbenchStore {
  let state: WorkbenchState = { model: null, selection: null, loadError: null };
  const listeners = new Set<() => void>();

  const set = (next: Partial<WorkbenchState>) => {
    state = { ...state, ...next };
    listeners.forEach((l) => l());
  };

  bus.on("model.loaded", ({ model }) => set({ model, loadError: null }));
  bus.on("model.error", ({ message }) => set({ loadError: message }));
  bus.on("selection.changed", ({ nodeId }) => set({ selection: nodeId }));

  return {
    getState: () => state,
    subscribe(listener) {
      listeners.add(listener);
      return () => {
        listeners.delete(listener);
      };
    },
  };
}
