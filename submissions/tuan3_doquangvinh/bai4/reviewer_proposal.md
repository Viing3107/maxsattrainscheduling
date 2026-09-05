# Đề xuất cải tiến formulation TRP (Bài 4 — tuần 3)

## Câu hỏi 1: Ký hiệu nào còn thiếu định nghĩa tường minh?

1. **$H$**: "giới hạn thời gian của bài toán". Bài báo chỉ nói "H giới hạn các mốc thời gian" nhưng **không có ràng buộc nào thực sự dùng H**. nghĩa là H được nêu ra rồi bỏ lơ, không có tác dụng gì trong mô hình.
2. **$a_i$**: công thức tính trễ dùng đến
   $r_i^{\mathrm{dest}}$ (ga đích) nhưng chưa nói ga đích là gì
3. **$w$, $\eta$**: công thức chi phí dùng chúng nhưng không nói lấy từ đâu

### Đề xuất

| Ký hiệu                  | Vấn đề                                | Vị trí       |
| ------------------------ | ------------------------------------- | ------------ |
| $H$                      | Không xuất hiện trong ràng buộc nào   | Sau dòng 217 |
| $a_i$                    | $r_i^{\mathrm{dest}}$ chưa định nghĩa | Dòng 217–219 |
| $w_{ik}, \eta_{ik}, w_i$ | Không nói nguồn                       | Dòng 235     |

## Câu hỏi 2: Separation bất đối xứng $l_{ij}^{rq}$ được chuyển thành AMO clique như thế nào?

Hiểu đơn giản thì đây là câu hỏi "hai chỗ trong bài báo có mâu thuẫn không?":

- **Chỗ thứ nhất** (232-234): hai tàu xung đột thì một tàu phải nhường trước, với thời gian an toàn - và thời gian an toàn theo mỗi chiều là khác nhau (tàu 1 nhường tàu 2 thì chờ 10 giây, tàu 2 nhường tàu 1 thì chờ 30 giây - đây là ý "bất đối xứng")
- **Chỗ thứ hai** (555–580): ta gom các tàu đang đứng cùng lúc trên một tài nguyên thành một clique và buộc trong nhóm này AMO

$\Rightarrow$ khoảng thời gian an toàn không bị mất đi mà nó được giấu vào định nghĩa "đang đứng". Hai tàu chỉ được tính là "cùng đứng" tại những mốc thời gian mà việc cùng đứng là bất khả kháng dù ai nhường ai. Những mốc đó tạo thành nhóm cấm, và "tối đa 1 tàu trong nhóm" tự động bao hàm cả hai chiều của ràng buộc nhường nhường.

## Câu hỏi 3: Proposition bảo toàn tính exact của DDD

> Gọi $\mathcal{A}$ là tập các lịch trình khả thi của hệ ràng buộc TRP gồm: (1) giờ vào không sớm hơn earliest, (2) ràng buộc đi đường trên lộ trình cố định (chặng sau $\ge$ chặng trước + thời gian chạy), (3) ràng buộc xung đột tài nguyên (disjunction nhường nhường); và $c(\delta)$ là hàm chi phí trễ. Giả sử tại một vòng lặp DDD nào đó, CNF được tăng cường bằng hai thay đổi:
>
> **(i)** thêm các mệnh đề precedence $\;\neg d^{ir}(\tau) \vee d^{iq}(\tau + L_{ir \to iq})$, trong đó $L_{ir \to iq} \ge l_i^r$ là một **cận dưới hợp lệ** thu được bằng cách "xích" các ràng buộc đi đường (2) dọc theo lộ trình cố định của tàu (ví dụ: phải đi qua 2 chặng, mỗi chặng $l_i^r$ phút $\Rightarrow$ đến chặng sau không sớm hơn $l_i^{r} + l_i^{q}$ phút);
>
> **(ii)** trên mỗi clique $C(\tau)$ gồm các occupation indicator cấm đồng thời, thay bộ mệnh đề pairwise bằng bộ mệnh đề sequential-counter.
>
> Khi đó:
>
> **(a) Propagation không loại lịch nào.** Mọi lịch trình $s \in \mathcal{A}$ đều
> thỏa sẵn mọi bound được truyền: $s(t^{iq}) \ge s(t^{ir}) + L_{ir \to iq}$. Nói cách
> khác, các mệnh đề mới thêm không loại bỏ bất kỳ lịch khả thi nào.
>
> **(b) SC $\equiv$ pairwise.** Với mọi cách gán giá trị cho $\{x_v : v \in C(\tau)\}$, bộ mệnh đề SC được thỏa $\Leftrightarrow$ **tối đa một** $x_v$ = true, đúng ý nghĩa của các mệnh đề pairwise $\neg x_{v_a} \vee \neg x_{v_b}$. Hai cách mã hóa định nghĩa cùng một tập nghiệm của CNF
