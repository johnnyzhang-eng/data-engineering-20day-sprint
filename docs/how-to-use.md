# 怎样用这些材料自学

English summary: Use Python 3 to build the synthetic SQLite database, then work through the available daily exercises and lessons. VS Code and a SQLite extension are optional. Most materials are in Chinese.

Reference solutions, hidden Python test cases, and assessment quizzes are private and excluded from the public repository. Both checkers exit with a missing answer or test cases message in a public checkout. Use the published expected results and your own test cases for manual checks.

[返回 README](../README.md) · [学习任务清单](syllabus.md) · [每天怎样学、练、测、记](learning-path.md)

## 先了解公开版本的边界

这是一个零基础学习者的 20 天面试准备记录，练习材料随学习进度补充，并不表示 20 天的材料已经全部发布。题目、讲义和真实作答可以复用；已有的 `answers.sql`、`answers.py` 和每日记录可能包含错误或求助后的修改，不能当作标准答案。

标准答案在 `private/answer-keys/`，小测在 `private/quizzes/`；整个 `private/` 已被根目录 `.gitignore` 排除，公开下载或克隆不会得到它们。Python 的隐藏用例也在私有答案文件中，公开仓库没有这些用例。

因此，**建库和运行自己的程序可用，但公开版本不能直接使用两个脚本自动判题或做材料自检**。缺少答案不表示你做错，也不是建库失败；重新建库不会生成答案。下面保留脚本的准确用法，便于理解现有材料中的命令，并明确哪些输出只在具备相应答案文件时才会出现。

## 环境与建库

先将仓库下载或克隆到自己的电脑，打开终端并进入仓库根目录，也就是同时包含 `README.md`、`tools/` 和 `exercises/` 的目录。下文命令都从这里运行。

- 必需：Python 3，带标准库 `sqlite3`。初始 SQL 练习和 Python 第 1 课不需要安装第三方包；后续课程如有依赖，以该课说明为准。
- 可选：VS Code 和能打开 SQLite 数据库、执行查询的扩展，例如现有题面使用的 SQLite3 Editor。也可以用其他 SQLite 客户端，或下面的 Python 标准库方式运行 SQL。
- Python 检查器用 `signal.SIGALRM` 限时，适用于 macOS/Linux。Windows 原生环境若需使用该检查器，可在 WSL 中运行；这不会解决公开版本缺少用例的问题。

确认解释器和 SQLite 运行库，再建库：

```sh
python3 --version
python3 -c "import sqlite3; print(sqlite3.sqlite_version)"
python3 exercises/sql/data/build_db.py
```

如果系统命令名是 `python`，先确认它对应 Python 3，再替换下文的 `python3`。SQL 进阶用到窗口函数，需要 SQLite 3.25.0 或以上；扩展和 Python 可能使用不同版本的 SQLite。

数据库生成在 `exercises/sql/data/practice.sqlite3`。建库命令会先生成并校验新数据库，成功后替换已有练习库，所以自己的数据不要存到这个库里。成功输出包括 `Database:`、各表行数、`Window functions: PASS` 和完整性检查 `PASS`；这些只证明练习库通过校验，不证明作答正确。

## 按天做题

先用[任务清单](syllabus.md)了解全貌，再按当前已有的 [`docs/days/`](days/) 选择当天练习；具体当天的材料和安排见该日说明。课程日不等于日历日期，Python 的 `p01` 是课号，也不等于 SQL 的 `d01`。当天说明引用了尚未公开的材料或私有文件时，先做现有公开练习；私人项目事实卡和原定小测不是使用公开练习的前置条件。

| 位置 | 怎么用 |
|---|---|
| [`exercises/sql/data/`](../exercises/sql/data/) | 建库脚本和共用 SQLite 练习库 |
| [`exercises/sql/d01/problems.md`](../exercises/sql/d01/problems.md) 及后续 `dNN/` | 题面、示范、数据约定和预期结果；按题号练习 |
| [`exercises/sql/d01/data-reference.md`](../exercises/sql/d01/data-reference.md) | 小表数据和字段含义，供预测、手算和查表 |
| [`exercises/python/p01/`](../exercises/python/p01/) 及已有的 `pNN/` | `lesson.md` 是讲解和题目，`data.py` 是静态合成数据（如该课提供），`answers.py` 是函数作答文件 |
| [`docs/notes/`](notes/) | 概念讲义和延伸阅读 |
| [`daily/`](../daily/) | 仓库所有者的真实首稿、错误和复测记录，适合做完后参考 |

每题先预测输出和边界，再自己写、保存、运行，最后核对结果并讲清为什么。保留错误首稿，另存修改后的版本；自己的学习记录写到自己的文件里，记录题号、首稿、最高求助级别、最终结果、错因和复测日期。可以在首次作答后的第 2 天、第 7 天换条件复测。

### SQL：写自己的文件并运行

可以另建 `my-d01.sql`，避免把已有作答误当作自己的答案。每题保留检查器识别的题头格式，例如：

```sql
-- 1.2｜自己的作答
-- 在下面写一条完整的 SQL，结尾加英文分号。
```

这里的 `｜` 是全角竖线，题号要与题面一致；每个题头下只放一条 SQL，注释不算作答。示例没有填写本题答案。

在 SQLite 客户端打开 `exercises/sql/data/practice.sqlite3`，将作答文件关联到这个数据库，每次选中一条完整语句（含分号）运行。读取查询返回的结果表格；保存文件或编辑器没有报错，都不代表查询已执行。按题面核对输出列名、行数、值，以及要求排序时的顺序。

没有 SQLite 扩展时，也可以只用 Python 运行文件中的单题 SQL。下面的命令要求 `my-d01.sql` 里只有一道题的一条查询，不能放整天的多条 SQL。多行命令适用于 macOS/Linux/WSL；Windows 原生 PowerShell/CMD 可将其中从 `from pathlib` 开始到最后一行 `print(row)` 为止的 Python 代码保存为 `.py` 文件，再从仓库根目录运行该文件：

```sh
python3 - <<'PY'
from pathlib import Path
import sqlite3

with sqlite3.connect("file:exercises/sql/data/practice.sqlite3?mode=ro", uri=True) as conn:
    cursor = conn.execute(Path("my-d01.sql").read_text(encoding="utf-8"))
    print([column[0] for column in cursor.description])
    for row in cursor:
        print(row)
PY
```

此命令显示你查询的列名和结果，**不自动判对错**。Python 输出的 `None` 对应 SQL 的 NULL；NULL 与金额 0 不同。题面未要求排序时，不按碰巧显示的行序判断对错。

### Python：写函数并核对返回值

先读对应 `lesson.md`，按函数名、参数和返回值要求独立作答。已有 `answers.py` 可能是空模板，也可能有仓库所有者的尝试；在自己的副本里保留原文件，再写自己的版本，保留题目要求的函数名和参数。

可以在自己的文件中调用函数、打印返回值，再给自己写 `assert` 检查。根据题面选择空输入、缺失值、零、重复值等适用边界，先算清预期再运行。仅运行 `python3 exercises/python/p01/answers.py` 可能没有任何输出：定义函数不会自动调用函数，没有报错也不代表通过测试。

## 两个自测脚本

### 公开版本会得到什么

以下命令可以显示帮助，不需要私有答案：

```sh
python3 tools/check.py --help
python3 tools/check_py.py --help
```

公开版本运行 `python3 tools/check.py d01` 会提示：

```text
没有 d01 的标准答案（private/answer-keys/d01*.sql）
```

运行 `python3 tools/check_py.py p01` 会提示：

```text
没有 p01 课的 Python 用例（private/answer-keys/py-p01.py）
```

这两种情况都以退出码 1 结束，在执行作答前就停止。公开题面中的预期结果仍可用于人工核对；Python 可以按上一节自行设计用例，但这不等于运行了原来的隐藏用例。小测和标准答案也不会由帮助命令或 `--self-test` 补齐。

### SQL：`tools/check.py`

下面的判题命令都需要对应的私有标准答案文件：

```sh
python3 tools/check.py d01 1.2 --file my-d01.sql
python3 tools/check.py d01 --file my-d01.sql
python3 tools/check.py d01
```

第一条检查指定题号；省略题号则检查答案库中当天的全部题目。天数可写 `d01` 或 `1`。`--file` 指定自己的一个作答文件；不写时会读取 `exercises/sql/d01/` 下全部 `.sql`，同题号的后读内容可能覆盖先读内容，因此另存作答时建议显式指定 `--file`。

| 输出 | 含义与下一步 |
|---|---|
| `通过` | 在当前数据和检查规则下与参考结果一致；仍需自己解释边界 |
| `还没作答` | 没有读到该题的 SQL；检查题号、题头和文件路径 |
| `语法：…` | 语句不能执行，可能是标点、语法或一题下有多条语句；超 10 秒也会停止 |
| `输出列不对` / `行数不对` | 检查列名、列顺序、过滤条件或连接粒度 |
| `行数对，但有…行的值不一样` | 行数相同但内容不符，检查表达式与 NULL 的处理 |
| `内容对，顺序不对` | 本题要求排序，检查 `ORDER BY` |
| `结果碰巧对了，但排序键比答案少…` | 检查题面中的并列规则和次排序键 |

脚本不展示标准 SQL 或预期结果值；通过但缺少结尾分号时会附提示。SQL 以只读方式连接练习库。

### Python：`tools/check_py.py`

下面的判题命令需要对应课的私有隐藏用例：

```sh
python3 tools/check_py.py p01 3
python3 tools/check_py.py p01
```

第一条检查第 1 课第 3 题，第二条检查这一课全部题目。课号可写 `p01` 或 `1`。脚本固定读取 `exercises/python/p01/answers.py`，**不支持 `--file`**；另存到其他位置的作答不会被它读取。

| 输出 | 含义与下一步 |
|---|---|
| `通过 N/N` | 当前函数通过这 N 个用例，不代表所有可能输入都已覆盖 |
| `没过 M/N 个用例` | 有 M 个失败；会显示用例说明、你的返回值或异常，不显示预期返回值 |
| `还没作答` / `还没有函数…` | 函数只有占位内容，或函数名不符；保留要求的签名并填写函数体 |
| `语法：…` / `文件一运行就报错：…` | 整个作答文件无法加载，先按提示行号修正 |
| `超过 5 秒没结束，检查循环` | 单次函数调用超时，检查循环和终止条件 |

检查器比较函数的返回值，会隐藏函数的 `print` 输出。要按题意 `return`，不能仅把结果打印出来。

### 退出码、检查日志与材料自检

正常判题时，全部题目通过返回 0；失败、未答或缺答案返回 1；命令参数格式错误通常返回 2。具备答案并进入判题流程后，非空作答的检查会在本地 `private/progress/checks.jsonl` 留底，相同作答和结果不重复记录。

```sh
python3 tools/check.py d01 --self-test
python3 tools/check_py.py p01 --self-test
```

`--self-test` 检查的是材料本身：SQL 参考查询与记录的预期结果是否一致，Python 参考实现是否通过用例以及作答文件是否有要求的函数。它**不是检查你的作答是否正确**，也需要私有答案；公开版本同样会提示缺少答案或用例。

## 记录求助级别与表现等级

两种等级分别回答“用了多少帮助”和“这次做到了什么”，不要互相替代。定义与[学习路径](learning-path.md)一致，每题记录用过的最高求助级别。

| 求助级别 | 含义 |
|---|---|
| L0 | 无帮助，自己作答和纠错 |
| L1 | 方向提示 |
| L2 | 关键步骤 |
| L3 | 完整示范 |

| 表现等级 | 本次表现 |
|---|---|
| P0 | 做不出或结果错 |
| P1 | 结果对 |
| P2 | 能讲清边界和为什么 |
| P3 | 能比较方案、迁移到新场景 |

只有 L0 下完成的题，才算独立的 P1–P3。照着示范写对记 L3；“脚本通过”只描述这次结果，不能替代解释和迁移表现，也不要直接写成“已掌握”。

## 为什么先写后看答案

看着别人的答案觉得熟悉，与合上资料后能自己写出，是两种不同的表现。先留下自己的预测和首稿，核对之后才知道具体错在哪里；隔几天换条件再做，才能观察是否还能独立完成。已有的公开作答也尽量放在自己尝试之后再看。

完全陌生的新概念可以先学示范，记 L3，之后换数据或条件独立做一道变式，再记录实际表现。自学时可以另找未见题做限时闭卷测试，但公开仓库不提供原定的私有小测，也不能把做过的题当作未见题。

方法的背景、适用条件和原始资料见[学习科学讲义](notes/m0-learning-science.md)，日常流程见[学习路径](learning-path.md)。

代码按 [MIT License](../LICENSE) 使用；讲义、题目、学习记录等文字按 [Creative Commons Attribution 4.0 International（CC BY 4.0）](../LICENSE-docs) 使用。
