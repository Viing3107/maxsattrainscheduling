#!/usr/bin/env python3

""" 
command: python3 parse_results.py MaxSatDefault_infsteps180.json

JSON mẫu:
[   
    {
        "avg_tracks": 20.931034088134766,
        "conflicting_visit_pairs": 5915,
        "conflicts": 33,
        "delay_cost_type": "InfiniteSteps180",
        "index": 0,
        "name": "origA1",
        "solves": [
            {
                "algorithm_time": 0.15571339099999998,
                "avg_time_points": 1.7948511665325824,
                "cost": 34,
                "delay_cost_type": "InfiniteSteps180",
                "iterations": 143,
                "lb": 34,
                "max_time_points": 11,
                "num_clauses_total": 3034,
                "num_conflicts": 44,
                "num_time_points": 2231,
                "num_traveltime": 925,
                "num_vars_total": 1029,
                "objective_iters": 12,
                "resource_iters": 1,
                "sol_time": 166.73639,
                "solver_name": "MaxSatDddLadderRC2",
                "solver_time": 0.007070499,
                "status": "ok",
                "total_time": 0.16278249,
                "travel_and_resource_iters": 31,
                "travel_iters": 98,
                "ub": 34
            }
        ],
        "trains": 29
    },
]

CSV kỳ vọng:
name, sol_time, iterations, status
"""
import argparse
import csv
import json
from pathlib import Path

FIELDS = (
    "name",
    "sol_time",
    "iterations",
    "status"
)

def main():
    parser = argparse.ArgumentParser(
        description="Xuất JSON sang CSV"
    )
    parser.add_argument("input_json", type=Path, help="tệp JSON")
    parser.add_argument(
        "--format",
        choices=("compact",),
        default="compact",
        help="định dạng output",
    )
    parser.add_argument(
        "--overwrite",
        action="store_true",
        help="ghi đè tệp CSV cũ",
    )
    args = parser.parse_args()

    data = json.loads(args.input_json.read_text(encoding="utf-8"))
    rows = []

    for problem in data:
        name = problem.get("name", "")
        solves = problem.get("solves", [])
        for solve in solves:
            rows.append(
                {
                    "name": name,
                    "sol_time": solve.get("sol_time", ""),
                    "iterations": solve.get("iterations", ""),
                    "status": solve.get("status", ""),
                }
            )

    output_csv = args.input_json.with_suffix(".csv")
    if output_csv.exists() and not args.overwrite:
        parser.error(f"file CSV đã tồn tại: {output_csv}; sử dụng --overwrite")

    with output_csv.open("w", newline="", encoding="utf-8") as file:
        writer = csv.DictWriter(file, fieldnames=FIELDS)
        writer.writeheader()
        writer.writerows(rows)

    print(f"Wrote {output_csv} ({len(rows)} rows)")

if __name__ == "__main__":
    main()