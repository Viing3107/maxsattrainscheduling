def encode_scl_precedence(x_r: list[int], x_q: list[int], h_r: list[int], h_q: list[int], l_r: int, next_var: int) -> tuple[list[list[int]], int]:
    """ 
    Tạo mệnh đề SCL (C1 - C7) mã hóa ràng buộc thứ tự B3.
    Args:
        x_r: literals x^i_{r,p} - tàu i xuất phát ở ga r tại interval p
        x_q: literals x^i_{q,t} - tàu i xuất phát ở ga q tại interval t (t = 1..m)
        h_r: thời điểm bắt đầu tương ứng của từng interval ở ga r
        h_q: thời điểm bắt đầu tương ứng của từng interval ở ga q
        l_r: thời gian chiếm dụng tối thiểu l^i_r ở ga r
        next_var: id tiếp theo dùng để cấp phát biến phụ R^i_{q, 1, t}
    Returns: 
        Trả về tuple (list_clauses, next_var).

    Ý nghĩa biến phụ: R^i_{q, 1, t} = 1 <=> tàu i đã xuất phát ở ga q tại interval nào đó ≤ t (biến tích lũy). Nhờ đó C7 chỉ cần 1 mệnh đề cho mỗi x^i_{r,p}: nếu r xuất phát tại h_r[p] thì q phải bắt đầu sau h_r[p] + l_r, tức -R_{K_p} với K_p = max{t | h_q[t] < h_r[p] + l_r}.
    """
    clauses: list[list[int]] = []
    m = len(x_q)

    # Cấp phát m biến phụ R^i_{q,1} .. R^i_{q,m} (R[0] ứng với t = 1)
    R = list(range(next_var, next_var + m))
    next_var += m

    # (C1): R^i_{q,1} -> x^i_{q,1}
    clauses.append([-R[0], x_q[0]])
    # (C2) tại t = 1: x^i_{q,1} -> R^i_{q,1}
    clauses.append([-x_q[0], R[0]])

    for t in range(1, m):
        # (C2): x^i_{q,t} -> R^i_{q,t}
        clauses.append([-x_q[t], R[t]])
        # (C3): R^i_{q,t-1} -> R^i_{q,t}
        clauses.append([-R[t - 1], R[t]])
        # (C4): R^i_{q,t} -> R^i_{q,t-1} v x^i_{q,t}
        clauses.append([-R[t], R[t - 1], x_q[t]])
        # (C5): x^i_{q,t} -> -R^i_{q,t-1}
        clauses.append([-R[t - 1], -x_q[t]])

    # (C6): R^i_{q,m}  (đơn nguyên - ép tàu phải xuất phát ở ga q)
    clauses.append([R[m - 1]])

    # (C7): x^i_{r,p} -> -R^i_{q,K_p},  K_p = max{t | h^i_{q,t} < h^i_{r,p} + l^i_r}
    for p in range(len(x_r)):
        # K_p = chỉ số (1-based) interval muộn nhất ở ga q vẫn "quá sớm"
        K_p = max((t for t in range(1, m + 1) if h_q[t - 1] < h_r[p] + l_r), default=0)
        if K_p == 0:
            # Tối ưu biên: không có interval nào của q quá sớm -> bỏ qua C7
            continue
        if K_p == m:
            # Tối ưu biên: mọi interval của q đều quá sớm -> x^i_{r,p} bị cấm
            clauses.append([-x_r[p]])
        else:
            clauses.append([-x_r[p], -R[K_p - 1]])

    return clauses, next_var

""" Các hàm bổ trợ sử dụng cho mã hóa trực tiếp"""
def generate_time_points(m: int, start: int = 0, step: int = 10) -> list[int]:
    """Sinh m mốc thời gian cách đều nhau mô phỏng các interval xuất phát."""
    return [start + i * step for i in range(m)]

def exactly_one_clauses(x_q: list[int]) -> list[list[int]]:
    """ 
    Ràng buộc B1 (Exactly-One) trên các interval của ga q:
        - ALO:  x_1 v x_2 v ... v x_m 
        - AMO:  pairwise -x_i v -x_j
    """
    clauses = [list(x_q)]
    for i in range(len(x_q)):
        for j in range(i + 1, len(x_q)):
            clauses.append([-x_q[i], -x_q[j]])
    return clauses

def direct_precedence_clauses(x_r: list[int], x_q: list[int], h_r: list[int], h_q: list[int], l_r: int) -> list[list[int]]:
    """ 
    Mã hóa Direct cho ràng buộc thứ tự B3: cho mỗi cặp interval (p, t) mà interval t của ga q "quá sớm" so với h_r[p] + l_r, cấm đồng thời x_r[p] và x_q[t]. Số mệnh đề tăng bùng nổ O(n x m).
    """
    clauses = []
    for p in range(len(x_r)):
        for t in range(len(x_q)):
            if h_q[t] < h_r[p] + l_r:
                clauses.append([-x_r[p], -x_q[t]])
    return clauses

if __name__ == "__main__":
    """ 
    Kiểm thử nhanh hàm mã hóa với mock data (n = 3 interval ga r, m = 4 ga q, l_r = 5).
    """
    x_r = [101, 102, 103]
    x_q = [201, 202, 203, 204]
    h_r = [10, 20, 30]
    h_q = [0, 10, 20, 30]
    l_r = 5

    clauses, next_var = encode_scl_precedence(x_r, x_q, h_r, h_q, l_r, next_var=1)
    print(f"Số biến phụ R: 4 (id 1..{next_var - 1})")
    print(f"Tổng số mệnh đề: {len(clauses)}")
    for c in clauses:
        print(c)
