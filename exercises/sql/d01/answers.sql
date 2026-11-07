-- database: ../data/practice.sqlite3
-- Day 01 作答区；数据库：../data/practice.sqlite3。
-- 每次选中一条完整语句（含分号）运行，保留本人首稿。
-- .1是示范复写区；其余先独立作答。AI答案不记作本人独立作答。

-- 1.1｜示范｜选择列并筛选订单
-- 输入表：s_orders
-- 需求：返回状态为 paid 且金额至少 100 元的订单，只输出
-- order_id, city, amount；将输出金额列命名为
-- order_amount。不要求行序。
SELECT order_id, city, amount AS order_amount
FROM s_orders
WHERE status = 'paid' and amount >= 100;



-- 1.2｜小表练习
-- 输入表：s_orders
-- 返回“上海且已支付”的订单，以及所有已退款订单。输出
-- order_id, city, amount, status，不要求行序。
SELECT order_id, city, amount, status 
FROM s_orders
WHERE (status = 'paid' and city = '上海') OR status = 'refunded';
-- 口述追问：若新增一笔“北京、已退款”的订单，
-- 当前查询会不会留下它？为什么？（假设其余字段合法）


-- 1.3｜小表练习
-- 输入表：s_orders
-- 返回城市属于北京或深圳、且状态为 paid 的订单。输出
-- order_id, user_id, city，不要求行序。
SELECT order_id, user_id, city
FROM s_orders
WHERE (city = '北京' OR city = '深圳') AND  status = 'paid';
-- 口述追问：为什么把两个城市条件放进括号，
-- 再与已支付条件用 AND 连接？


-- 1.4｜小表练习
-- 输入表：s_orders
-- 返回金额在 100 至 200 元之间（含两端）、且订单日期在
-- 2026-10-02 至 2026-10-06 之间（含两端）的订单。输出
-- order_id, amount, order_date，不要求行序。
SELECT order_id, amount, order_date
FROM s_orders
WHERE (amount BETWEEN 100 AND 200) AND (order_date between '2026-10-02' and '2026-10-06');
-- 口述变式：若日期改写为 DD-MM-YYYY，比较
-- '31-01-2026' 与 '01-02-2026'：按文本先后、
-- 按真实日期先后，各是哪一个在前？


-- 1.5｜小表练习
-- 输入表：s_users
-- 返回姓名以“小”开头、或者城市缺失的用户。输出 user_id,
-- name, city，不要求行序。
SELECT user_id, name, city
FROM s_users
WHERE name LIKE '小%' OR city IS NULL;
-- 口述追问：这里为什么用 OR，而不是 AND？


-- 1.6｜大表业务题
-- 输入表：orders
-- 字段：order_id, user_id, order_time, amount,
-- status, channel；order_time 为 YYYY-MM-DD HH:MM:SS 文本。
-- 运营要核查 2026-10-01 当天零点起至 2026-10-08 当天零点
-- 前的订单：状态为 paid，渠道属于 app 或 wechat，金额至
-- 少 300 元且小于 500 元。输出 order_id, user_id, amount
-- , order_time，不要求行序。
SELECT order_id, user_id, amount, order_time
FROM orders
WHERE order_time >='2026-10-01 00:00:00' 
    AND order_time < '2026-10-08 00:00:00'
    AND status = 'paid'
    AND (channel = 'app' OR channel = 'wechat')
    AND amount >= 300
    AND amount < 500;


-- 2.1｜示范｜金额最高的四笔订单
-- 输入表：s_orders
-- 需求：排除金额缺失的订单
-- ，按金额从大到小取前四笔；金额
-- 相同，订单号较小的在前。输出 order_id, amount。
SELECT order_id, amount
FROM s_orders
WHERE amount IS NOT NULL 
ORDER BY amount DESC, order_id ASC
LIMIT 4;



-- 2.2｜小表练习
-- 输入表：s_orders
-- 返回金额已知的订单中最便宜的三笔，金额升序、同金额按订
-- 单号升序。输出 order_id, amount。
SELECT order_id, amount
FROM s_orders
WHERE amount IS NOT NULL
ORDER BY amount ASC , order_id ASC
LIMIT 3;



-- 2.3｜小表练习
-- 输入表：s_orders
-- 返回订单表出现过的不同城市，只输出 city；缺失城市保留
-- 一行，不要求行序。
SELECT DISTINCT city 
FROM s_orders;




-- 2.4｜小表练习
-- 输入表：s_orders
-- 返回不同的“用户、订单城市”组合，输出 user_id, city，按
-- 用户号升序。不要把重复下单算成新的组合。
SELECT DISTINCT user_id, city
FROM s_orders
ORDER BY user_id ASC;




-- 2.5｜小表练习
-- 输入表：s_orders
-- 返回最近四笔 paid 订单，按订单日期降序，同日按订单号降
-- 序。输出 order_id, order_date, amount。
SELECT order_id, order_date, amount
FROM s_orders
WHERE status = 'paid' 
ORDER BY order_date DESC , order_id DESC
LIMIT 4;




-- 2.6｜大表业务题
-- 输入表：orders
-- 财务抽查状态为 paid 且金额已知的前十笔高额订单。按金额
-- 降序，同金额按订单号升序，输出 order_id, user_id,
-- amount。
SELECT order_id, user_id, amount
FROM orders
WHERE status = 'paid' AND amount IS NOT NULL
ORDER BY amount DESC , order_id ASC
LIMIT 10;
-- 3.1｜示范｜行数、已知金额数和用户数
-- 输入表：s_orders
-- 需求：只返回一行，依次输出总订单数 order_count、金额已
-- 知订单数 known_amount_count、不同下单用户数 user_count
-- 、已知金额合计 total_amount、已知金额均值 avg_amount、
-- 城市已知订单数 known_city_count、不同已知城市数
-- city_count。
SELECT count(*) as order_count,
    count(amount) as known_amount_count,
    count(DISTINCT user_id) as user_count,
    sum(amount) as total_amount,
    avg(amount) as avg_amount,
    count(city) as known_city_count,
    count(DISTINCT city) as city_count
FROM s_orders;




-- 3.2｜小表练习
-- 输入表：s_orders
-- 仅统计 paid 订单。返回一行：order_count（总笔数）、
-- known_amount_count（金额已知笔数）、city_count（不同的
-- 已知城市数）。
SELECT count(*) AS order_count,
    count(amount) AS known_amount_count,
    count(DISTINCT city) AS city_count
FROM s_orders
WHERE status ='paid' ;




-- 3.3｜小表练习
-- 输入表：s_orders
-- 统计上海订单的金额合计和已知金额均值，输出一行
-- total_amount, avg_amount。
SELECT sum(amount) as total_amount,
    avg(amount) as avg_amount
FROM s_orders
WHERE city ='上海';


-- 3.4｜小表练习
-- 输入表：s_orders
-- 只统计城市为成都的订单，输出一行：总笔数 order_count、
-- 金额已知笔数 known_amount_count、金额合计 total_amount
-- 、已知金额均值 avg_amount。保留数据库对缺失汇总值的原
-- 始表达。
SELECT count(*) as order_count,
    count(amount) as known_amount_count,
    sum(amount) as total_amount,
    avg(amount) as avg_amount
FROM s_orders
WHERE city ='成都' ;



-- 3.5｜小表练习
-- 输入表：s_orders
-- 只统计金额缺失的订单，输出一行：总笔数 order_count、金
-- 额已知笔数 known_amount_count、不同已知金额数
-- amount_count、金额合计 total_amount、已知金额均值
-- avg_amount。
SELECT count(*) as order_count,
    count(amount) as known_amount_count,
    count(DISTINCT amount) as amount_count,
    sum(amount) as total_amount,
    avg(amount) as avg_amount
FROM s_orders 
WHERE amount IS NULL;





-- 3.6｜大表业务题
-- 输入表：orders
-- 统计 2026-10-01 零点起至 2026-10-28 零点前的 paid 订单
-- ，输出一行：总笔数 order_count、金额已知笔数
-- known_amount_count、不同下单用户数 user_count、已知金
-- 额合计 total_amount、已知金额均值 avg_amount。
SELECT count(*) as order_count,
    count(amount) as known_amount_count,
    count(DISTINCT user_id) as user_count,
    sum(amount) as total_amount,
    avg(amount) as avg_amount
FROM orders
WHERE order_time >= '2026-10-01 00:00:00' AND order_time < '2026-10-28 00:00:00'
    AND status = 'paid';