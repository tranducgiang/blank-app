# macro.py
"""
Module chứa các hằng số và bảng tra cứu chung cho toàn bộ ứng dụng
"""

from datetime import datetime


# ──────────────────────────────────────────────────────────────
# CSS
# ──────────────────────────────────────────────────────────────
APP_CSS = """
<style>
.stApp { background-color: #0d0d1a; }

.stButton button {
    font-size: 13px;
    padding: 4px 16px;
    background-color: #1e1e30;
    color: #aaaacc;
    border: 1px solid #333;
    border-radius: 6px;
    margin: 2px;
    cursor: pointer;
}
.stButton button:hover {
    background-color: #2a2a40;
    color: white;
}

.start-btn button {
    background-color: #00aa44;
    color: white;
    border-color: #00ff66;
    font-weight: bold;
}
.start-btn button:hover { background-color: #00cc55; }

.info-text {
    color: #7fff7f;
    margin-left: 14px;
    font-size: 11px;
}

div[data-testid="stVerticalBlock"] { gap: 0rem; }
</style>
"""

# ──────────────────────────────────────────────────────────────
# TỨ TRỤ / XEM LỘC
# ──────────────────────────────────────────────────────────────

_GIO_MAP = {
    "Tý (23-1)": 23, "Sửu (1-3)": 1,  "Dần (3-5)": 3,  "Mão (5-7)": 5,
    "Thìn (7-9)": 7, "Tỵ (9-11)": 9,  "Ngọ (11-13)": 11, "Mùi (13-15)": 13,
    "Thân (15-17)": 15, "Dậu (17-19)": 17, "Tuất (19-21)": 19, "Hợi (21-23)": 21,
}

# ==================== BẢNG CHUYỂN CHỮ HÁN → TIẾNG VIỆT ====================
HAN_TO_CAN = {
    "甲": "Giáp", "乙": "Ất", "丙": "Bính", "丁": "Đinh", "戊": "Mậu",
    "己": "Kỷ", "庚": "Canh", "辛": "Tân", "壬": "Nhâm", "癸": "Quý",
}

HAN_TO_CHI = {
    "子": "Tý", "丑": "Sửu", "寅": "Dần", "卯": "Mão", "辰": "Thìn",
    "巳": "Tỵ", "午": "Ngọ", "未": "Mùi", "申": "Thân", "酉": "Dậu",
    "戌": "Tuất", "亥": "Hợi",
}

# ==================== NGŨ HÀNH ====================
NGU_HANH = {
    # Thiên can
    "Giáp": "Mộc", "Ất": "Mộc",
    "Bính": "Hỏa", "Đinh": "Hỏa",
    "Mậu": "Thổ", "Kỷ": "Thổ",
    "Canh": "Kim", "Tân": "Kim",
    "Nhâm": "Thủy", "Quý": "Thủy",
    # Địa chi
    "Tý": "Thủy", "Hợi": "Thủy",
    "Dần": "Mộc", "Mão": "Mộc",
    "Tỵ": "Hỏa", "Ngọ": "Hỏa",
    "Thân": "Kim", "Dậu": "Kim",
    "Thìn": "Thổ", "Tuất": "Thổ", "Sửu": "Thổ", "Mùi": "Thổ",
}

# ==================== TÀI TINH (KHẮC RA) ====================
TAI_MAP = {
    "Mộc": "Thổ",  # Mộc khắc Thổ
    "Hỏa": "Kim",  # Hỏa khắc Kim
    "Thổ": "Thủy", # Thổ khắc Thủy
    "Kim": "Mộc",  # Kim khắc Mộc
    "Thủy": "Hỏa", # Thủy khắc Hỏa
}

# ==================== LỘC THẦN ====================
LOC_THAN = {
    "Giáp": "Dần", "Ất": "Mão",
    "Bính": "Tỵ", "Đinh": "Ngọ",
    "Mậu": "Tỵ", "Kỷ": "Ngọ",
    "Canh": "Thân", "Tân": "Dậu",
    "Nhâm": "Hợi", "Quý": "Tý",
}

# ==================== ÂM DƯƠNG CỦA CAN ====================
AM_DUONG_CAN = {
    "Giáp": "Dương", "Ất": "Âm",
    "Bính": "Dương", "Đinh": "Âm",
    "Mậu": "Dương", "Kỷ": "Âm",
    "Canh": "Dương", "Tân": "Âm",
    "Nhâm": "Dương", "Quý": "Âm",
}

# ==================== 60 HOA GIÁP ====================
CAN_CHI_60 = [
    "Giáp Tý", "Ất Sửu", "Bính Dần", "Đinh Mão", "Mậu Thìn", "Kỷ Tỵ", "Canh Ngọ", "Tân Mùi", "Nhâm Thân", "Quý Dậu",
    "Giáp Tuất", "Ất Hợi", "Bính Tý", "Đinh Sửu", "Mậu Dần", "Kỷ Mão", "Canh Thìn", "Tân Tỵ", "Nhâm Ngọ", "Quý Mùi",
    "Giáp Thân", "Ất Dậu", "Bính Tuất", "Đinh Hợi", "Mậu Tý", "Kỷ Sửu", "Canh Dần", "Tân Mão", "Nhâm Thìn", "Quý Tỵ",
    "Giáp Ngọ", "Ất Mùi", "Bính Thân", "Đinh Dậu", "Mậu Tuất", "Kỷ Hợi", "Canh Tý", "Tân Sửu", "Nhâm Dần", "Quý Mão",
    "Giáp Thìn", "Ất Tỵ", "Bính Ngọ", "Đinh Mùi", "Mậu Thân", "Kỷ Dậu", "Canh Tuất", "Tân Hợi", "Nhâm Tý", "Quý Sửu",
    "Giáp Dần", "Ất Mão", "Bính Thìn", "Đinh Tỵ", "Mậu Ngọ", "Kỷ Mùi", "Canh Thân", "Tân Dậu", "Nhâm Tuất", "Quý Hợi"
]

# ==================== BẢNG TÀNG CAN THEO THÁNG (CHO TIẾT KHÍ) ====================
# Cấu trúc: "Địa chi": {"start_date": (tháng, ngày), "schedule": [(can, số_ngày, hành), ...]}
MONTH_SCHEDULE = {
    "Dần": {"start_date": (2, 4), "schedule": [("Mậu", 7, "Thổ"), ("Bính", 7, "Hỏa"), ("Giáp", 16, "Mộc")]},
    "Mão": {"start_date": (3, 5), "schedule": [("Giáp", 10, "Mộc"), ("Ất", 20, "Mộc")]},
    "Thìn": {"start_date": (4, 4), "schedule": [("Ất", 9, "Mộc"), ("Quý", 3, "Thủy"), ("Mậu", 18, "Thổ")]},
    "Tỵ": {"start_date": (5, 5), "schedule": [("Mậu", 5, "Thổ"), ("Canh", 9, "Kim"), ("Bính", 16, "Hỏa")]},
    "Ngọ": {"start_date": (6, 5), "schedule": [("Bính", 10, "Hỏa"), ("Kỷ", 9, "Thổ"), ("Đinh", 11, "Hỏa")]},
    "Mùi": {"start_date": (7, 7), "schedule": [("Đinh", 9, "Hỏa"), ("Ất", 3, "Mộc"), ("Kỷ", 18, "Thổ")]},
    "Thân": {"start_date": (8, 7), "schedule": [("Mậu", 7, "Thổ"), ("Nhâm", 7, "Thủy"), ("Canh", 16, "Kim")]},
    "Dậu": {"start_date": (9, 7), "schedule": [("Canh", 10, "Kim"), ("Tân", 20, "Kim")]},
    "Tuất": {"start_date": (10, 8), "schedule": [("Tân", 9, "Kim"), ("Đinh", 3, "Hỏa"), ("Mậu", 18, "Thổ")]},
    "Hợi": {"start_date": (11, 7), "schedule": [("Mậu", 7, "Thổ"), ("Giáp", 7, "Mộc"), ("Nhâm", 16, "Thủy")]},
    "Tý": {"start_date": (12, 7), "schedule": [("Nhâm", 10, "Thủy"), ("Quý", 20, "Thủy")]},
    "Sửu": {"start_date": (1, 5), "schedule": [("Quý", 9, "Thủy"), ("Tân", 3, "Kim"), ("Kỷ", 18, "Thổ")]},
}

# ==================== HÀM TIỆN ÍCH ====================
def parse_ganzhi(ganzhi_str: str) -> tuple[str, str]:
    """
    Nhận chuỗi Can Chi từ lunar_python (2 ký tự Hán, ví dụ '甲子')
    và trả về tuple tiếng Việt ('Giáp', 'Tý').
    """
    s = ganzhi_str.strip().replace(" ", "")
    can_han = s[0] if len(s) > 0 else ""
    chi_han = s[1] if len(s) > 1 else ""
    can_viet = HAN_TO_CAN.get(can_han, can_han)
    chi_viet = HAN_TO_CHI.get(chi_han, chi_han)
    return can_viet, chi_viet


def get_chi_by_date(date_obj: datetime) -> str:
    """Xác định Địa chi của tháng dựa vào ngày"""
    month, day = date_obj.month, date_obj.day
    
    if (month == 2 and day >= 4) or (month == 3 and day <= 4):
        return "Dần"
    elif (month == 3 and day >= 5) or (month == 4 and day <= 4):
        return "Mão"
    elif (month == 4 and day >= 5) or (month == 5 and day <= 4):
        return "Thìn"
    elif (month == 5 and day >= 5) or (month == 6 and day <= 4):
        return "Tỵ"
    elif (month == 6 and day >= 5) or (month == 7 and day <= 6):
        return "Ngọ"
    elif (month == 7 and day >= 7) or (month == 8 and day <= 6):
        return "Mùi"
    elif (month == 8 and day >= 7) or (month == 9 and day <= 6):
        return "Thân"
    elif (month == 9 and day >= 7) or (month == 10 and day <= 7):
        return "Dậu"
    elif (month == 10 and day >= 8) or (month == 11 and day <= 6):
        return "Tuất"
    elif (month == 11 and day >= 7) or (month == 12 and day <= 6):
        return "Hợi"
    elif (month == 12 and day >= 7) or (month == 1 and day <= 4):
        return "Tý"
    else:
        return "Sửu"


def get_element_for_date(date_obj: datetime) -> str:
    """Tính hành tiết khí cho một ngày dựa vào MONTH_SCHEDULE"""
    month, day = date_obj.month, date_obj.day
    
    # Xác định tháng chi và ngày bắt đầu
    if (month == 2 and day >= 4) or (month == 3 and day <= 4):
        chi = "Dần"
        start_date = datetime(date_obj.year, 2, 4)
    elif (month == 3 and day >= 5) or (month == 4 and day <= 4):
        chi = "Mão"
        start_date = datetime(date_obj.year, 3, 5)
    elif (month == 4 and day >= 5) or (month == 5 and day <= 4):
        chi = "Thìn"
        start_date = datetime(date_obj.year, 4, 4)
    elif (month == 5 and day >= 5) or (month == 6 and day <= 4):
        chi = "Tỵ"
        start_date = datetime(date_obj.year, 5, 5)
    elif (month == 6 and day >= 5) or (month == 7 and day <= 6):
        chi = "Ngọ"
        start_date = datetime(date_obj.year, 6, 5)
    elif (month == 7 and day >= 7) or (month == 8 and day <= 6):
        chi = "Mùi"
        start_date = datetime(date_obj.year, 7, 7)
    elif (month == 8 and day >= 7) or (month == 9 and day <= 6):
        chi = "Thân"
        start_date = datetime(date_obj.year, 8, 7)
    elif (month == 9 and day >= 7) or (month == 10 and day <= 7):
        chi = "Dậu"
        start_date = datetime(date_obj.year, 9, 7)
    elif (month == 10 and day >= 8) or (month == 11 and day <= 6):
        chi = "Tuất"
        start_date = datetime(date_obj.year, 10, 8)
    elif (month == 11 and day >= 7) or (month == 12 and day <= 6):
        chi = "Hợi"
        start_date = datetime(date_obj.year, 11, 7)
    elif (month == 12 and day >= 7) or (month == 1 and day <= 4):
        chi = "Tý"
        start_date = datetime(date_obj.year, 12, 7)
    else:
        chi = "Sửu"
        start_date = datetime(date_obj.year, 1, 5)
    
    days_since = (date_obj - start_date).days + 1
    schedule = MONTH_SCHEDULE[chi]["schedule"]
    
    total = 0
    for can, days, hanh in schedule:
        total += days
        if days_since <= total:
            return hanh
    return schedule[-1][2]


# macro.py (thêm vào cuối file)

# ==================== NGÀY BẮT ĐẦU TIẾT KHÍ ====================
# Format: (tháng, ngày, tên tiết khí)
TIET_KHI_STARTS = [
    (1, 5, "Tiểu Hàn"), (1, 20, "Đại Hàn"),
    (2, 4, "Lập Xuân"), (2, 19, "Vũ Thủy"),
    (3, 5, "Kinh Trập"), (3, 20, "Xuân Phân"),
    (4, 4, "Thanh Minh"), (4, 20, "Cốc Vũ"),
    (5, 5, "Lập Hạ"), (5, 21, "Tiểu Mãn"),
    (6, 5, "Mang Chủng"), (6, 21, "Hạ Chí"),
    (7, 7, "Tiểu Thử"), (7, 23, "Đại Thử"),
    (8, 7, "Lập Thu"), (8, 23, "Xử Thử"),
    (9, 7, "Bạch Lộ"), (9, 23, "Thu Phân"),
    (10, 8, "Hàn Lộ"), (10, 23, "Sương Giáng"),
    (11, 7, "Lập Đông"), (11, 22, "Tiểu Tuyết"),
    (12, 7, "Đại Tuyết"), (12, 21, "Đông Chí"),
]

# ==================== BẢNG TÀNG CAN THEO THÁNG ====================
MONTH_SCHEDULE = {
    "Dần": {"start_date": (2, 4), "schedule": [("Mậu", 7, "Thổ"), ("Bính", 7, "Hỏa"), ("Giáp", 16, "Mộc")]},
    "Mão": {"start_date": (3, 5), "schedule": [("Giáp", 10, "Mộc"), ("Ất", 20, "Mộc")]},
    "Thìn": {"start_date": (4, 4), "schedule": [("Ất", 9, "Mộc"), ("Quý", 3, "Thủy"), ("Mậu", 18, "Thổ")]},
    "Tỵ": {"start_date": (5, 5), "schedule": [("Mậu", 5, "Thổ"), ("Canh", 9, "Kim"), ("Bính", 16, "Hỏa")]},
    "Ngọ": {"start_date": (6, 5), "schedule": [("Bính", 10, "Hỏa"), ("Kỷ", 9, "Thổ"), ("Đinh", 11, "Hỏa")]},
    "Mùi": {"start_date": (7, 7), "schedule": [("Đinh", 9, "Hỏa"), ("Ất", 3, "Mộc"), ("Kỷ", 18, "Thổ")]},
    "Thân": {"start_date": (8, 7), "schedule": [("Mậu", 7, "Thổ"), ("Nhâm", 7, "Thủy"), ("Canh", 16, "Kim")]},
    "Dậu": {"start_date": (9, 7), "schedule": [("Canh", 10, "Kim"), ("Tân", 20, "Kim")]},
    "Tuất": {"start_date": (10, 8), "schedule": [("Tân", 9, "Kim"), ("Đinh", 3, "Hỏa"), ("Mậu", 18, "Thổ")]},
    "Hợi": {"start_date": (11, 7), "schedule": [("Mậu", 7, "Thổ"), ("Giáp", 7, "Mộc"), ("Nhâm", 16, "Thủy")]},
    "Tý": {"start_date": (12, 7), "schedule": [("Nhâm", 10, "Thủy"), ("Quý", 20, "Thủy")]},
    "Sửu": {"start_date": (1, 5), "schedule": [("Quý", 9, "Thủy"), ("Tân", 3, "Kim"), ("Kỷ", 18, "Thổ")]},
}


def get_tiet_khi_from_date(date_obj):
    """
    Xác định tiết khí dựa vào ngày
    Args:
        date_obj: datetime object
    Returns:
        str: Tên tiết khí
    """
    month, day = date_obj.month, date_obj.day
    
    current_term = "Đông Chí"  # mặc định
    for m, d, term in TIET_KHI_STARTS:
        if (month > m) or (month == m and day >= d):
            current_term = term
        else:
            break
    
    return current_term


def get_hanh_tiet_khi_from_date(date_obj):
    """
    Tính hành tiết khí dựa vào MONTH_SCHEDULE
    Args:
        date_obj: datetime object
    Returns:
        str: Ngũ hành (Mộc, Hỏa, Thổ, Kim, Thủy)
    """
    month, day = date_obj.month, date_obj.day
    year = date_obj.year
    
    # Xác định tháng chi và ngày bắt đầu tháng
    if (month == 2 and day >= 4) or (month == 3 and day <= 4):
        chi = "Dần"
        start_date = datetime(year, 2, 4)
    elif (month == 3 and day >= 5) or (month == 4 and day <= 4):
        chi = "Mão"
        start_date = datetime(year, 3, 5)
    elif (month == 4 and day >= 5) or (month == 5 and day <= 4):
        chi = "Thìn"
        start_date = datetime(year, 4, 4)
    elif (month == 5 and day >= 5) or (month == 6 and day <= 4):
        chi = "Tỵ"
        start_date = datetime(year, 5, 5)
    elif (month == 6 and day >= 5) or (month == 7 and day <= 6):
        chi = "Ngọ"
        start_date = datetime(year, 6, 5)
    elif (month == 7 and day >= 7) or (month == 8 and day <= 6):
        chi = "Mùi"
        start_date = datetime(year, 7, 7)
    elif (month == 8 and day >= 7) or (month == 9 and day <= 6):
        chi = "Thân"
        start_date = datetime(year, 8, 7)
    elif (month == 9 and day >= 7) or (month == 10 and day <= 7):
        chi = "Dậu"
        start_date = datetime(year, 9, 7)
    elif (month == 10 and day >= 8) or (month == 11 and day <= 6):
        chi = "Tuất"
        start_date = datetime(year, 10, 8)
    elif (month == 11 and day >= 7) or (month == 12 and day <= 6):
        chi = "Hợi"
        start_date = datetime(year, 11, 7)
    elif (month == 12 and day >= 7) or (month == 1 and day <= 4):
        chi = "Tý"
        start_date = datetime(year, 12, 7)
    else:
        chi = "Sửu"
        start_date = datetime(year, 1, 5)
    
    # Tính số ngày từ đầu tháng
    days_since_start = (date_obj - start_date).days + 1
    
    # Lấy schedule
    schedule = MONTH_SCHEDULE[chi]["schedule"]
    
    # Tìm hành tương ứng
    total = 0
    for can, days, hanh in schedule:
        total += days
        if days_since_start <= total:
            return hanh
    
    return schedule[-1][2]


def get_tiet_khi_info(date_obj):
    """
    Hàm tổng hợp: nhận datetime, trả về (tiết_khí, hành_tiết_khí)
    Args:
        date_obj: datetime object
    Returns:
        tuple: (tiet_khi, hanh_tiet_khi)
    """
    tiet_khi = get_tiet_khi_from_date(date_obj)
    hanh = get_hanh_tiet_khi_from_date(date_obj)
    return tiet_khi, hanh


    # ==================== BỔ SUNG CHO TuViAnalyzer ====================

# Danh sách Thiên can và Địa chi (dạng list)
DANH_SACH_CAN = ["Giáp", "Ất", "Bính", "Đinh", "Mậu", "Kỷ", "Canh", "Tân", "Nhâm", "Quý"]
DANH_SACH_CHI = ["Tý", "Sửu", "Dần", "Mão", "Thìn", "Tỵ", "Ngọ", "Mùi", "Thân", "Dậu", "Tuất", "Hợi"]

# Map sinh - dùng để tra cứu hành sinh cho Nhật chủ
SINH_MAP = {
    "Thủy": "Mộc",
    "Mộc": "Hỏa", 
    "Hỏa": "Thổ",
    "Thổ": "Kim",
    "Kim": "Thủy"
}

# Map khắc - dùng để tra cứu hành khắc Nhật chủ
KHAC_MAP = {
    "Mộc": "Thổ",
    "Thổ": "Thủy", 
    "Thủy": "Hỏa",
    "Hỏa": "Kim",
    "Kim": "Mộc"
}

LUC_HOP = {
    "Tý": "Sửu", "Sửu": "Tý",
    "Dần": "Hợi", "Hợi": "Dần",
    "Mão": "Tuất", "Tuất": "Mão",
    "Thìn": "Dậu", "Dậu": "Thìn",
    "Tỵ": "Thân", "Thân": "Tỵ",
    "Ngọ": "Mùi", "Mùi": "Ngọ"
}

LUC_XUNG = {
    "Tý": "Ngọ", "Ngọ": "Tý",
    "Sửu": "Mùi", "Mùi": "Sửu",
    "Dần": "Thân", "Thân": "Dần",
    "Mão": "Dậu", "Dậu": "Mão",
    "Thìn": "Tuất", "Tuất": "Thìn",
    "Tỵ": "Hợi", "Hợi": "Tỵ"
}