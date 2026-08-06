# Member Role Report — Day 10: Data Pipeline & Data Observability

## 1. Thông tin cá nhân

| Thông tin         | Nội dung                  |
| ------------------ | -------------------------- |
| Họ và tên       | Phạm Trung Kiên             |
| MSSV               | 2A202601525                    |
| Khóa/Lớp         | K3              |
| Tên nhóm         | ricon     |
| Vai trò chính    | Thành viên 2 (RAG & Evaluation)                 |
| Repository         | https://github.com/mquangggg/K3_Day10_Data-Pipeline-Data-Observability-ricon |
| Ngày hoàn thành | 2026-08-06               |

## 2. Vai trò và phạm vi công việc

### Phần việc sở hữu

| Module/deliverable | File/hàm phụ trách | Input nhận vào | Output bàn giao  | Trạng thái                                 |
| ------------------ | --------------------- | ---------------- | ----------------- | -------------------------------------------- |
| Xây dựng Test Set      | `src/evaluation/testset.py` (Hàm `build_test_set`) | Dữ liệu sạch (`papers_clean.json`) | File `test_set.json` (chứa 20 câu hỏi) | Hoàn thành |
| Cấu hình Vector DB      | `src/retrieval/index.py` (Lớp `LocalEmbeddingIndex`) | Dữ liệu dạng DataFrame | Chroma DB (`papers-baseline`) | Hoàn thành |
| Đánh giá & Chấm điểm RAG      | `src/evaluation/metrics.py` (Hàm `evaluate_pipeline`) | Vector DB + Test set | `baseline_metrics.json`, `corrupted_metrics.json`... | Hoàn thành |

### Việc hỗ trợ ngoài phạm vi chính

| Hoạt động                         | Thành viên/module được hỗ trợ | Kết quả                    |
| ------------------------------------ | ------------------------------------ | ---------------------------- |
| Debug lỗi tích hợp toàn hệ thống CP1, CP3 | Hỗ trợ Thành viên 1 (`phase1.py` và `corruption_flow.py`) | Sửa lỗi khởi tạo `Settings()` thành `load_settings()`, sửa lỗi sai field config của class `Paths`, vá lỗi đường dẫn Python `sys.path`. |

## 3. Kết quả theo vai trò

| Nhiệm vụ đã thực hiện | File/hàm/artifact liên quan | Kết quả bàn giao       | Cách xác minh         |
| --------------------------- | ----------------------------- | ------------------------- | ----------------------- |
| Xây dựng thành công bộ Test set gồm 20 câu hỏi bám sát dữ liệu thực tế | `src/evaluation/testset.py` | `data/eval/test_set.json` | Đọc file JSON trực tiếp |
| Sinh bảng điểm đo lường độ suy giảm của RAG khi gặp dữ liệu bẩn | `src/evaluation/metrics.py` | `data/results/corrupted_metrics.json` | Mở xem kết quả metric |

Nêu một output cụ thể mà phần việc của bạn tạo ra hoặc giúp xác minh:
Tạo ra các file `*_metrics.json` đóng vai trò là "thước đo" để cả nhóm thấy được mức độ nguy hiểm của Dữ liệu bẩn (Làm tụt Retrieval Hit Rate từ 1.0 xuống 0.8).

## 4. Giải thích phần kỹ thuật đã thực hiện

### Vấn đề cần giải quyết
Kiểm thử thủ công (gõ từng câu hỏi rồi tự đọc câu trả lời) không thể scale khi làm Data Pipeline. Cần một cơ chế (LLM as a Judge) tự động đọc Test Set, gọi Vector DB để sinh câu trả lời, và chấm điểm tự động.

### Cách triển khai
- **Tạo Test Set:** Thay vì tự nghĩ câu hỏi, code quét qua `clean_df`, lọc ra các bài có `authors_joined` hoặc `categories_joined` không rỗng, từ đó sinh ra câu hỏi theo pattern "Ai là tác giả của..." và lưu Ground Truth là doc_id tương ứng.
- **Chấm điểm:** LLM so sánh câu trả lời của RAG System với Ground Truth (được truyền sẵn trong Test Set).

### Input, output và contract

| Thành phần                   | Mô tả                                     |
| ------------------------------ | ------------------------------------------- |
| Input                          | `clean_df` (Dữ liệu đã làm sạch do TV1 bàn giao) |
| Output                         | `test_set.json` (Bộ 20 câu) và `metrics.json` |
| Module phụ thuộc             | `src/evaluation/testset.py`, `src/retrieval/index.py` |
| Module sử dụng output        | `src/observability/reporting.py` (của TV3 dùng metric để sinh báo cáo) |
| Điều kiện lỗi cần xử lý | Xử lý lỗi mảng giá trị của pandas khi lọc rows (dùng chuỗi `_joined` thay vì list). |

### Cách xác minh

```bash
python script/run_phase1.py
python script/run_corruption_flow.py
```

## 5. Một quyết định kỹ thuật quan trọng

- **Bối cảnh:** Lựa chọn phương pháp xử lý lỗi array khi sinh Test Set (`ValueError: The truth value of an array with more than one element is ambiguous`).
- **Các phương án đã cân nhắc:** 1. Viết hàm lambda check array. 2. Dùng thẳng các field đã được ghép thành chuỗi (`authors_joined`, `categories_joined`).
- **Phương án đã chọn:** Dùng field dạng chuỗi (`_joined`).
- **Lý do:** Trade-off về độ phức tạp. Việc check chuỗi `pd.notna()` và `.strip()` an toàn, dễ code hơn rất nhiều so với chọc vào trong mảng.
- **Bằng chứng quyết định phù hợp:** Chạy lệnh `run_phase1.py` sinh Test set 20 câu thành công tuyệt đối.

## 6. Một lỗi hoặc blocker đã xử lý

- **Triệu chứng/lỗi nguyên văn:** `ValueError: The truth value of an array with more than one element is ambiguous. Use a.any() or a.all()`
- **Lệnh hoặc bước tái hiện:** Chạy `build_test_set` trên các bài báo có nhiều tác giả (lưu dạng mảng).
- **Nguyên nhân gốc:** Pandas không cho phép dùng `pd.notna()` trực tiếp trên một cell chứa list.
- **Cách xử lý:** Đổi `row['authors']` thành `row['authors_joined']`.
- **Cách xác minh sau khi sửa:** Chạy lại `python script/run_phase1.py` và luồng đi qua mượt mà.
- **Điều học được:** Luôn phải cực kỳ cẩn thận với kiểu dữ liệu của Pandas khi dùng chung với logic boolean.

## 7. Hiểu biết về luồng end-to-end

1. Dữ liệu đi từ API Crossref -> Raw (JSON/CSV) -> Được clean để xóa dòng trống/xử lý mảng -> Build thành các Document có chứa Embeddings lưu vào ChromaDB (Vector Index).
2. Evaluation set chứa sẵn câu hỏi và ID bài báo (Ground Truth). Khi chấm điểm, ta kiểm tra xem RAG có mò ra đúng cái ID bài báo Ground truth đó không (để tính Hit rate).
3. Quality checks đo độ bẩn của Dữ liệu (số null, schema). Còn Freshness monitoring đo độ cũ của bài báo (Age days) so với thời điểm hiện tại.
4. Việc dùng chung 1 test set là BẮT BUỘC. Nếu đổi test set khác, ta không thể chứng minh được độ tụt điểm (Delta) là do dữ liệu bẩn, mà người khác sẽ cãi là do "bộ câu hỏi sau khó hơn bộ câu hỏi trước".
5. Repair thành công dựa trên 2 yếu tố: Quality Checks pass (hết data bẩn) và RAG Metrics phục hồi lại mốc Baseline (chứng minh ở file `corruption_report.md`).

## 8. Phân tích kết quả

### Metrics chính

| Metric/signal          | Baseline | Corrupted | Repaired | Nhận xét của cá nhân |
| ---------------------- | -------: | --------: | -------: | ------------------------- |
| `retrieval_hit_rate` |      1.0 |       0.8 |      1.0 | Data bẩn làm RAG tìm sai tài liệu hẳn 20% |
| `mean_token_f1`      |      0.0623 |       0.0554 |      0.0623 | Câu trả lời của AI kém sát nghĩa hơn khi bị nhiễu |
| Quality checks         |      True |       False |      True | Phát hiện ngay 20% dòng lỗi khi làm bẩn |
| Freshness status       |      Fresh |       True |      True | |

### Kết luận từ số liệu

1. **[Làm bẩn Data]** → [Sinh ra null/text nhiễu, Quality check Fail] → [Hit Rate tụt từ 1.0 xuống 0.8, trả lời sai].
2. **[Khôi phục Data bằng Raw]** → [Quality check Pass 100%] → [Hit Rate phục hồi lại 1.0].

**Corruption nào ảnh hưởng rõ nhất và vì sao?**
Việc truncate (cắt cụt) Title và nhét Noise vào nội dung tác động mạnh nhất. RAG hoàn toàn bị "mù" khi Embeddings sinh ra từ đoạn text nhiễu không còn khớp với Embeddings của câu hỏi Test set.

## 9. Điều học được và hướng cải thiện

### Ba điều quan trọng nhất

1. Garbage In, Garbage Out: Model xịn đến mấy mà Data bẩn thì kết quả RAG vẫn sai bét.
2. Việc chia tách Baseline, Corrupted và Repaired ra các VectorDB riêng biệt là tối quan trọng để có thể so sánh chéo.
3. RAG Agent có tính ngẫu nhiên nên bộ Eval cần có Ground Truth cố định (như Doc ID) để đo đạc sự chính xác một cách máy móc, thay vì chấm dựa trên cảm tính.

### Nếu có thêm thời gian

Mình muốn thêm cơ chế Retry ở tầng RAG: Nếu VectorDB trả về Context quá kém chất lượng (Cosine similarity thấp), hệ thống sẽ chủ động tự cảnh báo thay vì cố ép LLM phải "bịa" ra câu trả lời dựa trên context rác.

## 10. Cam kết của thành viên

- [x] Nội dung báo cáo phản ánh đúng phần việc và mức hiểu của tôi.
- [x] Tôi có thể giải thích luồng end-to-end, không chỉ module mình phụ trách.
- [x] Mọi kết luận về kết quả đều có artifact hoặc metric để đối chiếu.
- [x] Tôi không ghi “đã chạy thành công” cho phần chưa được kiểm chứng.
- [x] Báo cáo không chứa `.env`, API key, token hoặc secret.
- [x] Báo cáo này không phải bản sao nguyên văn của báo cáo nhóm hoặc báo cáo thành viên khác.

**Họ và tên:** Phạm Kiên
**Ngày xác nhận:** 2026-08-06
