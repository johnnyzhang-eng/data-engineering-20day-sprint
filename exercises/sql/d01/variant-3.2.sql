-- database: ../data/practice.sqlite3
-- d01-3.2-v1｜计数的换条件变式
-- 输入表：s_orders；合上 3.2 示范后独立写。
-- 仅统计 cancelled（已取消）订单，返回一行，依次输出：
-- order_count：订单总笔数；
-- known_amount_count：金额已知笔数；
-- city_count：不同的已知城市数。
-- 本人作答：
SELECT count(*) as order_count,
    count(amount) as known_amount_count,
    count(DISTINCT city) as city_count
FROM s_orders
WHERE status ='cancelled' ;


