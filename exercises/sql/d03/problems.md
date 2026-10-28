# D3｜JOIN：从匹配行到业务口径

学习日：2026-11-02。全部是合成数据；5 个主题，每个 1 道示范、4 道小表练习、1 道大表业务题。先预测，再在同目录 `answers.sql` 独立作答；示范属于 L3，不计独立能力。练习页的完整结果用于运行后核对，先预测时请由陪练遮住结果区。标准 SQL 答案仅在 private/answer-keys/d03.sql 中供判卷。

运行环境：首次或需要补齐 D3 小表时运行 `python3 exercises/sql/data/build_db.py`（重建合成库），在 SQLite3 Editor 打开 `exercises/sql/data/practice.sqlite3`；每次选中一条完整语句（含分号）运行，所有练习只查询、不改数据。原 s_users、s_orders 和大表数据保持原固定种子数据。

金额为整数元，NULL 是缺失，不是 0；日期为同一业务时区的 ISO 文本。订单城市与用户资料城市是不同字段，不互相补全。用户表主键不可重复；订单里的 user_id、明细里的 order_id 则故意重复，模拟一对多连接。

## 表结构与完整小表

```text
s_users(user_id 主键, name, city 可空, channel 可空)
s_orders(order_id 主键, user_id, city 可空, amount 可空, order_date, status)
s_products(product_id 主键, name, category)
s_order_items(order_id, product_id, qty, price, 联合主键(order_id,product_id))
users(user_id 主键, city 可空, register_date, channel 可空)
orders(order_id 主键, user_id, order_time, amount 可空, status, channel 可空)
products(product_id 主键, category, price [商品价])
order_items(order_id, product_id, qty, price [成交单价], 联合主键(order_id,product_id))
```

小表商品明细是教学样本：110 故意没有明细，107 的明细成交价为 0；106、109 整单金额缺失但有明细。已知整单金额且有明细的订单，其金额与明细合计相等。112 找不到用户 99，用户 10 从未下单；小表不启用订单到用户的外键。

`s_users`：

| user_id | name | city | channel |
| --- | --- | --- | --- |
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

`s_orders`：

| order_id | user_id | city | amount | order_date | status |
| --- | --- | --- | --- | --- | --- |
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

`s_products`：

| product_id | name | category |
| --- | --- | --- |
| 201 | 杯子 | 日用 |
| 202 | 贴纸 | 文具 |
| 203 | 袋子 | 日用 |

`s_order_items`：

| order_id | product_id | qty | price |
| --- | --- | --- | --- |
| 101 | 201 | 1 | 50 |
| 101 | 202 | 2 | 25 |
| 102 | 203 | 2 | 100 |
| 103 | 201 | 1 | 50 |
| 104 | 202 | 4 | 25 |
| 105 | 201 | 1 | 50 |
| 105 | 203 | 1 | 100 |
| 106 | 202 | 1 | 25 |
| 107 | 202 | 1 | 0 |
| 108 | 203 | 3 | 100 |
| 109 | 201 | 2 | 50 |
| 111 | 203 | 1 | 100 |
| 112 | 201 | 1 | 50 |


## 1｜INNER JOIN：只留下匹配行

### 1.1 示范：给订单补用户姓名

查询订单 101、112 的用户姓名。输出 order_id, name，按订单号升序；先预测哪笔会消失。


```sql
SELECT o.order_id, u.name
FROM s_orders AS o
INNER JOIN s_users AS u ON u.user_id = o.user_id
WHERE o.order_id IN (101,112)
ORDER BY o.order_id;
```

为什么：FROM 先定义两张表的配对关系，ON 只保留为真的组合，WHERE 再筛连接结果，SELECT 决定输出。把它想成“为每笔订单找相同 user_id 的用户”；不必真的构造所有组合，优化器可以利用索引。INNER JOIN 不保留找不到资料的订单，也不会自动去重。同名列用 o.user_id、u.user_id 区分，AS 后的 o、u 只是本条语句内的表别名。NULL = NULL 仍是未知，不能用城市缺失互相配对。


<details>
<summary>运行后核对：完整预期结果</summary>

| order_id | name |
| --- | --- |
| 101 | 小林 |

</details>

### 1.2 小表练习

给所有 paid 订单补姓名。输出 order_id, name, amount，按订单号升序。只保留能匹配用户的订单。


<details>
<summary>运行后核对：完整预期结果</summary>

| order_id | name | amount |
| --- | --- | --- |
| 101 | 小林 | 100 |
| 102 | 小周 | 200 |
| 104 | 阿青 | 100 |
| 105 | 阿雨 | 150 |
| 107 | 阿明 | 0 |
| 109 | 阿宁 | NULL |
| 110 | 小苏 | 200 |

</details>

### 1.3 小表练习

查询注册渠道为 web 的用户的全部状态订单。输出 order_id, name, status，按订单号升序。渠道取用户表，不是订单状态。


<details>
<summary>运行后核对：完整预期结果</summary>

| order_id | name | status |
| --- | --- | --- |
| 102 | 小周 | paid |
| 106 | 小周 | pending |
| 107 | 阿明 | paid |

</details>

### 1.4 小表练习

找订单城市缺失、但用户资料城市已知的订单。输出 order_id, name, user_city（用户城市），按订单号升序。


<details>
<summary>运行后核对：完整预期结果</summary>

| order_id | name | user_city |
| --- | --- | --- |
| 111 | 小方 | 北京 |

</details>

### 1.5 小表练习

查询订单号至少为 109 且能匹配用户的订单。输出 order_id, user_id（订单用户号）, name，按订单号升序；口述 112 为何没有出现。


<details>
<summary>运行后核对：完整预期结果</summary>

| order_id | user_id | name |
| --- | --- | --- |
| 109 | 7 | 阿宁 |
| 110 | 8 | 小苏 |
| 111 | 9 | 小方 |

</details>

### 1.6 大表业务题

在 orders、users 中查询用户资料城市为上海、2026-10-01 零点起至 2026-10-08 零点前的 paid 订单。输出 order_id, user_id, user_city, amount，按订单号升序取前 20 行。

## 2｜LEFT JOIN：保留左表与 ON / WHERE 的边界

### 2.1 示范：保留没有订单的用户

仅查询用户 10，保留其资料及可能的订单。输出 user_id, name, order_id，按用户号、订单号升序。


```sql
SELECT u.user_id,u.name,o.order_id
FROM s_users AS u
LEFT JOIN s_orders AS o ON o.user_id=u.user_id
WHERE u.user_id=10
ORDER BY u.user_id,o.order_id;
```

为什么：LEFT JOIN 先按 ON 匹配；某个左行完全没有匹配时，补一行右侧全 NULL 的结果。左行有两条匹配就有两行，绝不是“左表多少行就输出多少行”。随后 WHERE 仍只保留真：把右表 status = 'paid' 放 WHERE 会删掉补出的 NULL 行；要保留所有左用户并只连接 paid 订单，应把该条件写入 ON。用右表非空主键判断有没有匹配，不用本来就可缺失的 amount、city。


<details>
<summary>运行后核对：完整预期结果</summary>

| user_id | name | order_id |
| --- | --- | --- |
| 10 | 小禾 | NULL |

</details>

### 2.2 小表练习

以订单为左表查询 105、112，保留找不到用户的订单。输出 order_id, matched_user_id（用户表主键）, name, user_city，按订单号升序。


<details>
<summary>运行后核对：完整预期结果</summary>

| order_id | matched_user_id | name | user_city |
| --- | --- | --- | --- |
| 105 | 4 | 阿雨 | NULL |
| 112 | NULL | NULL | NULL |

</details>

### 2.3 小表练习

保留用户 6、9、10，并只连接 paid 订单。输出 user_id, order_id，按用户号、订单号升序；不得因没有 paid 订单丢掉用户。


<details>
<summary>运行后核对：完整预期结果</summary>

| user_id | order_id |
| --- | --- |
| 6 | NULL |
| 9 | NULL |
| 10 | NULL |

</details>

### 2.4 小表练习

保留用户 1、2、10，只连接金额至少 150 的订单（不限状态）。输出 user_id, order_id, amount，按用户号、订单号升序。


<details>
<summary>运行后核对：完整预期结果</summary>

| user_id | order_id | amount |
| --- | --- | --- |
| 1 | NULL | NULL |
| 2 | 102 | 200 |
| 10 | NULL | NULL |

</details>

### 2.5 小表练习

订单 106、109、112 为左表连接用户，输出 order_id, amount, matched_user_id，按订单号升序。解释金额缺失与没匹配上用户为何是两件事。


<details>
<summary>运行后核对：完整预期结果</summary>

| order_id | amount | matched_user_id |
| --- | --- | --- |
| 106 | NULL | 2 |
| 109 | NULL | 7 |
| 112 | 50 | NULL |

</details>

### 2.6 大表业务题

users 中用户号 1–10 都必须保留，只连接 2026-10-01 零点起至 2026-10-08 零点前的 paid 订单。逐用户输出 user_id, order_count（匹配订单数）, total_amount（已知订单金额和）；无匹配时计数为 0、金额和保持 NULL。按用户号升序。

## 3｜一对多、重复连接键与统计粒度

### 3.1 示范：数行还是数订单

用户 1、2、10 左连接全部订单，逐用户输出 user_id, joined_rows（连接行数）, order_count（真实订单数），按用户号升序。


```sql
SELECT u.user_id,COUNT(*) AS joined_rows,COUNT(o.order_id) AS order_count
FROM s_users AS u
LEFT JOIN s_orders AS o ON o.user_id=u.user_id
WHERE u.user_id IN (1,2,10)
GROUP BY u.user_id
ORDER BY u.user_id;
```

为什么：s_users.user_id 唯一，而 s_orders.user_id 会重复：一位用户两笔订单，连接后用户资料也出现两次。同一个连接键在两侧分别出现 m、n 次，等值匹配就产生 m×n 个组合。s_order_items.order_id 也重复，订单连明细后粒度变为“一行一商品明细”。LEFT JOIN 后 COUNT(*) 会把无匹配时的占位行计入；COUNT(o.order_id) 才数实际订单。SUM(o.amount) 在明细层可能反复累计整单金额；SUM(DISTINCT o.amount) 也不是修复方法，因为不同订单可以金额相同。先确定输出一行代表什么，再决定是否要连接明细以及聚合哪一列。


<details>
<summary>运行后核对：完整预期结果</summary>

| user_id | joined_rows | order_count |
| --- | --- | --- |
| 1 | 2 | 2 |
| 2 | 2 | 2 |
| 10 | 1 | 0 |

</details>

### 3.2 小表练习

s_users 内连接全部 s_orders，输出一行 joined_rows（连接行数）、user_count（不同用户数）。解释这两个数为何不同，订单 112 是否参加。


<details>
<summary>运行后核对：完整预期结果</summary>

| joined_rows | user_count |
| --- | --- |
| 11 | 9 |

</details>

### 3.3 小表练习

订单 101、105、110 左连接 s_order_items。逐订单输出 order_id, joined_rows, item_count（用明细非空的 product_id 计数），按订单号升序。


<details>
<summary>运行后核对：完整预期结果</summary>

| order_id | joined_rows | item_count |
| --- | --- | --- |
| 101 | 2 | 2 |
| 105 | 2 | 2 |
| 110 | 1 | 0 |

</details>

### 3.4 小表练习

诊断订单 101、105 连接明细后的重复累计：输出 order_id, repeated_order_amount（直接 SUM 整单金额的错误口径）, item_total（SUM(qty*price)）, order_amount（该订单原金额，使用分组键或 MAX），按订单号升序。指出前一列为何偏大。


<details>
<summary>运行后核对：完整预期结果</summary>

| order_id | repeated_order_amount | item_total | order_amount |
| --- | --- | --- | --- |
| 101 | 200 | 100 | 100 |
| 105 | 300 | 150 | 150 |

</details>

### 3.5 小表练习

故障复现：把用户 1、6 按“城市相等”连接订单，而不是按 user_id。输出 user_id（用户表）, order_id，按用户号、订单号升序。口述为何同城不能证明是本人下单，NULL 城市又会怎样。


<details>
<summary>运行后核对：完整预期结果</summary>

| user_id | order_id |
| --- | --- |
| 1 | 101 |
| 1 | 103 |
| 1 | 108 |
| 6 | 101 |
| 6 | 103 |
| 6 | 108 |

</details>

### 3.6 大表业务题

用户经营统计：users 连接 orders，只统计 2026-10-01 零点起至 2026-10-08 零点前的 paid 订单，逐用户输出 user_id, order_count, known_amount_count, total_amount，只留下至少 2 笔订单者，按用户号升序。保持订单粒度，不连接明细。

## 4｜反连接：没有下过单与没有符合条件的订单

### 4.1 示范：从未下过单的用户

返回从未下过任何订单的用户，输出 user_id, name，按用户号升序。


```sql
SELECT u.user_id,u.name
FROM s_users AS u
LEFT JOIN s_orders AS o ON o.user_id=u.user_id
WHERE o.order_id IS NULL
ORDER BY u.user_id;
```

为什么：找“没有匹配”的常用方法是 LEFT JOIN ... ON ... WHERE 右表非空主键 IS NULL。先连接所有订单再挑没有匹配的用户，表示“从未下单”；在 ON 里加 paid 再判断主键 NULL，表示“从未下过 paid 订单”，不等于从未下单。判断对象必须是非空主键（如 order_id），不可用可空 amount。NOT EXISTS 也可等价表达，但今天不要求子查询；不要把 NOT IN 与 NULL 的陷阱混入新语法。


<details>
<summary>运行后核对：完整预期结果</summary>

| user_id | name |
| --- | --- |
| 10 | 小禾 |

</details>

### 4.2 小表练习

找没有 paid 订单的用户（允许有其他状态订单）。输出 user_id, name，按用户号升序。


<details>
<summary>运行后核对：完整预期结果</summary>

| user_id | name |
| --- | --- |
| 6 | 小陈 |
| 9 | 小方 |
| 10 | 小禾 |

</details>

### 4.3 小表练习

找订单中的孤立用户引用：返回找不到用户资料的订单。输出 order_id, user_id（订单中的值），按订单号升序。


<details>
<summary>运行后核对：完整预期结果</summary>

| order_id | user_id |
| --- | --- |
| 112 | 99 |

</details>

### 4.4 小表练习

返回完全没有商品明细的订单。输出 order_id, amount，按订单号升序。判断列选明细的非空 product_id。


<details>
<summary>运行后核对：完整预期结果</summary>

| order_id | amount |
| --- | --- |
| 110 | 200 |

</details>

### 4.5 小表练习

返回在 2026-10-05（含）至 2026-10-07（不含）期间没有任何状态订单的用户。输出 user_id，按用户号升序；其他日期下过单也应保留。


<details>
<summary>运行后核对：完整预期结果</summary>

| user_id |
| --- |
| 1 |
| 2 |
| 3 |
| 4 |
| 5 |
| 10 |

</details>

### 4.6 大表业务题

召回人群规模：统计 users 中在 2026-10-20 零点起至 2026-10-28 零点前没有 paid 订单的用户数，输出一行 user_count。其他状态订单不能排除用户，订单金额缺失也仍是一笔订单。

## 5｜多表连接：沿关系走到明细，再确定金额口径

### 5.1 示范：四表追到商品

连接 s_users、s_orders、s_order_items、s_products，查询订单 101。输出 user_id, name（用户）, order_id, product_id, product_name, qty, item_amount（qty*price），按商品号升序。


```sql
SELECT u.user_id,u.name,o.order_id,p.product_id,p.name AS product_name,i.qty,i.qty*i.price AS item_amount
FROM s_users AS u
JOIN s_orders AS o ON o.user_id=u.user_id
JOIN s_order_items AS i ON i.order_id=o.order_id
JOIN s_products AS p ON p.product_id=i.product_id
WHERE o.order_id=101
ORDER BY p.product_id;
```

为什么：关系是用户 → 订单 → 订单明细 → 商品。每多连一张表，都重新检查保留哪些行、一行代表什么；INNER JOIN 明细会排除缺明细的订单，LEFT JOIN 后继续 INNER JOIN 商品也可能删掉之前补出的空行。要保留空链就继续 LEFT JOIN。明细收入用成交时 i.price，不用商品现价，也不直接累计 o.amount；SUM(i.qty*i.price) 可以包括整单 amount 缺失但明细已知的订单。COUNT(DISTINCT o.order_id) 数去重订单，COUNT(*) 数当前明细行，类别间的订单计数不能直接相加当作总订单数。


<details>
<summary>运行后核对：完整预期结果</summary>

| user_id | name | order_id | product_id | product_name | qty | item_amount |
| --- | --- | --- | --- | --- | --- | --- |
| 1 | 小林 | 101 | 201 | 杯子 | 1 | 50 |
| 1 | 小林 | 101 | 202 | 贴纸 | 2 | 50 |

</details>

### 5.2 小表练习

连接上述四表，查 paid 订单中的文具类商品明细。输出 order_id, name（用户）, product_name, item_amount，按订单号、商品号升序。


<details>
<summary>运行后核对：完整预期结果</summary>

| order_id | name | product_name | item_amount |
| --- | --- | --- | --- |
| 101 | 小林 | 贴纸 | 50 |
| 104 | 阿青 | 贴纸 | 100 |
| 107 | 阿明 | 贴纸 | 0 |

</details>

### 5.3 小表练习

连接用户、订单、明细，按用户资料城市统计 paid 订单的明细收入。输出 city, item_revenue。只统计能同时匹配用户和明细的订单；缺失城市成一组，排序缺失在前、其他城市升序。


<details>
<summary>运行后核对：完整预期结果</summary>

| city | item_revenue |
| --- | --- |
| NULL | 150 |
| 上海 | 100 |
| 北京 | 200 |
| 杭州 | 0 |
| 武汉 | 100 |
| 深圳 | 100 |

</details>

### 5.4 小表练习

保留用户 1、8、10，依次左连接全部订单及明细。输出 user_id, order_id, product_id，按用户号、订单号、商品号升序。用户 8 有订单但没明细，用户 10 没订单；两者都保留。


<details>
<summary>运行后核对：完整预期结果</summary>

| user_id | order_id | product_id |
| --- | --- | --- |
| 1 | 101 | 201 |
| 1 | 101 | 202 |
| 1 | 103 | 201 |
| 8 | 110 | NULL |
| 10 | NULL | NULL |

</details>

### 5.5 小表练习

只连接订单、明细、商品三表（不要求用户资料存在），按商品类别统计 paid 订单。输出 category, order_count（不同订单）, item_count（明细行）, item_revenue，按类别升序。解释为何订单 112 应计入，110 不计入。


<details>
<summary>运行后核对：完整预期结果</summary>

| category | order_count | item_count | item_revenue |
| --- | --- | --- | --- |
| 文具 | 3 | 3 | 150 |
| 日用 | 5 | 6 | 550 |

</details>

### 5.6 大表业务题

连接 users、orders、order_items、products；统计用户注册渠道为 app、订单为 paid、订单时间在 2026-10-01 零点起至 2026-10-08 零点前的明细。按商品类别输出 category, order_count（类别内不同订单）, unit_count（商品件数之和）, item_revenue（按成交明细价），按类别升序。不排除整单 amount 缺失的订单。

## 原理核对与课后口述

1. INNER JOIN 与 LEFT JOIN 在没有匹配时各返回什么？
2. 为什么同为 LEFT JOIN，右表筛选写 ON 与 WHERE 可能不同？
3. 用户接订单、订单接明细后，一行分别代表什么？COUNT(*)、COUNT(右表主键) 为什么不同？
4. 如何区分“没有订单”“没有 paid 订单”“订单金额缺失”？
5. 一笔订单有两种类别时，各类别的订单数能不能相加？

这里描述的是查询语义，不是保证数据库按固定物理步骤逐行执行。依据：[SQLite SELECT 的 JOIN、补空行和 WHERE 说明](https://www.sqlite.org/lang_select.html#determination_of_input_data_from_clause_processing)；NULL 比较依据：[SQLite 表达式说明](https://www.sqlite.org/lang_expr.html)。截至本次材料构建已对照官方文档；本课只使用标准的 INNER/LEFT JOIN ... ON，不依赖 NATURAL JOIN 或 SQLite 宽松分组语法。
