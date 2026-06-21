import { useEffect, useRef, useState } from "react";
import { marked } from "marked";
import DOMPurify from "dompurify";
import Prism from "prismjs";
import "prismjs/components/prism-yaml";
import "prismjs/components/prism-python";
import "prismjs/themes/prism.css";
import type { IDockviewPanelProps } from "dockview";
import { useServices } from "../services";

interface DocState {
  loading: boolean;
  error?: string;
  html?: string;
  text?: string;
}

export function DocumentPanel(props: IDockviewPanelProps) {
  const { dataSource } = useServices();
  const documentId = (props.params as { documentId?: string } | undefined)?.documentId;
  const [state, setState] = useState<DocState>({ loading: Boolean(documentId) });
  const htmlRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    if (!documentId) {
      setState({ loading: false });
      return;
    }
    let cancelled = false;
    setState({ loading: true });
    dataSource
      .getDocument(documentId)
      .then((doc) => {
        if (cancelled) return;
        if (doc.contentType === "markdown") {
          const rendered = marked.parse(doc.text) as string;
          const html = DOMPurify.sanitize(rendered); // sanitize authored content
          setState({ loading: false, html });
        } else {
          setState({ loading: false, text: doc.text });
        }
      })
      .catch((e: unknown) => {
        if (!cancelled) setState({ loading: false, error: e instanceof Error ? e.message : String(e) });
      });
    return () => {
      cancelled = true;
    };
  }, [documentId, dataSource]);

  // After sanitized HTML is in the DOM: render mermaid blocks (lazy), then highlight code.
  useEffect(() => {
    const root = htmlRef.current;
    if (!state.html || !root) return;

    const mermaidBlocks = root.querySelectorAll<HTMLElement>("code.language-mermaid");
    if (mermaidBlocks.length > 0) {
      import("mermaid").then(({ default: mermaid }) => {
        mermaid.initialize({ startOnLoad: false, theme: "default" });
        mermaidBlocks.forEach(async (code, i) => {
          const source = code.textContent ?? "";
          try {
            const { svg } = await mermaid.render(`mmd-${documentId}-${i}`, source);
            const holder = document.createElement("div");
            holder.innerHTML = svg;
            (code.closest("pre") ?? code).replaceWith(holder);
          } catch {
            /* leave the fenced source as-is on render error */
          }
        });
      });
    }

    Prism.highlightAllUnder(root);
  }, [state.html, documentId]);

  let body: React.ReactNode;
  if (!documentId) body = <Message muted>Select a node to open its document.</Message>;
  else if (state.loading) body = <Message muted>Loading…</Message>;
  else if (state.error) body = <Message error>Failed to load {documentId}: {state.error}</Message>;
  else if (state.html)
    body = (
      <div
        ref={htmlRef}
        className="doc-html overflow-auto p-4 text-sm leading-relaxed"
        dangerouslySetInnerHTML={{ __html: state.html }}
      />
    );
  else body = <pre className="overflow-auto p-4 text-xs">{state.text}</pre>;

  return <div className="h-full w-full overflow-auto bg-white text-slate-800">{body}</div>;
}

function Message({ children, muted, error }: { children: React.ReactNode; muted?: boolean; error?: boolean }) {
  const tone = error ? "text-red-600" : muted ? "text-slate-400" : "text-slate-700";
  return <div className={`p-4 text-sm ${tone}`}>{children}</div>;
}
