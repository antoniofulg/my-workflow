# Layered adoption memory

- The adopter uses four fixed layers in catalog order; the manifest records schema 1 and no timestamps.
- `plan` and `status` are read-only; all apply writes are staged only after path, conflict, and packet preflight.
