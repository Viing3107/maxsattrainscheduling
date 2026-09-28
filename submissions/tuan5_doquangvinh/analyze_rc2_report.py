"""Generate plotnine figures and a LaTeX report for the four RC2 variants."""

import csv
import math
import statistics
from pathlib import Path

import pandas as pd
from plotnine import (
    aes,
    element_text,
    geom_col,
    geom_hline,
    geom_line,
    ggplot,
    labs,
    position_dodge,
    scale_fill_brewer,
    scale_y_log10,
    scale_y_continuous,
    theme,
    theme_minimal,
)

ROOT = Path(__file__).resolve().parents[2]
RESULTS = ROOT / "results" / "improvements"
OUT = Path(__file__).resolve().parent
CONFIGS = ("RC2-Base", "RC2+B", "RC2+R", "RC2+B+R")
OBJECTIVES = ("finsteps123", "infsteps180", "cont")


def newest_dir(config):
    candidates = sorted(RESULTS.glob(f"*-{config}"))
    if not candidates:
        raise FileNotFoundError(f"Missing result directory for {config}")
    return candidates[-1]


def load_rows(path):
    with path.open(newline="", encoding="utf-8-sig") as stream:
        return [{(k or "").strip(): (v or "").strip() for k, v in row.items()} for row in csv.DictReader(stream)]


def number(row, key):
    try:
        value = float(row.get(key, ""))
        return value if math.isfinite(value) else None
    except (TypeError, ValueError):
        return None


def summarize(rows):
    solved = [row for row in rows if row.get("status") == "ok"]
    times = [number(row, "sol_time") for row in solved]
    times = [value for value in times if value is not None]
    total = [number(row, "total_time") for row in rows]
    total = [value for value in total if value is not None]
    costs = [number(row, "cost") for row in solved]
    costs = [value for value in costs if value is not None]
    optimal = 0
    for row in solved:
        lb, ub = number(row, "lb"), number(row, "ub")
        if lb is not None and ub is not None and abs(lb - ub) <= 1e-6 * max(1.0, abs(ub)):
            optimal += 1
    return {
        "N": len(rows),
        "OK": len(solved),
        "Failed": len(rows) - len(solved),
        "Success": 100 * len(solved) / len(rows) if rows else 0,
        "Mean solve (ms)": statistics.mean(times) if times else None,
        "Median solve (ms)": statistics.median(times) if times else None,
        "Mean total (s)": statistics.mean(total) if total else None,
        "Mean cost": statistics.mean(costs) if costs else None,
        "Optimal": optimal,
    }


def write_csv(records):
    fields = ["Configuration", "Objective", "N", "OK", "Failed", "Success", "Mean solve (ms)", "Median solve (ms)", "Mean total (s)", "Mean cost", "Optimal"]
    with (OUT / "summary.csv").open("w", newline="", encoding="utf-8") as stream:
        writer = csv.DictWriter(stream, fieldnames=fields)
        writer.writeheader()
        writer.writerows(records)


def plot_success(records):
    rows = [{"Configuration": r["Configuration"], "Objective": r["Objective"], "Success": r["Success"]} for r in records]
    rows = pd.DataFrame(rows)
    chart = (
        ggplot(rows, aes("Objective", "Success", fill="Configuration"))
        + geom_col(position=position_dodge(width=0.8), width=0.7)
        + scale_y_continuous(limits=(0, 105))
        + scale_fill_brewer(type="qual", palette="Dark2")
        + labs(x="Objective", y="Solved instances (%)", fill="Configuration")
        + theme_minimal()
        + theme(figure_size=(8, 4.5), axis_text_x=element_text(rotation=0))
    )
    chart.save(OUT / "success_rate.png", dpi=180, verbose=False)


def plot_time(records):
    rows = [{"Configuration": r["Configuration"], "Objective": r["Objective"], "Mean solve (ms)": r["Mean solve (ms)"] or 0.001} for r in records]
    rows = pd.DataFrame(rows)
    chart = (
        ggplot(rows, aes("Objective", "Mean solve (ms)", fill="Configuration"))
        + geom_col(position=position_dodge(width=0.8), width=0.7)
        + scale_y_log10()
        + scale_fill_brewer(type="qual", palette="Dark2")
        + labs(x="Objective", y="Mean successful solve time (ms, log scale)", fill="Configuration")
        + theme_minimal()
        + theme(figure_size=(8, 4.5))
    )
    chart.save(OUT / "mean_solve_time.png", dpi=180, verbose=False)


def plot_speedup(data):
    rows = []
    for objective in OBJECTIVES:
        base = {row.get("name"): number(row, "sol_time") for row in data[("RC2-Base", objective)] if row.get("status") == "ok"}
        combined = {row.get("name"): number(row, "sol_time") for row in data[("RC2+B+R", objective)] if row.get("status") == "ok"}
        ratios = sorted(base[name] / combined[name] for name in set(base) & set(combined) if base[name] and combined[name])
        rows.extend({"Objective": objective, "Instance rank": index, "Speedup": value} for index, value in enumerate(ratios, 1))
    rows = pd.DataFrame(rows)
    chart = (
        ggplot(rows, aes("Instance rank", "Speedup"))
        + geom_line(color="#2a9d8f")
        + geom_hline(yintercept=1, linetype="dashed", color="#555555")
        + labs(x="Common successful instances", y="RC2-Base / RC2+B+R solve time", title="Per-instance speedup")
        + theme_minimal()
        + theme(figure_size=(10, 4.5), subplots_adjust={"wspace": 0.25})
    )
    chart.save(OUT / "per_instance_speedup.png", dpi=180, verbose=False)


def latex_escape(value):
    return str(value).replace("&", r"\&").replace("%", r"\%").replace("_", r"\_")


def fmt(value, digits=2):
    return "--" if value is None else f"{value:.{digits}f}"


def write_latex(records, directories):
    lines = [r"\documentclass[11pt,a4paper]{article}", r"\usepackage[margin=2.2cm]{geometry}", r"\usepackage{booktabs}", r"\usepackage{graphicx}", r"\usepackage{float}", r"\usepackage[T5]{fontenc}", r"\usepackage[utf8]{inputenc}", r"\usepackage[vietnamese]{babel}", r"\title{Phân tích thực nghiệm bốn cấu hình RC2}", r"\author{Do Quang Vinh}", r"\date{\today}", r"\begin{document}", r"\maketitle", "", r"\section{Thiết lập thực nghiệm}", r"So sánh bốn cấu hình RC2 trên 72 instance và ba objective: \texttt{finsteps123}, \texttt{infsteps180} và \texttt{cont}.", "", r"\begin{table}[H]", r"\centering", r"\caption{Các cấu hình được so sánh}", r"\begin{tabular}{lcc}", r"\toprule", r"Cấu hình & B: bound propagation & R: selective refinement \\", r"\midrule", r"RC2-Base & Tắt & Tắt \\", r"RC2+B & Bật & Tắt \\", r"RC2+R & Tắt & Bật \\", r"RC2+B+R & Bật & Bật \\", r"\bottomrule", r"\end{tabular}", r"\end{table}", "", r"\section{Bảng thống kê}", r"Mean solve time chỉ tính trên các instance có trạng thái \texttt{ok}; mean total time bao gồm mọi dòng ghi nhận.", "", r"\begin{table}[H]", r"\centering", r"\scriptsize", r"\begin{tabular}{llrrrrrrrr}", r"\toprule", r"Config. & Objective & N & OK & Fail & Success (\%) & Mean (ms) & Median (ms) & Total (s) & Opt. \\", r"\midrule"]
    for record in records:
            lines.append("{} & {} & {} & {} & {} & {:.1f} & {} & {} & {} & {} \\\\".format(latex_escape(record["Configuration"]), latex_escape(record["Objective"]), record["N"], record["OK"], record["Failed"], record["Success"], fmt(record["Mean solve (ms)"]), fmt(record["Median solve (ms)"]), fmt(record["Mean total (s)"]), record["Optimal"]))
    lines += [r"\bottomrule", r"\end{tabular}", r"\end{table}", "", r"\section{Biểu đồ}", r"\begin{figure}[H]", r"\centering", r"\includegraphics[width=0.9\textwidth]{success_rate.png}", r"\caption{Tỷ lệ instance giải thành công.}", r"\end{figure}", r"\begin{figure}[H]", r"\centering", r"\includegraphics[width=0.9\textwidth]{mean_solve_time.png}", r"\caption{Thời gian giải trung bình trên các instance thành công.}", r"\end{figure}", r"\begin{figure}[H]", r"\centering", r"\includegraphics[width=0.95\textwidth]{per_instance_speedup.png}", r"\caption{Tỷ số thời gian RC2-Base trên RC2+B+R; giá trị lớn hơn 1 nghĩa là RC2+B+R nhanh hơn.}", r"\end{figure}", "", r"\section{Nhận xét}"]
    for objective in OBJECTIVES:
        subset = [r for r in records if r["Objective"] == objective]
        best_success = max(subset, key=lambda r: r["Success"])
        fastest = min((r for r in subset if r["Median solve (ms)"] is not None), key=lambda r: r["Median solve (ms)"])
        lines.append(rf"Với objective \texttt{{{objective}}}, {best_success['Configuration']} có tỷ lệ thành công cao nhất ({best_success['Success']:.1f}\%), trong khi {fastest['Configuration']} có median thời gian thấp nhất ({fastest['Median solve (ms)']:.2f} ms).")
    lines += [r"Các giá trị cost trung bình chỉ được tính trên tập instance giải thành công của từng cấu hình; vì vậy cần dùng tập instance chung nếu muốn kết luận về chất lượng nghiệm. Kết quả hiện tại cho thấy refinement có chọn lọc có thể giảm median thời gian, nhưng việc kết hợp bound propagation không tự động cải thiện tỷ lệ thành công.", r"\section{Nguồn dữ liệu}"]
    for config, directory in directories.items():
        lines.append(rf"\texttt{{{latex_escape(config)}}}: \texttt{{{latex_escape(directory.name)}}}\\")
    lines += [r"\end{document}"]
    (OUT / "report.tex").write_text("\n".join(lines) + "\n", encoding="utf-8")


def main():
    OUT.mkdir(exist_ok=True)
    data, records = {}, []
    directories = {config: newest_dir(config) for config in CONFIGS}
    for config, directory in directories.items():
        for objective in OBJECTIVES:
            rows = load_rows(directory / f"{config}_{objective}.csv")
            data[(config, objective)] = rows
            records.append({"Configuration": config, "Objective": objective, **summarize(rows)})
    write_csv(records)
    write_latex(records, directories)
    plot_success(records)
    plot_time(records)
    plot_speedup(data)
    print(f"Generated LaTeX report and plotnine figures in {OUT}")


if __name__ == "__main__":
    main()
