import type { GraphModel } from "@archspec/model";

export interface DocumentContent {
  id: string;
  contentType: string;
  text: string;
}

/**
 * Reading data is a *pull* operation, kept off the event bus. `view` mode reads
 * embedded data; `serve` mode reads the live read-only API. Panels depend only on
 * this interface, so they stay mode-agnostic.
 */
export interface DataSource {
  getModel(): Promise<GraphModel>;
  getDocument(id: string): Promise<DocumentContent>;
}

export interface EmbeddedData {
  model: GraphModel;
  documents: Record<string, DocumentContent>;
}

/** `sda graph view` — model + documents embedded in the static export. */
export function createEmbeddedDataSource(embedded: EmbeddedData): DataSource {
  return {
    async getModel() {
      return embedded.model;
    },
    async getDocument(id) {
      const doc = embedded.documents[id];
      if (!doc) throw new Error(`Document not found: ${id}`);
      return doc;
    },
  };
}

/** `sda graph serve` — read-only local API. No write endpoints. */
export function createHttpDataSource(baseUrl = ""): DataSource {
  return {
    async getModel() {
      const res = await fetch(`${baseUrl}/model`);
      if (!res.ok) throw new Error(`Failed to load model (${res.status})`);
      return res.json() as Promise<GraphModel>;
    },
    async getDocument(id) {
      const res = await fetch(`${baseUrl}/doc/${encodeURIComponent(id)}`);
      if (!res.ok) throw new Error(`Failed to load document ${id} (${res.status})`);
      return res.json() as Promise<DocumentContent>;
    },
  };
}
