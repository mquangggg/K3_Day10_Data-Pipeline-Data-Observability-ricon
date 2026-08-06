# Hướng Dẫn Thiết Lập Môi Trường Data Pipeline - Data Observability

## Giới Thiệu

Hướng dẫn này sẽ giúp bạn thiết lập môi trường phát triển cho dự án Data Pipeline - Data Observability. Dự án này mô phỏng một pipeline dữ liệu nhỏ cho hệ thống RAG (Retrieval-Augmented Generation) sử dụng dữ liệu bài báo học thuật từ Crossref.

## Yêu Cầu Hệ Thống

- **Python 3.11, 3.12 hoặc 3.13** (theo `pyproject.toml` và `uv.lock`)
- Internet để lấy dữ liệu từ Crossref và tải embedding model lần đầu
- API key của ít nhất một LLM provider nếu chạy các bước có gọi LLM

## Bước 1: Kiểm Tra Phiên Bản Python

```bash
python --version
```

Hệ thống nên hiển thị phiên bản Python 3.11, 3.12 hoặc 3.13.

## Bước 2: Cài Đặt Môi Trường Phát Triển

### Cách A - Dùng uv (Khuyến nghị)

Tại thư mục gốc của project:

```bash
uv sync
```

`uv sync` sẽ tạo môi trường `.venv`, cài project và dependency theo `uv.lock`.

### Cách B - Dùng pip

Tạo và kích hoạt virtual environment:

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install --upgrade pip
python -m pip install -e .
```

## Bước 3: Cấu Hình File .env

Sao chép file mẫu và cấu hình các API key:

```powershell
Copy-Item .env.example .env
```

Mở file `.env` và điền API key cho provider bạn muốn sử dụng:

```dotenv
LLM_PROVIDER=gemini
LLM_MODEL=gemini-2.5-flash
GOOGLE_API_KEY=your_key_here
OPENAI_API_KEY=
ANTHROPIC_API_KEY=
OPENROUTER_API_KEY=
OPENROUTER_BASE_URL=https://openrouter.ai/api/v1
OLLAMA_BASE_URL=http://localhost:11434
CUSTOM_LLM_BASE_URL=
CUSTOM_LLM_API_KEY=
```

## Bước 4: Kiểm Tra Thư MỤC DỮ LIỆU

Các thư mục dữ liệu đã được tạo sẵn trong quá trình cài đặt:

- `data/raw/` - Lưu trữ dữ liệu thô từ nguồn
- `data/clean/` - Lưu trữ dữ liệu đã làm sạch
- `data/embeddings/` - Lưu trữ embedding và chỉ mục
- `data/eval/` - Lưu trữ tập dữ liệu đánh giá
- `data/results/` - Lưu trữ kết quả đánh giá
- `data/quality/` - Lưu trữ báo cáo chất lượng dữ liệu
- `data/reports/` - Lưu trữ báo cáo tổng hợp

## Bước 5: Chạy Pipeline Baseline

Sau khi hoàn thành cài đặt, bạn có thể chạy pipeline baseline:

```bash
uv run python script/run_phase1.py
```

Hoặc nếu dùng pip:

```bash
python script/run_phase1.py
```

## Bước 6: Kiểm Tra Kết Quả

Sau khi chạy baseline, kiểm tra các thư mục dữ liệu:

- `data/raw/`: raw response và records từ Crossref
- `data/clean/`: cleaned CSV/JSON
- `data/embeddings/`: embedding manifest
- `data/eval/`: evaluation test set
- `data/results/baseline_metrics.json`: metrics của baseline
- `data/quality/`: data quality và freshness report
- `data/reports/phase1_report.md`: báo cáo baseline

## Các Lỗi Thường Gặp

| Triệu chứng | Nguyên nhân thường gặp | Cách kiểm tra/xử lý |
|-------------|------------------------|---------------------|
| `requires a different Python` | Python nằm ngoài khoảng 3.11-3.13 | Chạy `python --version`, chọn Python phù hợp rồi tạo lại `.venv` |
| `No module named 'pipelines'` | Mới cài `requirements.txt`, chưa cài project | Trong `.venv`, chạy `python -m pip install -e .` |
| `GOOGLE_API_KEY is required` | Provider mặc định là Gemini nhưng chưa có key | Điền `GOOGLE_API_KEY` hoặc đổi `LLM_PROVIDER` sang provider đã cấu hình |
| `NotImplementedError: Student task...` | Chạm tới phần starter chưa implement | Mở đúng file được ghi trong traceback và hoàn thành `TODO(student)` |
| Crossref trả `429`/`503` | Rate limit hoặc lỗi tạm thời | Implement retry/backoff theo yêu cầu trong `src/ingestion/crossref.py` |
| Chạy corruption flow nhưng thiếu baseline artifact | Chưa chạy xong Pha 1 | Chạy baseline và kiểm tra `data/results/baseline_metrics.json` trước |

## Checklist Trước Khi Nộp

- [ ] Cài đặt được trên môi trường sạch bằng một trong hai cách ở trên
- [ ] Baseline pipeline chạy end-to-end
- [ ] Corruption flow chạy sau baseline
- [ ] Có đầy đủ raw, clean, embedding, evaluation, quality và report artifacts
- [ ] Metrics/report khớp với artifact thực tế
- [ ] Chứng minh được before/corrupted/repaired bằng số liệu
- [ ] Không có API key hoặc `.env` trong Git
- [ ] Đã đối chiếu [Rubric.md](Rubric.md)