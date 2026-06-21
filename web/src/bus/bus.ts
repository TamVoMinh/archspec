import type { EventMap, EventName } from "./events";

type Handler<K extends EventName> = (payload: EventMap[K]) => void;

/** Front-end-only pub/sub. Fire-and-forget; no correlation ids, no replies. */
export interface EventBus {
  emit<K extends EventName>(name: K, payload: EventMap[K]): void;
  on<K extends EventName>(name: K, handler: Handler<K>): () => void;
}

export function createEventBus(): EventBus {
  const handlers = new Map<EventName, Set<(payload: unknown) => void>>();

  return {
    emit(name, payload) {
      handlers.get(name)?.forEach((h) => h(payload));
    },
    on(name, handler) {
      let set = handlers.get(name);
      if (!set) {
        set = new Set();
        handlers.set(name, set);
      }
      const erased = handler as (payload: unknown) => void;
      set.add(erased);
      return () => {
        set!.delete(erased);
      };
    },
  };
}
