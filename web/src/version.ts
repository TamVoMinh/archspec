import { SCHEMA_VERSION, type GraphModel } from "@archspec/model";

/**
 * Returns a message if the model's schema version isn't supported by this viewer,
 * else null. Guards a frozen `view` export against a newer/older model.
 */
export function versionMismatch(model: GraphModel): string | null {
  if (model.schemaVersion !== SCHEMA_VERSION) {
    return `Unsupported model schema version ${model.schemaVersion} — this viewer supports ${SCHEMA_VERSION}. Rebuild the export with a matching sda-cli.`;
  }
  return null;
}
