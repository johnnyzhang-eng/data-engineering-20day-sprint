"""D1 合成数据；只读 practice.sqlite3 生成，按 rowid 排列。SQL NULL 对应 None。"""

S_ORDERS = [
    {'order_id': 101, 'user_id': 1, 'city': '上海', 'amount': 100, 'order_date': '2026-10-01', 'status': 'paid'},
    {'order_id': 102, 'user_id': 2, 'city': '北京', 'amount': 200, 'order_date': '2026-10-01', 'status': 'paid'},
    {'order_id': 103, 'user_id': 1, 'city': '上海', 'amount': 50, 'order_date': '2026-10-02', 'status': 'cancelled'},
    {'order_id': 104, 'user_id': 3, 'city': '深圳', 'amount': 100, 'order_date': '2026-10-03', 'status': 'paid'},
    {'order_id': 105, 'user_id': 4, 'city': None, 'amount': 150, 'order_date': '2026-10-03', 'status': 'paid'},
    {'order_id': 106, 'user_id': 2, 'city': '北京', 'amount': None, 'order_date': '2026-10-04', 'status': 'pending'},
    {'order_id': 107, 'user_id': 5, 'city': '杭州', 'amount': 0, 'order_date': '2026-10-04', 'status': 'paid'},
    {'order_id': 108, 'user_id': 6, 'city': '上海', 'amount': 300, 'order_date': '2026-10-05', 'status': 'refunded'},
    {'order_id': 109, 'user_id': 7, 'city': '武汉', 'amount': None, 'order_date': '2026-10-05', 'status': 'paid'},
    {'order_id': 110, 'user_id': 8, 'city': '深圳', 'amount': 200, 'order_date': '2026-10-06', 'status': 'paid'},
    {'order_id': 111, 'user_id': 9, 'city': None, 'amount': 100, 'order_date': '2026-10-06', 'status': 'cancelled'},
    {'order_id': 112, 'user_id': 99, 'city': '北京', 'amount': 50, 'order_date': '2026-10-07', 'status': 'paid'},
]

S_USERS = [
    {'user_id': 1, 'name': '小林', 'city': '上海', 'channel': 'app'},
    {'user_id': 2, 'name': '小周', 'city': '北京', 'channel': 'web'},
    {'user_id': 3, 'name': '阿青', 'city': '深圳', 'channel': 'app'},
    {'user_id': 4, 'name': '阿雨', 'city': None, 'channel': 'wechat'},
    {'user_id': 5, 'name': '阿明', 'city': '杭州', 'channel': 'web'},
    {'user_id': 6, 'name': '小陈', 'city': '上海', 'channel': 'app'},
    {'user_id': 7, 'name': '阿宁', 'city': '武汉', 'channel': None},
    {'user_id': 8, 'name': '小苏', 'city': '深圳', 'channel': 'wechat'},
    {'user_id': 9, 'name': '小方', 'city': '北京', 'channel': 'app'},
    {'user_id': 10, 'name': '小禾', 'city': '成都', 'channel': 'web'},
]

