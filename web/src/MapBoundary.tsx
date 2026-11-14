import { Component, type ReactNode } from "react";

// Si el mapa falla por cualquier motivo, se muestra un aviso en su lugar y el resto de la página sigue funcionando.
export class MapBoundary extends Component<{ fallback: ReactNode; children: ReactNode }, { failed: boolean }> {
  state = { failed: false };
  static getDerivedStateFromError() {
    return { failed: true };
  }
  componentDidCatch(error: unknown) {
    console.error("[GOLIAT] el mapa falló; se muestra el resto de la página", error);
  }
  render() {
    return this.state.failed ? this.props.fallback : this.props.children;
  }
}
