#%%
from typing import Callable
import random
import time

from pysat.formula import CNF
from pysat.solvers import Cadical153
from pathlib import Path
import matplotlib.pyplot as plt
from matplotlib.patches import Patch

SCRIPT_DIR = Path(__file__).parent.resolve()
print(SCRIPT_DIR)

counter = 1
def newVar() -> int:
    global counter
    var = counter
    counter += 1
    return var

def pw_amo(cnf: CNF, lits: list) -> int:
    n = len(lits)
    if n <= 1: return 0
    for i in range(n):
        for j in range(i + 1, n):
            cnf.append([-lits[i], -lits[j]])
    return len(cnf.clauses)

def sc_amo(cnf: CNF, lits: list):
    n = len(lits)
    if n <= 1: return 0
    s = [newVar() for _ in range(n - 1)]
    cnf.append([-lits[0], s[0]])
    for i in range(1, n - 1):
        cnf.append([-lits[i], s[i]])
        cnf.append([-s[i - 1], s[i]])
        cnf.append([-s[i - 1], -lits[i]])
    cnf.append([-s[n - 2], -lits[n - 1]])
    return len(cnf.clauses)

def measure(build_fn: Callable, n: int, reps: int = 200):
    records = []
    for _ in range(reps):
        cnf = CNF()
        lits = [newVar() for _ in range(n)]
        build_fn(cnf, lits)
        idx = random.randint(0, n - 1)
        cnf.append([lits[idx]])  # unit: 1 bien = True
        t0 = time.perf_counter()
        s = Cadical153(bootstrap_with=cnf)
        s.solve()
        elapsed_ms = (time.perf_counter() - t0) * 1000
        stats = s.accum_stats()
        records.append({
            "time_ms": elapsed_ms,
            "conflicts": stats.get("conflicts", 0),
            "decisions": stats.get("decisions", 0),
            "propagations": stats.get("propagations", 0),
            "encoding": build_fn.__name__,
            "n": n,
        })
        s.delete()
    return records

def plot_clause_counts():
    sizes = list(range(2, 21))
    pairwise_counts = [n * (n - 1) // 2 for n in sizes]
    sc_counts = [3 * n - 4 for n in sizes]

    plt.figure(figsize=(7, 4.5))
    plt.plot(sizes, pairwise_counts, marker="o", label="Pairwise")
    plt.plot(sizes, sc_counts, marker="o", label="Sequential Counter")
    plt.axvline(6, color="0.45", linestyle="--", label=r"$\theta = 6$")
    plt.xlabel("Số biến (n)")
    plt.ylabel("Số mệnh đề")
    plt.title("Số mệnh đề mã hóa AMO theo lý thuyết")
    plt.xticks(sizes)
    plt.grid(alpha=0.25)
    plt.legend()
    plt.tight_layout()
    plt.savefig(f"{SCRIPT_DIR}/clause_count_comparison.pdf")
    plt.close()

def plot_runtime(records):
    sizes = sorted({record["n"] for record in records})
    pairwise = [[record["time_ms"] for record in records if record["n"] == n and record["encoding"] == "pw_amo"] for n in sizes]
    sequential = [[record["time_ms"] for record in records if record["n"] == n and record["encoding"] == "sc_amo"] for n in sizes]

    positions = list(range(len(sizes)))
    plt.figure(figsize=(8, 4.5))
    plt.boxplot(pairwise, positions=[p - 0.18 for p in positions], widths=0.3,
                patch_artist=True, boxprops={"facecolor": "#4C78A8"},
                medianprops={"color": "black"}, tick_labels=["PW"] * len(sizes))
    plt.boxplot(sequential, positions=[p + 0.18 for p in positions], widths=0.3,
                patch_artist=True, boxprops={"facecolor": "#F58518"},
                medianprops={"color": "black"}, tick_labels=["SC"] * len(sizes))
    plt.xticks(positions, sizes)
    plt.xlabel("Số biến (n)")
    plt.ylabel("Thời gian giải (ms)")
    plt.title("Thời gian giải thực tế")
    plt.grid(axis="y", alpha=0.25)
    plt.legend(handles=[
        Patch(facecolor="#4C78A8", label="Pairwise"),
        Patch(facecolor="#F58518", label="Sequential Counter"),
    ])
    plt.tight_layout()
    plt.savefig(f"{SCRIPT_DIR}/runtime_vs_n.pdf")
    plt.close()


if __name__ == "__main__":
    plot_clause_counts()
    assignments = [8, 10, 12, 15]
    records = []
    for n in assignments:
        records.extend(measure(pw_amo, n))
        records.extend(measure(sc_amo, n))
    plot_runtime(records)

    for n in assignments:
        for encoding in ("pw_amo", "sc_amo"):
            subset = [r for r in records if r["n"] == n and r["encoding"] == encoding]
            print(
                f"n = {n:2d} {encoding:6s} "
                f"time = {sum(r['time_ms'] for r in subset) / len(subset):.4f} ms, "
                f"conflicts = {sum(r['conflicts'] for r in subset) / len(subset):.2f}, "
                f"decisions = {sum(r['decisions'] for r in subset) / len(subset):.2f}, "
                f"propagations = {sum(r['propagations'] for r in subset) / len(subset):.2f}"
            )
            
#%%