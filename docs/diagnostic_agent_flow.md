# diagnostic_agent.py 执行逻辑流程图

对应文件：

```text
app/tax_risk_agent/agent/diagnostic_agent.py
```

## Mermaid 流程图

```mermaid
flowchart TD
    A["调用 TaxRiskDiagnosticAgent.run(request)"] --> B["初始化 trace / findings / chart_paths"]
    B --> C["读取企业财务数据 _load_financial"]
    C --> D{"是否找到财务数据？"}

    D -->|"否"| E["返回 DATA_MISSING 风险"]
    E --> F["needs_human_review = true"]

    D -->|"是"| G["调用 MetricTool.calculate 计算财务指标"]
    G --> H["查询行业基准 _load_benchmarks"]
    H --> I["调用 RuleRetrievalTool 召回候选税务规则"]

    I --> J["遍历 risk_scenarios 风险场景"]
    J --> K["生成当前风险场景假设"]
    K --> L["调用 _evaluate_scenario"]

    L --> M{"指标是否存在？"}
    M -->|"否"| N["生成 review_required：缺少指标"]
    M -->|"是"| O["生成指标证据 Evidence"]

    O --> P{"行业基准是否存在？"}
    P -->|"否"| Q["追加规则证据，生成 review_required"]
    P -->|"是"| R["生成行业基准证据 Evidence"]

    R --> S{"指标是否触发阈值条件？"}
    S -->|"否"| T["当前风险场景不生成 finding"]
    S -->|"是"| U{"是否需要查询发票明细？"}

    U -->|"是"| V["调用 _invoice_concentration_evidence 查询发票对手方集中度"]
    U -->|"否"| W["跳过发票明细查询"]
    V --> X["追加发票证据"]
    W --> Y["匹配税务规则 _match_rule"]
    X --> Y

    Y --> Z{"是否匹配到规则？"}
    Z -->|"是"| AA["追加规则证据"]
    Z -->|"否"| AB["继续判断是否需要交叉验证"]
    AA --> AB

    AB --> AC{"是否配置 cross_check？"}
    AC -->|"否"| AD["生成 RiskFinding"]
    AC -->|"是"| AE["执行交叉验证"]

    AE --> AF{"交叉验证是否支持风险成立？"}
    AF -->|"否"| AG["当前风险场景不生成 finding"]
    AF -->|"是"| AH["追加交叉验证证据"]
    AH --> AD

    AD --> AI["加入 findings"]
    N --> AI
    Q --> AI
    T --> AJ["继续下一个风险场景"]
    AG --> AJ
    AI --> AJ
    AJ --> J

    J --> AK["所有风险场景扫描完成"]
    AK --> AL["调用 _surface_unhandled_rules 处理未建模但被召回的规则"]
    AL --> AM{"findings 是否为空？"}

    AM -->|"是"| AN["生成 NO_HIGH_CONFIDENCE 人工复核结论"]
    AM -->|"否"| AO["进入报告生成准备"]

    AN --> AO
    AO --> AP["可选生成指标图表 render_metric_chart"]
    AP --> AQ["调用 LLMClient.summarize_findings 生成摘要"]
    AQ --> AR["组装 DiagnosticResult"]
    AR --> AS["ReportGenerator.render 生成 Markdown 报告"]
    AS --> AT["返回 DiagnosticResult"]
```

## 简化理解

```text
run(request)
  ↓
读财务数据
  ↓
算指标
  ↓
查行业基准
  ↓
查规则库
  ↓
逐个风险场景评估
  ↓
证据充分：生成风险结论
证据不足：生成人工复核
  ↓
处理未覆盖规则
  ↓
生成摘要和报告
  ↓
返回诊断结果
```

## 核心设计

`diagnostic_agent.py` 不再只硬编码某几个风险，而是通过 `RiskScenario` 风险场景配置驱动诊断。

每个风险场景统一走：

```text
指标证据
  ↓
行业基准
  ↓
明细查询
  ↓
规则检索
  ↓
交叉验证
  ↓
结论 / 人工复核
```

