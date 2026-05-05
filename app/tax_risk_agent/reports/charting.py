"""诊断报告图表渲染模块。

本模块负责把税务风险诊断过程中计算出的企业指标和行业基准转换为图片图表。
当前实现生成一张关键税务指标对比柱状图，供 Markdown 报告引用。
"""

from pathlib import Path  # 导入路径类型，用于创建输出目录和返回图表文件路径。


def render_metric_chart(metrics: dict[str, float], benchmarks: dict[str, dict], output_dir: Path) -> Path | None:
    """渲染企业关键税务指标与行业分位基准的对比图。

    Args:
        metrics: 企业侧已计算出的指标字典，例如差旅费率、税负率、毛利率。
        benchmarks: 行业基准字典，按指标名保存 p50、p75、p90 等分位值。
        output_dir: 图表输出目录。

    Returns:
        成功时返回生成的 PNG 文件路径；如果当前环境缺少 matplotlib，则返回 None。
    """
    # 流程 1：确保图表输出目录存在，避免保存图片时因为目录缺失失败。
    output_dir.mkdir(parents=True, exist_ok=True)

    # 流程 2：固定生成文件名，报告生成器可以稳定引用该图表路径。
    path = output_dir / "tax_metric_comparison.png"

    # 流程 3：延迟导入 matplotlib；如果运行环境没有图表依赖，则跳过图表生成。
    try:
        import matplotlib.pyplot as plt
    except Exception:
        return None

    # 流程 4：选择需要展示的关键指标，并分别取企业值、行业 P75 值和中文显示标签。
    names = ["travel_expense_ratio", "vat_burden_rate", "gross_margin"]
    values = [metrics.get(name, 0.0) for name in names]
    p75 = [benchmarks.get(name, {}).get("p75", 0.0) for name in names]
    labels = ["差旅费率", "税负率", "毛利率"]

    # 流程 5：创建柱状图画布，并把企业指标和行业 P75 画成并列柱，便于横向比较。
    fig, ax = plt.subplots(figsize=(8, 4.5))
    x_positions = range(len(names))
    ax.bar([x - 0.18 for x in x_positions], values, width=0.36, label="企业")
    ax.bar([x + 0.18 for x in x_positions], p75, width=0.36, label="行业P75")

    # 流程 6：设置坐标轴、标题和图例，让图表在报告中能独立表达含义。
    ax.set_xticks(list(x_positions), labels)
    ax.set_ylabel("Ratio")
    ax.set_title("企业关键税务指标与行业分位对比")
    ax.legend()

    # 流程 7：自动调整布局后保存为 PNG，并关闭画布释放资源。
    fig.tight_layout()
    fig.savefig(path, dpi=160)
    plt.close(fig)

    # 输出：返回图表路径，供诊断结果和报告生成器引用。
    return path
