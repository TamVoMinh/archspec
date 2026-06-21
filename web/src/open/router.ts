import type { EventBus } from "../bus/bus";
import type { ContentType } from "../bus/events";
import type { Capability, PanelManifest, PanelRegistry } from "../panels/registry";

export interface OpenParams {
  documentId: string;
  contentType: ContentType;
}

/**
 * How the router materializes a panel. The implementation (in App) reuses an
 * existing panel for the manifest id when present (open-intent = reuse), else
 * creates one. `notifyNoHandler` surfaces a clear message when nothing is eligible.
 */
export interface Mounter {
  open(manifest: PanelManifest, params: OpenParams): void;
  notifyNoHandler(contentType: ContentType): void;
}

/**
 * Dispatches `document.open` to a panel that handles the content type in the
 * current mode. Picks the first eligible manifest deterministically; surfaces a
 * clear message when none is eligible. Returns an unsubscribe function.
 */
export function createOpenRouter(
  bus: EventBus,
  registry: PanelRegistry,
  mode: Capability,
  mounter: Mounter,
): () => void {
  return bus.on("document.open", ({ id, contentType }) => {
    const eligible = registry.resolve(contentType, mode);
    if (eligible.length === 0) {
      mounter.notifyNoHandler(contentType);
      return;
    }
    mounter.open(eligible[0], { documentId: id, contentType });
  });
}
