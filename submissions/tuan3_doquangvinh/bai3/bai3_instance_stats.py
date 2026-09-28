import csv
from collections import defaultdict
from dataclasses import dataclass
from pathlib import Path

SCRIPT_DIR = Path(__file__).parent.resolve()
ROOT_DIR = SCRIPT_DIR.parent.parent.parent
INSTANCES_DIR = ROOT_DIR / "instances"

print(ROOT_DIR)

@dataclass(frozen=True)
class Operation:
    train_id: str
    resource_id: str
    start: int
    end: int

def parse_operations(instance_path: Path) -> list[Operation]:
    """ 
    lấy input từ folder instances và trả về danh sách các operations
    """
    operations = []
    with instance_path.open(encoding="utf-8") as file:
        for line in file:
            fields = line.split()
            if not fields or fields[0].startswith("TrainId="): continue

            values = {field.split("=")[0]: int(field.split("=")[1]) for field in fields[2:]}
            operations.append(Operation(
                train_id = fields[1].removeprefix("Train"),
                resource_id = fields[0],
                start = values["BaseTime"],
                end = values["BaseTime"] + values["RunTime"],
            ))
    return operations

def find_cliques (operations: list[Operation]) -> list[frozenset[int]]:
    """ 
    liệt kê tất cả các maximal clique
    """
    by_resource = defaultdict(list)
    for idx, op in enumerate(operations): by_resource[op.resource_id].append((idx, op))
    
    cliques: set[frozenset[int]] = set()
    for resource_ops in by_resource.values():
        for t in {op.start for _, op in resource_ops}:
            clique = frozenset(
                idx for idx, op in resource_ops if op.start <= t < op.end
            )
            if len(clique) >= 2: cliques.add(clique)
    return sorted(cliques, key=lambda c: (len(c), tuple(c)))

def read_instance_stats(instance_path: Path) -> dict[str, int | float]:
    """ 
    trả về dict dạng: {
        số tàu,
        số operations,
        số cặp xung đột,
        số clique có kích thước >= 6,
        kích thước clique lớn nhất,
        kích thước clique trung bình,
        tổng số điểm thời gian ban đầu trước DDD iteration đầu tiên
    }
    - cặp xung đột: cặp operation thỏa mãn cùng resource nhưng khác tàu
    - clique: tập các operation overlap thời gian tại một thời điểm t
    - số mốc thời gian trong lưới thô ban đầu trước khi tinh chỉnh DDD chính là số visit. 1 visit được định nghĩa là 1 sự kiện tàu rời station vào track, hoặc tàu rời track vào station. Mỗi dòng trong instance bao gồm 2 sự kiện: Tàu chờ ở station rồi đi vào track, và tàu đi trên track đến station tiếp theo -> số visit = 2 * số oprations + sự kiện track vào ga đích.
    """
    operations = parse_operations(instance_path)
    
    train_ids = {operation.train_id for operation in operations}

    by_resource = defaultdict(list)
    for index, operation in enumerate(operations):
        by_resource[operation.resource_id].append(index)
    conflict_pairs = 0
    for indices in by_resource.values():
        for i, left in enumerate(indices):
            for right in indices[i + 1:]:
                if operations[left].train_id != operations[right].train_id: conflict_pairs += 1
    
    clique_sizes = [len(clique) for clique in find_cliques(operations)]

    return {
        "trains": len(train_ids),
        "operations": len(operations),
        "conflict_pairs": conflict_pairs,
        "cliques_ge_6": sum(size >= 6 for size in clique_sizes),
        "max_clique_size": max(clique_sizes, default=0),
        "mean_clique_size": sum(clique_sizes) / len(clique_sizes) if clique_sizes else 0,
        "initial_time_points": 2 * len(operations) + len(train_ids),
    }

def write_outputs(rows: list[dict[str, int | float]]) -> None:
    fieldnames = [
        "instance", "trains", "operations", "conflict_pairs", "cliques_ge_6",
        "max_clique_size", "mean_clique_size", "initial_time_points",
    ]
    csv_path = SCRIPT_DIR / "instance_stats.csv"
    with csv_path.open("w", encoding="utf-8") as file:
        writer = csv.DictWriter(file, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)

    tex_path = SCRIPT_DIR / "instance_stats.tex"
    with tex_path.open("w", encoding="utf-8") as file:
        file.write("\\begin{tabular}{lrrrrrrr}\n\\toprule\n")
        file.write("Instance & Trains & Operations & Conflicts & Cliques $\\geq 6$ & Max clique & Mean clique & Initial time points \\\\\n")
        file.write("\\midrule\n")
        for row in rows:
            file.write(
                f"{row['instance']} & {row['trains']} & {row['operations']} & "
                f"{row['conflict_pairs']} & {row['cliques_ge_6']} & "
                f"{row['max_clique_size']} & {row['mean_clique_size']:.2f} & "
                f"{row['initial_time_points']} \\\\\n"
            )
        file.write("\\bottomrule\n\\end{tabular}\n")

# if __name__ == "__main__":
#     rows = []
#     for instance_path in sorted(INSTANCES_DIR.glob("*/Instance*.txt")):
#         row = read_instance_stats(instance_path)
#         row["instance"] = f"{instance_path.parent.name}/{instance_path.stem}"
#         rows.append(row)
#     write_outputs(rows)
#     print(f"Wrote {len(rows)} instances to instance_stats.csv and instance_stats.tex")