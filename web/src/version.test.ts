import { describe, it, expect } from "vitest";
import { SCHEMA_VERSION, type GraphModel } from "@archspec/model";
import { versionMismatch } from "./version";

describe("versionMismatch", () => {
  it("accepts a matching schema version", () => {
    const model: GraphModel = { schemaVersion: SCHEMA_VERSION, graph: {} };
    expect(versionMismatch(model)).toBeNull();
  });

  it("reports a mismatch for an unsupported version", () => {
    const model: GraphModel = { schemaVersion: SCHEMA_VERSION + 1, graph: {} };
    const msg = versionMismatch(model);
    expect(msg).toContain("Unsupported model schema version");
  });
});
