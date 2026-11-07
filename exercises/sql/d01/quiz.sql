-- database: ../data/practice.sqlite3
-- D1 收尾小测｜5 题，共 20 分钟
-- 闭卷：无 AI、无文档；不运行 SQL，不使用检查器。
-- 到时停笔并保存；保留交卷首稿，交卷后另记订正。
-- 金额单位：整数元。NULL 表示缺失；日期格式 YYYY-MM-DD。
-- 表结构：
-- s_orders(order_id, user_id, city, amount, order_date, status)
-- s_users(user_id, name, city, channel)

-- Q1｜筛选与缺失值
-- 返回订单号不小于 104、状态为 paid 或 pending，且满足
-- “金额缺失或城市缺失”的订单。
-- 输出 order_id, city, amount, status，按订单号升序。
-- BEGIN Q1
SELECT order_id, city, amount, status
FROM s_orders
WHERE order_id >= 104 and (status ='paid' or status ='pending')  
    and (city IS NULL or amount IS NULL)
ORDER BY order_id ASC;

-- END Q1


-- Q2｜排序与截取
-- 从金额已知、金额小于 200 且状态不是 cancelled 的订单中，
-- 取金额最高的两笔。输出 order_id, amount, order_date；
-- 金额降序，同金额按订单日期升序，再按订单号升序。
-- BEGIN Q2
SELECT order_id, amount, order_date
FROM s_orders
WHERE amount IS NOT NULL
    and amount < 200
    and status IS NOT 'cancelled'
ORDER BY amount ASC, order_id ASC;

-- END Q2


-- Q3｜组合去重
-- 只看城市已知、状态为 paid 或 pending 的订单，返回出现过的
-- 不同“城市、订单状态”组合。输出 city, status，按城市、状态均升序。
-- 同一城市不同状态分别保留，同一组合的多笔订单只留一行。
-- BEGIN Q3
SELECT DISTINCT city, status
FROM s_orders
WHERE status ='paid' and status ='pending'
ORDER BY city ASC, status ASC;

-- Q4｜筛选后聚合
-- 只统计 2026-10-01 至 2026-10-03（含两端）的 paid 订单，
-- 输出一行：order_count, known_amount_count, total_amount, avg_amount。
-- 另说明 AVG 的分母是什么（写在下方注释中）。
-- BEGIN Q4
SELECT count(*) as order_count, 
    count(amount IS NOT NULL) as known_amount_count, 
    sum(amount) as total_amount, 
    avg(amount) as avg_amount
FROM s_orders
WHERE order_date BETWEEN '2026-10-01 00:00:00' and '2026-10-03 00:00:00'
    and status ='paid' ;

-- END Q4
-- 我的解释：分母是amount之和，当然是paid，以及日期范围内


-- Q5｜NULL 与零
-- 返回 paid 订单中金额缺失或金额为零的订单，
-- 输出 order_id, user_id, amount，按订单号升序。
-- 另说明缺失和零的区别（写在下方注释中）。
-- BEGIN Q5
SELECT order_id, user_id, amount
FROM s_orders
WHERE status ='paid' 
    and (amount IS NULL or amount =0)
ORDER BY order_id ASC;
-- END Q5
-- 我的解释：null是缺失，0是知道是0
