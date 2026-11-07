# p01｜从 SQL 到 Python

约 60 分钟：读与试 20 分钟，复写示范 8 分钟，四题 22 分钟，闭卷小测 10 分钟。这里的代码是 AI 教材；你的模板保持空白，自己写出的代码才是作答。

## 为什么要写 Python

SQL 描述“要哪些行、算什么”；Python 让你逐条拿出记录，判断、累积，再交回结果。今天把 D1 的同一份数据换一种表达，不学数据库连接。`data.py` 是从练习库只读生成的静态数据：`S_ORDERS` 为 12 个订单字典组成的列表，`S_USERS` 为 10 个用户字典组成的列表；SQL 的 NULL 写作 Python 的 `None`。

VS Code 上下分栏：上面编辑 `answers.py`，下面放本讲义或 `data.py`；终端停在仓库根目录。系统 `python3` 足够，不需要安装包。

## 怎么写：先认识装数据的盒子

```python
amount = 100
city = "上海"
missing = None
paid = True
```

`=` 是赋值：让名字指向右边的值。这里依次是整数 `int`、文本 `str`、表示缺失的 `None`、布尔值 `bool`。真假写作 `True`、`False`，大小写固定。小数是 `float`，均值通常会得到小数。`None` 不是字符串 `"None"`，也不是 0。

```python
order = {"order_id": 101, "city": "上海", "amount": 100, "status": "paid"}
orders = [order]
print(order["city"])
print(orders[0]["amount"])
```

字典 `{}` 像一行数据，键是字段名，`order["city"]` 取该字段的值；键拼错会报 `KeyError`。列表 `[]` 像有顺序的一组行，`orders[0]` 取第一行，下标从 0 开始。字典里每组键值、列表里相邻元素要用英文逗号分开。上面两次打印分别显示 `上海` 和 `100`。空列表写 `[]`，空字典写 `{}`。

```python
ids = []
ids.append(101)
print(len(ids))
print(101 in ids)
```

`append` 在列表末尾加入一个值；`len` 数元素个数；`in` 判断是否包含，`not in` 判断是否不包含。这里显示 `1` 和 `True`。不要写 `ids = ids.append(101)`：`append` 修改列表，自己的返回值是 `None`。

## 循环、判断与累积

```python
count = 0
for order in orders:
    if order["status"] == "paid":
        count = count + 1
```

`for` 每轮把下一行绑定到 `order`；`if` 只在条件成立时执行其缩进里的语句。`count = count + 1` 先算旧值加 1，再保存新值。空列表使循环执行零次。`==` 比较是否相等，结果是真或假；不能把赋值 `=` 写到这个判断位置。`!=` 是不相等，`>=` 包含下限。

```python
amount = order["amount"]
if amount is not None and amount >= 100:
    print("金额已知且至少 100")
```

用 `is None` 判断缺失，`is not None` 判断非缺失；不要用 `is` 比较城市或金额是否相等。`and` 要求两边成立，`or` 任意一边成立即可。`and` 从左到右短路：左边不成立就不算右边，因此 `None` 不会拿去与数字比大小。`and` 优先于 `or`；混用时给业务条件加括号，如 `(city == "北京" or city == "深圳") and paid`，每边都写完整比较。别写 `city == "北京" or "深圳"`。

不要用 `if amount:` 表达“金额已知”：0 与 `None` 都会被视为假，但 0 必须参加合计和均值。Python 没有 SQL 的三值逻辑；例如 `None == None` 是 `True`，不能把 SQL 的 `NULL = NULL` 规则直接搬来。

## 函数把结果交出去

```python
def add_one(value):
    result = value + 1
    return result

number = add_one(4)
print(number)
```

`def` 定义函数；`value` 是形参，调用时的 `4` 是实参。函数体在调用时才执行。`return` 把结果交给调用者，并结束这次调用；`print` 只显示信息，它的返回值是 `None`。没有执行 `return` 的函数也返回 `None`。本课自测读取返回值，不读取打印内容。

`def`、`for`、`if` 行末都要英文冒号 `:`；下一层统一缩进 4 个空格，别混用 Tab。全角 `：`、`（`、`）`、弯引号不是对应的 Python 语法符号。注释以 `#` 开头；模板的 `pass` 是占位语句，作答时删掉并写自己的函数体。Python 通常不用行末分号。

## 题 1｜示范：筛选订单号

输入 `orders`（与 `S_ORDERS` 同结构，字段齐全，金额为整数或 None）。仅保留 `status == "paid"` 且金额已知且 `amount >= 100` 的订单，返回订单号列表。按输入出现顺序保留，不排序、不去重；空输入或无符合行返回 `[]`。不能改输入。

对照 SQL：`SELECT order_id FROM s_orders WHERE status = 'paid' AND amount >= 100`。SQL 没写 ORDER BY 时不保证顺序；本题的 Python 顺序是额外明确的要求。

```python
def paid_order_ids(orders):
    result = []
    for order in orders:
        amount = order["amount"]
        if order["status"] == "paid" and amount is not None and amount >= 100:
            result.append(order["order_id"])
    return result
```

逐行读：

1. 定义接收一个列表的函数，参数名 `orders` 可以接不同数据，不是写死 `S_ORDERS`。
2. 准备存结果的空列表，必须放在循环外。
3. 依次取出每一个订单字典。
4. 取金额，后面读起来更清楚。
5. 逐项检查状态、缺失、下限；漏掉任一条件都会改变结果。
6. 符合时追加订单号，注意是 `order_id` 字段，不是整个字典。
7. 循环全部结束后返回；此行与 `for` 同层，不能缩进到循环里。

复写后自测：`python3 tools/check_py.py p01 1`。本数据的正确返回值是 `[101, 102, 104, 105, 110]`。示范记 L3；后面自己做四题，不看私有答案。

## 题 2–5｜独立练习

共同约定：只使用传入参数，不改输入，不依赖固定行数。字段齐全，金额为整数或 None，状态为字符串，城市为字符串或 None。把下面的需求翻译成函数；模板上方也附有相同完整题面。

**2. `count_status(orders, status)`**：返回状态恰好等于参数 `status` 的订单笔数（整数）。只看状态；金额为 None 或 0 的符合行也计数。空输入或无符合行返回 0。对照 `COUNT(*) ... WHERE status = ...`；不是数所有判断的个数。Python 的 `len([True, False])` 为 2，它并不只数 True，与 SQLite 中 `COUNT(条件)` 的陷阱相似。

**3. `sum_known_amounts(orders)`**：不筛选城市或状态，返回所有已知金额的合计，0 也参与。空输入或金额全是 None 时返回 None，不是 0。否则返回整数；如果已知金额只有 0，应返回 0。对照 SQL `SUM(amount)`。思考：除了累计金额，还要怎样区分“没有已知金额”与“已知合计为零”？

**4. `mean_known_amounts(orders)`**：不筛选城市或状态，返回所有已知金额的均值，分母只数非 None 金额，0 计入分母。空输入或金额全是 None 时返回 None；否则返回数值，不要求四舍五入。对照 SQL `AVG(amount)`；除法用 `/`。不要用全表行数作分母。

**5. `unique_cities(orders)`**：返回去重的城市列表，按城市在输入中第一次出现的先后顺序；None 也保留一个，不跳过。空输入返回 `[]`，只含 None 返回 `[None]`。对照 `SELECT DISTINCT city` 的去重含义；SQL 没写 ORDER BY 不保证顺序，而本题明确首次出现顺序。用列表的 `in` / `not in` 就够了，不需要集合或排序。

## 自己检查与闭卷收尾

每题先自己预测边界，再写、保存、运行。看不懂报错先定位行号：英文标点 → 冒号 → 缩进 → 字段拼写 → 筛选条件。结果不对先自改两次，再请陪练；自测后自己改对仍算 L0，AI 提示按 L1–L3 记录。不要把“通过用例”写成“已掌握”。

```sh
python3 tools/check_py.py p01 3
python3 tools/check_py.py p01
```

检查器只报告失败类别和你的返回值，隐藏预期值。做完由陪练出 3 道闭卷小测，10 分钟，纸面作答，不运行、不用检查器。

## 核对资料

本课以本机 Python 3.14 为准。语法与行为核对自 Python 3.14 官方教程：[变量与列表](https://docs.python.org/3.14/tutorial/introduction.html)、[循环和函数](https://docs.python.org/3.14/tutorial/controlflow.html)、[数据结构](https://docs.python.org/3.14/tutorial/datastructures.html)、[真假值与比较](https://docs.python.org/3.14/library/stdtypes.html#truth-value-testing)。SQL 对照按本仓库 SQLite 练习口径，不能推成所有语言的共同规则。
