import { createContext, useContext } from "react";
import type { EventBus } from "./bus/bus";
import type { WorkbenchStore } from "./store/store";
import type { DataSource } from "./data/source";
import type { Capability, PanelRegistry } from "./panels/registry";

/** Shared singletons made available to panels via context. */
export interface Services {
  bus: EventBus;
  store: WorkbenchStore;
  dataSource: DataSource;
  registry: PanelRegistry;
  mode: Capability;
}

const ServicesContext = createContext<Services | null>(null);

export const ServicesProvider = ServicesContext.Provider;

export function useServices(): Services {
  const services = useContext(ServicesContext);
  if (!services) throw new Error("useServices must be used within a ServicesProvider");
  return services;
}
