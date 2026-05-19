import datetime
from lunar_python import Solar, Lunar
import pandas as pd

# Bảng chuyển đổi Can Chi sang tiếng Việt
CAN_VIET = {
    "甲": "Giáp",
    "乙": "Ất",
    "丙": "Bính",
    "丁": "Đinh",
    "戊": "Mậu",
    "己": "Kỷ",
    "庚": "Canh",
    "辛": "Tân",
    "壬": "Nhâm",
    "癸": "Quý",
}

CHI_VIET = {
    "子": "Tý",
    "丑": "Sửu",
    "寅": "Dần",
    "卯": "Mão",
    "辰": "Thìn",
    "巳": "Tỵ",
    "午": "Ngọ",
    "未": "Mùi",
    "申": "Thân",
    "酉": "Dậu",
    "戌": "Tuất",
    "亥": "Hợi",
}

# Bảng chuyển đổi Con giáp sang tiếng Việt
ZODIAC_VIET = {
    "Rat": "Tý",
    "Ox": "Sửu",
    "Tiger": "Dần",
    "Rabbit": "Mão",
    "Dragon": "Thìn",
    "Snake": "Tỵ",
    "Horse": "Ngọ",
    "Goat": "Mùi",
    "Monkey": "Thân",
    "Rooster": "Dậu",
    "Dog": "Tuất",
    "Pig": "Hợi",
}

# Bảng chuyển đổi tháng âm lịch (nếu cần)
MONTH_VIET = {
    1: "Một", 2: "Hai", 3: "Ba", 4: "Bốn", 5: "Năm",
    6: "Sáu", 7: "Bảy", 8: "Tám", 9: "Chín", 10: "Mười",
    11: "Mười một", 12: "Mười hai"
}



class InternationalFixedCalendarLich13Thang:
    def __init__(self):
        self.month_names = [
            "January", "February", "March", "April", "May", "June",
            "Sol", "July", "August", "September", "October", "November", "December"
        ]
        #SOL là tháng thứ 7, nằm giữa tháng 6 và tháng 7 của lịch Gregory
        self.days_of_week = ["Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"]
        # Thứ tự các thứ trong tuần của IFC (Luôn cố định)
        self.thu_trong_tuan = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]
    #Lich 13 tháng có 28 ngày mỗi tháng, tổng cộng 364 ngày, còn lại 1 hoặc 2 ngày đặc biệt (Year Day và Leap Day)
    def get_ifc_date(self, date_obj):
        """Chuyển đổi từ ngày Gregory sang IFC"""
        day_of_year = date_obj.timetuple().tm_yday
        is_leap = (date_obj.year % 4 == 0 and date_obj.year % 100 != 0) or (date_obj.year % 400 == 0)
        
        # Xử lý ngày nhuận (Leap Day) và ngày cuối năm (Year Day)
        if is_leap:
            if day_of_year == 169: # Ngày nhuận thường rơi vào sau 28/6
                return "Leap Day", None, date_obj.year
            elif day_of_year > 169:
                day_of_year -= 1
        
        if day_of_year > 364:
            return "Year Day", None, date_obj.year

        # Tính toán tháng và ngày
        month_idx = (day_of_year - 1) // 28         # // lấy phần nguyên để xác định tháng
        day_of_month = ((day_of_year - 1) % 28) + 1
        thu_idx = (day_of_month - 1) % 7
        return self.thu_trong_tuan[thu_idx],day_of_month, self.month_names[month_idx], date_obj.year

    # def display_month(self, month_name, year):
    #     """In ra bảng lịch của một tháng cụ thể"""
    #     print(f"\n--- {month_name} {year} ---")
    #     print(" ".join(self.days_of_week))
        
    #     for day in range(1, 29):
    #         print(f"{day:3}", end=" ")
    #         if day % 7 == 0:
    #             print()

    def get_enoch_info(self,ngay_can_tinh):
        # Mốc Xuân Phân 2026 (Ngày 1 tháng 1 năm mới của Enoch)
        xuan_phan_2026 = datetime.date(2026, 3, 20)
        
        # Tính toán số ngày từ Xuân phân
        delta = (ngay_can_tinh - xuan_phan_2026).days
        
        # Nếu trước Xuân phân 2026 thì thuộc năm cũ (364 ngày)
        if delta < 0:
            day_of_enoch_year = delta + 365 # 364 ngày + 1
            label_nam = "cũ"
        else:
            day_of_enoch_year = (delta % 364) + 1
            label_nam = "mới"

        # Tính Mùa, Tháng, Ngày
        mua_idx = (day_of_enoch_year - 1) // 91
        ten_mua = ["Xuân", "Hạ", "Thu", "Đông"][mua_idx]
        day_in_season = ((day_of_enoch_year - 1) % 91) + 1
        
        if day_in_season <= 30:
            thang = 1 + (mua_idx * 3)
            ngay = day_in_season
        elif day_in_season <= 60:
            thang = 2 + (mua_idx * 3)
            ngay = day_in_season - 30
        else:
            thang = 3 + (mua_idx * 3)
            ngay = day_in_season - 60

        # Tính Thứ (Enoch bắt đầu năm vào Thứ Tư)
        cac_thu = ["Thứ Tư", "Thứ Năm", "Thứ Sáu", "Thứ Bảy", "Chủ Nhật", "Thứ Hai", "Thứ Ba"]
        thu_idx = (day_of_enoch_year - 1) % 7
        thu_ten = cac_thu[thu_idx]

        # In kết quả theo cấu trúc yêu cầu
        print(f"\n--- Thông tin ngày {ngay_can_tinh} theo Lịch Enoch ---")
        print(f"Ngày: {day_of_enoch_year} tuần thứ {(day_of_enoch_year - 1) // 7 + 1} của năm Enoch {label_nam}.")
        mo_ta_thang = "tháng cuối cùng của Mùa " + ten_mua if thang % 3 == 0 else f"Mùa {ten_mua}"
        print(f"Vị trí: Ngày {ngay}, Tháng {thang} ({mo_ta_thang}).")
        print(f"Thứ: {thu_ten}.")

        #hàm tìm thứ 2 của mỗi tuần
    



    def solar_to_lunar_with_ganzhi(self,year: int, month: int, day: int):
        """
        Chuyển đổi ngày Dương lịch sang Âm lịch kèm Can Chi

        Args:
            year (int): Năm dương lịch
            month (int): Tháng dương lịch (1-12)
            day (int): Ngày dương lịch (1-31)

        Returns:
            dict: {
                'solar_date': 'YYYY-MM-DD',
                'lunar_year': int,
                'lunar_month': int,
                'lunar_day': int,
                'is_leap': bool,
                'year_ganzhi': str,   # Can Chi của năm (ví dụ: Giáp Thìn)
                'month_ganzhi': str,  # Can Chi của tháng
                'day_ganzhi': str,    # Can Chi của ngày
                'zodiac': str,        # Con giáp (ví dụ: Thìn)
                'full_lunar_date': str  # Ngày âm lịch đầy đủ
            }
        """
        # Tạo đối tượng Solar từ ngày đầu vào
        solar = Solar.fromYmd(year, month, day)

        # Chuyển đổi sang Lunar
        lunar = solar.getLunar()

        # Lấy Can Chi
        year_ganzhi = lunar.getYearInGanZhi()      # Can Chi của năm
        month_ganzhi = lunar.getMonthInGanZhi()    # Can Chi của tháng
        day_ganzhi = lunar.getDayInGanZhi()        # Can Chi của ngày

        # Lấy con giáp
        zodiac = lunar.getYearShengXiao()           # Ví dụ: Thìn, Tỵ, Ngọ...

        # Tạo chuỗi ngày âm lịch đầy đủ
        full_lunar_date = lunar.toFullString()

        return {
            'solar_date': f"{year}-{month:02d}-{day:02d}",
            'lunar_year': lunar.getYear(),
            'lunar_month': lunar.getMonth(),
            'lunar_day': lunar.getDay(),
            'year_ganzhi': year_ganzhi,
            'month_ganzhi': month_ganzhi,
            'day_ganzhi': day_ganzhi,
            'zodiac': zodiac,
            'full_lunar_date': full_lunar_date
        }


    # def get_lunar_info_for_date(date_obj: datetime.date):
    #     """
    #     Wrapper cho datetime.date object
    #     """
    #     return solar_to_lunar_with_ganzhi(date_obj.year, date_obj.month, date_obj.day)    

    def convert_ganzhi_to_viet(self, ganzhi: str) -> str:
        """
        Chuyển đổi Can Chi từ tiếng Trung sang tiếng Việt
        Ví dụ: "甲子" -> "Giáp Tý"
        """
        if len(ganzhi) != 2:
            return ganzhi
        
        can = ganzhi[0]
        chi = ganzhi[1]
        
        can_viet = CAN_VIET.get(can, can)
        chi_viet = CHI_VIET.get(chi, chi)
        
        return f"{can_viet} {chi_viet}"


    def convert_zodiac_to_viet(self, zodiac_en: str) -> str:
            """
            Chuyển đổi tên Con giáp từ tiếng Anh/Trung sang tiếng Việt
            """
            return ZODIAC_VIET.get(zodiac_en, zodiac_en)
            
    def convert_lunar(self):
        """
        Đọc file CSV có cột 'date' định dạng mm/dd/yyyy
        Chuyển sang âm lịch định dạng mm/dd/yyyy
        """
        df = pd.read_csv(r"D:\PYTra\AstroFiDeepSeek\duonglich.csv")
        
        def to_lunar(date_str):
            d = pd.to_datetime(date_str, format='%m/%d/%Y')
            lunar = Solar.fromYmd(d.year, d.month, d.day).getLunar()
            ganzhi = lunar.getDayInGanZhi()
            return f"{lunar.getMonth():02d}/{lunar.getDay():02d}/{lunar.getYear()}"
        
        df['lunar_date'] = df['date'].apply(to_lunar)
        df.to_csv(r"D:\PYTra\AstroFiDeepSeek\output_lunar_dates.csv", index=False)
        print(f"✅ Đã lưu {len(df)} dòng vào D:\\PYTra\\AstroFiDeepSeek\\output_lunar_dates.csv")


    
    def process_lunar_csv(self,input_file, output_file):
        df = pd.read_csv(input_file)
        
        def get_info(row):
            d = pd.to_datetime(row['date'], format='%m/%d/%Y')
            lunar = Solar.fromYmd(d.year, d.month, d.day).getLunar()
            can_chi = self.convert_ganzhi_to_viet(lunar.getDayInGanZhi())
            return pd.Series({
                'lunar_date': f"{lunar.getMonth():02d}/{lunar.getDay():02d}/{lunar.getYear()}",
                'can': can_chi.split()[0],  # Lấy phần Can
                'chi': can_chi.split()[1]   # Lấy phần Chi
            })
        
        df[['lunar_date', 'can', 'chi']] = df.apply(get_info, axis=1)
        df[['date', 'lunar_date', 'can', 'chi']].to_csv(output_file, index=False, encoding='utf-8-sig')
        print(f"✅ Đã lưu {len(df)} dòng vào {output_file}")
        
class SpiritualTradingCalc:
    def __init__(self):
        # Mốc Trăng Non chuẩn (New Moon Reference)
        self.reference_new_moon = datetime.datetime(2000, 1, 6, 18, 14)
        self.lunar_month = 29.530588853  # Độ dài trung bình một tháng âm lịch
        
        # Mốc Xuân Phân 2026 cho lịch Enoch
        self.enoch_new_year = datetime.date(2026, 3, 20)
        # Các mốc chuyển mùa Enoch 2026 (Xuân phân 20/03)
        self.enoch_seasons = {
            "Xuân (Đầu năm)": datetime.date(2026, 3, 20),
            "Hạ":             datetime.date(2026, 6, 19),
            "Thu":            datetime.date(2026, 9, 18),
            "Đông":           datetime.date(2026, 12, 18)
        }
        
        # Danh sách New Moon 2026 (Dữ liệu dự báo thiên văn)
        self.new_moons = [
            datetime.date(2026, 1, 19), datetime.date(2026, 2, 17),
            datetime.date(2026, 3, 19), datetime.date(2026, 4, 17),
            datetime.date(2026, 5, 17), datetime.date(2026, 6, 15),
            datetime.date(2026, 7, 14), datetime.date(2026, 8, 13),
            datetime.date(2026, 9, 11), datetime.date(2026, 10, 10),
            datetime.date(2026, 11, 9), datetime.date(2026, 12, 9),
            datetime.date(2026, 12, 30) # New Moon cuối năm
        ]

    def get_enoch_data(self, date_obj):
        """Tính toán thông tin lịch Enoch"""
        delta = (date_obj - self.enoch_new_year).days

        # Chu kỳ 1 năm Enoch = 364 ngày, với YearDay/LeapDay tách riêng.
        if delta < 0:
            # Delta âm có thể xuống quá -364, nên dùng modulo an toàn
            day_of_year = (delta % 364) + 1
            status = "cũ"
        else:
            day_of_year = (delta % 364) + 1
            status = "mới"

        # Tính Mùa (91 ngày/mùa)
        mua_idx = (day_of_year - 1) // 91
        mua_names = ["Xuân", "Hạ", "Thu", "Đông"]
        day_in_season = ((day_of_year - 1) % 91) + 1

        # Tính Thứ (Enoch bắt đầu từ Thứ Tư)
        thu_names = ["Thứ 4", "Thứ 5", "Thứ 6", "Thứ 7", "Chủ Nhật", "Thứ 2", "Thứ 3"]
        thu = thu_names[(day_of_year - 1) % 7]

        return day_of_year, status, mua_names[mua_idx], day_in_season, thu

    def get_lunar_phase(self, date_obj):
        """Tính khoảng cách đến điểm Sóc (New Moon)"""
        # Chuyển date thành datetime để tính toán chính xác
        dt_obj = datetime.datetime.combine(date_obj, datetime.time(0, 0))
        diff = dt_obj - self.reference_new_moon
        days_passed = diff.total_seconds() / (24 * 3600)
        
        # Vị trí trong chu kỳ trăng (0 = New Moon, 14.7 = Full Moon)
        phase_days = days_passed % self.lunar_month
        
        # Khoảng cách tới kỳ Trăng Non tiếp theo
        days_to_next_new_moon = self.lunar_month - phase_days
        
        return phase_days, days_to_next_new_moon

    def soi_keo(self, date_obj):
        en_day, en_status, en_mua, en_day_mua, en_thu = self.get_enoch_data(date_obj)
        phase_days, next_nm = self.get_lunar_phase(date_obj)
        
        print(f"--- PHÂN TÍCH NGÀY: {date_obj.strftime('%d/%m/%Y')} ---")
        print(f"Lịch Enoch: Ngày {en_day} ({en_status}), {en_thu}, Mùa {en_mua} (Ngày {en_day_mua}/91)")
        print(f"Trạng thái Trăng: {phase_days:.2f} ngày sau New Moon")
        print(f"Khoảng cách đến New Moon tiếp theo: {next_nm:.2f} ngày")
        
        # Logic soi kèo "tâm linh"
        if phase_days < 1.5 or next_nm < 1.5:
            print(">>> CẢNH BÁO: Điểm hội tụ New Moon! Dễ có biến động mạnh (Volatility).")
        elif 14 <= phase_days <= 15.5:
            print(">>> CẢNH BÁO: Trăng Tròn (Full Moon)! Cẩn thận đảo chiều xu hướng.")
        else:
            print(">>> Xu hướng đang trong chu kỳ ổn định.")
    
    def soi_keo_hoi_tu_2026(self):
        # Thêm mốc New Moon gần nhất của tháng 12
        # New Moon gần ngày 18/12/2026 nhất thực tế là ngày 09/12 hoặc 30/12
        # Lưu ý: Chu kỳ trăng 29.5 ngày nên tháng 12/2026 có 2 lần New Moon.
    
        print(f"{'Mùa Enoch':<15} | {'Ngày Enoch':<12} | {'New Moon Gần Nhất':<15} | {'Lệch (Ngày)'}")
        print("-" * 70)
        
        for ten, ngay_en in self.enoch_seasons.items():
            closest_nm = min(self.new_moons, key=lambda d: abs(d - ngay_en))
            diff = (closest_nm - ngay_en).days
            
            canh_bao = "🚨 HỘI TỤ MẠNH" if abs(diff) <= 2 else ""
            print(f"{ten:<15} | {ngay_en} | {closest_nm} | {diff:>2} ngày {canh_bao}")
    
    def get_enoch_mondays(self, start_date, end_date):
        mondays = []
        current_date = start_date
        if isinstance(start_date, datetime.datetime):
            current_date = start_date.date()
        
        end_date_obj = end_date
        if isinstance(end_date, datetime.datetime):
            end_date_obj = end_date.date()

        while current_date <= end_date_obj:
            # Lấy dữ liệu Enoch từ hàm có sẵn
            en_day, status, en_mua, en_day_mua, en_thu = self.get_enoch_data(current_date)
            
            if en_thu == "Thứ 2":
                # 1. Xác định chỉ số mùa (0: Xuân, 1: Hạ, 2: Thu, 3: Đông)
                mua_list = ["Xuân", "Hạ", "Thu", "Đông"]
                mua_idx = mua_list.index(en_mua)
                
                # 2. Tính tháng trong mùa (1, 2, hoặc 3) dựa trên quy tắc 30-30-31
                if en_day_mua <= 30:
                    thang_trong_mua = 1
                    ngay_trong_thang = en_day_mua
                elif en_day_mua <= 60:
                    thang_trong_mua = 2
                    ngay_trong_thang = en_day_mua - 30
                else:
                    thang_trong_mua = 3
                    ngay_trong_thang = en_day_mua - 60
                
                # 3. Tính tổng số tháng thực tế (từ 1 đến 12)
                thang_thuc_te = (mua_idx * 3) + thang_trong_mua
                
                dt_ms = int(datetime.datetime.combine(current_date, datetime.time(0, 0)).timestamp() * 1000)
                
                mondays.append({
                    'time': dt_ms,
                    'label': f"Thứ 2, {ngay_trong_thang}/{thang_thuc_te}",
                    'date_obj': current_date  # <--- ĐÂY CHÍNH LÀ BIẾN BẠN CẦN
                })
                current_date += datetime.timedelta(days=7)
            else:
                current_date += datetime.timedelta(days=1)
        return mondays
    
    def get_solar_event(self, date_obj):
        """Kiểm tra xem ngày có trùng với các điểm Phân/Chí không (Sai số +/- 1 ngày)"""
        # Các mốc trung bình hàng năm
        events = {
            "Xuân Phân": (3, 20),
            "Hạ Chí": (6, 21),
            "Thu Phân": (9, 22),
            "Đông Chí": (12, 21)
        }
        
        for name, (month, day) in events.items():
            # Tạo đối tượng date cho sự kiện trong năm của date_obj
            event_date = datetime.date(date_obj.year, month, day)
            # Nếu ngày đang xét cách sự kiện trong khoảng 1 ngày
            if abs((date_obj - event_date).days) <= 7:
                return f" [{name}]"
        return ""
    

import pandas as pd
import os
from glob import glob
class ReadFiles:
    def read_multiple_excel_files(self, file_pattern, sheet_name=0):
        """
        Đọc nhiều file Excel từ một pattern hoặc danh sách file
        file excel có 2 loại của binance + Bingx

        
        Args:
            file_pattern (str or list): Đường dẫn pattern (vd: "data/*.xlsx") hoặc list file paths
            sheet_name (int or str): Tên sheet hoặc số thứ tự sheet (mặc định sheet đầu tiên)
        
        Returns:
            dict: {tên_file: DataFrame}
        """
            # Lấy đường dẫn thư mục chứa script hiện tại
        script_dir = os.path.dirname(os.path.abspath(__file__))
        # Tạo đường dẫn tuyệt đối đến file pattern
        full_pattern = os.path.join(script_dir, file_pattern)
        print(f"📂 Đang tìm trong: {full_pattern}")
    
        files = glob(full_pattern)
        print(f"🔍 Tìm thấy {len(files)} file")

        # Lấy danh sách file
        # if isinstance(file_pattern, list):
        #     files = file_pattern
        # else:
        #     files = glob(file_pattern)
        
        if not files:
            print("❌ Không tìm thấy file nào!")
            return {}
        
        results = {}
        for file in files:
            try:
                df = pd.read_excel(file, sheet_name=sheet_name)
                file_name = os.path.basename(file)
                results[file_name] = df
                print(f"✅ Đã đọc: {file_name} - {len(df)} dòng")
            except Exception as e:
                print(f"❌ Lỗi đọc {file}: {e}")
        
        return results

readexcel = ReadFiles()
data =readexcel.read_multiple_excel_files("files/*.xlsx")

    # Truy cập từng file
for file_name, df in data.items():
    print(f"\n📊 {file_name}:")
    print(df.head())

# Hoặc với 1 giá trị đơn lẻ
date_str = "20-4-2025 12:12:12"
date_obj = pd.to_datetime(date_str, format='%d-%m-%Y %H:%M:%S')
new_date = date_obj.strftime('%m/%d/%Y')
print(new_date)  # 04/20/2025

# --- Chạy thử ---
# hom_nay = datetime.date(2026, 4, 1)  # Thay đổi ngày ở đây nếu cần %yyyy %m %d
# cal = InternationalFixedCalendarLich13Thang()
# cal.process_lunar_csv("files\duonglich.csv", "files\output_lunar_dates.csv")

# t,d, m, y = cal.get_ifc_date(hom_nay)
# print(f"\nNgày {hom_nay} theo Lịch Gregory 13Thang tương ứng với: {t} {d} {m} {y} (IFC) \n")
# cal.get_enoch_info(hom_nay)


# # Chạy thử cho hôm nay
# #SpiritualTradingCalc
# #tinh lich Enoch + Trăng cho ngày hôm nay 
# calc = SpiritualTradingCalc()
# calc.soi_keo(hom_nay)
# calc.soi_keo_hoi_tu_2026()

# Test với ngày 16/05/2026
# result = cal.solar_to_lunar_with_ganzhi(2026, 5,1)
# print("KẾT QUẢ CHUYỂN ĐỔI:")
# print(f"  Dương lịch: {result['solar_date']}")
# print(f"  Âm lịch: {result['lunar_year']}-{result['lunar_month']}-{result['lunar_day']}")
# print(f"  Năm Can Chi: {cal.convert_ganzhi_to_viet(result['year_ganzhi'])}")
# print(f"  Tháng Can Chi: {cal.convert_ganzhi_to_viet(result['month_ganzhi'])}")
# print(f"  Ngày Can Chi: {cal.convert_ganzhi_to_viet(result['day_ganzhi'])}")
# print(f"  Con giáp: {cal.convert_zodiac_to_viet(result['zodiac'])}")
# print(f"  Đầy đủ: {result['full_lunar_date']}")

# print("\n" + "-" * 50 + "\n")

    # Test với datetime.date object
# test_date = datetime.date(2026, 5, 16)
# result2 = cal.get_lunar_info_for_date(test_date)
# print(f"Từ datetime.date({test_date}):")
# print(f"  Âm lịch: {result2['lunar_year']}-{result2['lunar_month']}-{result2['lunar_day']}")
# print(f"  Năm {result2['year_ganzhi']}, tháng {result2['month_ganzhi']}, ngày {result2['day_ganzhi']}")