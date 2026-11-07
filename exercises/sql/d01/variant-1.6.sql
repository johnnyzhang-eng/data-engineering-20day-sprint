-- database: ../data/practice.sqlite3
-- d01-1.6-v1｜L3 示范后的独立变式
-- 输入表：orders；合上原题示范后独立写。
-- 字段：order_id, user_id, order_time, amount, status, channel。
-- 时间：2026-10-08 00:00:00 起，至 2026-10-11 00:00:00 前。
-- 状态为 pending；渠道为 web 或 wechat。
-- 金额大于 100 元且不超过 300 元。
-- 输出 order_id, user_id, amount, order_time，不要求排序。
-- 本人作答：


SELECT order_id, user_id, amount, order_time
FROM orders
WHERE order_time >= '2026-10-08 00:00:00'
    AND order_time < '2026-10-11 00:00:00'
    AND status = 'pending' 
    AND (channel = 'web' OR channel = 'wechat')
    AND amount > 100 
    AND amount <= 300;
