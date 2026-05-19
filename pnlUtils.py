# pnlUtils.py
import pandas as pd
import os
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
def get_solar_terms(year):
    """Lấy thông tin tứ khí"""
    return {
        'Xuân phân': {'date': pd.Timestamp(f'{year}-03-20'), 'icon': '🌸', 'color': '#FF69B4'},
        'Hạ chí':    {'date': pd.Timestamp(f'{year}-06-21'), 'icon': '☀️', 'color': '#FF6B35'},
        'Thu phân':  {'date': pd.Timestamp(f'{year}-09-22'), 'icon': '🍂', 'color': '#FFA500'},
        'Đông chí':  {'date': pd.Timestamp(f'{year}-12-21'), 'icon': '❄️', 'color': '#4FC3F7'},
    }

def get_all_solar_dates(df):
    """Lấy tất cả ngày tứ khí từ dataframe"""
    all_solar_dates = set()
    for y in df["date"].dt.year.dropna().unique():
        if not pd.isna(y):
            for info in get_solar_terms(int(y)).values():
                all_solar_dates.add(info['date'])
    return all_solar_dates

# ==================== NGŨ HÀNH ====================
def canchi_color(can: str, chi: str) -> tuple:
    """Trả về (can_color, chi_color) theo ngũ hành."""
    cc = HANH_COLOR.get(CAN_HANH.get(str(can).strip(), ""), "#aaaaaa")
    hc = HANH_COLOR.get(CHI_HANH.get(str(chi).strip(), ""), "#aaaaaa")
    return cc, hc

def get_hanh(can, chi):
    """Lấy ngũ hành của can và chi"""
    hc = CAN_HANH.get(str(can).strip(), "?")
    hh = CHI_HANH.get(str(chi).strip(), "?")
    return hc, hh

# ==================== ĐỌC DỮ LIỆU ====================
def load_pnl_data():
    """Đọc dữ liệu PNL từ các file Excel"""
    script_dir = os.path.dirname(os.path.abspath(__file__))
    all_pnl = []
    
    # Đọc file Excel từ thư mục files
    files = glob(os.path.join(script_dir, "files/*.xlsx"))
    if files:
        for file in files:
            try:
                df_excel = pd.read_excel(file, engine='openpyxl')
                if 'closeTime(UTC+8)' in df_excel.columns and 'Realized PNL' in df_excel.columns:
                    df_s = df_excel[['closeTime(UTC+8)', 'Realized PNL']].copy()
                    df_s['closeTime(UTC+8)'] = pd.to_datetime(
                        df_s['closeTime(UTC+8)'], format='%Y-%m-%d %H:%M:%S', errors='coerce')
                    df_s['Realized PNL'] = pd.to_numeric(df_s['Realized PNL'], errors='coerce')
                    df_s = df_s.dropna()
                    df_s['date'] = df_s['closeTime(UTC+8)'].dt.floor('D')
                    all_pnl.append(df_s[['date', 'Realized PNL']])
                    print(f"✅ Đã đọc {os.path.basename(file)}: {len(df_s)} giao dịch")
            except Exception as e:
                print(f"Lỗi đọc {file}: {e}")
    
    # Đọc file Excel Binance
    files_binance = glob(os.path.join(script_dir, "filesbinance/*.xlsx"))
    if files_binance:
        print(f"\n📂 Tìm thấy {len(files_binance)} file Binance:")
        for file in files_binance:
            try:
                print(f"\n   📄 Đang xử lý: {os.path.basename(file)}")
                df_binance = pd.read_excel(file, header=9, engine='openpyxl')
                
                time_col = None
                pnl_col = None
                
                for col in df_binance.columns:
                    col_str = str(col).strip()
                    if 'Thời gian' in col_str:
                        time_col = col
                    if 'Lợi nhuận đã thực hiện' in col_str:
                        pnl_col = col
                
                if time_col is None or pnl_col is None:
                    print(f"   ⚠️ Không tìm thấy cột cần thiết!")
                    continue
                
                df_s = df_binance[[time_col, pnl_col]].copy()
                df_s = df_s.dropna(subset=[time_col, pnl_col])
                df_s[time_col] = pd.to_datetime(df_s[time_col], format='%y-%m-%d %H:%M:%S', errors='coerce')
                df_s[pnl_col] = pd.to_numeric(df_s[pnl_col], errors='coerce')
                df_s = df_s.dropna()
                
                df_s = df_s.rename(columns={time_col: 'closeTime(UTC+8)', pnl_col: 'Realized PNL'})
                df_s['date'] = df_s['closeTime(UTC+8)'].dt.date
                all_pnl.append(df_s[['date', 'Realized PNL']])
                print(f"   ✅ Đã đọc {len(df_s)} giao dịch từ Binance")
                
            except Exception as e:
                print(f"   ❌ Lỗi đọc {file}: {e}")
    
    return all_pnl

def load_calendar_data(csv_path="files/calendar_with_moon.csv"):
    """Đọc dữ liệu lịch"""
    df_full = pd.read_csv(csv_path)
    df_full["date"] = pd.to_datetime(df_full["date"], errors="coerce")
    df_full["moon_numeric"] = pd.to_numeric(df_full["moon"], errors="coerce")
    return df_full

def merge_pnl_to_calendar(df_full, all_pnl):
    """Gộp dữ liệu PNL vào calendar"""
    if all_pnl:
        df_all_pnl = pd.concat(all_pnl, ignore_index=True)
        df_all_pnl['date'] = pd.to_datetime(df_all_pnl['date'])
        daily_pnl = df_all_pnl.groupby('date')['Realized PNL'].sum().reset_index()
        daily_pnl = daily_pnl.sort_values('date')
        
        pnl_dict = dict(zip(daily_pnl['date'], daily_pnl['Realized PNL']))
        df_full['pnl'] = df_full['date'].map(pnl_dict).fillna(0)
        
        print(f"\n✅ TỔNG HỢP:")
        print(f"   📊 Tổng số giao dịch: {len(df_all_pnl)}")
        print(f"   📅 Số ngày có giao dịch: {len(daily_pnl)}")
        print(f"   💰 Tổng PNL: {daily_pnl['Realized PNL'].sum():,.2f} USD")
        
        return df_full, daily_pnl
    else:
        df_full['pnl'] = 0
        print("\n⚠️ Không có dữ liệu PNL nào được đọc!")
        return df_full, None

def filter_special_dates(df_full):
    """Lọc các ngày đặc biệt"""
    all_solar_dates = get_all_solar_dates(df_full)
    
    df_full["specdate_clean"] = df_full["specdate"].astype(str).str.strip().str.lower()
    df_full["is_moon_phase"] = df_full["moon_numeric"].isin([0, 90, 180, 270])
    df_full["is_specdate"] = df_full["specdate_clean"].isin(["ram", "rằm", "m1", "mùng 1"])
    df_full["is_solar_term"] = df_full["date"].isin(all_solar_dates)
    df_full["has_pnl"] = df_full["pnl"] != 0
    
    df_filtered = df_full[
        df_full["is_moon_phase"] | df_full["is_specdate"] |
        df_full["is_solar_term"] | df_full["has_pnl"]
    ].copy().sort_values("date").reset_index(drop=True)
    
    print(f"📅 Sau lọc: {len(df_filtered)} ngày (từ {len(df_full)})")
    return df_filtered

def load_all_data(csv_path="files/calendar_with_moon.csv"):
    """Tải toàn bộ dữ liệu"""
    print("📂 Đang đọc dữ liệu...")
    
    # Đọc calendar
    df_full = load_calendar_data(csv_path)
    
    # Đọc PNL
    all_pnl = load_pnl_data()
    
    # Gộp dữ liệu
    df_full, daily_pnl = merge_pnl_to_calendar(df_full, all_pnl)
    
    # Lọc ngày đặc biệt
    df_filtered = filter_special_dates(df_full)
    
    return df_filtered, df_full, daily_pnl