# Source this file to finalize Codex sessions and expose a manual fallback.

_ai_memory_finalize() {
  if command ai-memory finalize-session; then
    return 0
  fi

  print -u2 -- 'ai-memory: finalize-session failed; run handoff manually.'
  return 1
}

codex() {
  local codex_status

  if command codex "$@"; then
    codex_status=0
  else
    codex_status=$?
  fi

  _ai_memory_finalize || true
  return "$codex_status"
}

handoff() {
  _ai_memory_finalize
}
