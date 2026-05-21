# pnlUtils.py
"""
Tiện ích xử lý dữ liệu PNL và lịch âm dương.
"""

import io
import os
import pandas as pd
from glob import glob
from functools import lru_cache

# ==================== CẤU HÌNH ====================
WINDOW_SIZE = 100

# ==================== NGŨ HÀNH MÀU SẮC ====================
CAN_HANH = {
    "Giáp": "Mộc", "Ất": "Mộc",
    "Bính": "Hỏa", "Đinh": "Hỏa",
    "Mậu": "Thổ", "Kỷ": "Thổ",
    "Canh": "Kim", "Tân": "Kim",
    "Nhâm": "Thủy", "Quý": "Thủy",
}

CHI_HANH = {
    "Tý": "Thủy", "Hợi": "Thủy",
    "Dần": "Mộc", "Mão": "Mộc",
    "Tỵ": "Hỏa", "Ngọ": "Hỏa",
    "Thân": "Kim", "Dậu": "Kim",
    "Thìn": "Thổ", "Tuất": "Thổ", "Sửu": "Thổ", "Mùi": "Thổ",
}

HANH_COLOR = {
    "Mộc": "#4caf50",
    "Hỏa": "#ff5252",
    "Thổ": "#ffb300",
    "Kim": "#b0bec5",
    "Thủy": "#29b6f6",
}

SEASON_COLORS = {
    'spring': 'rgba(255, 105, 180, 0.10)',
    'summer': 'rgba(255, 100,  30, 0.10)',
    'autumn': 'rgba(255, 165,   0, 0.10)',
    'winter': 'rgba( 30, 170, 255, 0.10)',
}

# ==================== TỨ KHÍ ====================
@lru_cache(maxsize=50)
def get_solar_terms(year: int) -> dict:
    """Lấy thông tin tứ khí (ngày cố định gần đúng)."""
    return {
        'Xuân phân': {'date': pd.Timestamp(f'{year}-03-20'), 'icon': '🌸', 'color': '#FF69B4'},
        'Hạ chí':    {'date': pd.Timestamp(f'{year}-06-21'), 'icon': '☀️', 'color': '#FF6B35'},
        'Thu phân':  {'date': pd.Timestamp(f'{year}-09-22'), 'icon': '🍂', 'color': '#FFA500'},
        'Đông chí':  {'date': pd.Timestamp(f'{year}-12-21'), 'icon': '❄️', 'color': '#4FC3F7'},
    }


def get_all_solar_dates(df: pd.DataFrame) -> set:
    """Lấy tập hợp tất cả ngày tứ khí xuất hiện trong df."""
    dates = set()
    for y in df["date"].dt.year.dropna().unique():
        for info in get_solar_terms(int(y)).values():
            dates.add(info['date'])
    return dates


# ==================== NGŨ HÀNH ====================
def canchi_color(can: str, chi: str) -> tuple:
    """Trả về (can_color, chi_color) theo ngũ hành."""
    cc = HANH_COLOR.get(CAN_HANH.get(str(can).strip(), ""), "#aaaaaa")
    hc = HANH_COLOR.get(CHI_HANH.get(str(chi).strip(), ""), "#aaaaaa")
    return cc, hc


def get_hanh(can: str, chi: str) -> tuple:
    """Trả về (hành_can, hành_chi)."""
    return (
        CAN_HANH.get(str(can).strip(), "?"),
        CHI_HANH.get(str(chi).strip(), "?"),
    )


# ==================== ĐỌC FILE CỤC BỘ ====================
def _parse_bingx_df(df: pd.DataFrame) -> pd.DataFrame | None:
    """Chuẩn hoá DataFrame BingX thành (date, Realized PNL)."""
    if 'closeTime(UTC+8)' not in df.columns or 'Realized PNL' not in df.columns:
        return None
    df = df[['closeTime(UTC+8)', 'Realized PNL']].copy()
    df['closeTime(UTC+8)'] = pd.to_datetime(
        df['closeTime(UTC+8)'], format='%Y-%m-%d %H:%M:%S', errors='coerce')
    df['Realized PNL'] = pd.to_numeric(df['Realized PNL'], errors='coerce')
    df = df.dropna()
    df['date'] = df['closeTime(UTC+8)'].dt.floor('D')
    return df[['date', 'Realized PNL']]


def _parse_binance_df(df: pd.DataFrame) -> pd.DataFrame | None:
    """
    Chuẩn hoá DataFrame Binance (header=9) thành (date, Realized PNL).
    Hỗ trợ cả format ngày '%Y-%m-%d %H:%M:%S' và '%y-%m-%d %H:%M:%S'.
    """
    time_col = next((c for c in df.columns if 'Thời gian' in str(c)), None)
    pnl_col  = next((c for c in df.columns if 'Lợi nhuận đã thực hiện' in str(c)), None)
    if time_col is None or pnl_col is None:
        return None

    df = df[[time_col, pnl_col]].copy()
    df = df.dropna(subset=[time_col, pnl_col])

    # Thử format 4-chữ-số năm trước, rồi 2-chữ-số
    parsed = pd.to_datetime(df[time_col], format='%Y-%m-%d %H:%M:%S', errors='coerce')
    if parsed.isna().all():
        parsed = pd.to_datetime(df[time_col], format='%y-%m-%d %H:%M:%S', errors='coerce')
    df[time_col] = parsed

    df[pnl_col] = pd.to_numeric(df[pnl_col], errors='coerce')
    df = df.dropna()
    df = df.rename(columns={time_col: 'closeTime(UTC+8)', pnl_col: 'Realized PNL'})
    df['date'] = df['closeTime(UTC+8)'].dt.floor('D')
    return df[['date', 'Realized PNL']]


def load_local_pnl_data() -> list[pd.DataFrame]:
    """
    Đọc PNL từ file Excel cục bộ (thư mục files/ và filesbinance/).
    Chỉ dùng khi chạy không có upload (chế độ mặc định).
    """
    script_dir = os.path.dirname(os.path.abspath(__file__))
    results = []

    # BingX
    for path in glob(os.path.join(script_dir, "files/*.xlsx")):
        try:
            df_raw = pd.read_excel(path, engine='openpyxl')
            parsed = _parse_bingx_df(df_raw)
            if parsed is not None:
                results.append(parsed)
                print(f"✅ BingX {os.path.basename(path)}: {len(parsed)} GD")
            else:
                print(f"⚠️ BingX {os.path.basename(path)}: không đúng cấu trúc")
        except Exception as e:
            print(f"❌ BingX {os.path.basename(path)}: {e}")

    # Binance
    for path in glob(os.path.join(script_dir, "filesbinance/*.xlsx")):
        try:
            df_raw = pd.read_excel(path, header=9, engine='openpyxl')
            parsed = _parse_binance_df(df_raw)
            if parsed is not None:
                results.append(parsed)
                print(f"✅ Binance {os.path.basename(path)}: {len(parsed)} GD")
            else:
                print(f"⚠️ Binance {os.path.basename(path)}: không tìm thấy cột cần thiết")
        except Exception as e:
            print(f"❌ Binance {os.path.basename(path)}: {e}")

    return results


# ==================== XỬ LÝ UPLOAD ====================
def process_uploaded_file(uploaded_file, exchange_type: str) -> tuple[pd.DataFrame | None, str | None]:
    """
    Xử lý một file upload duy nhất.

    FIX: đọc bytes một lần, tránh lỗi 'file đã được đọc hết' khi parse Binance.

    Returns:
        (df, None)    nếu thành công
        (None, msg)   nếu lỗi
    """
    try:
        raw_bytes = uploaded_file.read()   # đọc một lần duy nhất
        if exchange_type == "BingX":
            df_raw = pd.read_excel(io.BytesIO(raw_bytes), engine='openpyxl')
            parsed = _parse_bingx_df(df_raw)
            if parsed is None:
                return None, f"BingX '{uploaded_file.name}': thiếu cột closeTime(UTC+8) hoặc Realized PNL"

        elif exchange_type == "Binance":
            df_raw = pd.read_excel(io.BytesIO(raw_bytes), header=9, engine='openpyxl')
            parsed = _parse_binance_df(df_raw)
            if parsed is None:
                return None, f"Binance '{uploaded_file.name}': không tìm thấy cột Thời gian hoặc Lợi nhuận đã thực hiện"

        else:
            return None, f"Loại sàn không hỗ trợ: {exchange_type}"

        return parsed, None

    except Exception as e:
        return None, f"{exchange_type} '{uploaded_file.name}': {e}"


def process_multiple_uploads(
    uploaded_files_dict: dict,
) -> tuple[list[pd.DataFrame], list[str]]:
    """
    Xử lý nhiều file upload từ nhiều sàn.

    Args:
        uploaded_files_dict: {"BingX": [file, ...], "Binance": [file, ...]}

    Returns:
        (all_pnl_list, errors)
    """
    all_pnl_list, errors = [], []

    for exchange_type, files in uploaded_files_dict.items():
        for f in (files or []):
            print(f"⏳ {exchange_type} – {f.name}")
            df, err = process_uploaded_file(f, exchange_type)
            if err:
                errors.append(err)
            else:
                all_pnl_list.append(df)
                print(f"   ✅ {len(df)} GD")

    return all_pnl_list, errors


# ==================== CALENDAR ====================
def load_calendar_data(csv_path: str = "files/calendar_with_moon.csv") -> pd.DataFrame:
    """Đọc file lịch âm dương."""
    df = pd.read_csv(csv_path)
    df["date"] = pd.to_datetime(df["date"], errors="coerce")
    df["moon_numeric"] = pd.to_numeric(df["moon"], errors="coerce")
    return df


# ==================== TỔNG HỢP DỮ LIỆU ====================
def _aggregate_pnl(pnl_list: list[pd.DataFrame]) -> pd.DataFrame | None:
    """Gộp danh sách DataFrame PNL thành daily_pnl."""
    if not pnl_list:
        return None
    combined = pd.concat(pnl_list, ignore_index=True)
    combined['date'] = pd.to_datetime(combined['date'])
    daily = combined.groupby('date')['Realized PNL'].sum().reset_index()
    return daily.sort_values('date')


def filter_special_dates(df_full: pd.DataFrame) -> pd.DataFrame:
    """Giữ lại các ngày đặc biệt: pha trăng, specdate, tứ khí, và ngày có PNL."""
    all_solar = get_all_solar_dates(df_full)

    df_full["specdate_clean"] = df_full["specdate"].astype(str).str.strip().str.lower()
    df_full["is_moon_phase"]  = df_full["moon_numeric"].isin([0, 90, 180, 270])
    df_full["is_specdate"]    = df_full["specdate_clean"].isin(["ram", "rằm", "m1", "mùng 1"])
    df_full["is_solar_term"]  = df_full["date"].isin(all_solar)
    df_full["has_pnl"]        = df_full["pnl"] != 0

    mask = (
        df_full["is_moon_phase"] | df_full["is_specdate"] |
        df_full["is_solar_term"] | df_full["has_pnl"]
    )
    result = df_full[mask].copy().sort_values("date").reset_index(drop=True)
    print(f"📅 Sau lọc: {len(result)} ngày (từ {len(df_full)})")
    return result


def build_full_data(
    pnl_list: list[pd.DataFrame],
    calendar_df: pd.DataFrame | None = None,
) -> tuple[pd.DataFrame | None, pd.DataFrame | None, pd.DataFrame | None]:
    """
    Gộp PNL vào calendar, lọc ngày đặc biệt.

    Returns:
        (df_filtered, df_full, daily_pnl)  hoặc  (None, None, None) nếu lỗi
    """
    daily_pnl = _aggregate_pnl(pnl_list)
    if daily_pnl is None:
        print("⚠️ Không có dữ liệu PNL hợp lệ!")
        return None, None, None

    if calendar_df is None:
        calendar_df = load_calendar_data()

    pnl_dict = dict(zip(daily_pnl['date'], daily_pnl['Realized PNL']))
    calendar_df = calendar_df.copy()
    calendar_df['pnl'] = calendar_df['date'].map(pnl_dict).fillna(0)

    df_filtered = filter_special_dates(calendar_df)

    total_pnl = daily_pnl['Realized PNL'].sum()
    print(
        f"✅ Xây dựng xong: {len(df_filtered)} ngày đặc biệt, "
        f"{len(daily_pnl)} ngày GD, tổng PNL {total_pnl:+,.2f} USD"
    )
    return df_filtered, calendar_df, daily_pnl


def load_all_data(
    csv_path: str = "files/calendar_with_moon.csv",
) -> tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame | None]:
    """
    Tải dữ liệu mặc định từ file cục bộ.
    Dùng khi khởi động app lần đầu (không có upload).
    """
    print("📂 Đang đọc dữ liệu cục bộ...")
    calendar_df = load_calendar_data(csv_path)
    pnl_list    = load_local_pnl_data()

    df_filtered, df_full, daily_pnl = build_full_data(pnl_list, calendar_df)

    # Nếu không có PNL, vẫn trả về calendar với pnl = 0
    if df_filtered is None:
        calendar_df['pnl'] = 0
        df_filtered = filter_special_dates(calendar_df)
        df_full     = calendar_df

    return df_filtered, df_full, daily_pnl


# ==================== THỐNG KÊ ====================
def get_data_summary(df_filtered: pd.DataFrame, daily_pnl: pd.DataFrame) -> dict:
    """Trả về dict thống kê tóm tắt."""
    if df_filtered is None or daily_pnl is None:
        return {}
    return {
        "total_special_days":  len(df_filtered),
        "total_trading_days":  len(daily_pnl),
        "total_pnl":           daily_pnl['Realized PNL'].sum(),
        "max_pnl":             daily_pnl['Realized PNL'].max(),
        "min_pnl":             daily_pnl['Realized PNL'].min(),
        "start_date":          daily_pnl['date'].min(),
        "end_date":            daily_pnl['date'].max(),
    }