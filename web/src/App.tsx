import { useEffect, useRef } from "react";
import { DockviewReact, type DockviewReadyEvent } from "dockview";
import { createEventBus } from "./bus/bus";
import { createStore } from "./store/store";
import { createEmbeddedDataSource, createHttpDataSource, type EmbeddedData } from "./data/source";
import { SAMPLE_DATA } from "./data/sample";
import { PanelRegistry, type Capability } from "./panels/registry";
import { createOpenRouter, type Mounter } from "./open/router";
import { GraphViewPanel } from "./panels/GraphViewPanel";
import { DocumentPanel } from "./panels/DocumentPanel";
import { ExplorerPanel } from "./panels/ExplorerPanel";
import { ServicesProvider, type Services } from "./services";

const components = {
  "graph-view": GraphViewPanel,
  document: DocumentPanel,
  explorer: ExplorerPanel,
};

function createServices(): Services {
  const bus = createEventBus();
  const store = createStore(bus);

  // Data source by context:
  //  - `sda graph view`  → model+docs embedded as window.__ARCHSPEC_DATA__ (offline)
  //  - dev (`pnpm dev`)  → bundled sample data
  //  - `sda graph serve` → read-only HTTP API
  const embedded = (window as unknown as { __ARCHSPEC_DATA__?: EmbeddedData }).__ARCHSPEC_DATA__;
  let mode: Capability;
  let dataSource;
  if (embedded) {
    mode = "view";
    dataSource = createEmbeddedDataSource(embedded);
  } else if (import.meta.env.DEV) {
    mode = "view";
    dataSource = createEmbeddedDataSource(SAMPLE_DATA);
  } else {
    mode = "serve";
    dataSource = createHttpDataSource("");
  }

  const registry = new PanelRegistry();
  registry.register({ id: "graph-view", title: "Graph", handles: ["graph"], capability: "view" });
  registry.register({
    id: "document",
    title: "Document",
    handles: ["markdown", "service-detail", "yaml"],
    capability: "view",
  });

  return { bus, store, dataSource, registry, mode };
}

export default function App() {
  const servicesRef = useRef<Services | null>(null);
  if (!servicesRef.current) servicesRef.current = createServices();
  const services = servicesRef.current;

  // Load the model (pull), then announce it on the bus.
  useEffect(() => {
    let cancelled = false;
    services.dataSource
      .getModel()
      .then((model) => {
        if (!cancelled) services.bus.emit("model.loaded", { model });
      })
      .catch((e) => console.error("Failed to load model", e));
    return () => {
      cancelled = true;
    };
  }, [services]);

  const onReady = (event: DockviewReadyEvent) => {
    const api = event.api;
    api.addPanel({ id: "graph-view", component: "graph-view", title: "Graph" });
    const explorer = api.addPanel({
      id: "explorer",
      component: "explorer",
      title: "Explorer",
      position: { referencePanel: "graph-view", direction: "left" },
    });
    // Lock the explorer rail to a fixed width so opening/closing a document doesn't
    // let dockview redistribute width into it (it's a sidebar, not a flex column).
    explorer.group.api.setConstraints({ minimumWidth: 280, maximumWidth: 280 });
    explorer.group.api.setSize({ width: 280 });

    const mounter: Mounter = {
      open(manifest, params) {
        const existing = api.getPanel(manifest.id);
        if (existing) {
          existing.api.updateParameters(params);
          existing.api.setActive();
        } else {
          api.addPanel({
            id: manifest.id,
            component: manifest.id,
            title: manifest.title,
            params,
            position: { referencePanel: "graph-view", direction: "right" },
          });
        }
      },
      notifyNoHandler(contentType) {
        console.warn(`No panel handles content type: ${contentType}`);
      },
    };
    createOpenRouter(services.bus, services.registry, services.mode, mounter);

    api.onDidAddPanel((p) => services.bus.emit("panel.mounted", { panelId: p.id }));
    api.onDidRemovePanel((p) => services.bus.emit("panel.disposed", { panelId: p.id }));
  };

  return (
    <ServicesProvider value={services}>
      <DockviewReact components={components} onReady={onReady} className="dockview-theme-light archspec-theme" />
    </ServicesProvider>
  );
}
