# D01｜SQL：单表查询、排序、聚合与 NULL

所有数据均为合成数据。本页有 3 道示范、12 道小表练习、3 道大表业务题。按主题依次完成；练习先自己写，示范可以运行和修改。作答填在同目录 `answers.sql`，不要改数据库中的数据。

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

## ① SELECT / WHERE

### 1.1 示范｜选择列并筛选订单

表：`s_orders(order_id, user_id, city, amount, order_date, status)`。

需求：返回状态为 `paid` 且金额至少 100 元的订单，只输出 `order_id, city, amount`；将输出金额列命名为 `order_amount`。不要求行序。

```sql
SELECT order_id, city, amount AS order_amount
FROM s_orders
WHERE status = 'paid' AND amount >= 100;
```

为什么：`FROM` 确定输入表，`WHERE` 针对每一行判断条件，只有结果为真的行留下，`SELECT` 再决定输出哪些列及列名。`AND` 要求两边都成立；`OR` 至少一边成立，混用时用括号明确范围（`AND` 优先于 `OR`）。数值直接写，字符串用单引号；`=` 比较相等，`<>` 比较不等，另有 `>、>=、<、<=`。`amount` 为 NULL 时，`amount >= 100` 为“未知”，不会通过 WHERE；城市为 NULL 但其他条件为真的行仍会留下。

同一层查询的 WHERE 写原列名 `amount`，不依赖 SELECT 才命名的 `order_amount`。**方言说明：MySQL 不允许在同层 WHERE 引用这样的 SELECT 别名；SQLite 有允许非聚合别名出现在 WHERE 的历史扩展，同名别名还可能指回原列，因此不能写成“SQLite 一定报错”。Hive 也不应依赖这一扩展，本课统一写原列名或原表达式。**这里的先后是理解查询结果的逻辑模型，不代表数据库逐句执行文本。

`IN ('北京', '深圳')` 表示属于列出的值；`BETWEEN 100 AND 200` 两端都包含。`LIKE '小%'` 中 `%` 代表任意长度（含零个）的字符，`_` 代表一个字符。缺失值用 `IS NULL` 或 `IS NOT NULL` 判断，不能用 `= NULL`。**方言说明：LIKE 的大小写行为受引擎、排序规则和配置影响；SQLite 默认对 ASCII 大小写不敏感，不推广到全部字符或 MySQL/Hive。本页中文前缀题不依赖大小写差异。**

预期结果（NULL 表示缺失；题目未要求排序时行序不限）：

| order_id | city | order_amount |
| --- | --- | --- |
| 101 | 上海 | 100 |
| 102 | 北京 | 200 |
| 104 | 深圳 | 100 |
| 105 | NULL | 150 |
| 110 | 深圳 | 200 |

### 1.2 小表练习

表：`s_orders(order_id, user_id, city, amount, order_date, status)`。

返回“上海且已支付”的订单，以及所有已退款订单。输出 `order_id, city, amount, status`，不要求行序。

预期结果（NULL 表示缺失；题目未要求排序时行序不限）：

| order_id | city | amount | status |
| --- | --- | --- | --- |
| 101 | 上海 | 100 | paid |
| 108 | 上海 | 300 | refunded |

### 1.3 小表练习

表：`s_orders(order_id, user_id, city, amount, order_date, status)`。

返回城市属于北京或深圳、且状态为 `paid` 的订单。输出 `order_id, user_id, city`，不要求行序。

预期结果（NULL 表示缺失；题目未要求排序时行序不限）：

| order_id | user_id | city |
| --- | --- | --- |
| 102 | 2 | 北京 |
| 104 | 3 | 深圳 |
| 110 | 8 | 深圳 |
| 112 | 99 | 北京 |

### 1.4 小表练习

表：`s_orders(order_id, user_id, city, amount, order_date, status)`。

返回金额在 100 至 200 元之间（含两端）、且订单日期在 2026-10-02 至 2026-10-06 之间（含两端）的订单。输出 `order_id, amount, order_date`，不要求行序。

预期结果（NULL 表示缺失；题目未要求排序时行序不限）：

| order_id | amount | order_date |
| --- | --- | --- |
| 104 | 100 | 2026-10-03 |
| 105 | 150 | 2026-10-03 |
| 110 | 200 | 2026-10-06 |
| 111 | 100 | 2026-10-06 |

### 1.5 小表练习

表：`s_users(user_id, name, city, channel)`。

返回姓名以“小”开头、或者城市缺失的用户。输出 `user_id, name, city`，不要求行序。

预期结果（NULL 表示缺失；题目未要求排序时行序不限）：

| user_id | name | city |
| --- | --- | --- |
| 1 | 小林 | 上海 |
| 2 | 小周 | 北京 |
| 4 | 阿雨 | NULL |
| 6 | 小陈 | 上海 |
| 8 | 小苏 | 深圳 |
| 9 | 小方 | 北京 |
| 10 | 小禾 | 成都 |

### 1.6 大表业务题

表：`orders(order_id, user_id, order_time, amount, status, channel)`。

运营要核查 2026-10-01 当天零点起至 2026-10-08 当天零点前的订单：状态为 `paid`，渠道属于 `app` 或 `wechat`，金额至少 300 元且小于 500 元。输出 `order_id, user_id, amount, order_time`，不要求行序。

## ② ORDER BY / LIMIT / DISTINCT

### 2.1 示范｜金额最高的四笔订单

表：`s_orders(order_id, user_id, city, amount, order_date, status)`。

需求：排除金额缺失的订单，按金额从大到小取前四笔；金额相同，订单号较小的在前。输出 `order_id, amount`。

```sql
SELECT order_id, amount
FROM s_orders
WHERE amount IS NOT NULL
ORDER BY amount DESC, order_id ASC
LIMIT 4;
```

为什么：先筛选、再决定输出，排序后截取前四行。`ASC` 升序，`DESC` 降序，省略方向默认升序。第二个排序键只在第一个键并列时起作用；唯一订单号让截取结果确定。没有 ORDER BY 时，返回顺序没有保证。`DISTINCT` 消除**整组输出列**都相同的重复结果；语法是在 SELECT 后写 DISTINCT，例如 `SELECT DISTINCT status FROM s_orders;`。输出两列时去重的是两列组合，不是只看第一列。

**方言说明：SQLite、MySQL 与 Hive 都有 LIMIT，但 Hive 的 ORDER BY 是全局排序，SORT BY 只保证每个 reducer 内有序，不能替换；部分 Hive 严格模式要求 ORDER BY 配合 LIMIT。本课查询不需要 SORT BY。SQLite 默认升序时 NULL 在前、降序时在后；跨方言不依赖默认 NULL 排序，后续可用 CASE 明确次序。**DISTINCT 输出中的多个 NULL 在去重时视为相同，这与 `NULL = NULL` 的比较结果不同。

预期结果（NULL 表示缺失；题目未要求排序时行序不限）：

| order_id | amount |
| --- | --- |
| 108 | 300 |
| 102 | 200 |
| 110 | 200 |
| 105 | 150 |

### 2.2 小表练习

表：`s_orders(order_id, user_id, city, amount, order_date, status)`。

返回金额已知的订单中最便宜的三笔，金额升序、同金额按订单号升序。输出 `order_id, amount`。

预期结果（NULL 表示缺失；题目未要求排序时行序不限）：

| order_id | amount |
| --- | --- |
| 107 | 0 |
| 103 | 50 |
| 112 | 50 |

### 2.3 小表练习

表：`s_orders(order_id, user_id, city, amount, order_date, status)`。

返回订单表出现过的不同城市，只输出 `city`；缺失城市保留一行，不要求行序。

预期结果（NULL 表示缺失；题目未要求排序时行序不限）：

| city |
| --- |
| 上海 |
| 北京 |
| 深圳 |
| NULL |
| 杭州 |
| 武汉 |

### 2.4 小表练习

表：`s_orders(order_id, user_id, city, amount, order_date, status)`。

返回不同的“用户、订单城市”组合，输出 `user_id, city`，按用户号升序。不要把重复下单算成新的组合。

预期结果（NULL 表示缺失；题目未要求排序时行序不限）：

| user_id | city |
| --- | --- |
| 1 | 上海 |
| 2 | 北京 |
| 3 | 深圳 |
| 4 | NULL |
| 5 | 杭州 |
| 6 | 上海 |
| 7 | 武汉 |
| 8 | 深圳 |
| 9 | NULL |
| 99 | 北京 |

### 2.5 小表练习

表：`s_orders(order_id, user_id, city, amount, order_date, status)`。

返回最近四笔 `paid` 订单，按订单日期降序，同日按订单号降序。输出 `order_id, order_date, amount`。

预期结果（NULL 表示缺失；题目未要求排序时行序不限）：

| order_id | order_date | amount |
| --- | --- | --- |
| 112 | 2026-10-07 | 50 |
| 110 | 2026-10-06 | 200 |
| 109 | 2026-10-05 | NULL |
| 107 | 2026-10-04 | 0 |

### 2.6 大表业务题

表：`orders(order_id, user_id, order_time, amount, status, channel)`。

财务抽查状态为 `paid` 且金额已知的前十笔高额订单。按金额降序，同金额按订单号升序，输出 `order_id, user_id, amount`。

## ③ 聚合与 NULL

### 3.1 示范｜行数、已知金额数和用户数

表：`s_orders(order_id, user_id, city, amount, order_date, status)`。

需求：只返回一行，依次输出总订单数 `order_count`、金额已知订单数 `known_amount_count`、不同下单用户数 `user_count`、已知金额合计 `total_amount`、已知金额均值 `avg_amount`、城市已知订单数 `known_city_count`、不同已知城市数 `city_count`。

```sql
SELECT COUNT(*) AS order_count,
       COUNT(amount) AS known_amount_count,
       COUNT(DISTINCT user_id) AS user_count,
       SUM(amount) AS total_amount,
       AVG(amount) AS avg_amount,
       COUNT(city) AS known_city_count,
       COUNT(DISTINCT city) AS city_count
FROM s_orders;
```

为什么：没有 GROUP BY 的聚合把筛选后的所有行视为一组，输出一个汇总行。`COUNT(*)` 数行，`COUNT(列)` 只数该列非 NULL 的行，`COUNT(DISTINCT 列)` 数该列不同的非 NULL 值。多次下单的用户只计一次；城市缺失的订单仍是一行，但不进入城市计数。

`SUM` 和 `AVG` 忽略 NULL；AVG 的分母是非 NULL 个数。`0` 会参与两者。这里金额合计 1250，金额已知的有 10 笔，所以均值是 125，不能除以 12。输入没有任何非 NULL 金额（包括根本没有输入行）时，SUM 和 AVG 都为 NULL，COUNT 为 0。无 GROUP BY 的聚合在空输入上仍输出一行；有 GROUP BY 时空输入没有组，输出零行。

**方言说明：这些单列计数及 NULL 规则适用于本课 SQLite、MySQL、Hive；SUM/AVG 的返回数值类型与精度可能不同。SQLite 的 TOTAL() 是本地扩展且空输入返回 0，本课不用它替代 SUM。**均值核对时允许最后几位小数的表示差异，不先把 NULL 改为零。

预期结果（NULL 表示缺失；题目未要求排序时行序不限）：

| order_count | known_amount_count | user_count | total_amount | avg_amount | known_city_count | city_count |
| --- | --- | --- | --- | --- | --- | --- |
| 12 | 10 | 10 | 1250 | 125.0 | 10 | 5 |

### 3.2 小表练习

表：`s_orders(order_id, user_id, city, amount, order_date, status)`。

仅统计 `paid` 订单。返回一行：`order_count`（总笔数）、`known_amount_count`（金额已知笔数）、`city_count`（不同的已知城市数）。

预期结果（NULL 表示缺失；题目未要求排序时行序不限）：

| order_count | known_amount_count | city_count |
| --- | --- | --- |
| 8 | 7 | 5 |

### 3.3 小表练习

表：`s_orders(order_id, user_id, city, amount, order_date, status)`。

统计上海订单的金额合计和已知金额均值，输出一行 `total_amount, avg_amount`。

预期结果（NULL 表示缺失；题目未要求排序时行序不限）：

| total_amount | avg_amount |
| --- | --- |
| 450 | 150.0 |

### 3.4 小表练习

表：`s_orders(order_id, user_id, city, amount, order_date, status)`。

只统计城市为成都的订单，输出一行：总笔数 `order_count`、金额已知笔数 `known_amount_count`、金额合计 `total_amount`、已知金额均值 `avg_amount`。保留数据库对缺失汇总值的原始表达。

预期结果（NULL 表示缺失；题目未要求排序时行序不限）：

| order_count | known_amount_count | total_amount | avg_amount |
| --- | --- | --- | --- |
| 0 | 0 | NULL | NULL |

### 3.5 小表练习

表：`s_orders(order_id, user_id, city, amount, order_date, status)`。

只统计金额缺失的订单，输出一行：总笔数 `order_count`、金额已知笔数 `known_amount_count`、不同已知金额数 `amount_count`、金额合计 `total_amount`、已知金额均值 `avg_amount`。

预期结果（NULL 表示缺失；题目未要求排序时行序不限）：

| order_count | known_amount_count | amount_count | total_amount | avg_amount |
| --- | --- | --- | --- | --- |
| 2 | 0 | 0 | NULL | NULL |

### 3.6 大表业务题

表：`orders(order_id, user_id, order_time, amount, status, channel)`。

统计 2026-10-01 零点起至 2026-10-28 零点前的 `paid` 订单，输出一行：总笔数 `order_count`、金额已知笔数 `known_amount_count`、不同下单用户数 `user_count`、已知金额合计 `total_amount`、已知金额均值 `avg_amount`。

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
