# Member Role Report — Day 10: Data Pipeline & Data Observability

> Mỗi thành viên trong nhóm tự hoàn thành mẫu này để báo cáo đúng vai trò, phần việc và mức hiểu của mình. Không sao chép nguyên báo cáo chung hoặc báo cáo của thành viên khác. Thay nội dung trong dấu `[ ]` và xóa các dòng hướng dẫn không cần thiết trước khi nộp.

## 1. Thông tin cá nhân

| Thông tin         | Nội dung                  |
| ------------------ | -------------------------- |
| Họ và tên       | Lương Ngọc Quang        |
| MSSV               | 01563                      |
| Khóa/Lớp         | K3                        |
| Tên nhóm         | K3_Day10_Data-Pipeline-Data-Observability |
| Vai trò chính    | Observability & Reporting Owner |
| Repository         | https://github.com/mquangggg/K3_Day10_Data-Pipeline-Data-Observability-ricon |
| Ngày hoàn thành | 2026-08-06                 |

## 2. Vai trò và phạm vi công việc

### Phần việc sở hữu

| Module/deliverable | File/hàm phụ trách | Input nhận vào | Output bàn giao  | Trạng thái                                 |
| ------------------ | --------------------- | ---------------- | ----------------- | -------------------------------------------- |
| Data Quality Checks | `src/observability/quality.py` | Clean DataFrame | `corrupted_quality.json`, `repaired_quality.json` | ✅ Hoàn thành |
| Freshness Reports | `src/observability/quality.py` | Clean DataFrame | `corrupted_freshness.json`, `repaired_freshness.json` | ✅ Hoàn thành |
| Corruption Impact Reports | `src/observability/reporting.py` | Baseline/Corrupted/Repaired metrics & quality | `corruption_report.md` | ✅ Hoàn thành |
| Observability Analysis | `script/generate_observability_analysis.py` | All quality/freshness/metrics data | `observability_analysis_cp5.md` | ✅ Hoàn thành |
| Demo Summary & Guide | `script/demo_summary.py` | All artifacts & reports | `DEMO_SUMMARY.md` | ✅ Hoàn thành |
| Artifact Verification | `script/verify_artifacts.py` | All data/report files | Security scan report | ✅ Hoàn thành |

### Việc hỗ trợ ngoài phạm vi chính

| Hoạt động                         | Thành viên/module được hỗ trợ | Kết quả                    |
| ------------------------------------ | ------------------------------------ | ---------------------------- |
| Fix testset.py pd.notna() issue | Member 2 (RAG & Evaluation) | Fixed pandas array handling for test set generation |
| Fix reporting.py boolean formatting | Member 1 (Data Foundation) | Fixed markdown table formatting for quality booleans |
| Generate repaired data quality checks | Member 2 (RAG & Evaluation) | Pre-populated repaired quality/freshness for evaluation |

## 3. Kết quả theo vai trò

| Nhiệm vụ đã thực hiện | File/hàm/artifact liên quan | Kết quả bàn giao       | Cách xác minh         |
| --------------------------- | ----------------------------- | ------------------------- | ----------------------- |
| CP5: Data Quality Checks for Corrupted | `data/quality/corrupted_quality.json` | Quality gate assessment (Passed: True→False) | `cat data/quality/corrupted_quality.json` |
| CP5: Freshness Reports | `data/quality/corrupted_freshness.json` | Freshness signal monitoring | `cat data/quality/corrupted_freshness.json` |
| CP5: Corruption Impact Analysis | `data/reports/observability_analysis_cp5.md` | Detailed signal-quality-performance linkage | `cat data/reports/observability_analysis_cp5.md` |
| CP6: Repaired Quality Checks | `data/quality/repaired_quality.json` | Quality verification (Passed: restored to True) | `cat data/quality/repaired_quality.json` |
| CP6: Final Comparison Report | `data/reports/corruption_report.md` | 3-state comparison (Baseline→Corrupted→Repaired) | `cat data/reports/corruption_report.md` |
| CP6: Demo Summary | `data/reports/DEMO_SUMMARY.md` | Presentation guide + demo script | `cat data/reports/DEMO_SUMMARY.md` |
| CP6: Artifact Verification | Script output | Security scan + integrity check | `python script/verify_artifacts.py` |

**Nội dung chính bàn giao:**

Báo cáo Data Observability hoàn chỉnh cho toàn pipeline (Baseline → Corrupted → Repaired):
1. **Quality Gate Detection**: Empty summary count (0→2→0) correctly triggers quality failures
2. **Signal-to-Performance Linkage**: Quality degradation predicts RAG metrics degradation (Hit Rate: 1.0→0.0→1.0)
3. **Repair Validation**: Data restored from raw source passes all quality checks
4. **Artifact Management**: All 3 states maintained separately, no overwrites, fully reproducible
5. **Presentation Ready**: Complete demo guide with slide deck, live script, and Q&A talking points

## 4. Giải thích phần kỹ thuật đã thực hiện

### Vấn đề cần giải quyết

Member 3 (Observability & Reporting Owner) giải quyết vấn đề chính: **Làm sao phát hiện khi dữ liệu tệ làm giảm chất lượng RAG trước khi chạy evaluation đầy đủ?**

Pipeline cần:
- Đo lường data quality signals (null counts, uniqueness, freshness, empty summaries)
- Liên kết corruption types với quality degradation
- Xác minh rằng repair từ raw data khôi phục tất cả quality metrics
- Tạo báo cáo comparison đầy đủ cho 3 trạng thái (baseline/corrupted/repaired)

### Cách triển khai

**1. Data Quality Checks (CP1-CP5)**
- Implement `run_data_quality_checks()`: Kiểm tra paper_id uniqueness, null values, empty summaries, stale rows
- Định nghĩa quality gates: Tất cả fields bắt buộc phải có giá trị, paper_id phải duy nhất
- Đầu vào: Clean DataFrame từ Member 1
- Output: JSON report với boolean "passed" và chi tiết từng metric

**2. Freshness Monitoring (CP1-CP6)**
- Implement `build_freshness_report()`: Tính toán age_days, phát hiện stale records (>180 days)
- Đầu vào: Published date field từ dataframe
- Output: Freshness JSON với is_fresh flag

**3. Corruption Analysis (CP5)**
- Chạy quality checks trên corrupted data → phát hiện failed gates
- Liên kết corruption types (blank summaries, truncation, noise) với chất lượng signals
- Tạo corruption log analysis showing correlation: Corruption type → Quality metric impact

**4. Repair Verification (CP6)**
- Chạy quality checks trên repaired data
- So sánh repaired vs baseline: Verify row count, quality gates, summary empty counts
- Confirm restoration: "Repaired data matches baseline perfectly"

**5. Comprehensive Reporting**
- Implement `generate_corruption_report()`: 3-state comparison table
- Tính delta metrics: corruption_impact = corrupted - baseline, recovery_effect = repaired - corrupted
- Format markdown reports với visual indicators (✅ ❌ 📈 📉)

### Input, output và contract

| Thành phần                   | Mô tả                                     |
| ------------------------------ | ------------------------------------------- |
| Input | Clean DataFrame (24 records) + raw records snapshot + test set + baseline metrics |
| Output | Quality JSON files, Freshness JSON files, Corruption reports (MD), Analysis documents, Demo guide |
| Module phụ thuộc | Member 1 (Data cleaning) → produces clean_df, corruption_log |
| Module sử dụng output | Member 2 (Evaluation) → uses quality/freshness for baseline expectation setting; Leadership → uses reports for presentation |
| Điều kiện lỗi cần xử lý | Empty dataframe → skip checks; Missing fields → default to 0; Null dates → handle with default; Division by zero in metrics → use NaN |

### Cách xác minh

```bash
# Verify baseline quality checks pass
python -c "import json; print(json.load(open('data/quality/baseline_quality.json'))['passed'])"
# Expected: True

# Verify corrupted quality fails
python -c "import json; print(json.load(open('data/quality/corrupted_quality.json'))['passed'])"
# Expected: False (due to empty summaries: 2)

# Verify repaired quality restored
python -c "import json; print(json.load(open('data/quality/repaired_quality.json'))['passed'])"
# Expected: True

# Run complete verification
python script/verify_artifacts.py
# Expected: 16 files scanned, 0 security issues, all consistency checks pass
```

- **Kết quả mong đợi:** Quality signals correctly detect corruption (empty summaries 0→2→0), repaired data matches baseline perfectly
- **Kết quả thực tế:** ✅ All quality gates verified, ✅ Freshness signals stable, ✅ Repaired data 100% matches baseline
- **Artifact/log:** `data/quality/corrupted_quality.json` (shows passed=False), `data/quality/repaired_quality.json` (shows passed=True)

## 5. Một quyết định kỹ thuật quan trọng

- **Bối cảnh:** Khi phát hiện quality gate failure trên corrupted data (empty summaries = 2), tôi phải quyết định: Nên chỉ báo lỗi đơn giản hay tạo chi tiết liên kết corruption type → quality metric?

- **Các phương án đã cân nhắc:**
  1. **Đơn giản (simple reporting):** Chỉ output "Quality PASSED/FAILED" - nhanh nhưng không chỉ ra nguyên nhân
  2. **Chi tiết (diagnostic reporting):** Tạo chi tiết linkage: Blank Summaries corruption → empty_summary_count ↑ → quality gate failed
  3. **Tối ưu (hybrid):** Cả hai: summary flags + detailed analysis document

- **Phương án đã chọn:** **Hybrid approach** - Output JSON giữ nguyên đơn giản, nhưng thêm chi tiết analysis document

- **Lý do:** 
  - **Correctness**: Membership sử dụng JSON để input vào evaluation, nên phải đơn giản & nhất quán
  - **Data Quality**: Analysis document giúp leadership hiểu correlation giữa corruption types và quality signals
  - **Reproducibility**: Chi tiết linkage giúp verify rằng quality checks working correctly
  - **Trade-off**: Thêm file analysis (không ảnh hưởng pipeline) nhưng tăng value for demo

- **Bằng chứe quyết định phù hợp:** 
  - ✅ JSON files được sử dụng bởi evaluation pipeline (kept simple)
  - ✅ Analysis document cho thấy: Blank Summaries (2) → empty_summary_count (2) → quality gate failed
  - ✅ Leadership & demo audience hiểu được signal chain
  - ✅ Metrics confirmed: Hit Rate degradation matches quality degradation

## 6. Một lỗi hoặc blocker đã xử lý

- **Triệu chứng/lỗi nguyên văn:** 
  ```
  ValueError: The truth value of an array with more than one element is ambiguous. Use a.any() or a.all()
  File "src/evaluation/testset.py", line 28, in build_test_set
    if 'authors' in row and pd.notna(row['authors']):
  ```

- **Lệnh hoặc bước tái hiện:** 
  ```bash
  python script/run_corruption_flow.py
  ```

- **Nguyên nhân gốc:** 
  Trong `src/evaluation/testset.py`, hàm `build_test_set()` gọi `pd.notna(row['authors'])` để kiểm tra null values. 
  Tuy nhiên, `row['authors']` là một numpy array (được lưu dưới dạng list khi convert from dict), và `pd.notna()` trên array trả về array boolean, không phải single boolean. 
  Khi Python cố gắng convert array boolean này thành `True/False` trong if-statement, nó không biết nên dùng giá trị nào → lỗi.

- **Cách xử lý:** 
  Thay vì dùng `pd.notna()` trực tiếp trên row values, tôi tạo helper function:
  ```python
  def has_value(val):
      if val is None:
          return False
      val_str = str(val).strip()
      return len(val_str) > 0
  ```
  Sau đó thay tất cả `pd.notna(row['field'])` thành `has_value(row['field'])` trong testset.py

- **Cách xác minh sau khi sửa:** 
  ```bash
  python script/run_corruption_flow.py
  # Success: "Loaded existing raw records"
  # -> "Loading weights: 100%"
  # -> "Loaded corrupted data: 24 records"
  # (No ValueError)
  ```

- **Điều học được:** Khi làm việc với Pandas Series/DataFrame, cần cẩn thận với array broadcasting. `pd.notna()` thiết kế để return boolean array, không single boolean. Với row từ iterrows(), tốt hơn là convert to string và kiểm tra trực tiếp thay vì dùng Pandas utilities.

## 7. Hiểu biết về luồng end-to-end

Giải thích ngắn gọn bằng lời của bạn:

1. **Dữ liệu đi từ Crossref đến vector index như thế nào?**
   Raw records từ Crossref API → Member 1 làm sạch (chuẩn hóa, loại trùng, tính age_days) → bàn giao clean DataFrame (24 papers) 
   → Member 2 tạo MiniLM embeddings (384-dim vectors từ text_for_embedding) → lưu Chroma collection papers-baseline (indexed by paper_id)

2. **Evaluation set và ground-truth document IDs dùng để đo retrieval/answer quality ra sao?**
   Member 2 tạo test_set.json: 5 papers × 4 loại câu hỏi = 20 questions. Mỗi question có ground_truth_doc_ids (paper_id của câu trả lời đúng).
   Khi evaluate: query → semantic search → kiểm tra xem paper_id trong top-k results có match ground_truth_doc_ids không → Retrieval Hit Rate.
   Sau đó LLM trả lời dựa trên retrieved docs → so sánh answer text với ground_truth → Token F1 score.

3. **Quality checks khác freshness monitoring ở điểm nào trong bài lab?**
   - **Quality Checks** (Member 3): Kiểm tra structural integrity của data (null values, duplicates, required fields). Pass/fail gates.
   - **Freshness Monitoring** (Member 3): Kiểm tra temporal relevance (published date, age_days). Is_fresh flag.
   - Khác: Quality = về structure, Freshness = về thời gian. Cả hai chạy cùng lúc, cả hai critical.

4. **Vì sao phải dùng cùng test set cho baseline, corrupted và repaired?**
   Để công bằng so sánh 3 trạng thái. Nếu dùng test sets khác nhau, không biết degradation là do corruption hay do test set bias.
   Cùng 20 questions → cùng ground truth → cùng evaluation criteria → delta metrics phản ánh chính xác impact của corruption vs repair.

5. **Repair được xem là thành công dựa trên artifact và metric nào?**
   - **Artifacts**: Repaired data regenerated from raw → phải giống baseline (24 records, all quality gates pass, empty_summary_count = 0)
   - **Metrics**: Repaired Hit Rate phải bằng Baseline Hit Rate (1.0). Nếu khác → repaired quality/embeddings có vấn đề.
   - Xác minh bằng: `diff papers_clean.csv papers_clean_repaired.csv` (empty) + quality check script output (passed=True).

---

## 8. Phân tích kết quả

### Metrics chính

| Metric/signal          | Baseline | Corrupted | Repaired | Nhận xét của cá nhân |
| ---------------------- | -------: | --------: | -------: | ------------------------- |
| retrieval_hit_rate | 1.0000 | 0.0000 | 1.0000 | Corruption làm mất toàn bộ retrieval accuracy (empty summaries + noise). Repair phục hồi hoàn toàn. |
| mean_token_f1 | 0.0623 | 0.0000 | 0.0623 | F1 score = 0 khi không retrieve đúng docs → không có text để so sánh. Repair khôi phục. |
| judge_accuracy | 0.0 | 0.0 | 0.0 | Khi retrieval fail → không có context → LLM không trả lời được → accuracy = 0 |
| Quality checks (passed) | ✅ True | ❌ False | ✅ True | Empty summaries (0→2→0) là nguyên nhân chính. Tất cả khác đều ổn. |
| Freshness status (is_fresh) | ✅ True | ✅ True | ✅ True | Date corruption không vượt ngưỡng 180 days → freshness không bị ảnh hưởng |

### Kết luận từ số liệu

**Chuỗi 1: Corruption → Quality Degradation → Metric Degradation**
```
Corruption Applied: Blank Summaries (2), Noise Injected (2), Titles Truncated (2)
                        ↓
Quality Signal Degraded: empty_summary_count: 0 → 2, quality gates: True → False
                        ↓
RAG Metrics Degraded: Hit Rate: 1.0 → 0.0, Token F1: 0.0623 → 0.0
                        ↓
Mechanism: Empty summaries → No text for embedding → Poor vectors → Can't retrieve anything
```

**Chuỗi 2: Repair → Quality Recovery → Metric Recovery**
```
Repair Action: Re-clean from raw data
                        ↓
Quality Signal Recovered: empty_summary_count: 2 → 0, quality gates: False → True
                        ↓
RAG Metrics Recovered: Hit Rate: 0.0 → 1.0, Token F1: 0.0 → 0.0623
                        ↓
Validation: Repaired data matches baseline perfectly (row count, quality gates, freshness)
```

**Corruption nào ảnh hưởng rõ nhất?**
- **Blank Summaries (2)**: MOST CRITICAL. Directly triggers quality gate failure (empty_summary_count violates threshold).
- **Noise Injected (2)**: SIGNIFICANT. Distorts text → poor embeddings → lower semantic similarity.
- **Titles Truncated (2)**: MODERATE. Title is partial but still present. Affects retrieval quality but not as severe as blank.
- **Wrong Dates (2)**: NEGLIGIBLE. Dates not within threshold, so freshness signal not triggered.
- **Dropped Records (2)**: NOT MEASURED. Net row count = 24 (did drop 2 but added 2 duplicates). Quality checks don't flag this.

Kết luận: **Blank summaries là culprit chính**. Nó directly failed quality gates + destroys embedding quality.

**Kết quả khác với kỳ vọng?**
- ✅ Kỳ vọng: Quality gate failure signal → Expected RAG metrics degradation. **Result**: Fully confirmed. Quality checks correctly predicted metric impact.
- ✅ Kỳ vọng: Freshness signals stable despite date corruption. **Result**: Confirmed. Date corruption within threshold, so is_fresh unchanged.
- ✅ Kỳ vọng: Repaired data matches baseline. **Result**: Confirmed. 100% match on all quality metrics.
- ⚠️ Kỳ vọng: Hit Rate degradation clear causality. **Result**: Confirmed but more severe (1.0→0.0) due to ALL summaries empty (2 out of small dataset). If only 1 summary was blank, might see partial degradation.

---

## 9. Điều học được và hướng cải thiện

### Ba điều quan trọng nhất

1. **Data Quality Signals là Early Warning System**: Không cần chạy evaluation đầy đủ (2-3 phút) để phát hiện vấn đề. Quality checks chạy trong vài giây, phát hiện degradation. 
   Ứng dụng: Trong production, chạy quality checks thường xuyên để phát hiện data drift trước khi ảnh hưởng agent.

2. **Signal-to-Performance Linkage phải được chứng minh bằng thực nghiệm**: Ban đầu, tôi chỉ định nghĩa quality gates. Nhưng khi corruption áp dụng + evaluation chạy, mới thấy:
   - Empty summary (1 metric) → Complete hit rate failure (1 high-level metric). 
   - Correlation này giúp prioritize nên monitor quality signals nào trước.

3. **Repair Strategy phải từ Reliable Source**: Nếu phụ thuộc vào manual fixes hoặc partial re-cleaning, không thể guarantee restoration. 
   Nhưng vì tôi lưu raw data snapshot nguyên vẹn, có thể re-run cleaning pipeline từ đầu → 100% reproducible recovery.
   Học: Always preserve immutable source. Make cleaning idempotent.

### Nếu có thêm thời gian

**Cải thiện 1: Implement Data Observability Dashboard**
- Cách: Tạo real-time dashboard (Grafana/Streamlit) hiển thị quality metrics + freshness + retrieval metrics side-by-side
- Lý do: Hiện tại, metrics nằm rải rác trong JSON files. Dashboard giúp ngay thấy correlation between quality degradation → metric impact
- Cách đo: Dashboard response time < 1s, auto-update mỗi khi quality checks chạy

**Cải thiện 2: Implement Anomaly Detection on Quality Signals**
- Cách: Chạy moving average trên quality metrics (e.g., empty_summary_count, null_count) → flag if violation
- Lý do: Hiện tại phát hiện corruption chỉ sau run toàn bộ. Anomaly detection có thể phát hiện incremental degradation trước.
- Cách đo: Test với partial corruption (1-2 records vs 2) → verify detection sensitivity

**Cải thiện 3: Document Quality Gate Thresholds & Tuning Process**
- Cách: Tạo notebook giải thích: Tại sao empty_summary_count threshold = 0? Nếu cho phép 1-2 empty, metric thay đổi ra sao?
- Lý do: Hiện tại thresholds hard-coded. Tuning chúng dựa trên business needs → quality gates không generic được.
- Cách đo: Experiment notebook với different thresholds → show precision/recall tradeoff for quality gate triggering

## 10. Cam kết của thành viên

Đánh dấu sau khi tự kiểm tra:

- [x] Nội dung báo cáo phản ánh đúng phần việc và mức hiểu của tôi.
- [x] Tôi có thể giải thích luồng end-to-end, không chỉ module mình phụ trách.
- [x] Mọi kết luận về kết quả đều có artifact hoặc metric để đối chiếu.
- [x] Tôi không ghi "đã chạy thành công" cho phần chưa được kiểm chứng.
- [x] Báo cáo không chứa `.env`, API key, token hoặc secret.
- [x] Báo cáo này không phải bản sao nguyên văn của báo cáo nhóm hoặc báo cáo thành viên khác.

**Họ và tên:** Lương Ngọc Quang
**Ngày xác nhận:** 2026-08-06
