# data-engineering-20day-sprint

[English](#english) · [中文](#中文)

## English

A public record of a beginner preparing for data engineering internship interviews in 20 days, plus the practice materials used along the way. Most lessons and exercises are in Chinese, and materials are added as the learning progresses.

What is here:

- SQL exercises on a synthetic database, each small-table exercise with its full expected result.
- Python exercises (`exercises/python/`), one function per problem.
- Lecture notes (`docs/notes/`) and daily records of the learner's actual attempts, including mistakes and how much help was used.
- Two self-check scripts, `tools/check.py` (SQL) and `tools/check_py.py` (Python). They compare against reference answers and hidden test cases that are kept private, so in a public checkout they report that the answers are missing.

To try the SQL exercises, run from the repository root with Python 3:

```sh
python3 exercises/sql/data/build_db.py   # builds exercises/sql/data/practice.sqlite3
```

Then open `exercises/sql/d01/problems.md`, write your queries, run them against `practice.sqlite3` with any SQLite client, and compare with the expected result tables. The [usage guide](docs/how-to-use.md) covers setup, the exercise format and the help levels used in the records.

All data is synthetic. No company code or company data is included.

Code (`tools/`, and `.py` / `.sql` files under `exercises/`) is under the [MIT License](LICENSE); written materials (lecture notes, exercise statements, learning records) are under [CC BY 4.0](LICENSE-docs).

## 中文

用 20 天，把数据工程实习面试需要的基础，从"讲不出、写不出"补到"能亲手写出来、能讲清为什么"。

**状态**：第 1 天于 2026-11-05 开始。按学习日计，一个学习日可能跨几个日历日，进度见 `daily/`。

**从这里看起**：[学习任务清单](docs/syllabus.md)。20 天要学的全部内容都在里面，每一项配一个"原理"问题，独立做对才打勾。

### 原则

- 记录真实作答，包括错误、求助程度和复测结果。
- 只用公开资料或合成数据，不包含任何公司内部代码或数据。
- 用模拟面试衡量进步，而不是用学了多少内容。

### 目录

| 位置 | 内容 |
|---|---|
| [`docs/syllabus.md`](docs/syllabus.md) | 学习任务清单（13 个模块） |
| [`docs/learning-path.md`](docs/learning-path.md) | 每天怎样学、练、测、记 |
| [`docs/how-to-use.md`](docs/how-to-use.md) | 别人怎样用这些材料自学 |
| `docs/days/` | 每天的目标与练习范围 |
| `daily/` | 每日记录 |
| `exercises/` | 练习题与作答 |
| `interviews/` | 模拟面试 |
| [`research/`](research/) | 公开 JD 与面经统计 |
| `tools/` | 工具脚本 |
