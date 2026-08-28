export function assertSupportedBunVersion(version: string): void {
  if (!Bun.semver.satisfies(version, "1.4.x")) {
    throw new Error(`Bun 1.4.x is required for the structural test gate; found ${version}`);
  }
}

assertSupportedBunVersion(Bun.version);
