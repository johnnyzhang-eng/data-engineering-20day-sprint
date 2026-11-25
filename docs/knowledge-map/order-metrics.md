# 一笔订单怎样被算了两遍

## 从岗位到学习任务

[岗位样本](../../research/jd/jd-list.jsonl)中的数仓开发实习记录 `J4-01` 将 SQL 聚合、关联等列入技能要求，把指标计算和数据校验列入工作职责。下面的学习任务是从这些条款推导的：给定订单表和明细表，能说明一行代表什么，计算订单级金额，并用反例发现关联导致的重复计数。技能优先级仍需按目标职位核对。

**前置**：先会用 `SELECT`、`SUM` 和主键读一张表。用 [CS50 SQL 的 Relating](https://cs50.harvard.edu/sql/weeks/1/)理解表之间的关系，用 [D3](../days/d03.md)亲手练连接，再读 [Kimball 的四步设计法](https://www.kimballgroup.com/data-warehouse-business-intelligence-resources/kimball-techniques/dimensional-modeling-techniques/four-4-step-design-process/)和[仓库的粒度讲义](../notes/m3-02-fact-dim.md)理解为什么要先定粒度。

## 先预测，再执行

订单 1 金额 100，有两个商品。订单 2 金额 80，有一个商品。业务口径是每笔订单的金额只加一次，所以独立预期是 180。执行以下合成数据示例，可以用 SQLite 验证。

```sql
CREATE TABLE orders (order_id INTEGER PRIMARY KEY, amount INTEGER NOT NULL);
CREATE TABLE items (
    order_id INTEGER NOT NULL REFERENCES orders(order_id),
    product TEXT NOT NULL
);
INSERT INTO orders VALUES (1, 100), (2, 80);
INSERT INTO items VALUES (1, 'A'), (1, 'B'), (2, 'C');

-- 按订单粒度求和：180
SELECT SUM(amount) FROM orders;

-- 关联到了商品粒度：3 行，金额 280
SELECT COUNT(*) AS joined_rows, SUM(o.amount) AS amount_after_join
FROM orders AS o
JOIN items AS i ON i.order_id = o.order_id;
```

连接返回三行，第一笔订单的金额出现在两行。使用 [SQLite 的 SELECT 说明](https://www.sqlite.org/lang_select.html)核对连接对输入行的影响。实际必须使用商品表时，先问清是筛选符合条件的订单，还是计算商品指标。两种问题需要不同查询。

**独立验收**：在示例中加入订单 3（金额 80，有一条明细）和订单 4（金额 100，没有明细）。业务口径仍是每笔订单加一次。先写出订单级预期，再运行查询并逐行比较。

| 订单 | 正确的金额贡献 |
| --- | ---: |
| 1 | 100 |
| 2 | 80 |
| 3 | 80 |
| 4 | 100 |
| 合计 | 360 |

错误的内连接也会得到 360，因为它多算了订单 1 的 100，同时漏掉订单 4 的 100。请检查每个订单 ID 出现一次，并和上表比较金额，再检查总额。说明为什么 `SUM(DISTINCT amount)` 也会错：两笔金额相等的订单仍然是两笔订单。

## 从模型到 agent

| 形态 | 订单问题中的行为 | 可以核验什么 |
| --- | --- | --- |
| 单次模型调用 | 模型根据表结构和业务口径提出一条 SQL，人手动运行。 | 文本有没有引用实际存在的列，查询结果是否等于独立预期。 |
| 预定工作流 | 程序按固定步骤准备合成库、运行查询并对照预期。 | 工具是否真的执行，是否记录了结果与失败条件。 |
| 根据反馈决策的 agent | 系统给模型可用工具，模型根据异常结果选择看表结构、抽样或查看连接后的行数。 | 工具轨迹和最终数据库结果，外加异常时能否停止并明确指出缺失的业务口径。 |

[Anthropic 的工作流与 agent 说明](https://www.anthropic.com/research/building-effective-agents)提供了两种执行方式的区分，[Agent 评估](https://www.anthropic.com/research/demystifying-evals-for-ai-agents)说明怎样检查工具执行轨迹和实际结果。表格是同一案例的设计对照。目前可以运行上面的 SQLite 样例，agent 尚未实现。
