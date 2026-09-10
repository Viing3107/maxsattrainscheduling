"""
Kiểm tra tính tương đương logic 100% giữa:
    - Ràng buộc vật lý B3 gốc + Exactly-One (B1);
    - Mã hóa Direct (baseline O(n*m)) + Exactly-One;
    - Mã hóa SCL (C1-C7, biến tích lũy R) + Exactly-One.
"""

from bai1_scl_precedence import (
    direct_precedence_clauses,
    encode_scl_precedence,
    exactly_one_clauses,
    generate_time_points,
)


""" Check so sánh giữa nghiệm vật lý và nghiệm CNF """
def physical_b3_ok(assign, x_r: list[int], x_q: list[int], h_r: list[int], h_q: list[int], l_r: int):
    """ 
    Ràng buộc vật lý B3 gốc:
        - Exactly-One: tàu xuất phát ở ga q đúng 1 interval;
        - Precedence: nếu tàu xuất phát ga r tại h_r[p] thì phải xuất phát ga q sau h_r[p] + l_r.
    """
    if sum(1 for v in x_q if assign[v]) != 1: return False
    start_q = 0
    for t in range(len(x_q)):
        if assign[x_q[t]]:
            start_q = h_q[t]
            break
    for p in range(len(x_r)):
        if assign[x_r[p]] and start_q < h_r[p] + l_r:
            return False
    return True

def cnf_satisfied(assign, clauses):
    """Kiểm tra một tập mệnh đề CNF thỏa mãn dưới phép gán assign."""
    return all(any(assign[abs(l)] if l > 0 else not assign[abs(l)] for l in c) for c in clauses)


def check_logical_equivalence(n=3, m=4, l_r=5, verbose=True):
    """ 
    Duyệt qua 2^(n+m) tổ hợp gán giá trị cho biến quyết định x_r, x_q.
    Với mỗi gán:
        - Direct: chỉ có biến quyết định -> kiểm tra trực tiếp;
        - SCL: biến phụ R được duyệt thêm 2^m tổ hợp
    So sánh với ràng buộc vật lý B3 + Exactly-One.
    """
    x_r = list(range(1, n + 1))
    x_q = list(range(n + 1, n + m + 1))
    h_r = generate_time_points(n, start=0, step=10)
    h_q = generate_time_points(m, start=0, step=10)

    # Theo đề bài: tập nghiệm CNF = "mã hóa B3 + Exactly-One".
    # Direct cũng được cộng EO để so sánh công bằng trên cùng tiền đề B1.
    eo = exactly_one_clauses(x_q)
    direct_clauses = direct_precedence_clauses(x_r, x_q, h_r, h_q, l_r) + eo
    scl_clauses, next_var = encode_scl_precedence(x_r, x_q, h_r, h_q, l_r, next_var=n + m + 1)
    scl_clauses = scl_clauses + eo
    r_vars = list(range(n + m + 1, next_var))

    if verbose:
        print(f"Checker: n={n} (ga r), m={m} (ga q), l_r={l_r}")
        print(f"  Direct : {len(direct_clauses)} mệnh đề (gồm EO), {n + m} biến")
        print(f"  SCL    : {len(scl_clauses)} mệnh đề (gồm EO), {n + m + len(r_vars)} biến (thêm {len(r_vars)} biến R)")

    num_assign = 1 << (n + m)
    num_sat = 0
    mismatches = 0
    for mask in range(num_assign):
        assign = {v: bool((mask >> i) & 1) for i, v in enumerate(x_r + x_q)}
        phys = physical_b3_ok(assign, x_r, x_q, h_r, h_q, l_r)
        sat_direct = cnf_satisfied(assign, direct_clauses)

        # SCL: tồn tại phép gán R thỏa mãn hay không (2^m tổ hợp)
        sat_scl = False
        for r_mask in range(1 << len(r_vars)):
            r_assign = {v: bool((r_mask >> i) & 1) for i, v in enumerate(r_vars)}
            if cnf_satisfied(assign | r_assign, scl_clauses):
                sat_scl = True
                break

        if phys:
            num_sat += 1
        if phys != sat_direct or phys != sat_scl:
            mismatches += 1
            print(f"  MISMATCH: {assign} | physical={phys} direct={sat_direct} scl={sat_scl}")

    if verbose:
        print(f"  Duyệt 2^{n + m} = {num_assign} gán giá trị: {num_sat} nghiệm vật lý, {mismatches} mismatch")
        print("  => Tương đương logic 100%" if mismatches == 0 else "  => KHÔNG tương đương!")
    return mismatches == 0

def run_checker():
    """Chạy checker cho nhiều giá trị l_r (góc, biên, lớn hơn mọi interval)."""
    all_ok = True
    for l_r in [0, 5, 15, 100]:
        all_ok &= check_logical_equivalence(n=3, m=4, l_r=l_r)
        print()
    if not all_ok:
        raise SystemExit("Checker FAILED: mã hóa không tương đương!")
    print("=> Cả Direct và SCL đều tương đương 100% với B3 + Exactly-One.\n")


if __name__ == "__main__":
    run_checker()