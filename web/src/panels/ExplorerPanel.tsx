import { useEffect, useMemo, useRef, useState, useSyncExternalStore } from "react";
import { Tree, type NodeRendererProps } from "react-arborist";
import { ChevronDown, ChevronRight } from "lucide-react";
import type { IDockviewPanelProps } from "dockview";
import { useServices } from "../services";
import { buildTree, labelDimensions, type GroupBy, type TreeNode } from "../explorer/tree";
import { nodeToContent } from "../graph/nodeContent";

const TYPE_DOT: Record<string, string> = {
  problem: "#ea580c",
  adr: "#4f46e5",
  service: "#0d9488",
};

const STRUCTURAL_GROUPINGS: { value: GroupBy; label: string }[] = [
  { value: "type", label: "Type" },
  { value: "system", label: "System" },
  { value: "group", label: "Service group" },
];

const titleCase = (s: string) => s.charAt(0).toUpperCase() + s.slice(1);

export function ExplorerPanel(_props: IDockviewPanelProps) {
  const { bus, store } = useServices();
  const model = useSyncExternalStore(store.subscribe, () => store.getState().model);
  const selection = useSyncExternalStore(store.subscribe, () => store.getState().selection);
  // "type" is the universal default (Problems/ADRs/Services reads well for flat and
  // partitioned projects alike); switch to "system" for a partition-first view.
  const [groupBy, setGroupBy] = useState<GroupBy>("type");
  const [filter, setFilter] = useState("");

  const data = useMemo(() => (model ? buildTree(model, groupBy) : []), [model, groupBy]);
  const empty = !model || Object.keys(model.graph).length === 0;

  // Group-by options: structural + any classification dimensions present in the model.
  const groupings = useMemo(() => {
    const dims = model ? labelDimensions(model) : [];
    return [
      ...STRUCTURAL_GROUPINGS,
      ...dims.map((d) => ({ value: `label:${d}` as GroupBy, label: titleCase(d) })),
    ];
  }, [model]);

  // react-arborist needs explicit pixel dimensions; track the tree area's size.
  const areaRef = useRef<HTMLDivElement>(null);
  const [size, setSize] = useState({ width: 0, height: 0 });
  useEffect(() => {
    const el = areaRef.current;
    if (!el) return;
    const ro = new ResizeObserver(() => setSize({ width: el.clientWidth, height: el.clientHeight }));
    ro.observe(el);
    return () => ro.disconnect();
  }, []);

  const openLeaf = (n: TreeNode) => {
    if (n.kind !== "artifact" || !n.artifactId || !model) return;
    const node = model.graph[n.artifactId];
    if (!node) return;
    bus.emit("selection.changed", { nodeId: n.artifactId });
    const mapping = nodeToContent(node);
    if (mapping) bus.emit("document.open", { id: n.artifactId, contentType: mapping.contentType });
  };

  function Row({ node, style }: NodeRendererProps<TreeNode>) {
    const d = node.data;
    const isFolder = d.kind === "folder";
    return (
      <div
        style={style}
        className={`flex h-7 items-center gap-1.5 pr-2 text-sm cursor-pointer ${
          node.isSelected ? "bg-indigo-50 text-slate-900" : "text-slate-700 hover:bg-slate-100"
        }`}
        onClick={() => (isFolder ? node.toggle() : openLeaf(d))}
      >
        {isFolder ? (
          node.isOpen ? <ChevronDown size={14} className="text-slate-400" /> : <ChevronRight size={14} className="text-slate-400" />
        ) : (
          <span className="ml-0.5 inline-block h-2 w-2 shrink-0 rounded-full" style={{ background: TYPE_DOT[d.ntype ?? ""] ?? "#94a3b8" }} />
        )}
        <span className="truncate">{d.name}</span>
        {isFolder && <span className="ml-auto text-xs text-slate-400">{d.count}</span>}
      </div>
    );
  }

  return (
    <div className="flex h-full w-full flex-col bg-white text-slate-800">
      <div className="flex items-center gap-2 border-b border-slate-200 px-2 py-1.5">
        <select
          value={groupBy}
          onChange={(e) => {
            setFilter("");
            setGroupBy(e.target.value as GroupBy);
          }}
          className="rounded border border-slate-200 bg-white px-1.5 py-1 text-xs text-slate-600 outline-none"
          title="Group by"
        >
          {groupings.map((g) => (
            <option key={g.value} value={g.value}>{g.label}</option>
          ))}
        </select>
        <input
          value={filter}
          onChange={(e) => setFilter(e.target.value)}
          placeholder="Filter…"
          className="w-full bg-transparent text-sm outline-none placeholder:text-slate-400"
        />
      </div>
      <div ref={areaRef} className="relative flex-1 overflow-hidden">
        {empty ? (
          <div className="p-4 text-sm text-slate-400">
            No architecture yet — run <code>sda capture</code> and <code>sda build</code>.
          </div>
        ) : (
          <Tree<TreeNode>
            data={data}
            openByDefault={false}
            width={size.width}
            height={size.height}
            rowHeight={28}
            indent={14}
            searchTerm={filter}
            selection={selection ? `leaf:${selection}` : undefined}
          >
            {Row}
          </Tree>
        )}
      </div>
    </div>
  );
}
