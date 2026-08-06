# Member Role Report — Day 10: Data Pipeline & Data Observability

## 1. Thông tin cá nhân

| Thông tin         | Nội dung                  |
| ------------------ | -------------------------- |
| Họ và tên       | **Vũ Minh Quang**             |
| MSSV               | **2A202601515**                     |
| Khóa/Lớp         | **K3**              |
| Tên nhóm         | **ricon**     |
| Vai trò chính    | **Trưởng nhóm (Lead + Ingest + Clean - Thành viên 1)**                 |
| Repository         | **https://github.com/mquangggg/K3_Day10_Data-Pipeline-Data-Observability-ricon** |
| Ngày hoàn thành | **2026-08-06**               |

## 2. Vai trò và phạm vi công việc

### Phần việc sở hữu

| Module/deliverable | File/hàm phụ trách | Input nhận vào | Output bàn giao  | Trạng thái                                 |
| ------------------ | --------------------- | ---------------- | ----------------- | -------------------------------------------- |
| Crossref Ingestion | [src/ingestion/crossref.py](file:///c:/Lab_10/K3_Day10_Data-Pipeline-Data-Observability-ricon/src/ingestion/crossref.py)<br>`fetch_source_records`, `load_raw_records` | Query, filter, max_results từ Settings | Raw response JSON & `crossref_records.json` (24 bản ghi thô) | Hoàn thành |
| Data Cleaning | [src/ingestion/cleaning.py](file:///c:/Lab_10/K3_Day10_Data-Pipeline-Data-Observability-ricon/src/ingestion/cleaning.py)<br>`build_clean_dataframe` | Raw records list & `run_date` | `papers_clean.csv` & `papers_clean.json` (24 bản ghi sạch) | Hoàn thành |
| Baseline Pipeline Orchestration | [src/pipelines/phase1.py](file:///c:/Lab_10/K3_Day10_Data-Pipeline-Data-Observability-ricon/src/pipelines/phase1.py)<br>`main()` | Settings, raw records | Baseline artifacts, vector index `papers-baseline`, baseline report | Hoàn thành |
| Corruption & Recovery Flow | [src/pipelines/corruption_flow.py](file:///c:/Lab_10/K3_Day10_Data-Pipeline-Data-Observability-ricon/src/pipelines/corruption_flow.py)<br>`main()` | Clean DF, raw records | Corrupted & Repaired artifacts, comparison report | Hoàn thành |

### Việc hỗ trợ ngoài phạm vi chính

| Hoạt động                         | Thành viên/module được hỗ trợ | Kết quả                    |
| ------------------------------------ | ------------------------------------ | ---------------------------- |
| Handoff Clean Schema & Data Lineage | Thành viên 2 (Pham Kien - RAG/Eval) | Bàn giao schema `papers_clean.csv` với 100% unique `paper_id` dạng DOI để xây dựng Vector DB và Test Set 20 câu hỏi. |
| Tích hợp Quality Checks & Reporting | Thành viên 3 (quangln2205 - Observability) | Sửa lỗi import `LocalEmbeddingIndex`, khớp tham số 10 argument cho `generate_corruption_report` giúp xuất báo cáo Markdown tự động. |

## 3. Kết quả theo vai trò

| Nhiệm vụ đã thực hiện | File/hàm/artifact liên quan | Kết quả bàn giao       | Cách xác minh         |
| --------------------------- | ----------------------------- | ------------------------- | ----------------------- |
| Ingestion dữ liệu từ Crossref API | [src/ingestion/crossref.py](file:///c:/Lab_10/K3_Day10_Data-Pipeline-Data-Observability-ricon/src/ingestion/crossref.py) | [data/raw/crossref_records.json](file:///c:/Lab_10/K3_Day10_Data-Pipeline-Data-Observability-ricon/data/raw/crossref_records.json) | Kiểm tra 24 bài báo thô với retry 3 lần exponential backoff. |
| Data Cleaning & Normalization | [src/ingestion/cleaning.py](file:///c:/Lab_10/K3_Day10_Data-Pipeline-Data-Observability-ricon/src/ingestion/cleaning.py) | [data/clean/papers_clean.csv](file:///c:/Lab_10/K3_Day10_Data-Pipeline-Data-Observability-ricon/data/clean/papers_clean.csv) | Kiểm tra `authors_joined`, `categories_joined`, `summary_chars`, `age_days`, `text_for_embedding`. |
| Điều phối Luồng Baseline | [src/pipelines/phase1.py](file:///c:/Lab_10/K3_Day10_Data-Pipeline-Data-Observability-ricon/src/pipelines/phase1.py) | [data/reports/phase1_report.md](file:///c:/Lab_10/K3_Day10_Data-Pipeline-Data-Observability-ricon/data/reports/phase1_report.md) | Chạy `python script/run_phase1.py` đạt Retrieval Hit Rate = 1.0000. |
| Điều phối Luồng Corruption & Recovery | [src/pipelines/corruption_flow.py](file:///c:/Lab_10/K3_Day10_Data-Pipeline-Data-Observability-ricon/src/pipelines/corruption_flow.py) | [data/reports/corruption_report.md](file:///c:/Lab_10/K3_Day10_Data-Pipeline-Data-Observability-ricon/data/reports/corruption_report.md) | Chạy `python script/run_corruption_flow.py` chứng minh phục hồi Hit Rate từ 0.8000 lên 1.0000. |

Nêu một output cụ thể mà phần việc của bạn tạo ra hoặc giúp xác minh:

> Bàn giao dữ liệu sạch `data/clean/papers_clean.csv` (24 bản ghi) và tệp báo cáo so sánh `data/reports/corruption_report.md` thể hiện chính xác chỉ số `Retrieval Hit Rate` sụt giảm từ 1.0000 xuống 0.8000 ở bản lỗi và hồi phục lại 1.0000 sau khi Repair.

## 4. Giải thích phần kỹ thuật đã thực hiện

### Vấn đề cần giải quyết

Đảm bảo dữ liệu đầu vào cho RAG Agent được thu thập chuẩn xác từ Crossref API, được làm sạch theo đúng schema thỏa thuận, tạo mã `paper_id` ổn định duy nhất xuyên suốt Data Lineage và kết nối toàn bộ 3 mô-đun (Ingestion, RAG/Eval, Observability) vào một pipeline chạy tự động.

### Cách triển khai

1. **Ingestion (`crossref.py`):** Lập trình hàm `fetch_source_records` gọi Crossref REST API với `requests` và cơ chế retry có delay lũy thừa cho các mã lỗi 429/503. Chuẩn hóa DOI thành dạng `doi_10_...` làm `paper_id`.
2. **Data Cleaning (`cleaning.py`):** Lập trình `build_clean_dataframe` loại bỏ bản ghi thiếu title/summary, xử lý khoảng trắng rác, ghép danh sách tác giả (`authors_joined`), thể loại (`categories_joined`), tính `age_days` so với ngày chạy và xây dựng chuỗi tổng hợp `text_for_embedding`.
3. **Pipeline Orchestration (`phase1.py` & `corruption_flow.py`):** Điều phối lần lượt 4 giai đoạn: Nạp dữ liệu thô $\rightarrow$ Làm sạch $\rightarrow$ Đánh chỉ mục Vector $\rightarrow$ Chấm điểm Test set $\rightarrow$ Xuất báo cáo Markdown.

### Input, output và contract

| Thành phần                   | Mô tả                                     |
| ------------------------------ | ------------------------------------------- |
| Input                          | Crossref API responses / `crossref_records.json` thô |
| Output                         | `papers_clean.csv` & `papers_clean.json` (Data Contract khóa cố định) |
| Module phụ thuộc             | `core.config` (Settings), `core.utils` |
| Module sử dụng output        | `retrieval.index` (Thành viên 2), `evaluation.testset` (Thành viên 2), `observability.quality` (Thành viên 3) |
| Điều kiện lỗi cần xử lý | Mạng gián đoạn (Retry backoff 429/503), DOI có ký tự đặc biệt, summary chứa khoảng trắng rác |

### Cách xác minh

```bash
.venv\Scripts\python.exe script/run_phase1.py
.venv\Scripts\python.exe script/run_corruption_flow.py
```

- **Kết quả mong đợi:** Pipeline chạy thành công không văng lỗi, sinh ra đủ kết quả Baseline (Hit Rate = 1.0000), Corrupted (Hit Rate = 0.8000, Quality Passed = False) và Repaired (Hit Rate = 1.0000, Quality Passed = True).
- **Kết quả thực tế:** 100% khớp mong đợi.
- **Artifact/log:** [data/reports/phase1_report.md](file:///c:/Lab_10/K3_Day10_Data-Pipeline-Data-Observability-ricon/data/reports/phase1_report.md) & [data/reports/corruption_report.md](file:///c:/Lab_10/K3_Day10_Data-Pipeline-Data-Observability-ricon/data/reports/corruption_report.md).

## 5. Một quyết định kỹ thuật quan trọng

- **Bối cảnh:** Cần chọn một identifier duy nhất và ổn định cho mỗi bài báo để làm khóa chính (Primary Key) kết nối giữa Raw Record, Clean CSV, Vector Index, và Test Set.
- **Các phương án đã cân nhắc:** 
  1. Phương án A: Dùng UUID ngẫu nhiên cho mỗi lần chạy pipeline (`uuid.uuid4()`).
  2. Phương án B: Dùng mã DOI từ Crossref được chuẩn hóa thành chuỗi `doi_10_...`.
- **Phương án đã chọn:** Phương án B (`doi_10_...`).
- **Lý do:** DOI là định danh chuẩn quốc tế của bài báo. Khi chuẩn hóa thành `doi_10_...` (thay `/` và `.` bằng `_`), định danh này tồn tại cố định tuyệt đối qua mọi lần chạy, giúp bộ câu hỏi `test_set.json` luôn liên kết đúng `ground_truth_doc_ids` dù dữ liệu bị corrupt hay repair.
- **Bằng chứng quyết định phù hợp:** Kiểm tra Data Lineage ở CP2 và CP5 cho thấy `paper_id` khớp 100% xuyên suốt từ raw $\rightarrow$ clean $\rightarrow$ embeddings $\rightarrow$ test set.

## 6. Một lỗi hoặc blocker đã xử lý

- **Triệu chứng/lỗi nguyên văn:**
  ```text
  TypeError: Settings.__init__() missing 23 required positional arguments
  ImportError: cannot import name 'build_chroma_index' from 'retrieval.index'
  ```
- **Lệnh hoặc bước tái hiện:** `python script/run_phase1.py`
- **Nguyên nhân gốc:** 
  1. Class `Settings` trong `core/config.py` là một `@dataclass` đòi hỏi khởi tạo qua hàm factory `load_settings()`.
  2. File `phase1.py` và `corruption_flow.py` nhập tên hàm cũ `build_chroma_index` vốn đã được tái cấu trúc thành phương thức `LocalEmbeddingIndex.build()`.
- **Cách xử lý:** 
  1. Sửa `Settings()` thành `load_settings()`.
  2. Thay `build_chroma_index` thành `LocalEmbeddingIndex.build(clean_df, settings)`.
- **Cách xác minh sau khi sửa:** Chạy lại `.venv\Scripts\python.exe script/run_phase1.py` cho kết quả exit code 0.
- **Điều học được:** Khi làm việc nhóm, cần đọc kỹ interface/signature của các class chung trước khi gọi để tránh lệch data contract.

## 7. Hiểu biết về luồng end-to-end

**Câu trả lời:**

1. **Dữ liệu đi từ Crossref đến vector index như thế nào?**
   Dữ liệu được `crossref.py` nạp từ API $\rightarrow$ lưu JSON thô $\rightarrow$ `cleaning.py` chuẩn hóa văn bản, ghép tác giả/thể loại, tính `text_for_embedding` $\rightarrow$ `index.py` dùng mô hình `all-MiniLM-L6-v2` đổi chuỗi thành vector 384 chiều $\rightarrow$ lưu trữ vào cơ sở dữ liệu Vector ChromaDB (`papers-baseline`).

2. **Evaluation set và ground-truth document IDs dùng để đo retrieval/answer quality ra sao?**
   Bộ `test_set.json` lưu câu hỏi kèm `ground_truth_doc_ids` (chứa `paper_id` chuẩn). Khi Evaluator chạy, nó truyền câu hỏi cho Agent/Index tìm kiếm top-K kết quả. Nếu `paper_id` của tài liệu retrieved trùng với `ground_truth_doc_ids`, `retrieval_hit_rate` tính là 1 (Hit), ngược lại là 0 (Miss).

3. **Quality checks khác freshness monitoring ở điểm nào trong bài lab?**
   - **Quality checks:** Kiểm tra tính toàn vẹn và hợp lệ của cấu trúc dữ liệu (số dòng, trùng lặp `paper_id`, null title, rỗng summary).
   - **Freshness monitoring:** Kiểm tra tính mới của dữ liệu theo mốc thời gian (`age_days` tính từ ngày xuất bản so với ngưỡng `freshness_threshold_days`).

4. **Vì sao phải dùng cùng test set cho baseline, corrupted và repaired?**
   Để đảm bảo tính nhất quán (Controlled Experiment). Khi giữ nguyên bộ đề thi `test_set.json`, bất kỳ sự thay đổi nào về chỉ số (`Hit Rate` giảm từ 1.0000 $\rightarrow$ 0.8000) đều phản ánh chính xác tác động của việc hỏng dữ liệu, chứ không phải do câu hỏi thay đổi.

5. **Repair được xem là thành công dựa trên artifact và metric nào?**
   Repair thành công khi:
   - Signal Quality Gates trong `repaired_quality.json` quay lại `passed = True`.
   - Báo cáo `corruption_report.md` ghi nhận `retrieval_hit_rate` phục hồi từ 0.8000 trở lại 1.0000 ($\Delta = +0.2000$).

## 8. Phân tích kết quả

### Metrics chính

| Metric/signal          | Baseline | Corrupted | Repaired | Nhận xét của cá nhân |
| ---------------------- | -------: | --------: | -------: | ------------------------- |
| `retrieval_hit_rate` |   1.0000 |    0.8000 |   1.0000 | Giảm 20% khi dữ liệu bị hỏng, phục hồi hoàn toàn sau khi repair. |
| `mean_token_f1`      |   0.0623 |    0.0554 |   0.0623 | Token F1 bị suy giảm nhẹ khi summary bị xóa/nhiễu. |
| `judge_accuracy`     |   0.0000 |    0.0000 |   0.0000 | Không bật LLM Judge nâng cao ở chạy thử nghiệm cục bộ. |
| `mean_judge_score`   |   0.0000 |    0.0000 |   0.0000 | Không bật LLM Judge nâng cao ở chạy thử nghiệm cục bộ. |
| Quality checks         |  ✅ Pass |    ❌ Fail |  ✅ Pass | Quality Gate phát hiện chính xác 2 dòng bị rỗng summary ở bản corrupted. |
| Freshness status       | ✅ Fresh |  ✅ Fresh | ✅ Fresh | Ngày xuất bản bài báo nằm trong ngưỡng cho phép (<= 180 ngày). |

### Kết luận từ số liệu

1. **[Data corruption]** (xóa bản ghi & rỗng summary) $\rightarrow$ **[quality signal `passed = False`]** $\rightarrow$ **[agent metric `retrieval_hit_rate` giảm từ 1.0000 xuống 0.8000]**.
2. **[Repair action]** (làm sạch lại từ nguồn thô `crossref_records.json`) $\rightarrow$ **[quality signal `passed = True`]** $\rightarrow$ **[agent metric `retrieval_hit_rate` phục hồi 100% về 1.0000]**.

**Corruption nào ảnh hưởng rõ nhất và vì sao?**
Hành động xóa bản ghi (Drop rows) và rỗng summary ảnh hưởng nghiêm trọng nhất vì làm mất hẳn thông tin ngữ nghĩa làm cho mô hình Vector không thể tìm ra đúng bài báo chứa đáp án.

## 9. Điều học được và hướng cải thiện

### Ba điều quan trọng nhất

1. **Tầm quan trọng của Single Source of Truth:** Dữ liệu thô gốc (`raw records`) cần được bảo quản nguyên vẹn để phục vụ quy trình Data Recovery tự động khi dữ liệu sạch bị nhiễm bẩn.
2. **Data Observability là lá chắn:** Hệ thống Quality Gates phát hiện lỗi sớm trước khi dữ liệu xấu đi vào Vector DB làm hỏng kết quả của RAG Agent.
3. **Data Lineage:** Mã định danh duy nhất (`paper_id`) xuyên suốt là yếu tố quyết định để truy vết và đánh giá đúng hiệu năng pipeline.

### Nếu có thêm thời gian

Thêm cơ chế tự động cảnh báo (Alerting webhook) khi Quality Gate báo `passed = False` để tự động kích hoạt luồng Repair mà không cần can thiệp thủ công.

## 10. Cam kết của thành viên

Đánh dấu sau khi tự kiểm tra:

- [x] Nội dung báo cáo phản ánh đúng phần việc và mức hiểu của tôi.
- [x] Tôi có thể giải thích luồng end-to-end, không chỉ module mình phụ trách.
- [x] Mọi kết luận về kết quả đều có artifact hoặc metric để đối chiếu.
- [x] Tôi không ghi “đã chạy thành công” cho phần chưa được kiểm chứng.
- [x] Báo cáo không chứa `.env`, API key, token hoặc secret.
- [x] Báo cáo này không phải bản sao nguyên văn của báo cáo nhóm hoặc báo cáo thành viên khác.

**Họ và tên:** **Vũ Minh Quang**  
**Ngày xác nhận:** **2026-08-06**
