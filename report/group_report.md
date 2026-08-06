# Group Report — Day 10: Data Pipeline & Data Observability

## 1. Thông tin bài nộp

| Thông tin         | Nội dung                  |
| ------------------ | -------------------------- |
| Khóa/Lớp         | **K3**              |
| Tên nhóm         | **ricon**     |
| Repository         | **https://github.com/mquangggg/K3_Day10_Data-Pipeline-Data-Observability-ricon** |
| Ngày hoàn thành | **2026-08-06**               |

### Thành viên và phân công

| STT | Họ và tên | MSSV | Vai trò chính | Module/deliverable sở hữu |
| --: | --- | --- | --- | --- |
| 1 | **Vũ Minh Quang** | **2A202601515** | Trưởng nhóm (Lead + Ingest + Clean) | `crossref.py`, `cleaning.py`, `phase1.py`, `corruption_flow.py` |
| 2 | **Phạm Trung Kiên** | **2A202601525** | RAG & Evaluation Owner | `index.py`, `testset.py`, `metrics.py`, `agent.py` |
| 3 | **Lương Ngọc Quang** | **2A202601563** | Observability & Reporting Owner | `quality.py`, `reporting.py`, `check_corrupted_quality.py` |

## 2. Tóm tắt kết quả

Nhóm **ricon** đã hoàn thành 100% các mục tiêu từ CP0 đến CP6 trong bài Lab Day 10. Hệ thống Data Pipeline & Data Observability được xây dựng tự động end-to-end kết nối 4 mảng: Ingestion từ Crossref API, Data Cleaning & Normalization, Vector Indexing (ChromaDB `all-MiniLM-L6-v2`) & RAG Evaluation, cùng với hệ thống Quan sát Data Quality Gates & Freshness Monitoring.

Pipeline cơ bản (Baseline) thu thập 24 bài báo thô, làm sạch đạt 100% duy nhất `paper_id` và đạt điểm số `Retrieval Hit Rate` tối đa **1.0000** trên bộ đề thi 20 câu hỏi `test_set.json`.

Khi thực hiện kịch bản hỏng dữ liệu có kiểm soát (Controlled Corruption), chất lượng RAG suy giảm rõ rệt: `Retrieval Hit Rate` sụt giảm 20% xuống còn **0.8000**, đồng thời hệ thống Quality Gates phát hiện lỗi sớm và chuyển trạng thái sang **`passed = False`** (phát hiện các dòng bị rỗng summary và tiêu đề bị biến dạng).

Nhờ cơ chế lưu trữ dữ liệu thô ban đầu làm Single Source of Truth, luồng Recovery (`build_clean_dataframe`) khôi phục lại 100% dữ liệu sạch mà không cần can thiệp thủ công, đưa `Retrieval Hit Rate` phục hồi hoàn toàn trở lại **1.0000** và Quality Gates khôi phục lại **`passed = True`**.

**Tóm tắt của nhóm:**

> Nhóm đã chứng minh được vai trò quyết định của Data Observability: giúp phát hiện lỗi nhiễm bẩn dữ liệu sớm trước khi dữ liệu xấu đi vào Vector DB làm giảm hiệu năng của RAG Agent, đồng thời khẳng định giá trị của cơ chế tự động khôi phục dữ liệu từ nguồn gốc tin cậy.

## 3. Kiến trúc và luồng dữ liệu

### Luồng end-to-end

```text
Crossref REST API
    -> raw response/raw records (data/raw/crossref_records.json)
    -> cleaning & data modeling (data/clean/papers_clean.csv)
    -> embedding + ChromaDB index (papers-baseline)
    -> evaluation baseline (data/results/baseline_metrics.json, Hit Rate = 1.0000)
    -> quality/freshness reports (data/quality/baseline_quality.json)
    -> controlled corruption (papers_clean_corrupted.csv)
    -> re-index & re-evaluate (papers-corrupted, Hit Rate = 0.8000, Quality = Fail)
    -> repair từ dữ liệu nguồn thô (papers_clean_repaired.csv)
    -> re-index & re-evaluate (papers-repaired, Hit Rate = 1.0000, Quality = Pass)
    -> comparison report (data/reports/corruption_report.md)
```

### Trách nhiệm của từng khối

| Khối             | Input          | Xử lý chính             | Output/artifact          | Owner          |
| ----------------- | -------------- | -------------------------- | ------------------------ | -------------- |
| Ingestion         | Crossref REST API | Fetch API, HTTP 429/503 retry, parse DOI | `data/raw/crossref_records.json` | Vũ Minh Quang |
| Cleaning          | Raw records list | Whitespace clean, `authors_joined`, `categories_joined`, `age_days`, `text_for_embedding` | `data/clean/papers_clean.csv` | Vũ Minh Quang |
| Embedding/index   | Clean DataFrame | `all-MiniLM-L6-v2`, ChromaDB collection building | `data/embeddings/papers_embeddings.json` | Phạm Trung Kiên |
| Evaluation        | Clean DataFrame & Index | Generator `build_test_set`, `evaluate_pipeline` | `data/eval/test_set.json`, `baseline_metrics.json` | Phạm Trung Kiên |
| Observability     | Clean DataFrame | Data Quality Gates (null, duplicate, summary), Freshness report | `data/quality/baseline_quality.json`, `freshness_report.json` | Lương Ngọc Quang |
| Corruption/repair | Clean DataFrame & Raw records | 6 kịch bản gây lỗi, repair tự động từ raw records | `papers_clean_corrupted.csv`, `papers_clean_repaired.csv` | Vũ Minh Quang |
| Orchestration     | Settings & Pipeline Modules | Điều phối luồng `phase1.py` & `corruption_flow.py` | `phase1_report.md`, `corruption_report.md` | Vũ Minh Quang |

## 4. Cách tái hiện kết quả

### Cấu hình không chứa secret

| Biến/cấu hình             | Giá trị sử dụng |
| ---------------------------- | ------------------- |
| `LLM_PROVIDER`             | `google` (hoặc `custom`) |
| `LLM_MODEL`                | `gemini-1.5-flash` |
| Embedding model              | `sentence-transformers/all-MiniLM-L6-v2` |
| Số lượng Crossref records | 24 records |
| Retrieval `top_k`          | 4 |
| Freshness threshold          | 180 days |
| Random seed                 | 42 |

### Lệnh cài đặt

```bash
python -m pip install -e .
```

### Lệnh chạy

Baseline pipeline:

```bash
python script/run_phase1.py
```

Corruption flow:

```bash
python script/run_corruption_flow.py
```

### Kết quả tái hiện

| Lệnh             | Trạng thái                                    | Thời điểm chạy gần nhất | Bằng chứng                         |
| ----------------- | ----------------------------------------------- | ----------------------------- | ------------------------------------ |
| Baseline pipeline | Thành công | 2026-08-06 11:34:29 | `data/reports/phase1_report.md` (Hit Rate = 1.0000) |
| Corruption flow   | Thành công | 2026-08-06 11:39:24 | `data/reports/corruption_report.md` (Delta Hit Rate = +0.2000) |

## 5. Ingestion, cleaning và data contract

### Nguồn dữ liệu

| Thuộc tính                | Giá trị                             |
| --------------------------- | ------------------------------------- |
| Source                      | Crossref REST API (`https://api.crossref.org/works`) |
| Query/filter                | `agentic retrieval augmented generation large language model` |
| Thời điểm lấy dữ liệu | 2026-08-06 |
| Số record nhận được    | 24 records |
| Cơ chế retry/backoff      | 3 retries với exponential backoff cho HTTP status 429/503 |

### Raw và clean schema

| Trường        | Kiểu dữ liệu | Bắt buộc?  | Ý nghĩa   | Xử lý khi thiếu/sai |
| --------------- | --------------- | ------------ | ----------- | ---------------------- |
| `paper_id` | string | Có | Định danh chuẩn hóa dạng `doi_10_...` | Tự sinh từ DOI hoặc gán fallback hash |
| `title` | string | Có | Tiêu đề bài báo | Bỏ qua bản ghi nếu thiếu title |
| `summary` | string | Có | Tóm tắt (Abstract) bài báo | Bỏ qua bản ghi nếu thiếu summary |
| `authors` | list[string] | Không | Danh sách tác giả | Gán `["Unknown"]` nếu thiếu |
| `published` | string (YYYY-MM-DD) | Có | Ngày xuất bản | Fallback về `1970-01-01` |
| `authors_joined` | string | Có | Chuỗi tác giả nối bằng dấu phẩy | Tạo từ `authors` |
| `categories_joined` | string | Có | Chuỗi thể loại nối bằng dấu phẩy | Tạo từ `categories` |
| `summary_chars` | int | Có | Độ dài ký tự của tóm tắt | Tính `len(summary)` |
| `age_days` | int | Có | Số ngày tuổi so với ngày chạy | Tính `(run_date - published).days` |
| `text_for_embedding` | string | Có | Văn bản hợp nhất dùng nhúng vector | Kết hợp title, summary, authors, categories |

### Quy tắc cleaning

| Quy tắc                                 | Quality dimension liên quan | Số record bị tác động | Cách xác minh      |
| ---------------------------------------- | ---------------------------- | -------------------------: | -------------------- |
| Loại bỏ bản ghi rỗng title/summary | Completeness | 0 bản ghi lỗi | `papers_clean.csv` (24/24 đủ) |
| Kiểm tra trùng lặp `paper_id` | Uniqueness | 0 bản ghi trùng | `df['paper_id'].is_unique == True` |
| Chuẩn hóa khoảng trắng rác | Validity | 24 bản ghi | Kiểm tra chuỗi sau `strip()` |

**Giải thích cách tạo `text_for_embedding`, document ID và `age_days`:**
- `paper_id`: Lấy DOI từ Crossref, thay toàn bộ `/` và `.` thành `_` để tạo chuỗi an toàn `doi_10_...`.
- `text_for_embedding`: Hợp nhất `title + " " + summary + " " + authors_joined + " " + categories_joined`.
- `age_days`: Ép kiểu `published` thành datetime và tính số ngày chênh lệch so với `run_date` hiện tại.

## 6. Evaluation setup

| Thành phần                             | Cấu hình thực tế          |
| ---------------------------------------- | ----------------------------- |
| Số câu hỏi                            | 20 câu hỏi |
| Các `question_type`                    | `authors`, `summary`, `date`, `categories` |
| Ground-truth document ID                 | Mảng chứa `paper_id` chuẩn của bài báo gốc |
| Embedding model                          | `sentence-transformers/all-MiniLM-L6-v2` |
| Vector store/collection                  | ChromaDB (`papers-baseline`) |
| Retrieval `top_k`                       | 4 |
| LLM provider/model                       | Google Gemini (`gemini-1.5-flash`) |
| Test set dùng chung cho ba trạng thái | `data/eval/test_set.json` |

**Giải thích vì sao test set được giữ nguyên khi đánh giá baseline, corrupted và repaired:**
Việc giữ nguyên bộ `test_set.json` đảm bảo nguyên tắc của một bài thí nghiệm có đối chứng (Controlled Experiment). Bất kỳ biến động nào về kết quả đánh giá (Hit Rate sụt giảm từ 1.0000 xuống 0.8000) đều phản ánh đúng tác động của việc nhiễm bẩn dữ liệu, chứ không phải do đề thi bị thay đổi.

## 7. Kết quả baseline

### Artifact checklist

| Artifact                 | Đường dẫn thực tế                | Trạng thái | Ghi chú   |
| ------------------------ | -------------------------------------- | ------------ | ---------- |
| Raw response/records     | `data/raw/crossref_records.json` | Có | 24 bài báo thô |
| Cleaned dataset          | `data/clean/papers_clean.csv` | Có | 24 bài báo sạch |
| Embedding manifest/index | `data/embeddings/papers_embeddings.json` | Có | Manifest 24 docs |
| Evaluation set           | `data/eval/test_set.json` | Có | 20 câu hỏi test set |
| Baseline metrics         | `data/results/baseline_metrics.json` | Có | Hit Rate = 1.0000 |
| Quality/freshness        | `data/quality/baseline_quality.json` | Có | Quality Passed = True |
| Baseline report          | `data/reports/phase1_report.md` | Có | Báo cáo Markdown Baseline |

### Baseline metrics

| Metric                 |       Giá trị | Diễn giải                             |
| ---------------------- | --------------: | --------------------------------------- |
| `retrieval_hit_rate` |     **1.0000** | 100% câu hỏi tìm đúng tài liệu chứa đáp án trong Top-4 kết quả. |
| `mean_token_f1`      |     **0.0623** | Độ trùng khớp từ vựng giữa câu trả lời và ground truth. |
| `judge_accuracy`     |     **0.0000** | Không kích hoạt LLM Judge nâng cao ở thử nghiệm cục bộ. |
| `mean_judge_score`   |     **0.0000** | Không kích hoạt LLM Judge nâng cao ở thử nghiệm cục bộ. |

## 8. Data quality và freshness

### Quality checks

| Check        | Quality dimension | Ngưỡng/kỳ vọng | Kết quả baseline      | Bằng chứng |
| ------------ | ----------------- | ------------------ | ----------------------- | ------------ |
| `paper_id_is_unique` | Uniqueness | `True` | `True` (0 trùng) | `baseline_quality.json` |
| `paper_id_null_count` | Completeness | `0` | `0` | `baseline_quality.json` |
| `title_null_count` | Completeness | `0` | `0` | `baseline_quality.json` |
| `summary_empty_count` | Completeness | `0` | `0` | `baseline_quality.json` |
| `passed` | Overall Gate | `True` | `True` | `baseline_quality.json` |

### Freshness

| Thuộc tính               | Giá trị                           |
| -------------------------- | ----------------------------------- |
| Freshness được đo tại | Clean DataFrame (`papers_clean.csv`) |
| Timestamp mới nhất       | `2026-08-05` |
| Ngưỡng freshness         | `180 days` |
| Trạng thái baseline      | **Fresh** (`is_fresh = True`) |
| Lý do                     | Tất cả bài báo đều được xuất bản trong vòng 180 ngày gần đây (`stale_rows = 0`). |

## 9. Corruption scenarios và repair

| Corruption         | Cách tạo | Record bị tác động | Quality signal kỳ vọng | Tác động thực tế | Cách repair   |
| ------------------ | ---------- | ---------------------: | ------------------------ | --------------------- | -------------- |
| Drop records | Xóa ngẫu nhiên bản ghi | 2 records | Giảm tổng số dòng | Giảm Hit Rate xuống 0.8000 | Nạp lại từ `crossref_records.json` |
| Blank summary | Làm rỗng trường `summary` | 2 records | `summary_empty_count > 0` | Quality Passed = `False` | Tái tạo lại từ dữ liệu thô gốc |
| Noise injection | Chèn ký tự nhiễu vào title/authors | 2 records | Biến dạng chuỗi text | Giảm chất lượng nhúng vector | Làm sạch lại từ raw record |
| Wrong date | Đổi ngày về quá khứ xa | 2 records | `stale_rows_count > 0` | Tăng số lượng dòng quá hạn | Lấy lại ngày `published` gốc |

Corruption log:

- Đường dẫn: `data/quality/corruption_log.json`
- Trạng thái: Có
- Nhận xét: Log ghi nhận đầy đủ 6 kịch bản gây hỏng dữ liệu và thông số chi tiết trước/sau khi corrupt.

**Giải thích cách repair đảm bảo dữ liệu được phục hồi từ nguồn đáng tin cậy:**
Hàm repair gọi lại `build_clean_dataframe(raw_records)` trực tiếp từ tệp dữ liệu thô ban đầu `data/raw/crossref_records.json` (Single Source of Truth). Quá trình này tạo lại một file sạch hoàn toàn mới mà không cần vá thủ công hay nắn chỉnh dữ liệu đã hỏng.

## 10. So sánh baseline, corrupted và repaired

| Metric/signal            | Baseline | Corrupted | Repaired | Thay đổi do corruption | Mức phục hồi | Nhận xét   |
| ------------------------ | -------: | --------: | -------: | -----------------------: | --------------: | ------------ |
| `retrieval_hit_rate`   |   1.0000 |    0.8000 |   1.0000 |                 -0.2000 |         +0.2000 | Phục hồi 100% về mức tối đa |
| `mean_token_f1`        |   0.0623 |    0.0554 |   0.0623 |                 -0.0069 |         +0.0069 | Phục hồi độ khớp từ vựng |
| `judge_accuracy`       |   0.0000 |    0.0000 |   0.0000 |                  0.0000 |          0.0000 | N/A |
| Quality checks pass/fail |  ✅ Pass |    ❌ Fail |  ✅ Pass |            Báo lỗi khẩn |     Trở lại xanh | Observability phát hiện và cảnh báo chuẩn |
| Freshness status         |  ✅ Fresh |  ✅ Fresh |  ✅ Fresh |                   Không đổi |        Giữ nguyên | Ngày xuất bản vẫn trong ngưỡng |

**Hai kết luận có quan hệ nhân quả được hỗ trợ bởi artifacts:**

1. **[Data corruption]** (xóa 2 bài báo & làm rỗng 2 summary) $\rightarrow$ **[Quality Gate báo `passed = False` tại `corrupted_quality.json`]** $\rightarrow$ **[RAG Agent bị trượt câu hỏi, `retrieval_hit_rate` sụt giảm 20% từ 1.0000 xuống 0.8000]**.
2. **[Repair action]** (chạy lại pipeline cleaning từ nguồn thô `crossref_records.json`) $\rightarrow$ **[Quality Gate khôi phục `passed = True`]** $\rightarrow$ **[RAG Agent khôi phục 100% `retrieval_hit_rate` trở lại 1.0000]**.

## 11. Vấn đề tích hợp quan trọng

Mô tả một vấn đề phát sinh khi ghép các module trong pipeline và cách nhóm xử lý:

- **Triệu chứng:** Khi chạy `python script/run_phase1.py`, chương trình văng lỗi `TypeError: Settings.__init__() missing required positional arguments` và `ImportError: cannot import name 'build_chroma_index'`.
- **Nguyên nhân:** Class `Settings` trong `core/config.py` yêu cầu khởi tạo thông qua hàm factory `load_settings()`. Đồng thời phương thức build Chroma index đã được tái cấu trúc thành `LocalEmbeddingIndex.build()`.
- **Cách xử lý:** Trưởng nhóm đã cập nhật `src/pipelines/phase1.py` và `src/pipelines/corruption_flow.py` gọi đúng `load_settings()` và `LocalEmbeddingIndex.build(clean_df, settings)`.
- **Cách xác minh:** Chạy thành công lệnh `.venv\Scripts\python.exe script/run_phase1.py` cho kết quả exit code 0.

## 12. Giới hạn và hướng cải thiện

| Giới hạn hiện tại | Ảnh hưởng   | Hướng cải thiện có thể kiểm chứng |
| --------------------- | -------------- | ----------------------------------------- |
| Quy mô dữ liệu nhỏ (24 bản ghi) | Chưa đo được hết độ trễ khi Vector DB lớn | Mở rộng thu thập 500-1000 bản ghi từ Crossref API |
| Kiểm thử repair thủ công bằng lệnh shell | Cần con người kích hoạt khi có sự cố | Tích hợp Webhook tự động chạy Repair khi Quality Gate báo Fail |

## 13. Checklist trước khi nộp

- [x] Thông tin nhóm và repository chính xác.
- [x] Phân công khớp với module, artifact và kết quả thực tế của 3 thành viên (`01515`, `01525`, `01563`).
- [x] Lệnh tái hiện đã được chạy lại trên phiên bản dùng để nộp.
- [x] Baseline, corrupted và repaired dùng cùng evaluation set.
- [x] Bảng metrics khớp với các file trong `data/results/`.
- [x] Quality/freshness conclusions khớp với `data/quality/`.
- [x] Các đường dẫn báo cáo và artifact truy cập được.
- [x] Mỗi thành viên đã hoàn thành báo cáo vai trò riêng (`individual_report_01515.md`, `individual_report_01525.md`, `individual_report_01563.md`).
- [x] Không có `.env`, API key, token hoặc secret trong source, report, log hay ảnh.
