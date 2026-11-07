#!/usr/bin/env python3
"""SQL 练习自测：运行本人作答，和标准答案的结果比较，只说通过与否、哪一类不对，不显示答案。只使用标准库。"""

import argparse
from collections import Counter
from datetime import datetime
import json
from pathlib import Path
import re
import sqlite3
import sys
import time


ROOT = Path(__file__).resolve().parents[1]
DB = ROOT / "exercises/sql/data/practice.sqlite3"
KEYS = ROOT / "private/answer-keys"
LOG = ROOT / "private/progress/checks.jsonl"
HEADER = re.compile(r"^--\s*(?:d\d{2}-)?(\d+\.\d+(?:-v\d+)?)\s*｜")
FULL_WIDTH = "；，（）‘’“”：。　"
TIME_LIMIT = 10


def day_name(value):
    digits = re.sub(r"^[dD]", "", value)
    if not digits.isdigit():
        raise argparse.ArgumentTypeError("天数写成 d02 或 2")
    return f"d{int(digits):02d}"


def item_order(item):
    base, _, variant = item.partition("-v")
    return tuple(int(part) for part in base.split(".")) + (int(variant or 0),)


def answer_blocks(paths):
    """按 `-- 4.3｜` 题头切开作答文件；题头下面的注释行不算作答。"""
    blocks = {}
    for path in paths:
        current = None
        for line in path.read_text(encoding="utf-8").splitlines():
            match = HEADER.match(line)
            if match:
                current = match.group(1)
                blocks[current] = []
            elif current and not line.lstrip().startswith("--"):
                blocks[current].append(line)
    return {item: "\n".join(lines).strip() for item, lines in blocks.items()}


def key_blocks(day):
    blocks = {}
    for path in sorted(KEYS.glob(f"{day}*.sql")):
        current = None
        for line in path.read_text(encoding="utf-8").splitlines():
            if line.startswith("-- BEGIN "):
                current = line[len("-- BEGIN "):].strip()
                blocks[current] = {"sql": [], "columns": None, "result": None}
            elif line.startswith("-- END "):
                current = None
            elif current is None:
                continue
            elif line.startswith("-- expected_columns:"):
                blocks[current]["columns"] = json.loads(line.split(":", 1)[1])
            elif line.startswith("-- expected_result:"):
                blocks[current]["result"] = json.loads(line.split(":", 1)[1])
            elif not line.lstrip().startswith("--"):
                blocks[current]["sql"].append(line)
    for block in blocks.values():
        block["sql"] = "\n".join(block["sql"]).strip()
    return blocks


def top_level(sql):
    """去掉引号内和括号内的文字，只留最外层，用来判断是否要求顺序。"""
    kept, depth, quoted = [], 0, False
    for char in sql:
        if char == "'":
            quoted = not quoted
        elif not quoted and char == "(":
            depth += 1
        elif not quoted and char == ")":
            depth -= 1
        kept.append(char if depth == 0 and not quoted else " ")
    return "".join(kept)


def ordered(sql):
    return re.search(r"\bORDER\s+BY\b", top_level(sql), re.IGNORECASE) is not None


def order_terms(sql):
    """最外层 ORDER BY 有几个排序键。数据里碰巧没有并列时，漏写次排序也能出对结果，靠它补查。"""
    match = re.search(r"\bORDER\s+BY\b(.*?)(?:\bLIMIT\b|;|$)", top_level(sql), re.IGNORECASE | re.DOTALL)
    return len(match.group(1).split(",")) if match else 0


def stray_symbol(sql):
    quoted = False
    for line in sql.splitlines():
        for index, char in enumerate(line):
            if char == "'":
                quoted = not quoted
            elif not quoted and line.startswith("--", index):
                break
            elif not quoted and char in FULL_WIDTH:
                return char, line.strip()
    return None


def connect():
    if not DB.exists():
        sys.exit(f"找不到 {DB.relative_to(ROOT)}，先在仓库根目录运行 python3 exercises/sql/data/build_db.py")
    conn = sqlite3.connect(f"file:{DB}?mode=ro", uri=True)
    return conn


def run(conn, sql):
    deadline = time.monotonic() + TIME_LIMIT
    conn.set_progress_handler(lambda: time.monotonic() > deadline, 10000)
    cursor = conn.execute(sql)
    columns = [column[0] for column in cursor.description] if cursor.description else []
    return columns, cursor.fetchall()


def normalize(row):
    return tuple(round(float(value), 6) if isinstance(value, (int, float)) else value for value in row)


def compare(columns, rows, want_columns, want_rows, keep_order):
    """返回 (结果代码, 给本人看的一句话)。不透露预期的值。"""
    if [c.lower() for c in columns] != [c.lower() for c in want_columns]:
        return "columns", f"输出列不对：你的是 {', '.join(columns)}；题目要的是 {', '.join(want_columns)}"
    got = [normalize(row) for row in rows]
    want = [normalize(row) for row in want_rows]
    if len(got) != len(want):
        more = "多了" if len(got) > len(want) else "少了"
        return "rows", f"行数不对：你的结果 {len(got)} 行，{more}"
    extra = Counter(got) - Counter(want)
    if extra:
        return "values", f"行数对，但有 {sum(extra.values())} 行的值不一样"
    if keep_order and got != want:
        return "order", "内容对，顺序不对"
    return "pass", "通过"


def check_one(conn, item, sql, key):
    if not sql:
        return "empty", "还没作答"
    symbol = stray_symbol(sql)
    if symbol:
        return "syntax", f"语法：有中文符号 {symbol[0]}，在这一行：{symbol[1]}"
    try:
        columns, rows = run(conn, sql)
    except sqlite3.OperationalError as error:
        if "interrupted" in str(error):
            return "syntax", f"运行超过 {TIME_LIMIT} 秒被停止，检查有没有漏掉连接条件"
        return "syntax", f"语法：{error}"
    except (sqlite3.ProgrammingError, sqlite3.Warning):
        return "syntax", "这一题下面有不止一条语句，只留一条"
    want_columns, want_rows = run(conn, key["sql"])
    keep_order = ordered(key["sql"])
    code, message = compare(columns, rows, want_columns, want_rows, keep_order)
    if code == "pass" and keep_order and order_terms(sql) < order_terms(key["sql"]):
        return "ties", "结果碰巧对了，但排序键比答案少：再看题目里\"相同时\"的并列规则"
    if code == "pass" and not sql.rstrip().endswith(";"):
        message += "（结尾没有分号）"
    return code, message


def log(day, item, code, sql):
    """每次检查留底，首稿和改了几次都能从这里查到；代码和结果都没变时不重复记。"""
    last = None
    if LOG.exists():
        for line in LOG.read_text(encoding="utf-8").splitlines():
            record = json.loads(line)
            if record["day"] == day and record["item"] == item:
                last = record
    if last and last["result"] == code and last["sql"] == sql:
        return
    LOG.parent.mkdir(parents=True, exist_ok=True)
    record = {"time": datetime.now().isoformat(timespec="seconds"), "day": day,
              "item": item, "result": code, "sql": sql}
    with LOG.open("a", encoding="utf-8") as handle:
        handle.write(json.dumps(record, ensure_ascii=False) + "\n")


def self_test(conn, keys):
    """材料自检：每条标准答案的运行结果要和它记下的 expected_result 一致。"""
    failed = 0
    for item in sorted(keys, key=item_order):
        key = keys[item]
        if key["result"] is None or key["columns"] is None:
            print(f"{item}\t缺 expected_result 或 expected_columns")
            failed += 1
            continue
        columns, rows = run(conn, key["sql"])
        code, message = compare(columns, rows, key["columns"], key["result"], ordered(key["sql"]))
        if code != "pass":
            print(f"{item}\t{message}")
            failed += 1
    print(f"自检 {len(keys)} 条，{len(keys) - failed} 条一致。")
    return failed == 0


def parser():
    result = argparse.ArgumentParser(
        description="自测 SQL 作答。例：python3 tools/check.py d02 4.3；不写题号就检查当天全部。",
        epilog="只告诉你通过与否和哪一类不对（列、行数、值、顺序、语法），不显示答案。"
               "每次检查记在 private/progress/checks.jsonl。")
    result.add_argument("day", type=day_name, help="第几天，如 d02")
    result.add_argument("item", nargs="?", help="题号，如 4.3、3.2-v1；省略则检查当天全部")
    result.add_argument("--file", type=Path, help="只读这个作答文件（默认读 exercises/sql/dNN/ 下全部 .sql）")
    result.add_argument("--self-test", action="store_true", help="材料自检：标准答案与 expected_result 是否一致")
    return result


def main():
    args = parser().parse_args()
    keys = key_blocks(args.day)
    if not keys:
        sys.exit(f"没有 {args.day} 的标准答案（private/answer-keys/{args.day}*.sql）")
    conn = connect()
    if args.self_test:
        sys.exit(0 if self_test(conn, keys) else 1)
    paths = [args.file] if args.file else sorted((ROOT / f"exercises/sql/{args.day}").glob("*.sql"))
    answers = answer_blocks(paths)
    if args.item:
        if args.item not in keys:
            sys.exit(f"{args.day} 没有 {args.item} 的标准答案，这题没法自测")
        items = [args.item]
    else:
        items = sorted(keys, key=item_order)
    all_pass = True
    for item in items:
        sql = answers.get(item, "")
        code, message = check_one(conn, item, sql, keys[item])
        if code != "empty":
            log(args.day, item, code, sql)
        all_pass = all_pass and code == "pass"
        print(f"{item}\t{message}")
    sys.exit(0 if all_pass else 1)


if __name__ == "__main__":
    main()
