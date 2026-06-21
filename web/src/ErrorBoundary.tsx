import { Component, type ReactNode } from "react";

interface Props {
  label?: string;
  children: ReactNode;
}
interface State {
  error: Error | null;
}

/** Contains a render error to one panel so a single failure can't crash the workbench. */
export class ErrorBoundary extends Component<Props, State> {
  state: State = { error: null };

  static getDerivedStateFromError(error: Error): State {
    return { error };
  }

  componentDidCatch(error: Error): void {
    console.error(`${this.props.label ?? "Panel"} render error:`, error);
  }

  render(): ReactNode {
    if (this.state.error) {
      return (
        <div className="p-4 text-sm text-red-600">
          {this.props.label ?? "This panel"} failed to render: {this.state.error.message}
        </div>
      );
    }
    return this.props.children;
  }
}
