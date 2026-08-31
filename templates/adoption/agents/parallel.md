During Execute, dispatch independent slices with the coordinator-assisted protocol when the
frozen plan exposes safe parallel work. Keep each worker in its own checkout, deliver pointers
through the coordinator, and let the coordinator own integration, verification, recovery, and
cleanup.

When a gate declares a resource shared with another checkout, consult
`python3 tools/resource_lock.py run --help` and wrap only that gate with the adopted command.
