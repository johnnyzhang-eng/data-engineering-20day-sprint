#!/usr/bin/env python3
"""Python 练习自测：用隐藏的测试用例调用本人写的函数，只说哪几个用例没过，不显示预期答案。只使用标准库。"""

import argparse
import ast
import contextlib
import copy
from datetime import datetime
import importlib.util
import io
import json
import math
from pathlib import Path
import re
import signal
import sys


ROOT = Path(__file__).resolve().parents[1]
KEYS = ROOT / "private/answer-keys"
LOG = ROOT / "private/progress/checks.jsonl"
TIME_LIMIT = 5


def lesson_name(value):
    """Python 按课号走（p01 = 第 1 课），不和课程日绑定。"""
    digits = re.sub(r"^[pP]", "", value)
    if not digits.isdigit():
        raise argparse.ArgumentTypeError("课号写成 p01 或 1")
    return f"p{int(digits):02d}"


def load(name, path):
    spec = importlib.util.spec_from_file_location(name, path)
    module = importlib.util.module_from_spec(spec)
    with contextlib.redirect_stdout(io.StringIO()):
        spec.loader.exec_module(module)
    return module


def unanswered(tree):
    """函数体只有 pass、...、文档字符串的，算还没作答。"""
    empty = set()
    for node in tree.body:
        if isinstance(node, ast.FunctionDef):
            if all(isinstance(stmt, ast.Pass) or
                   (isinstance(stmt, ast.Expr) and isinstance(stmt.value, ast.Constant))
                   for stmt in node.body):
                empty.add(node.name)
    return empty


def source_of(tree, text, name):
    for node in tree.body:
        if isinstance(node, ast.FunctionDef) and node.name == name:
            return ast.get_source_segment(text, node)
    return ""


def same(got, want):
    if type(want).__module__.startswith("pandas"):
        from pandas import testing
        assert_equal = testing.assert_frame_equal if hasattr(want, "columns") else testing.assert_series_equal
        try:
            assert_equal(got, want, check_dtype=False)
            return True
        except (AssertionError, TypeError):
            return False
    if isinstance(want, float) or (isinstance(got, float) and isinstance(want, int)):
        return isinstance(got, (int, float)) and not isinstance(got, bool) and math.isclose(got, want, rel_tol=1e-9, abs_tol=1e-9)
    if isinstance(want, (list, tuple)):
        return type(got) is type(want) and len(got) == len(want) and all(same(g, w) for g, w in zip(got, want))
    if isinstance(want, dict):
        return isinstance(got, dict) and got.keys() == want.keys() and all(same(got[k], want[k]) for k in want)
    return type(got) is type(want) and got == want


def call(func, args):
    def stop(*_):
        raise TimeoutError
    signal.signal(signal.SIGALRM, stop)
    signal.alarm(TIME_LIMIT)
    try:
        with contextlib.redirect_stdout(io.StringIO()):
            return func(*copy.deepcopy(args))
    finally:
        signal.alarm(0)


def short(value):
    text = " ".join(repr(value).split())
    return text if len(text) <= 80 else text[:77] + "..."


def where(error, path):
    """报错发生在本人文件的第几行。"""
    line = None
    trace = error.__traceback__
    while trace:
        if Path(trace.tb_frame.f_code.co_filename) == path:
            line = trace.tb_lineno
        trace = trace.tb_next
    return f"（{path.name} 第 {line} 行）" if line else ""


def run_cases(func, cases, path):
    """返回 (结果代码, 一句话)。用例的说明会显示，预期值不显示。"""
    failed = []
    for label, args, want in cases:
        try:
            got = call(func, args)
        except TimeoutError:
            failed.append(f"{label}：超过 {TIME_LIMIT} 秒没结束，检查循环")
            continue
        except Exception as error:
            failed.append(f"{label}：报错 {type(error).__name__}: {error}{where(error, path)}")
            continue
        if not same(got, want):
            failed.append(f"{label}：你返回 {short(got)}")
    if not failed:
        return "pass", f"通过 {len(cases)}/{len(cases)}"
    head = f"没过 {len(failed)}/{len(cases)} 个用例"
    return "fail", head + "\n    " + "\n    ".join(failed)


def log(day, item, code, source):
    last = None
    if LOG.exists():
        for line in LOG.read_text(encoding="utf-8").splitlines():
            record = json.loads(line)
            if record["day"] == day and record["item"] == item:
                last = record
    if last and last["result"] == code and last.get("code") == source:
        return
    LOG.parent.mkdir(parents=True, exist_ok=True)
    record = {"time": datetime.now().isoformat(timespec="seconds"), "day": day,
              "item": item, "result": code, "code": source}
    with LOG.open("a", encoding="utf-8") as handle:
        handle.write(json.dumps(record, ensure_ascii=False) + "\n")


def self_test(key, answers_path):
    """材料自检：参考答案要通过全部用例；作答模板里每题的函数都要有。"""
    failed = 0
    stubs = set()
    if answers_path.exists():
        stubs = {node.name for node in ast.parse(answers_path.read_text(encoding="utf-8")).body
                 if isinstance(node, ast.FunctionDef)}
    for item, problem in key.PROBLEMS.items():
        code, message = run_cases(getattr(key, problem["func"]), problem["cases"], Path(key.__file__))
        if code != "pass":
            print(f"{item}\t参考答案没过：{message}")
            failed += 1
        if problem["func"] not in stubs:
            print(f"{item}\t作答模板里没有函数 {problem['func']}")
            failed += 1
    print(f"自检 {len(key.PROBLEMS)} 题，{'全部一致' if not failed else f'{failed} 处问题'}。")
    return failed == 0


def parser():
    result = argparse.ArgumentParser(
        description="自测 Python 作答。例：python3 tools/check_py.py p01 3；不写题号就检查这一课全部。",
        epilog="只告诉你哪几个用例没过、你的函数返回了什么，不显示预期答案。每次检查记在 private/progress/checks.jsonl。")
    result.add_argument("day", type=lesson_name, help="第几课，如 p01")
    result.add_argument("item", nargs="?", help="题号，如 3；省略则检查这一课全部")
    result.add_argument("--self-test", action="store_true", help="材料自检：参考答案是否通过全部用例")
    return result


def main():
    args = parser().parse_args()
    key_path = KEYS / f"py-{args.day}.py"
    if not key_path.exists():
        sys.exit(f"没有 {args.day} 课的 Python 用例（{key_path.relative_to(ROOT)}）")
    folder = ROOT / f"exercises/python/{args.day}"
    answers_path = folder / "answers.py"
    sys.path.insert(0, str(folder))  # 让作答和用例都能 from data import ...
    key = load("cases", key_path)
    if args.self_test:
        sys.exit(0 if self_test(key, answers_path) else 1)
    text = answers_path.read_text(encoding="utf-8")
    try:
        tree = ast.parse(text)
    except SyntaxError as error:
        sys.exit(f"语法：{error.msg}（{answers_path.name} 第 {error.lineno} 行）。整个文件都运行不了，先改这一处")
    try:
        answers = load("answers", answers_path)
    except Exception as error:
        sys.exit(f"文件一运行就报错：{type(error).__name__}: {error}{where(error, answers_path)}")
    if args.item:
        if args.item not in key.PROBLEMS:
            sys.exit(f"{args.day} 没有第 {args.item} 题的用例")
        items = [args.item]
    else:
        items = list(key.PROBLEMS)
    empty = unanswered(tree)
    all_pass = True
    for item in items:
        name = key.PROBLEMS[item]["func"]
        func = getattr(answers, name, None)
        if func is None:
            code, message = "empty", f"还没有函数 {name}"
        elif name in empty:
            code, message = "empty", "还没作答"
        else:
            code, message = run_cases(func, key.PROBLEMS[item]["cases"], answers_path)
            log(args.day, f"py-{item}", code, source_of(tree, text, name))
        all_pass = all_pass and code == "pass"
        print(f"{item} {name}\t{message}")
    sys.exit(0 if all_pass else 1)


if __name__ == "__main__":
    main()
