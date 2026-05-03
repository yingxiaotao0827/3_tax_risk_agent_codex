from pathlib import Path


def render_metric_chart(metrics: dict[str, float], benchmarks: dict[str, dict], output_dir: Path) -> Path | None:
    output_dir.mkdir(parents=True, exist_ok=True)
    path = output_dir / "tax_metric_comparison.png"
    try:
        import matplotlib.pyplot as plt
    except Exception:
        return None

    names = ["travel_expense_ratio", "vat_burden_rate", "gross_margin"]
    values = [metrics.get(name, 0.0) for name in names]
    p75 = [benchmarks.get(name, {}).get("p75", 0.0) for name in names]
    labels = ["差旅费率", "税负率", "毛利率"]

    fig, ax = plt.subplots(figsize=(8, 4.5))
    x_positions = range(len(names))
    ax.bar([x - 0.18 for x in x_positions], values, width=0.36, label="企业")
    ax.bar([x + 0.18 for x in x_positions], p75, width=0.36, label="行业P75")
    ax.set_xticks(list(x_positions), labels)
    ax.set_ylabel("Ratio")
    ax.set_title("企业关键税务指标与行业分位对比")
    ax.legend()
    fig.tight_layout()
    fig.savefig(path, dpi=160)
    plt.close(fig)
    return path

