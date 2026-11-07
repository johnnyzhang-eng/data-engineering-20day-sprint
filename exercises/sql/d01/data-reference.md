# D1 输入数据参考

数据来源：`../data/practice.sqlite3`，均为合成数据。小表按主键升序展示。

金额单位为整数元；`NULL` 表示缺失，`0` 是已知的零。日期格式为 `YYYY-MM-DD`，时间格式为 `YYYY-MM-DD HH:MM:SS`。

## s_orders｜订单小表（12 行）

`order_id`：订单号；`user_id`：用户号；`city`：订单城市；`amount`：订单金额；`order_date`：订单日期；`status`：订单状态。

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

## s_users｜用户小表（10 行）

`user_id`：用户号；`name`：姓名；`city`：用户城市；`channel`：渠道。

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

## 值的含义

- `status`：`paid` 已支付；`completed` 已完成；`pending` 待支付；`cancelled` 已取消；`refunded` 已退款。
- `channel`：`app` 应用端；`web` 网页端；`wechat` 微信渠道。

## orders｜订单大表（20,000 行）

`order_id`：订单号；`user_id`：用户号；`order_time`：订单时间；`amount`：订单金额；`status`：订单状态；`channel`：渠道。

数据库中的实际表结构：

```sql
CREATE TABLE orders (
    order_id INTEGER PRIMARY KEY,
    user_id INTEGER NOT NULL REFERENCES users(user_id),
    order_time TEXT NOT NULL,
    amount INTEGER CHECK (amount >= 0),
    status TEXT NOT NULL CHECK (
        status IN ('paid', 'completed', 'pending', 'cancelled', 'refunded')
    ),
    channel TEXT
);
```
