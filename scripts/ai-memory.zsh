# Source this file to finalize Codex sessions and expose a manual fallback.

_ai_memory_finalize() {
  if command ai-memory finalize-session; then
    return 0
  else
    local finalization_status=$?
  fi

  print -u2 -- 'ai-memory: finalize-session failed; run handoff manually.'
  return "$finalization_status"
}

_ai_memory_should_finalize() {
  case "${1-}" in
    --help|-h|--version|-V|help|version|completion|exec|login|logout|mcp)
      return 1
      ;;
    *)
      return 0
      ;;
  esac
}

codex() {
  local codex_status

  if command codex "$@"; then
    codex_status=0
  else
    codex_status=$?
  fi

  if _ai_memory_should_finalize "$@"; then
    _ai_memory_finalize || true
  fi
  return "$codex_status"
}

handoff() {
  _ai_memory_finalize
}
