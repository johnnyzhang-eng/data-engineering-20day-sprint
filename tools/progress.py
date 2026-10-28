#!/usr/bin/env python3
"""记录正式作答，按首次作答的 D+2 / D+7 节点列出复测。只使用标准库。"""

import argparse
from collections import Counter, defaultdict
from datetime import date, timedelta
import json
from pathlib import Path
import sys


DEFAULT_FILE = Path(__file__).resolve().parents[1] / "private/progress/attempts.jsonl"
FIELDS = {"date", "day", "module", "item", "help", "perf", "correct", "note"}
LEVELS = ("L0", "L1", "L2", "L3")
PERFS = ("P0", "P1", "P2", "P3")
MODULES = tuple(f"M{i}" for i in range(1, 14))


def iso_date(value):
    try:
        parsed = date.fromisoformat(value)
    except (TypeError, ValueError):
        raise argparse.ArgumentTypeError("日期须为有效的 YYYY-MM-DD") from None
    if parsed.isoformat() != value:
        raise argparse.ArgumentTypeError("日期须为有效的 YYYY-MM-DD")
    return parsed


def positive_int(value):
    try:
        number = int(value)
    except (TypeError, ValueError):
        raise argparse.ArgumentTypeError("学习日须为正整数") from None
    if number < 1:
        raise argparse.ArgumentTypeError("学习日须为正整数")
    return number


def boolean(value):
    if value == "true":
        return True
    if value == "false":
        return False
    raise argparse.ArgumentTypeError("correct 只接受 true 或 false")


def validate(record):
    if not isinstance(record, dict) or set(record) != FIELDS:
        raise ValueError("记录必须且只能包含 " + ", ".join(sorted(FIELDS)))
    try:
        iso_date(record["date"])
    except argparse.ArgumentTypeError as error:
        raise ValueError(str(error)) from error
    if type(record["day"]) is not int or record["day"] < 1:
        raise ValueError("day 须为正整数")
    if record["module"] not in MODULES:
        raise ValueError("module 须为 M1–M13")
    if record["help"] not in LEVELS or record["perf"] not in PERFS:
        raise ValueError("help 须为 L0–L3，perf 须为 P0–P3")
    if type(record["correct"]) is not bool:
        raise ValueError("correct 须为 JSON true/false")
    if not isinstance(record["item"], str) or not record["item"].strip():
        raise ValueError("item 须为非空字符串")
    if not isinstance(record["note"], str):
        raise ValueError("note 须为字符串")


def read_records(path):
    if not path.exists():
        return []
    records = []
    for line_number, line in enumerate(path.read_text(encoding="utf-8").splitlines(), 1):
        if not line.strip():
            continue
        try:
            record = json.loads(line)
            validate(record)
        except (ValueError, TypeError) as error:
            raise ValueError(f"{path}:{line_number}: {error}") from error
        records.append(record)
    return records


def independent_correct(record):
    return record["help"] == "L0" and record["correct"]


def add(args):
    record = {
        "date": args.date.isoformat(),
        "day": args.day,
        "module": args.module,
        "item": args.item,
        "help": args.help_level,
        "perf": args.perf,
        "correct": args.correct,
        "note": args.note,
    }
    validate(record)
    # 检查旧记录，避免在损坏的台账后继续追加。
    read_records(args.file)
    args.file.parent.mkdir(parents=True, exist_ok=True)
    needs_newline = args.file.exists() and args.file.stat().st_size > 0
    if needs_newline:
        with args.file.open("rb") as stream:
            stream.seek(-1, 2)
            needs_newline = stream.read(1) != b"\n"
    with args.file.open("a", encoding="utf-8") as stream:
        if needs_newline:
            stream.write("\n")
        stream.write(json.dumps(record, ensure_ascii=False) + "\n")
    print(json.dumps(record, ensure_ascii=False))


def due(args):
    grouped = defaultdict(list)
    for index, record in enumerate(read_records(args.file)):
        if iso_date(record["date"]) <= args.date:
            grouped[(record["module"], record["item"])].append((record["date"], index, record))
    pending = []
    for (module, item), attempts in grouped.items():
        attempts.sort(key=lambda row: (row[0], row[1]))
        first = attempts[0][2]
        if independent_correct(first):
            continue
        first_date = iso_date(first["date"])
        slots = [first_date + timedelta(days=offset) for offset in (2, 7)]
        for _, _, record in attempts[1:]:
            if independent_correct(record):
                slots = []
                break
            # 每条正式复测最多完成一个到期节点；提前的失败作答不消耗节点。
            if slots and slots[0] <= iso_date(record["date"]):
                slots.pop(0)
        overdue = [slot for slot in slots if slot <= args.date]
        if overdue:
            pending.append((overdue[0], int(module[1:]), item, module, first_date, overdue))
    if not pending:
        print(f"截至 {args.date}：没有到期复测题。")
        return
    print("module\titem\tfirst_date\tdue_dates")
    for _, _, item, module, first_date, overdue in sorted(pending):
        # JSON 字符串保留题号里的换行/制表符，避免破坏列表格式。
        print(f"{module}\t{json.dumps(item, ensure_ascii=False)}\t{first_date}\t"
              + ",".join(slot.isoformat() for slot in overdue))


def summary(args):
    grouped = defaultdict(list)
    for record in read_records(args.file):
        if args.date is not None and record["date"] != args.date.isoformat():
            continue
        if args.day is not None and record["day"] != args.day:
            continue
        grouped[record["module"]].append(record)
    if not grouped:
        print("没有符合筛选条件的作答记录。")
        return
    print("module\tattempts\tcorrect\taccuracy\tL0\tL1\tL2\tL3\tP0\tP1\tP2\tP3\tindependent_P1_P3")
    all_records = []
    for module in sorted(grouped, key=lambda name: int(name[1:])):
        records = grouped[module]
        print_summary_row(module, records)
        all_records.extend(records)
    print_summary_row("TOTAL", all_records)
    print("P 分布包含全部作答；independent_P1_P3 仅计 L0 且正确的 P1–P3。正确率按作答次数计算。")


def print_summary_row(module, records):
    help_counts = Counter(record["help"] for record in records)
    perf_counts = Counter(record["perf"] for record in records)
    correct = sum(record["correct"] for record in records)
    independent = sum(independent_correct(record) and record["perf"] != "P0" for record in records)
    values = [module, len(records), correct, f"{correct / len(records):.1%}"]
    values.extend(help_counts[level] for level in LEVELS)
    values.extend(perf_counts[perf] for perf in PERFS)
    values.append(independent)
    print("\t".join(map(str, values)))


def parser():
    result = argparse.ArgumentParser(
        description="每日陪练作答台账：追加记录、列出复测、按模块统计。",
        epilog="示例：python3 tools/progress.py add --day 1 --module M1 --item d01:1.2 "
               "--help-level L0 --perf P1 --correct true --note '结果正确'",
    )
    result.add_argument("--file", type=Path, default=DEFAULT_FILE,
                        help="台账路径；默认仓库 private/progress/attempts.jsonl。可指定临时文件测试。")
    commands = result.add_subparsers(dest="command", required=True)
    add_parser = commands.add_parser("add", help="追加一次正式作答（含本次最高提示级别）")
    add_parser.add_argument("--date", type=iso_date, default=date.today(), help="作答日期 YYYY-MM-DD，默认今天")
    add_parser.add_argument("--day", type=positive_int, required=True, help="学习第几天，正整数")
    add_parser.add_argument("--module", choices=MODULES, required=True)
    add_parser.add_argument("--item", required=True, help="稳定题号；同题复测沿用相同 module 和 item")
    add_parser.add_argument("--help-level", choices=LEVELS, required=True,
                            help="本次最高求助级别；--help 留给命令帮助")
    add_parser.add_argument("--perf", choices=PERFS, required=True)
    add_parser.add_argument("--correct", type=boolean, required=True, metavar="{true,false}")
    add_parser.add_argument("--note", default="", help="错因、变式、口述等备注，默认空字符串")
    add_parser.set_defaults(action=add)

    due_parser = commands.add_parser(
        "due", help="列出截至指定日到期且未复测的题（含逾期）",
        description="以 (module,item) 识别题，按日期、同日按文件顺序确定首次作答。首次作答未同时"
                    "满足 L0 与正确的题，安排首次日期+2/+7 各一次。后续任何正式作答若 L0 且正确则停止复测。",
        epilog="每次正式作答只记一行，提示后修订合并记录最高 help；正式同日重测也会算后续作答。"
               "失败复测消耗最早一个已到期节点，提前失败不消耗；未做节点逾期保留。"
               "若两个节点均逾期，一次失败复测只消耗一个。未来记录不影响历史查询。",
    )
    due_parser.add_argument("--date", type=iso_date, default=date.today(), help="查询日 YYYY-MM-DD，默认今天")
    due_parser.set_defaults(action=due)

    summary_parser = commands.add_parser("summary", help="按模块统计求助/表现分布和正确率")
    summary_parser.add_argument("--date", type=iso_date, help="只统计这一日期；不指定则不限日期")
    summary_parser.add_argument("--day", type=positive_int, help="只统计这一学习日；与 --date 同时指定时取交集")
    summary_parser.set_defaults(action=summary)
    for command in (add_parser, due_parser, summary_parser):
        command.add_argument("--file", type=Path, default=argparse.SUPPRESS,
                             help="台账路径，也可放在子命令前；默认 private/progress/attempts.jsonl")
    return result


def main():
    command_parser = parser()
    args = command_parser.parse_args()
    try:
        args.action(args)
    except (OSError, UnicodeError, ValueError, OverflowError) as error:
        command_parser.exit(2, f"错误：{error}\n")


if __name__ == "__main__":
    main()
