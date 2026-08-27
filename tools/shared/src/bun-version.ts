if (!Bun.semver.satisfies(Bun.version, "1.4.x")) {
  throw new Error(`Bun 1.4.x is required for the structural test gate; found ${Bun.version}`);
}
