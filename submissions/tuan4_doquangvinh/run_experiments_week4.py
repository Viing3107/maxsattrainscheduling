import csv
import time
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from pathlib import Path
from pysat.formula import CNF
from pysat.solvers import Cadical153

from bai1_scl_precedence import (
    direct_precedence_clauses,
    encode_scl_precedence,
    generate_time_points,
)
from bai2_bruteforce_checker import run_checker

CUR_URL = Path(__file__).parent.resolve()

def measure_cnf(clauses):
    """Đo thống kê kích thước CNF và hiệu năng unit propagation của solver."""
    cnf = CNF(from_clauses=clauses)

    t0 = time.perf_counter()
    with Cadical153(bootstrap_with=cnf.clauses) as solver:
        solver.solve()
        stats = solver.accum_stats()
    elapsed = time.perf_counter() - t0

    return {
        "num_vars": cnf.nv,
        "num_clauses": len(cnf.clauses),
        "num_literals": sum(len(c) for c in cnf.clauses),
        "propagations": stats.get("propagations", 0),
        "conflicts": stats.get("conflicts", 0),
        "decisions": stats.get("decisions", 0),
        "solve_time_s": round(elapsed, 6),
    }

def build_cnf_pair(n, m, l_r=None):
    """ 
    Xây dựng bộ mệnh đề Direct và SCL cho 1 cặp ga r -> q. Nếu l_r=None: chọn l_r = step * m / 2 sao cho mỗi interval p của ga r bị chặn ~m/2 interval của ga q -> Direct thể hiện đúng tăng trưởng O(n x m) để so sánh với SCL tuyến tính O(m).
    """
    step = 10
    if l_r is None:
        l_r = step * m // 2
    x_r = list(range(1, n + 1))
    x_q = list(range(n + 1, n + m + 1))
    h_r = generate_time_points(n, step=step)
    h_q = generate_time_points(m, step=step)

    direct = direct_precedence_clauses(x_r, x_q, h_r, h_q, l_r)
    scl, _ = encode_scl_precedence(x_r, x_q, h_r, h_q, l_r, next_var=n + m + 1)
    return direct, scl

def run_benchmark():
    """Quét 12 cấu hình m x n, đo cả Direct lẫn SCL, ghi CSV."""
    rows = []
    for m in [8, 16, 32, 64]:
        for n in [4, 8, 16]:
            direct, scl = build_cnf_pair(n, m)
            for method, clauses in [("Direct", direct), ("SCL", scl)]:
                stats = measure_cnf(clauses)
                row = {"m": m, "n": n, "method": method, **stats}
                rows.append(row)
                print(
                    f"  m={m:>2}, n={n:>2} | {method:>6}"
                    f" | vars={stats['num_vars']:>3} | clauses={stats['num_clauses']:>4}"
                    f" | lits={stats['num_literals']:>5} | props={stats['propagations']:>7}"
                    f" | conflicts={stats['conflicts']:>5} | time={stats['solve_time_s']:.4f}s"
                )

    csv_path = CUR_URL / "experiment_results.csv"
    with open(csv_path, "w", newline="", encoding="UTF-8") as f:
        writer = csv.DictWriter(f, fieldnames=list(rows[0].keys()))
        writer.writeheader()
        writer.writerows(rows)
    print(f"\n=> Đã lưu kết quả vào {csv_path}\n")
    return rows

def plot_charts(rows):
    images_dir = CUR_URL / "images"
    images_dir.mkdir(exist_ok=True)

    ms = sorted({r["m"] for r in rows})
    ns = sorted({r["n"] for r in rows})

    charts = [
        ("num_vars", "Số biến CNF", "cnf_variables_comparison.png"),
        ("num_clauses", "Số mệnh đề CNF", "cnf_clauses_comparison.png"),
        ("num_literals", "Tổng số Literals", "cnf_literals_comparison.png")
    ]

    for metric, ylabel, filename in charts:
        fig, ax = plt.subplots(figsize=(8, 5))
        for method, color, ls in [("Direct", "tab:red", "-"), ("SCL", "tab:blue", "--")]:
            for n, marker in zip(ns, ["o", "s", "^"]):
                vals = [
                    next(r[metric] for r in rows if r["m"] == m and r["n"] == n and r["method"] == method)
                    for m in ms
                ]
                ax.plot(ms, vals, marker=marker, color=color, linestyle=ls, label=f"{method} (n={n})")
        ax.set_xlabel("Số interval ga sau m")
        ax.set_ylabel(ylabel)
        ax.set_title(f"{ylabel}: Direct (O(n x m)) vs SCL (O(m))")
        ax.set_xticks(ms)
        ax.grid(alpha=0.25)
        ax.legend(fontsize=8)
        fig.tight_layout()
        out_path = images_dir / filename
        fig.savefig(out_path, dpi=150)
        plt.close(fig)
        print(f"  Đã lưu {out_path}")

if __name__ == "__main__":
    run_checker()
    rows = run_benchmark()
    plot_charts(rows)