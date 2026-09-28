#%%
import matplotlib.pyplot as plt
import numpy as np
import csv
from pathlib import Path

SCRIPT_DIR = Path(__file__).parent.resolve()
ROOT_DIR = SCRIPT_DIR.parent.parent
IMGS_DIR = f"{SCRIPT_DIR}/images"
RESULT_DIR = f"{ROOT_DIR}/2026-05-16-Verified-Result-For-Graduation-Thesis"
MAXSAT_BASE_DIR = f"{RESULT_DIR}/maxsat_baseline"
MAXSAT_ABLATION_DIR = f"{RESULT_DIR}/maxsat_ablation"
MAXSAT_DEFAULT_DIR = f"{RESULT_DIR}/maxsat_verify"

MS_BASE = "maxsat_ddd_ladder"
MS_SC = "MaxsatOnlyScl"
MS_PREC = "MaxsatOnlyPrec"
MS_DEF = "MaxsatSclDefault"

STEP = "finsteps123.csv"
ROUND = "infsteps180.csv"
CONT = "cont.csv"

VARIANTS = {
    "MS_Base": {
        "step": f"{MAXSAT_BASE_DIR}/{MS_BASE}_{STEP}",
        "round": f"{MAXSAT_BASE_DIR}/{MS_BASE}_{ROUND}",
        "cont": f"{MAXSAT_BASE_DIR}/{MS_BASE}_{CONT}",
    },
    "MS_SC": {
        "step": f"{MAXSAT_ABLATION_DIR}/{MS_SC}_{STEP}",
        "round": f"{MAXSAT_ABLATION_DIR}/{MS_SC}_{ROUND}",
        "cont": f"{MAXSAT_ABLATION_DIR}/{MS_SC}_{CONT}",
    },
    "MS_Prec": {
        "step": f"{MAXSAT_ABLATION_DIR}/{MS_PREC}_{STEP}",
        "round": f"{MAXSAT_ABLATION_DIR}/{MS_PREC}_{ROUND}",
        "cont": f"{MAXSAT_ABLATION_DIR}/{MS_PREC}_{CONT}",
    },
    "MS_Default": {
        "step": f"{MAXSAT_DEFAULT_DIR}/{MS_DEF}_{STEP}",
        "round": f"{MAXSAT_DEFAULT_DIR}/{MS_DEF}_{ROUND}",
        "cont": f"{MAXSAT_DEFAULT_DIR}/{MS_DEF}_{CONT}",
    },
}

# tính thời gian giải trung bình trên 2 nhóm bài khó: Track và Station
GROUPS = {
    "Track": lambda name: name.startswith("track"),
    "Station": lambda name: name.startswith("station"),
}

def load_csv(path: Path) -> dict:
    """đọc CSV và trả về dict với key là tên instance"""
    with open(f"{path}", newline="", encoding="utf-8") as file:
        return {row["name"]: row for row in csv.DictReader(file)}

# print(load_csv(f"{MAXSAT_BASE_DIR}/{MS_BASE}_{STEP}"))

def get_instances(data_by_variant, group_filter):
    """Lấy các instance thỏa mãn chạy thành công ở cả 4 cấu hình"""
    common = None
    for data in data_by_variant.values():
        solved = {
            name for name, row in data.items() if group_filter(name) and row.get("status") == "ok"
        }
        common = solved if common is None else common & solved
    return sorted(common or [])

def average_time_ms(data, instances):
    """Cột total_time trong CSV tính bằng giây, đổi sang mili-giây."""
    times = [float(data[name]["total_time"]) * 1000 for name in instances]
    return sum(times) / len(times) if times else 0


def calculate_averages():
    results = {}
    for objective in ("step", "round", "cont"):
        data_by_variant = {
            variant: load_csv(path_by_objective[objective]) for variant, path_by_objective in VARIANTS.items()
        }
        results[objective] = {}
        for group, group_filter in GROUPS.items():
            instances = get_instances(data_by_variant, group_filter)
            results[objective][group] = {
                variant: average_time_ms(data, instances) for variant, data in data_by_variant.items()
            }
    return results

def plot_results(results):
    Path(IMGS_DIR).mkdir(exist_ok=True)
    objectives = ["step", "round", "cont"]
    variants = list(VARIANTS)
    x = np.arange(len(objectives))
    width = 0.1

    fig, axes = plt.subplots(1, 2, figsize=(12, 5), sharey=True)
    for axis, group in zip(axes, GROUPS):
        for index, variant in enumerate(variants):
            values = [results[obj][group][variant] for obj in objectives]
            axis.bar(x + (index - 1.5) * width, values, width, label=variant)
        axis.set_title(group)
        axis.set_xticks(x)
        axis.set_xticklabels(["Step", "Round", "Continuous"])
        axis.set_ylabel("Thời gian giải trung bình (ms, log scale)")
        axis.set_yscale("log")
        axis.grid(axis="y", alpha=0.3)
        axis.set_axisbelow(True)

    axes[1].legend(fontsize=8)
    fig.tight_layout()
    output = Path(IMGS_DIR) / "bai3_average_solve_time.png"
    fig.savefig(output, dpi=200, bbox_inches="tight")
    plt.close(fig)
    print(f"Đã lưu biểu đồ: {output}")


def plot_clause_comparison():
    """So sánh số clause của SC và Pairwise với clique size n = 2..12"""
    clique_sizes = np.arange(2, 13)
    pairwise_clauses = clique_sizes * (clique_sizes - 1) // 2
    sc_clauses = 3 * clique_sizes - 4

    fig, axis = plt.subplots(figsize=(8, 5))
    axis.plot(
        clique_sizes, pairwise_clauses, marker="o", linewidth=2,
        label="Pairwise (PW)", color="#777777"
    )
    axis.plot(
        clique_sizes, sc_clauses, marker="o", linewidth=2,
        label="Sequential Counter (SC)", color="#2ca02c"
    )

    axis.set_xlabel("Kích thước nhóm xung đột n")
    axis.set_ylabel("Số clause")
    axis.set_xticks(clique_sizes)
    axis.set_title("So sánh số clause giữa SC và Pairwise")
    axis.grid(True, alpha=0.3)
    axis.legend()
    fig.tight_layout()

    output = Path(IMGS_DIR) / "bai3_clause_sc_vs_pw.png"
    fig.savefig(output, dpi=200, bbox_inches="tight")
    plt.close(fig)
    print(f"Đã lưu biểu đồ clause: {output}")

if __name__ == "__main__":
    results = calculate_averages()
    plot_results(results)
    plot_clause_comparison()

#%%