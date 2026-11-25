#!/usr/bin/env bash
# run.sh <plugin dir> <plugin> <server> <workdir> <out.jsonl> <prompt>
P="$1"; PL="$2"; SV="$3"; W="$4"; OUT="$5"; PROMPT="$6"
pre="mcp__plugin_${PL}_${SV}__"
cd "$W" && claude -p "$PROMPT" \
  --plugin-dir "$P" \
  --setting-sources project \
  --permission-mode manual \
  --allowedTools "${pre}review_user_story" "${pre}parse_user_story" "${pre}explore_page" "${pre}check_locator" \
  --disallowedTools "${pre}write_test" "${pre}run_tests" "${pre}capture_baseline" "${pre}heal_locator" "${pre}save_login_state" Bash Write Edit \
  --max-budget-usd 1 \
  --output-format stream-json --verbose > "$OUT" 2> "$OUT.err"
echo "exit $?"
