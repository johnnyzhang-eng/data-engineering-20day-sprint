# p01 作答模板：示范也请自己复写。只把自己的代码写在函数体内。
# 数据参考：同目录 data.py 的 S_ORDERS / S_USERS；自测从仓库根目录运行。

# 1（示范）输入 orders：与 S_ORDERS 同结构的订单字典列表，字段齐全，金额为整数或 None。
# 仅保留 status == "paid"、amount 非 None 且 amount >= 100 的订单，返回 order_id 列表。
# 按输入顺序，不排序、不去重；空输入或没有符合行返回 []；不能改输入。
def paid_order_ids(orders):
    pass


# 2 输入 orders（同 S_ORDERS 结构）和 status（状态字符串）。
# 返回状态恰好等于 status 的订单笔数（整数）；只看状态，金额 None 和 0 的符合行也计数。
# 空输入或无符合行返回 0；不改输入，不写死 S_ORDERS。
def count_status(orders, status):
    pass


# 3 输入 orders（同 S_ORDERS 结构，金额为整数或 None）；不筛选城市或状态。
# 返回所有非 None 金额的整数合计，0 参与；空输入或金额全是 None 返回 None，而不是 0。
# 有已知金额且合计为零则返回 0；不改输入，不写死 S_ORDERS。
def sum_known_amounts(orders):
    pass


# 4 输入 orders（同 S_ORDERS 结构，金额为整数或 None）；不筛选城市或状态。
# 返回非 None 金额的均值（数值，不要求四舍五入）；分母仅数非 None，金额 0 也计入分母。
# 空输入或金额全是 None 返回 None；不改输入，不写死 S_ORDERS。
def mean_known_amounts(orders):
    pass


# 5 输入 orders（同 S_ORDERS 结构，城市为字符串或 None）。返回去重的城市列表。
# 按城市第一次在输入出现的顺序；None 保留一个，不跳过，不排序。
# 空输入返回 []，只含 None 返回 [None]；不改输入，不写死 S_ORDERS。
def unique_cities(orders):
    pass
