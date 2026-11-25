# Data Engineering Zoomcamp 与学习地图的对照

核对日期：2026-11-25。以 [Zoomcamp 课程目录和先修要求](https://github.com/DataTalksClub/data-engineering-zoomcamp/blob/813d2774083186d0c9705c920deaf3e6e1693335/README.md)和[结课项目评分说明](https://github.com/DataTalksClub/data-engineering-zoomcamp/blob/813d2774083186d0c9705c920deaf3e6e1693335/projects/README.md)为准。本页是选材建议和验收设计，关联 Issue #3 的 M04、M05、M06、M07、M08。尚未完成课程节选和项目建设。

## 哪些可以直接参考

| 要学的工作 | Zoomcamp 可复用的部分 | 在学习地图中怎么用 |
| --- | --- | --- |
| 数据怎样进入系统 | 数据摄取 workshop、容器和 PostgreSQL 示例 | 先在本地读文件或 API、存下原始数据，再练增量。熟悉基础指令后再引入容器 |
| 怎样让处理自动发生 | 编排模块、Kestra 示例 | 先解释依赖、任务失败、重跑、回填。具体调度器按目标岗位与项目需要选择 |
| 怎样从仓库产出指标 | BigQuery 仓库模块、dbt/DuckDB 的建模和测试 | 读分区、聚簇、转换与质量测试的对应章节，接到现有订单表粒度与数仓分层 |
| 数据变大或需要实时怎么办 | Spark 批处理和 JOIN/GroupBy 内部机制、Kafka 与 schema | 先完成本地批处理。有目标 JD 再选 Spark 性能或流处理加深 |
| 怎样交一个别人能跑的项目 | 结课项目的需求说明、从摄取到分析结果、复现说明和同伴评审 | 用评分表查是否缺环。首次本地练习可验证核心工程机制。若走官方项目评分，还要满足当期云、输出和同伴评审规则 |

## 结合本项目还要补什么

1. **零基础到能跟课。** Zoomcamp 假设会一些基本编程和 SQL。用 [Sprint D1](../days/d01.md)、[D2](../days/d02.md)、[D3](../days/d03.md)以及 [Python p01](../../exercises/python/p01/lesson.md)把 SQL、命令行和 Python 小练习接起来。左边 Kimi 讲解，右边 VS Code 独立运行。入门验收是能查一张表、预测 JOIN 行数、用 Python 读取小文件并观察结果。
2. **目标岗位和面试。** 用 [岗位原文](../../research/jd/jd-list.jsonl)和[面经统计](../../research/mianjing-stats.md)补窗口函数、数仓分层、粒度、数据倾斜、项目解释等深度。J4-01 明确写 SQL 窗口/聚合/关联和数仓分层。J4-03 的 Java/JVM 是引擎研发岗位要求，作为该方向分支处理。平台和组件深度依据岗位逐项决定，历史样本不代表当前市场。维度建模可用 [Kimball 四步法](https://www.kimballgroup.com/data-warehouse-business-intelligence-resources/kimball-techniques/dimensional-modeling-techniques/four-4-step-design-process/)及[现有粒度讲义](../notes/m3-02-fact-dim.md)打通业务与表设计。
3. **通过故障验证项目。** 借官方项目信息组织文件、流程、输出和复现说明。项目自定义增加重复订单、迟到退款、半途失败、同一批重跑与必要时的补数。先冻结逐日、逐订单预期，再对照初跑、失败恢复和重跑后的实际状态。先靠合成数据本地跑通这一最小项目，再看岗位决定是否加调度器或部署。参考 [Airflow 创建可重试任务的实践](https://airflow.apache.org/docs/apache-airflow/stable/best-practices.html#creating-a-task)。
4. **AI 发展的理解与可靠用模。** 用原论文、[CS50 AI](https://cs50.harvard.edu/ai/)和[工程评估资料](https://www.anthropic.com/research/demystifying-evals-for-ai-agents)另串搜索、学习、LLM 到 agent 的历史与方法。让模型参与写查询或排错，每次保留独立预期、反例、工具执行与结果比较。学习者独立表现另记。

达标要有三件能检查的东西：一份目标岗位逐条能力覆盖表，一项别人能复跑且能处理失败的项目，一次不用 AI 帮忙的变式练习和项目讲解。

## 是否参加下一期

[官方课程 README](https://github.com/DataTalksClub/data-engineering-zoomcamp#how-to-take-the-course)列下一期为 **2027 年 1 月**。截至本次核对，[正式报名页](https://courses.datatalks.club/register/de-zoomcamp/)说明会在新一届宣布时通知，[2027 届课程目录](https://github.com/DataTalksClub/data-engineering-zoomcamp/blob/813d2774083186d0c9705c920deaf3e6e1693335/cohorts/2027/README.md)也将日程和作业标为草稿。[开发环境](https://dev.courses.datatalks.club/)出现的 1 月 18 日可作为待核线索，正式日期听主办方公布。

公开课程可随时自学。想要有截止日期的作业、同伴评审和证书机会，可以参加 cohort。课程视频为录播。同伴评审和证书规则以当期正式说明为准。建议现在继续 SQL/Python 与本地项目基础，开课后再根据投入时间决定是否参加完整 cohort。

## 逐章核对与个人中文化记录

已按固定提交 813d277 核对七模块的 88 个单元，各章的目录和项目原文仍作课程基准。个人中文索引、可离线阅读的配套导读与第一节自编 SQL 练习保留在本地。课程汉化并未全部完成。

主课已有 AI 内容：[Kestra 编排中的上下文工程、Copilot 与 RAG](https://github.com/DataTalksClub/data-engineering-zoomcamp/blob/813d2774083186d0c9705c920deaf3e6e1693335/02-workflow-orchestration/README.md#25-using-ai-for-data-engineering-in-kestra)、[Bruin MCP 与 agent](https://github.com/DataTalksClub/data-engineering-zoomcamp/blob/813d2774083186d0c9705c920deaf3e6e1693335/05-data-platforms/04-bruin-mcp.md)，以及 [dlt 摄取 workshop](https://github.com/DataTalksClub/data-engineering-zoomcamp/blob/813d2774083186d0c9705c920deaf3e6e1693335/cohorts/2026/workshops/dlt.md)。这些可直接复用。完整补课分为 AI 历史与模型原理、独立构建与评估 LLM 应用、验证 AI 辅助开发三个问题。应用参考 [LLM Zoomcamp](https://github.com/DataTalksClub/llm-zoomcamp)，开发流程参考 [AI Dev Tools Zoomcamp](https://github.com/DataTalksClub/ai-dev-tools-zoomcamp)。
