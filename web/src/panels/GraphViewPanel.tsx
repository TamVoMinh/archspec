import { useEffect, useRef } from "react";
import cytoscape from "cytoscape";
import fcose from "cytoscape-fcose";
import type { IDockviewPanelProps } from "dockview";
import { useServices } from "../services";
import { toElements } from "../graph/elements";
import { nodeToContent } from "../graph/nodeContent";

let fcoseRegistered = false;
function ensureFcose() {
  if (!fcoseRegistered) {
    cytoscape.use(fcose);
    fcoseRegistered = true;
  }
}

// Persist computed node positions across rebuilds/remounts so the layout is
// stable — fcose runs once per node set, then positions are reused.
let cachedPositions: Record<string, { x: number; y: number }> | null = null;
let cachedSignature = "";

// Matches the design tokens in index.css (cytoscape renders to canvas, so the
// values must be literal, not CSS var() references).
const TYPE_COLORS: Record<string, string> = {
  problem: "#ea580c", // orange-600
  adr: "#4f46e5", // indigo-600 (accent)
  service: "#0d9488", // teal-600
  group: "#64748b", // slate-500
};
const ACCENT = "#4f46e5";
const EDGE = "#94a3b8"; // slate-400
const EDGE_STRONG = "#475569"; // slate-600
const LABEL = "#1e293b"; // slate-800

const STYLE: cytoscape.StylesheetStyle[] = [
  {
    selector: "node",
    style: {
      label: "data(label)", "font-size": 10, color: LABEL,
      "text-valign": "bottom", "text-halign": "center", "text-margin-y": 4,
      "font-weight": 500, width: 22, height: 22,
    },
  },
  { selector: "node[ntype='problem']", style: { "background-color": TYPE_COLORS.problem, shape: "round-rectangle" } },
  { selector: "node[ntype='adr']", style: { "background-color": TYPE_COLORS.adr, shape: "diamond" } },
  { selector: "node[ntype='service']", style: { "background-color": TYPE_COLORS.service, shape: "ellipse" } },
  { selector: "node[ntype='group']", style: { "background-color": TYPE_COLORS.group, shape: "hexagon" } },
  {
    selector: "node[kind='system']",
    style: {
      label: "data(label)", "font-size": 11, color: "#475569", "text-valign": "top", "text-halign": "center",
      "background-opacity": 0.05, "background-color": ACCENT, "border-width": 1, "border-color": "#c7d2fe", shape: "round-rectangle", padding: "14px",
    },
  },
  { selector: "node.selected", style: { "border-width": 3, "border-color": ACCENT, "border-opacity": 1 } },
  { selector: "edge", style: { width: 1.5, "line-color": EDGE, "target-arrow-color": EDGE, "target-arrow-shape": "triangle", "curve-style": "bezier", "arrow-scale": 0.8 } },
  { selector: "edge[kind='depends_on']", style: { "line-color": EDGE_STRONG, "target-arrow-color": EDGE_STRONG, width: 2 } },
  { selector: "edge[kind='affects']", style: { "line-style": "dashed" } },
  { selector: "edge[kind='addresses']", style: { "line-style": "dotted" } },
  { selector: "edge[kind='contains']", style: { "line-color": "#cbd5e1", "target-arrow-shape": "none" } },
];

export function GraphViewPanel(_props: IDockviewPanelProps) {
  const { bus, store } = useServices();
  const containerRef = useRef<HTMLDivElement>(null);
  const emptyRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    ensureFcose();
    const container = containerRef.current;
    if (!container) return;
    let cy: cytoscape.Core | undefined;
    let ro: ResizeObserver | undefined;

    const render = () => {
      const model = store.getState().model;
      cy?.destroy();
      cy = undefined;
      ro?.disconnect();
      const empty = !model || Object.keys(model.graph).length === 0;
      if (emptyRef.current) emptyRef.current.style.display = empty ? "flex" : "none";
      if (!model || empty) return;

      const elements = toElements(model);
      const signature = elements
        .filter((e) => !("source" in e.data))
        .map((e) => String(e.data.id))
        .sort()
        .join(",");
      // Reuse cached positions when the node set is unchanged, so a rebuild
      // (e.g. the dock splitting when a document opens) restores the SAME layout
      // instead of re-running fcose and jumping around.
      const usePreset = signature === cachedSignature && cachedPositions !== null;
      if (usePreset) {
        for (const el of elements) {
          if (!("source" in el.data)) {
            const p = cachedPositions![String(el.data.id)];
            if (p) (el as cytoscape.ElementDefinition).position = { ...p };
          }
        }
      }

      cy = cytoscape({
        container,
        elements: elements as cytoscape.ElementDefinition[],
        style: STYLE,
        minZoom: 0.2,
        maxZoom: 1.8, // cap fit() so a few nodes don't blow up, but still fill the space
      });
      cy.on("tap", "node", (e) => {
        const id = e.target.id();
        const node = model.graph[id];
        if (!node) return; // a system compound parent, not a real node
        bus.emit("selection.changed", { nodeId: id });
        const mapping = nodeToContent(node);
        if (mapping) bus.emit("document.open", { id, contentType: mapping.contentType });
      });

      // The dock panel may have zero size on mount; lay out once it is sized,
      // then just resize/fit on subsequent changes.
      let laidOut = false;
      const onSized = () => {
        if (!cy) return;
        const { width, height } = container.getBoundingClientRect();
        if (width === 0 || height === 0) return;
        cy.resize();
        if (!laidOut) {
          laidOut = true;
          if (usePreset) {
            cy.layout({ name: "preset" } as cytoscape.LayoutOptions).run();
          } else {
            const layout = cy.layout({ name: "fcose", animate: false, padding: 24 } as cytoscape.LayoutOptions);
            layout.on("layoutstop", () => {
              if (!cy) return;
              const positions: Record<string, { x: number; y: number }> = {};
              cy.nodes().forEach((n) => {
                positions[n.id()] = { ...n.position() };
              });
              cachedPositions = positions;
              cachedSignature = signature;
            });
            layout.run();
          }
        }
        cy.fit(undefined, 24);
        applySelection();
      };
      ro = new ResizeObserver(onSized);
      ro.observe(container);
      onSized();
    };

    const applySelection = () => {
      if (!cy) return;
      const selected = store.getState().selection;
      cy.nodes().removeClass("selected");
      if (selected) cy.getElementById(selected).addClass("selected");
    };

    // Only rebuild + re-layout when the MODEL changes. A selection change just
    // re-highlights — clicking a search result must not re-lay-out the graph.
    let lastModel = store.getState().model;
    render();
    const unsub = store.subscribe(() => {
      const model = store.getState().model;
      if (model !== lastModel) {
        lastModel = model;
        render();
      } else {
        applySelection();
      }
    });
    return () => {
      unsub();
      ro?.disconnect();
      cy?.destroy();
    };
  }, [bus, store]);

  return (
    <div style={{ position: "relative", width: "100%", height: "100%", background: "#fff" }}>
      {/* Cytoscape forces position:relative on its container, so size it explicitly. */}
      <div ref={containerRef} style={{ width: "100%", height: "100%" }} />
      <div
        ref={emptyRef}
        className="absolute inset-0 hidden items-center justify-center p-6 text-center text-sm text-slate-400"
      >
        No architecture yet — run <code className="mx-1">sda capture</code> and{" "}
        <code className="mx-1">sda build</code> to populate the graph.
      </div>
    </div>
  );
}
