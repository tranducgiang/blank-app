# PNL + Lịch Âm Dương + Tứ Trụ

Ứng dụng Streamlit kết hợp biểu đồ PNL giao dịch với lịch âm dương và xem lộc ngày theo Tứ Trụ.

---

## Cấu trúc dự án

```
.
├── streamlit_app.py        # Entry point — UI và điều phối
├── pnlUtils.py             # Đọc file, xử lý PNL, tiện ích dùng chung
├── drawchart.py            # Vẽ biểu đồ Plotly
├── tuvi.py                 # Tính Tứ Trụ và xem lộc ngày
├── files/
│   ├── calendar_with_moon.csv   # Dữ liệu lịch âm dương + pha trăng
│   └── *.xlsx                   # File PNL từ BingX (cục bộ)
└── filesbinance/
    └── *.xlsx                   # File PNL từ Binance (cục bộ)
```

---

## Map cấu trúc module

```
streamlit_app.py
│
├── APP_CSS                         hằng số CSS (inject 1 lần)
├── _init_session_state()           khởi tạo session state lần đầu
│
├── Sidebar
│   ├── _render_sidebar_upload()    UI file uploader BingX / Binance
│   ├── _handle_start_button()      xử lý nút START → load dữ liệu
│   ├── _handle_reset_button()      reset về dữ liệu mặc định
│   ├── _render_sidebar_status()    hiển thị nguồn dữ liệu hiện tại
│   └── _render_sidebar_stats()     thống kê PNL theo năm
│
├── Main area
│   ├── _render_chart_section()     nav năm + Plotly chart
│   └── _render_tuvi_section()
│       ├── _render_tuvi_input()    form nhập ngày sinh / giờ sinh
│       └── _render_tuvi_result()   hiển thị Tứ Trụ + kết luận lộc
│
├── import pnlUtils  ──────────────────────────────────────────────┐
└── import drawchart / tuvi                                         │
                                                                    ▼
pnlUtils.py
│
├── Upload (flow chính)
│   ├── process_uploaded_file(file, type)   1 file → DataFrame | error
│   └── process_multiple_uploads(dict)      nhiều file → [DataFrame], [errors]
│
├── Parse nội bộ
│   ├── _parse_bingx_df(df)        chuẩn hoá cột BingX
│   └── _parse_binance_df(df)      chuẩn hoá cột Binance (hỗ trợ 2 format ngày)
│
├── Tổng hợp dữ liệu
│   ├── _aggregate_pnl(list)       concat + groupby date
│   ├── build_full_data(pnl_list)  PNL + calendar + filter → (filtered, full, daily)
│   ├── filter_special_dates(df)   giữ pha trăng / specdate / tứ khí / ngày GD
│   └── load_all_data()            startup mặc định từ file cục bộ
│
├── Local files
│   └── load_local_pnl_data()      đọc files/ và filesbinance/
│
├── Calendar
│   └── load_calendar_data(path)   đọc CSV lịch âm dương
│
├── Tiện ích dùng chung (import bởi drawchart.py)
│   ├── canchi_color(can, chi)     → (can_color, chi_color)
│   ├── get_hanh(can, chi)         → (hành_can, hành_chi)
│   ├── get_solar_terms(year)      → dict tứ khí + màu + icon
│   ├── get_all_solar_dates(df)    → set ngày tứ khí
│   ├── HANH_COLOR                 dict màu 5 hành
│   └── SEASON_COLORS              dict màu 4 mùa
│
└── Thống kê
    └── get_data_summary(df, pnl)  → dict tóm tắt

drawchart.py
└── build_figure(df_filtered, year)
    ├── Nền 4 mùa (vrect)
    ├── PNL bars (màu xanh/đỏ)
    ├── Moon phase annotations
    ├── Specdate annotations (Rằm / Mùng 1)
    ├── Can Chi annotations (|PNL| > 10)
    └── Tứ khí vlines

tuvi.py
└── class TuViAnalyzer
    ├── tinh_tu_tru(ngay, gio)       → dict {nam, thang, ngay, gio, nhat_can, ...}
    ├── xem_loc_ngay(tu_tru, today)  → dict {co_tai, co_loc, ket_luan, mau_sac, ...}
    ├── get_tai_tinh(nhat_can)       → ngũ hành Tài Tinh
    ├── get_tai_can_chi(nhat_can)    → (can_list, chi_list)
    └── phan_biet_tai(nhat_can, can) → "Chính Tài" | "Thiên Tài"
```

---

## Bug đã fix

### Binance double-read (critical)

**Vị trí:** `pnlUtils.py` — `process_multiple_uploads` (code cũ)

**Nguyên nhân:**
```python
# Sai — đọc file 2 lần
df_excel = pd.read_excel(io.BytesIO(uploaded_file.read()), ...)   # lần 1: hết bytes
# ...
df_binance = pd.read_excel(io.BytesIO(uploaded_file.read()), ...) # lần 2: bytes rỗng → fail
```

Streamlit `UploadedFile` là stream chỉ đọc một lần. Sau lần `read()` đầu, con trỏ nằm ở cuối — lần 2 trả về `b""` dẫn đến DataFrame rỗng và không parse được gì.

**Fix:**
```python
raw_bytes = uploaded_file.read()  # đọc đúng 1 lần
df_raw    = pd.read_excel(io.BytesIO(raw_bytes), engine='openpyxl')           # BingX
df_raw    = pd.read_excel(io.BytesIO(raw_bytes), header=9, engine='openpyxl') # Binance
```

Logic được tách thành `process_uploaded_file(file, exchange_type)` nhận 1 file, xử lý xong trả về `(DataFrame | None, error | None)`.

---

## Format file Excel

### BingX
| Cột | Mô tả |
|-----|-------|
| `closeTime(UTC+8)` | Thời gian đóng lệnh, format `%Y-%m-%d %H:%M:%S` |
| `Realized PNL` | Lợi nhuận đã thực hiện |

### Binance
- Header nằm ở **dòng 9** (`header=9`)
- Tự động tìm cột chứa `Thời gian` và `Lợi nhuận đã thực hiện`
- Hỗ trợ format ngày `%Y-%m-%d %H:%M:%S` và `%y-%m-%d %H:%M:%S`

---

## Luồng dữ liệu

```
Upload files (sidebar)
        │
        ▼
process_multiple_uploads()
        │  gọi process_uploaded_file() cho từng file
        │  → _parse_bingx_df() hoặc _parse_binance_df()
        ▼
  [DataFrame, ...]
        │
        ▼
build_full_data(pnl_list)
        │  _aggregate_pnl()  → daily_pnl
        │  load_calendar_data()
        │  map PNL vào calendar
        │  filter_special_dates()
        ▼
  (df_filtered, df_full, daily_pnl)
        │
        ├──▶ build_figure()   →  Plotly chart
        └──▶ session_state    →  sidebar stats + year nav
```

---

## Phụ thuộc chính

```
streamlit
pandas
plotly
openpyxl
lunar-python    # dùng trong tuvi.py
```