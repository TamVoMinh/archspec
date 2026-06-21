import type { ContentType } from "../bus/events";

export type Capability = "view" | "serve";

/** A panel plugin's declaration. The only contribution type in the viewer. */
export interface PanelManifest {
  id: string;
  title: string;
  icon?: string;
  handles: ContentType[];
  capability: Capability;
}

/** In-memory registry of panel manifests, consulted by the open router. */
export class PanelRegistry {
  private manifests = new Map<string, PanelManifest>();

  register(manifest: PanelManifest): void {
    this.manifests.set(manifest.id, manifest);
  }

  all(): PanelManifest[] {
    return [...this.manifests.values()];
  }

  /**
   * Panels eligible to render `contentType` in the current mode. A `view`-capable
   * panel works in both modes; a `serve`-only panel works only when mode is serve.
   * Result is sorted by id for deterministic dispatch.
   */
  resolve(contentType: ContentType, mode: Capability): PanelManifest[] {
    return this.all()
      .filter((m) => m.handles.includes(contentType))
      .filter((m) => m.capability === "view" || m.capability === mode)
      .sort((a, b) => a.id.localeCompare(b.id));
  }
}
