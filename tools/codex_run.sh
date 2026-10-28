#!/usr/bin/env bash
# 调用 Codex（ChatGPT 桌面版自带 CLI），固定 gpt-6.1-sol + ultra，不加载插件和 MCP。
# 遇到"模型满载"就退避等待（1、2、4、8 分钟），然后续跑同一会话，不从头重来。
#
# 用法：tools/codex_run.sh <请求文件> <最终答复文件> <日志文件> [沙箱] [额外 codex 参数...]
#   沙箱：read-only（默认）| workspace-write
#   续跑已中断的会话：RESUME_SID=<session id> tools/codex_run.sh ...
set -u
CX="/Applications/ChatGPT.app/Contents/Resources/codex-cli/bin/codex"
req="$1"; out="$2"; log="$3"; sandbox="${4:-read-only}"
shift $(( $# < 4 ? $# : 4 ))
extra=("$@")

cd "$(git rev-parse --show-toplevel)" || exit 1
touch "$log"
common=(-m gpt-6.1-sol -c 'model_reasoning_effort="ultra"' -c "sandbox_mode=\"$sandbox\""
        -c features.plugins=false -c features.apps=false -c 'mcp_servers={}'
        --skip-git-repo-check -o "$out")
continue_msg="${CONTINUE_MSG:-上次因模型满载中断。请从中断处继续完成原任务，不要重复已完成的步骤。}"

attempt() {  # $1 = 会话 id，空则新开会话
  if [ -z "$1" ]; then
    "$CX" exec "${common[@]}" "${extra[@]}" - < "$req" >> "$log" 2>&1
  else
    "$CX" exec resume "$1" "${common[@]}" "${extra[@]}" "$continue_msg" >> "$log" 2>&1
  fi
}

sid="${RESUME_SID:-}"
for wait in 0 60 120 240 480; do
  [ "$wait" -gt 0 ] && { echo "[codex_run] 模型满载，${wait} 秒后续跑会话 ${sid}" >> "$log"; sleep "$wait"; }
  before=$(wc -c < "$log" 2>/dev/null || echo 0)
  attempt "$sid"; code=$?
  new=$(tail -c +"$((before + 1))" "$log")
  [ -z "$sid" ] && sid=$(printf '%s\n' "$new" | grep -m1 '^session id:' | awk '{print $3}')
  if printf '%s\n' "$new" | grep -q 'Selected model is at capacity'; then
    [ -n "$sid" ] && continue
    echo "[codex_run] 满载且没拿到会话 id，停止" >> "$log"; exit 2
  fi
  echo "[codex_run] 结束，exit=${code}，session=${sid}" >> "$log"
  exit "$code"
done
echo "[codex_run] 连续满载，已重试 4 次，停止。session=${sid}" >> "$log"
exit 3
