from pathlib import Path
from pysat.formula import CNF
from pysat.solvers import Cadical153

# config lấy path của folder hiện tại
CUR_URL = Path(__file__).parent.resolve()

def parse_input():
    # Lấy input từ instance A1 của dạng track run
    with open(f"{CUR_URL}/../../instances/addtracktime/InstanceA1.txt", "r", encoding="UTF-8") as file:
        # lấy header: TrainId=12 Delay=4076 FreeRun=2310
        header = ""
        while not header: header = file.readline().strip()
        trainId = header.split()[0].split("=")[1]
        
        # lấy resource: T28 Train12 AimedDepartureTime=0 WaitTime=0 BaseTime=4076 RunTime=470
        trackIds = []
        lowerBounds = []
        travelTimes = []
        for resource in file:
            resource = resource.strip().split()
            if not resource: break
            trackId = resource[0]
            lowerBound = int(resource[4].split("=")[1])
            travelTime = int(resource[5].split("=")[1])
            trackIds.append(trackId)
            lowerBounds.append(lowerBound)
            travelTimes.append(travelTime)
        return (trainId, trackIds, lowerBounds, travelTimes)

def compute_effective_lower_bounds(lowerBounds: list, travelTimes: list) -> list:
    """ 
    Hàm tính toán cận dưới hiệu dụng t_eff của tàu i
    Args:
        lowerBounds[j]: thời điểm tối thiểu mà tàu i được đi vào tài nguyên j
        travelTimes[j]: thời gian mà tàu i đi trên tài nguyên j
    Returns: 
        t_eff[j]: cận dưới thời điểm hiệu dụng của tàu i đi vào tài nguyên j
    """
    
    # t_eff[j] = lowerBound[j] for all j
    t_eff = [lowerBounds[j] for j in range(len(lowerBounds))]
    for j in range(len(lowerBounds) - 1): 
        # t_eff[j + 1] = max(t_eff[j + 1], t_eff[j] + travelTimes[j])
        t_eff[j + 1] = max(t_eff[j + 1], t_eff[j] + travelTimes[j])
    return t_eff

counter = 1
def new_var():
    global counter
    var = counter
    counter += 1
    return var
        
def add_sc_amo(cnf: CNF, lits: list) -> int:
    """ 
    Hàm mã hóa ràng buộc AMO sử dụng Sequential Counter
    Args:
        cnf: formula
        lits: danh sách các biến cần mã hóa
    Returns:
        số mệnh đề sử dụng
    """
    n = len(lits)
    if n <= 1: return 0
    # if n == 2:
    #     cnf.append([-lits[0], -lits[1]])
    #     return 1
    s = [new_var() for _ in range(n - 1)]
    
    # i = 0: x_0 -> s_0
    cnf.append([-lits[0], s[0]])
    
    # i = [1..n-2]
    for i in range(1, n - 1):
        # x_i -> s_i
        cnf.append([-lits[i], s[i]])
        
        # s_{i-1} -> s_i
        cnf.append([-s[i - 1], s[i]])
        
        # s_{i-1} -> -x_i
        cnf.append([-s[i - 1], -lits[i]])
    
    # i = n-1: s_{n-2} -> -x_{n-1}
    cnf.append([-s[n - 2], -lits[n - 1]])
    
    return len(cnf.clauses)
    
def add_pairwise_amo(cnf : CNF, lits: list) -> int:
    """ 
    Hàm mã hóa ràng buộc AMO sử dụng Pairwise
    Args:
        cnf: formula
        lits: danh sách các biến cần mã hóa
    Returns:
        số mệnh đề sử dụng
    """
    n = len(lits)
    if n <= 1: return 0
    for i in range(n - 1):
        for j in range(i + 1, n):
            # x_i -> -x_j
            cnf.append([-lits[i], -lits[j]])
    return len(cnf.clauses)

if __name__ == "__main__":
    """ 
    Chạy thử nghiệm với bộ test addtracktime/InstanceA1.txt
    -> Kết quả: Không có sự khác biệt giữa cận dưới ban đầu và cận dưới hiệu dụng
    
    trainId, trackIds, lowerBounds, travelTimes = parse_input()
    print(lowerBounds)
    print(travelTimes)
    t_eff = compute_effective_lower_bounds(lowerBounds, travelTimes)
    print(t_eff)
    """
    
    # Chạy thử nghiệm với mock data
    lowerBounds = [10, 20, 30]
    travelTimes = [50, 10]
    print(lowerBounds)
    print(travelTimes)
    t_eff = compute_effective_lower_bounds(lowerBounds, travelTimes)
    print(t_eff)
    
    print("-" * 50)
    print(f"{"Sequential Counter":>28}{"Pairwise":>20}")
    for n in range(2, 21):
        x = [new_var() for _ in range(n)]
        scCnf = CNF()
        pwCnf = CNF()
        scClauses = add_sc_amo(scCnf, x)
        pwClauses = add_pairwise_amo(pwCnf, x)
        print(f"n = {n:>2}:{scClauses:>20}{pwClauses:>20}")
    
    print("-" * 50)
    # kiểm chúng tính tương đương nghiệm với n = 5
    n = 5
    x = [new_var() for _ in range(n)]
    scCnf = CNF()
    pwCnf = CNF()
    add_sc_amo(scCnf, x)
    add_pairwise_amo(pwCnf, x)
    scSolver = Cadical153(bootstrap_with=scCnf.clauses)
    pwSolver = Cadical153(bootstrap_with=pwCnf.clauses)
    # assumption với tất cả 2^5 trường hợp
    for mask in range(1 << n):
        assignment = [x if (mask >> (x - 1)) & 1 else -x for x in range(1, n + 1)]
        
        scSat = scSolver.solve(assumptions=assignment)
        pwSat = pwSolver.solve(assumptions=assignment)
        
        if scSat != pwSat:
            print("Không tương đương nghiệm")
            exit()
    print("Sequential Counter và Pairwise tương đương nghiệm")