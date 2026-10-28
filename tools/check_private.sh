#!/usr/bin/env bash
# 提交前脱敏检查：拦截私人目录、个人联系方式、本机路径、密钥格式和 private/denylist.txt 中的词。
set -u
root="$(git rev-parse --show-toplevel)"
deny="$root/private/denylist.txt"
fail=0

files=$(git diff --cached --name-only --diff-filter=ACMR)
[ -z "$files" ] && exit 0

while IFS= read -r f; do
  case "$f" in
    private/*) echo "✗ ${f}：private/ 下的文件不能提交"; fail=1; continue ;;
  esac
  content="$(git show ":$f" 2>/dev/null)" || continue

  check() {  # $1 说明, $2 扩展正则
    hits=$(printf '%s\n' "$content" | grep -nE -- "$2" | head -3)
    if [ -n "$hits" ]; then
      echo "✗ ${f}：$1"; printf '%s\n' "$hits" | sed 's/^/    /'; fail=1
    fi
  }
  check "疑似手机号" '(^|[^0-9])1[3-9][0-9]{9}([^0-9]|$)'
  check "疑似邮箱" '[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}'
  check "本机绝对路径" '/Users/[A-Za-z0-9._-]+/'
  check "疑似密钥" '(sk-[A-Za-z0-9_-]{20,}|gh[pousr]_[A-Za-z0-9]{20,}|AKIA[0-9A-Z]{16}|-----BEGIN [A-Z ]*PRIVATE KEY-----)'

  if [ -f "$deny" ]; then
    while IFS= read -r term; do
      case "$term" in ''|\#*) continue ;; esac
      if printf '%s\n' "$content" | grep -qF -- "$term"; then
        echo "✗ ${f}：含私人词表中的词（见 private/denylist.txt）"; fail=1
      fi
    done < "$deny"
  fi
done <<< "$files"

if [ "$fail" -ne 0 ]; then
  echo "提交已拦截：请移除上述内容，或把文件移到 private/。"
  exit 1
fi
exit 0
