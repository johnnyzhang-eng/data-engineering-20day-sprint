# D02｜SQL：分组、执行顺序、CASE WHEN 与 NULL

所有数据均为合成数据。本页有 2 道示范、8 道小表练习、2 道大表业务题。承接 D1，保留原主题编号 ④⑤。按主题依次完成；练习先自己写，示范可以运行和修改。作答填在同目录 `answers.sql`，不要改数据库中的数据。

## 使用环境与数据约定

先在终端运行 `python3 exercises/sql/data/build_db.py`。在 VS Code 的 SQLite3 Editor 中打开 `exercises/sql/data/practice.sqlite3`，把 `answers.sql` 的查询关联到这个数据库后，选中**一条完整语句（含分号）**运行。结果是查询返回的表格，不是新增的数据表。扩展使用的 SQLite 运行库可能与 Python 不同，可在扩展里执行：

```sql
SELECT sqlite_version() AS sqlite_version;
```

金额和价格均为整数元；`NULL` 表示缺失，金额 `0` 是已知的零。日期采用固定宽度的 ISO 文本：日期 `YYYY-MM-DD`，时间 `YYYY-MM-DD HH:MM:SS`，本材料视作同一业务时区的本地时间。按这一格式保存的文本可以按时间先后比较。`orders.amount` 是整单金额，已知时等于明细的 `qty * price` 合计；金额缺失不代表没有明细。每个 `(user_id, login_date)` 最多一条登录记录。

本日只查询单表，不要求联表或窗口函数。小表的 `user_id=99` 没有用户资料，`s_users.user_id=10` 没有订单；这些是有意设置的数据边界。

### 表结构

```text
s_orders(order_id INTEGER 主键, user_id INTEGER, city TEXT 可空,
         amount INTEGER 可空, order_date TEXT, status TEXT)
s_users(user_id INTEGER 主键, name TEXT, city TEXT 可空, channel TEXT 可空)
users(user_id INTEGER 主键, city TEXT 可空, register_date TEXT, channel TEXT 可空)
orders(order_id INTEGER 主键, user_id INTEGER, order_time TEXT,
       amount INTEGER 可空, status TEXT, channel TEXT 可空)
products(product_id INTEGER 主键, category TEXT, price INTEGER)
order_items(order_id INTEGER, product_id INTEGER, qty INTEGER, price INTEGER,
            联合主键(order_id, product_id))
logins(user_id INTEGER, login_date TEXT, 联合主键(user_id, login_date))
```

`status` 的可能值为 `paid`（已支付）、`completed`（已完成）、`pending`（待支付）、`cancelled`（已取消）、`refunded`（已退款）；渠道为 `app`、`web`、`wechat` 或 NULL。小表城市为下表的字面值，不作资料补全。

### 可手算的小表

`s_orders`：

| order_id | user_id | city | amount | order_date | status |
|---:|---:|---|---:|---|---|
| 101 | 1 | 上海 | 100 | 2026-10-01 | paid |
| 102 | 2 | 北京 | 200 | 2026-10-01 | paid |
| 103 | 1 | 上海 | 50 | 2026-10-02 | cancelled |
| 104 | 3 | 深圳 | 100 | 2026-10-03 | paid |
| 105 | 4 | NULL | 150 | 2026-10-03 | paid |
| 106 | 2 | 北京 | NULL | 2026-10-04 | pending |
| 107 | 5 | 杭州 | 0 | 2026-10-04 | paid |
| 108 | 6 | 上海 | 300 | 2026-10-05 | refunded |
| 109 | 7 | 武汉 | NULL | 2026-10-05 | paid |
| 110 | 8 | 深圳 | 200 | 2026-10-06 | paid |
| 111 | 9 | NULL | 100 | 2026-10-06 | cancelled |
| 112 | 99 | 北京 | 50 | 2026-10-07 | paid |

`s_users`：

| user_id | name | city | channel |
|---:|---|---|---|
| 1 | 小林 | 上海 | app |
| 2 | 小周 | 北京 | web |
| 3 | 阿青 | 深圳 | app |
| 4 | 阿雨 | NULL | wechat |
| 5 | 阿明 | 杭州 | web |
| 6 | 小陈 | 上海 | app |
| 7 | 阿宁 | 武汉 | NULL |
| 8 | 小苏 | 深圳 | wechat |
| 9 | 小方 | 北京 | app |
| 10 | 小禾 | 成都 | web |

## ④ GROUP BY / HAVING 与逻辑执行顺序

### 4.1 示范｜已支付订单至少两笔的城市

表：`s_orders(order_id, user_id, city, amount, order_date, status)`。

需求：先限定 `paid` 订单，按订单城市统计，只留下至少两笔的城市。输出 `city, order_count, total_amount`，按城市升序。

```sql
SELECT city, COUNT(*) AS order_count, SUM(amount) AS total_amount
FROM s_orders
WHERE status = 'paid'
GROUP BY city
HAVING COUNT(*) >= 2
ORDER BY city ASC;
```

为什么：WHERE 筛的是原始订单行；GROUP BY 把留下的行按城市分组；COUNT 和 SUM 在各组内计算；HAVING 再筛组。把 `status = 'paid'` 放到 WHERE，可以让取消、退款等订单从一开始就不参加计数。`COUNT(*) >= 2` 是整组性质，不能直接写在同层 WHERE。若先不筛状态，其他状态订单就会改变城市组的笔数。

理解本日查询的逻辑顺序：`FROM → WHERE → GROUP BY/聚合 → HAVING → SELECT → DISTINCT → ORDER BY → LIMIT`。这是结果语义的学习模型；优化器可以合并、提前或改写实际操作，不代表固定物理执行顺序。没有写某个子句，就跳过相应步骤。GROUP BY 会把同一个分组键的 NULL 放在一组；该组内 COUNT(*) 仍数行，SUM 仍忽略金额 NULL。

**方言说明：分组查询只输出分组列或聚合表达式；不要利用 SQLite 允许某些未分组“裸列”的宽松行为。MySQL 的 ONLY_FULL_GROUP_BY 和 Hive 对这类写法有约束。HAVING 直接写聚合表达式，避免依赖别名解析差异。**本例不用 SELECT 别名作为 HAVING 条件。

预期结果（NULL 表示缺失；题目未要求排序时行序不限）：

| city | order_count | total_amount |
| --- | --- | --- |
| 北京 | 2 | 250 |
| 深圳 | 2 | 300 |

### 4.2 小表练习

表：`s_orders(order_id, user_id, city, amount, order_date, status)`。

按下单用户统计全部状态订单，只返回至少下过两笔订单的用户。输出 `user_id, order_count`，按用户号升序。

预期结果（NULL 表示缺失；题目未要求排序时行序不限）：

| user_id | order_count |
| --- | --- |
| 1 | 2 |
| 2 | 2 |

### 4.3 小表练习

表：`s_orders(order_id, user_id, city, amount, order_date, status)`。

先限定 `paid` 订单，再按订单城市统计，保留已知金额合计至少 200 元的城市。输出 `city, order_count, total_amount`，按合计金额降序，同金额按城市升序。

预期结果（NULL 表示缺失；题目未要求排序时行序不限）：

| city | order_count | total_amount |
| --- | --- | --- |
| 深圳 | 2 | 300 |
| 北京 | 2 | 250 |

### 4.4 小表练习

表：`s_users(user_id, name, city, channel)`。

按注册渠道统计用户数，只保留至少两名用户的渠道。输出 `channel, user_count`，按用户数降序，同数量按渠道升序。缺失渠道作为一个分组参与统计。

预期结果（NULL 表示缺失；题目未要求排序时行序不限）：

| channel | user_count |
| --- | --- |
| app | 4 |
| web | 3 |
| wechat | 2 |

### 4.5 小表练习

表：`s_orders(order_id, user_id, city, amount, order_date, status)`。

只统计 2026-10-03 至 2026-10-07（含两端）的订单，按状态分组，仅保留至少有两笔金额已知订单的状态。输出 `status, order_count, known_amount_count, avg_amount`，按状态升序。

预期结果（NULL 表示缺失；题目未要求排序时行序不限）：

| status | order_count | known_amount_count | avg_amount |
| --- | --- | --- | --- |
| paid | 6 | 5 | 100.0 |

### 4.6 大表业务题

表：`orders(order_id, user_id, order_time, amount, status, channel)`。

统计 2026-10-01 零点起至 2026-10-28 零点前的 `paid` 订单，按订单渠道分组（缺失渠道也成组），只保留已知金额合计至少 50000 元的渠道。输出 `channel, order_count, total_amount`，按合计金额降序；同金额按渠道升序，并列时缺失渠道在非缺失渠道前。

## ⑤ CASE WHEN 与 NULL 语义

### 5.1 示范｜按金额标记订单

表：`s_orders(order_id, user_id, city, amount, order_date, status)`。

需求：输出所有订单的 `order_id, amount, amount_band`。金额缺失标“金额缺失”，至少 200 元标“高额”，其余标“普通”，按订单号升序。

```sql
SELECT order_id, amount,
       CASE WHEN amount IS NULL THEN '金额缺失'
            WHEN amount >= 200 THEN '高额'
            ELSE '普通'
       END AS amount_band
FROM s_orders
ORDER BY order_id ASC;
```

为什么：CASE 是产生一个值的表达式，不会自动删行。它从上往下选择第一个为真的 WHEN 分支；后面即使也为真，不会再覆盖。金额 NULL 的比较（如 `>= 200`）是未知，不会命中，因此这里先明确标记缺失。没有 ELSE 且没有命中时，结果是 NULL。文字结果用单引号，别名不加单引号。

SQL 的比较有真、假、未知三种结果：`NULL = 0`、`NULL <> 0`、`NULL = NULL` 都是未知，WHERE 只保留真；`IS NULL` 才是在判断缺失。`NOT 未知` 仍是未知；`假 AND 未知` 为假，`真 OR 未知` 为真，其余与未知组合不一定能得到真或假。简单 CASE 的 `CASE amount WHEN NULL ...` 也不是检查 NULL，因为它做的是相等比较。CASE 表达式可以放在 SUM 等聚合函数里面；也可以在 GROUP BY 中完整重写同一个 CASE 表达式，按分类结果分组。聚合 CASE 产生的数值可将逐行分类与汇总结合；数字 `0` 是数值，NULL 是缺失，计数口径不能互换。

**方言说明：本课带条件的 CASE WHEN 及三值逻辑适用于 SQLite、MySQL、Hive。各分支统一返回文本或统一返回数值，避免 SQLite 的宽松类型掩盖 MySQL/Hive 的类型归并差异。Hive 与 MySQL 的专有条件函数不作为本课答案。**

预期结果（NULL 表示缺失；题目未要求排序时行序不限）：

| order_id | amount | amount_band |
| --- | --- | --- |
| 101 | 100 | 普通 |
| 102 | 200 | 高额 |
| 103 | 50 | 普通 |
| 104 | 100 | 普通 |
| 105 | 150 | 普通 |
| 106 | NULL | 金额缺失 |
| 107 | 0 | 普通 |
| 108 | 300 | 高额 |
| 109 | NULL | 金额缺失 |
| 110 | 200 | 高额 |
| 111 | 100 | 普通 |
| 112 | 50 | 普通 |

### 5.2 小表练习

表：`s_orders(order_id, user_id, city, amount, order_date, status)`。

仅返回 `paid` 订单的 `order_id, amount, amount_state`：金额缺失标“金额缺失”，金额等于零标“零金额”，其余标“正金额”。按订单号升序。

预期结果（NULL 表示缺失；题目未要求排序时行序不限）：

| order_id | amount | amount_state |
| --- | --- | --- |
| 101 | 100 | 正金额 |
| 102 | 200 | 正金额 |
| 104 | 100 | 正金额 |
| 105 | 150 | 正金额 |
| 107 | 0 | 零金额 |
| 109 | NULL | 金额缺失 |
| 110 | 200 | 正金额 |
| 112 | 50 | 正金额 |

### 5.3 小表练习

表：`s_orders(order_id, user_id, city, amount, order_date, status)`。

返回订单号为 105、106、109、111 的 `order_id, city_label`：城市缺失标“未填写”，否则使用订单原城市。按订单号升序。

预期结果（NULL 表示缺失；题目未要求排序时行序不限）：

| order_id | city_label |
| --- | --- |
| 105 | 未填写 |
| 106 | 北京 |
| 109 | 武汉 |
| 111 | 未填写 |

### 5.4 小表练习

表：`s_orders(order_id, user_id, city, amount, order_date, status)`。

返回所有订单的 `order_id, amount_band`：金额缺失标“未知”，不足 100 元标“低额”，至少 100 且不足 200 元标“中额”，至少 200 元标“高额”。按订单号升序。

预期结果（NULL 表示缺失；题目未要求排序时行序不限）：

| order_id | amount_band |
| --- | --- |
| 101 | 中额 |
| 102 | 高额 |
| 103 | 低额 |
| 104 | 中额 |
| 105 | 中额 |
| 106 | 未知 |
| 107 | 低额 |
| 108 | 高额 |
| 109 | 未知 |
| 110 | 高额 |
| 111 | 中额 |
| 112 | 低额 |

### 5.5 小表练习

表：`s_orders(order_id, user_id, city, amount, order_date, status)`。

统计全部订单，只返回一行三列：金额缺失订单数 `missing_count`、金额至少 100 元的订单数 `at_least_100_count`、金额不足 100 元的订单数 `below_100_count`。缺失金额不计入后两类。

预期结果（NULL 表示缺失；题目未要求排序时行序不限）：

| missing_count | at_least_100_count | below_100_count |
| --- | --- | --- |
| 2 | 7 | 3 |

### 5.6 大表业务题

表：`orders(order_id, user_id, order_time, amount, status, channel)`。

对全部订单生成业务状态：“成交”包括 `paid` 与 `completed`，“退款”包括 `refunded`，其余为“其他”。按业务状态汇总，输出 `business_status, order_count, known_amount_count, total_amount`；合计只计算已知金额。按总笔数降序，同笔数按业务状态升序。

## 语义核对来源

以下为示范解释的官方资料，独立练习题没有额外提示：

- [SQLite SELECT：分组、DISTINCT、排序与限制](https://sqlite.org/lang_select.html)
- [SQLite 聚合函数：COUNT、SUM、AVG](https://sqlite.org/lang_aggfunc.html)
- [SQLite 表达式：NULL、LIKE、BETWEEN、CASE](https://sqlite.org/lang_expr.html)
- [MySQL 8.4：SELECT 别名的使用限制](https://dev.mysql.com/doc/refman/8.4/en/problems-with-alias.html)
- [SQLite 官方论坛：WHERE 别名的历史扩展](https://sqlite.org/forum/info/36c281c5cc5395ea)
- [Apache Hive SELECT / HAVING](https://hive.apache.org/docs/latest/language/languagemanual-select/)
- [Apache Hive ORDER BY / SORT BY](https://hive.apache.org/docs/latest/language/languagemanual-sortby/)
- [Apache Hive 函数与聚合](https://hive.apache.org/docs/latest/language/languagemanual-udf/)
