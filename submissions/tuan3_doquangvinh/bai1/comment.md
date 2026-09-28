Reviewer #1: Optimization / TRP
Đóng góp hiện tại có vẻ incremental: sequential-counter AMO và precedence propagation đều là kỹ thuật chuẩn. Bài cần nói rõ hơn: cái mới nằm ở đâu so với Croella et al. 2024? Là clique construction? Là tích hợp vào DDD? Là empirical behavior trên track/station aggregation?
Formulation TRP ở main.tex (line 186) quá tối giản. Thiếu định nghĩa horizon, destination delay, scheduled arrival, objective formula, và cost functions cụ thể cho Step/Round/Cont.
Constraint conflict ở main.tex (line 201) dùng cặp tài nguyên (r,q) tổng quát, nhưng phần AMO clique ở main.tex (line 528) lại mô tả “fix a resource r”. Reviewer sẽ hỏi: các separation bất đối xứng l_ij^{rq} được chuyển thành same-time AMO clique như thế nào?
Cần một theorem/proposition chứng minh restricted MaxSAT-DDD vẫn exact sau hai thay đổi. Hiện chỉ có câu “removes no feasible schedule” cho precedence propagation, chưa đủ cho toàn bộ encoding.
Algorithm ở main.tex (line 569) có điểm nguy hiểm: nếu V = empty nhưng Cost(tau) != ell, vòng lặp refine với tập violation rỗng có thể không thêm gì mới. Cần giải thích cost-refinement hoặc điều kiện dừng này.
Reviewer #2: SAT / MaxSAT Encoding
Sequential-counter clauses ở main.tex (line 552) chưa đủ chính xác về index và boundary clauses. Reviewer SAT sẽ đòi clause set đầy đủ, ví dụ clause cuối kiểu ¬x_n ∨ ¬s_{n-1}.
Threshold n < 6 cho pairwise vs sequential counter có vẻ tùy ý. Cần justification: lý thuyết, microbenchmark, hoặc sensitivity analysis với threshold 4/6/8/10.
Bài nói SC giảm bottleneck Θ(n^2), nhưng Table CNF ở main.tex (line 938) cho thấy số variables/clauses không luôn giảm. Cần diễn giải lại: speedup có thể do cấu trúc clause/propagation/search, không chỉ formula size.
Câu “Rounded-cost speedups ... mainly reflect stronger propagation” ở main.tex (line 957) hơi võ đoán. Sequential counter thường không “stronger” hơn pairwise AMO theo nghĩa propagation đơn giản; cần evidence từ conflicts/decisions/propagations.
Soft-cost encoding gần như chưa được mô tả. Với continuous objective, đây là điểm mấu chốt vì bài nói memory pressure và many cost levels. Reviewer sẽ yêu cầu mô tả cách tạo weighted soft clauses.
Reviewer #3: Experimental Evaluation
So sánh commercial solvers chưa thật công bằng. Aggregate table ở main.tex (line 656) chỉ có Big-M Gurobi, nhưng commercial table ở main.tex (line 690) cho thấy BigM-CPLX chứng minh 72/72 ở cả ba objective. Nếu CPLEX mạnh nhất, cần đưa runtime vào bảng chính.
Caption “Gurobi Big-M only (best MILP baseline)” ở main.tex (line 754) sẽ bị chất vấn vì bảng trước đó cho thấy CPLEX chứng minh nhiều hơn Gurobi.
Average time chỉ tính trên proved-optimal runs ở main.tex (line 656) gây bias cho solver timeout nhiều. Nên thêm PAR10/PAR2, cactus plot, median, geometric mean, và solved-over-time.
Các kết quả 23 ms rất nhỏ; cần nói có chạy lặp lại không, single-thread hay multi-thread, warm cache, solver randomness, std/iqr. Không thì reviewer sẽ xem khác biệt vài ms là noise.
Thiếu thông tin solver settings: thread count, MIPGap, presolve, memory limit, version cụ thể của RC2/PySAT/Glucose/Gurobi/CPLEX.
Hard subset ở main.tex (line 626) cần giải thích vì sao chọn A1/A2/A8/A11/A12. Nếu chọn hậu nghiệm theo độ khó, cần nói rõ.
Vì contribution là clique/AMO, bài nên có bảng instance statistics: số trains, operations, conflicts, max/mean clique size, số clique có n >= 6, số time points, số soft clauses.
Reviewer #4: Presentation / Positioning
Title quá dài và hơi “engineering report”. Có thể rút còn: “Strengthened MaxSAT-DDD for Train Rescheduling via Cardinality Encoding and Precedence Propagation”.
Related-work table ở main.tex (line 137) rộng nhưng nông; phần learning-based hơi xa contribution. Nên rút và dùng chỗ cho MaxSAT/cardinality/DDT details.
Nhiều hình TikZ lớn, đặc biệt precedence propagation figure, khá đẹp nhưng chiếm diện tích. Với LLNCS, reviewer có thể thích formal encoding + results hơn minh họa dài.
Abstract nên thận trọng hơn: “up to 79.6% runtime reduction” là trên common-solved hard continuous track subset, không phải toàn bộ benchmark.
Data/code availability tốt, nhưng nên thêm commit hash/Zenodo DOI và script exact để reproduce tables.