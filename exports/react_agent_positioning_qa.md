# 当前项目还能叫 ReAct Agent 吗？

## 用户问题

当前项目没有真正的多轮交互输入机制，那这个项目还能叫做 ReAct Agent 吗？是 ReAct 推理过程吗？

## 回答

可以叫 **ReAct 风格的 Agent / 基于 ReAct 思想的风险诊断 Agent**，但如果严格说，它现在还不是那种“开放式多轮 ReAct Agent Executor”。

你的判断点很关键：**没有真正的多轮交互输入机制，不等于完全不是 ReAct；但它不是完整开放式 ReAct。**

## 结论

当前项目更准确的定位是：

> 一个受控的、业务状态机驱动的 ReAct-style Agent。

或者说：

> 基于 ReAct 思想实现的税务风险诊断状态机。

不建议说成：

> 完整自主开放式 ReAct Agent。

## 为什么它仍然有 ReAct 特征

ReAct 的核心不是一定要无限多轮聊天，而是把推理和行动交替起来：

```text
Reasoning / Thought
Action
Observation
再基于 Observation 更新判断
```

你的项目里确实有这个链路：

```text
Thought：
生成风险假设，比如差旅费占比可能异常

Action：
调用 Python 指标工具计算差旅费率

Observation：
得到差旅费率 8.17%

Action：
查询行业 P90

Observation：
行业 P90 = 5.50%

Action：
查询发票对手方集中度

Observation：
上海捷旅服务有限公司两张发票，金额 64 万

Action：
检索税务规则

Observation：
召回差旅费异常税务规则

Reasoning：
证据充分，形成高风险结论
```

所以它具备 ReAct 的关键结构：

```text
推理 + 工具调用 + 观察结果 + 再推理
```

这就是 ReAct 思想。

## 为什么它不是完整开放式 ReAct

完整开放式 ReAct 通常是这样：

```text
LLM 自己决定下一步要不要调用工具
LLM 自己决定调用哪个工具
LLM 自己根据 Observation 决定是否继续
直到达到 stop condition
```

比如：

```text
Thought: 差旅费偏高，我需要查行业基准
Action: query_sql(...)
Observation: P90 = 5.50%

Thought: 还需要查发票对手方
Action: query_sql(...)
Observation: 对手方集中

Thought: 需要查税务规则
Action: retrieve_rules(...)
Observation: 召回规则

Thought: 证据充分，可以结论
Final Answer: ...
```

而你现在项目里：

```text
工具调用顺序主要由状态机和风险场景配置决定
LLM 没有完全自主选择每一步工具
没有开放式循环让 LLM 自己决定下一步
```

所以严格讲，它是：

```text
规则约束下的 ReAct-style workflow
```

不是：

```text
LLM 自主驱动的 ReAct loop
```

## 这是不是缺点？

不是，反而在税务风控场景里是优点。

因为税务风险诊断属于高风险业务，不适合让 LLM 完全自由行动。

如果完全开放式 ReAct，可能出现：

```text
乱写 SQL
遗漏关键证据
跳过复核步骤
过度下结论
工具调用成本不可控
推理过程不可审计
```

所以在真实企业里，更合理的是：

```text
用状态机约束 Agent
用工具保证证据真实性
用规则库提供判断依据
用人工复核处理证据不足
```

这比“让 LLM 自由跑”更适合生产环境。

## 项目中最准确的说法

View时建议这样说：

> 我这个项目不是开放式无限循环的 ReAct Agent，而是一个受控 ReAct-style 税务诊断 Agent。它保留了 ReAct 的核心思想：先生成风险假设，再调用 SQL、Python 指标计算和规则检索工具获取 Observation，然后基于工具返回的证据更新判断并生成结论。不同的是，我没有让 LLM 完全自由决定工具调用顺序，而是用业务状态机和风险场景配置约束流程，保证税务风控场景下的可控性、可审计性和稳定性。

## 如果想升级成更标准的 ReAct Agent

需要加一个真正的 ReAct loop：

```python
while not done:
    thought = llm.generate_thought(context)
    action = llm.select_tool(thought, available_tools)
    observation = tool.run(action.input)
    memory.add(thought, action, observation)
    done = llm.should_finish(memory)
```

但要注意，生产里也不能完全放开，最好加约束：

```text
工具白名单
SQL 只读
最大工具调用次数
必须检查证据充分性
必须输出结构化 JSON
证据不足必须 review_required
```

也就是说，升级方向是：

```text
受控 ReAct 状态机
+
LLM 动态选择工具
+
预算和安全约束
```

## 更合理的项目描述

原来：

> 基于 ReAct 的风险推理：设计税务稽查 Agent，基于 ReAct 框架让 Agent 自主思考。

建议改成：

> 基于 ReAct 思想的受控风险推理：设计税务稽查 Agent 状态机，让 Agent 按 Thought-Action-Observation 的方式生成风险假设、调用 SQL/指标计算/规则检索工具补充证据，并在证据不足时转人工复核。

## 一句话总结

> 当前项目可以称为 ReAct-style Agent，因为它具备 Thought-Action-Observation 的推理和工具调用链路；但它不是完全开放式 ReAct Agent。更准确的说法是：基于 ReAct 思想的受控税务风险诊断 Agent 状态机。
