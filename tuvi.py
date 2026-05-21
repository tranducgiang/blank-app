# tuvi.py
"""
Module xem lộc ngày theo Tứ Trụ
Tích hợp vào ứng dụng PNL + Lịch Âm Dương
"""

from datetime import datetime
from lunar_python import Solar
import pandas as pd
from macro import (
    HAN_TO_CAN, HAN_TO_CHI, NGU_HANH, TAI_MAP, LOC_THAN, AM_DUONG_CAN,
    CAN_CHI_60, MONTH_SCHEDULE, TIET_KHI_STARTS,LUC_HOP, LUC_XUNG,
    DANH_SACH_CAN, DANH_SACH_CHI, SINH_MAP, KHAC_MAP,  # Thêm các biến mới
    parse_ganzhi, get_tiet_khi_info
)


class TuViAnalyzer:
    """Phân tích Tứ Trụ và xem lộc ngày"""
    
    # ==================== CÁC HẰNG SỐ ====================
    CAN = DANH_SACH_CAN
    CHI = DANH_SACH_CHI
    NGU_HANH = NGU_HANH
    LOC_THAN = LOC_THAN
    CAN_CHI_60 = CAN_CHI_60
    MONTH_SCHEDULE = MONTH_SCHEDULE
    LUC_HOP = LUC_HOP
    LUC_XUNG = LUC_XUNG
    # ==================== TÀI TINH ====================
    def get_tai_tinh(self, nhat_can):
        """Trả về ngũ hành Tài Tinh của Nhật Can"""
        if nhat_can not in self.NGU_HANH:
            return ""
        hanh = self.NGU_HANH[nhat_can]
        return TAI_MAP.get(hanh, "")
    
    def get_tai_can_chi(self, nhat_can):
        """Trả về danh sách Can/Chi thuộc Tài Tinh"""
        tai_hanh = self.get_tai_tinh(nhat_can)
        if not tai_hanh:
            return [], []
        can_tai = [c for c in self.CAN if self.NGU_HANH.get(c) == tai_hanh]
        chi_tai = [c for c in self.CHI if self.NGU_HANH.get(c) == tai_hanh]
        return can_tai, chi_tai
    
    # ==================== PHÂN BIỆT CHÍNH TÀI / THIÊN TÀI ====================
    def phan_biet_tai(self, nhat_can, can_ngay):
        """Xác định Chính Tài hay Thiên Tài dựa trên tính Âm Dương"""
        if nhat_can not in AM_DUONG_CAN or can_ngay not in AM_DUONG_CAN:
            return "Tài"
        
        if AM_DUONG_CAN[nhat_can] != AM_DUONG_CAN[can_ngay]:
            return "Chính Tài"
        else:
            return "Thiên Tài"
    
    # ==================== CAN CHI TỪ NGÀY ====================
    def get_can_chi_from_date(self, date):
        """Tính Can Chi từ ngày dương lịch"""
        base_date = datetime(1900, 1, 1)
        days_diff = (date - base_date).days
        index = days_diff % 60
        can_chi = self.CAN_CHI_60[index]
        return can_chi[0], can_chi[1]
    
    # ==================== TÍNH TỨ TRỤ ====================
    def tinh_tu_tru(self, ngay_thang_nam_sinh, gio_sinh=12):
        """Tính Tứ Trụ từ ngày sinh"""
        try:
            solar = Solar.fromYmdHms(
                ngay_thang_nam_sinh.year,
                ngay_thang_nam_sinh.month,
                ngay_thang_nam_sinh.day,
                gio_sinh, 0, 0
            )
            lunar = solar.getLunar()
            
            year_gan_zhi = lunar.getYearInGanZhi()
            month_gan_zhi = lunar.getMonthInGanZhi()
            day_gan_zhi = lunar.getDayInGanZhi()
            time_gan_zhi = lunar.getTimeInGanZhi()
            
            year_can, year_chi = parse_ganzhi(year_gan_zhi)
            month_can, month_chi = parse_ganzhi(month_gan_zhi)
            day_can, day_chi = parse_ganzhi(day_gan_zhi)
            time_can, time_chi = parse_ganzhi(time_gan_zhi)

            return {
                "nam": f"{year_can}{year_chi}",
                "thang": f"{month_can}{month_chi}",
                "ngay": f"{day_can}{day_chi}",
                "gio": f"{time_can}{time_chi}",
                "nhat_can": day_can,
                "nhat_chi": day_chi,
            }
        except Exception as e:
            print(f"Lỗi tính Tứ Trụ: {e}")
            return None
    
    # ==================== XEM LỘC NGÀY ====================
    def xem_loc_ngay(self, tu_tru, ngay_hom_nay):
        """Xem ngày có lộc hay không"""
        if not tu_tru:
            return None
        
        nhat_can = tu_tru["nhat_can"]
        nhat_chi = tu_tru["nhat_chi"]
        today_can, today_chi = self.get_can_chi_from_date(ngay_hom_nay)
        
        ket_qua = {
            "ngay_xem": ngay_hom_nay.strftime("%d/%m/%Y"),
            "nhat_can": nhat_can,
            "nhat_chi": nhat_chi,
            "today_can": today_can,
            "today_chi": today_chi,
            "co_tai": False,
            "co_loc": False,
            "loai_tai": None,
            "giai_thich": []
        }
        
        # 1. Kiểm tra Tài Tinh
        can_tai, chi_tai = self.get_tai_can_chi(nhat_can)
        if today_can in can_tai or today_chi in chi_tai:
            ket_qua["co_tai"] = True
            ket_qua["loai_tai"] = self.phan_biet_tai(nhat_can, today_can)
            ket_qua["giai_thich"].append(f"📌 Có Tài: {ket_qua['loai_tai']}")
        
        # 2. Kiểm tra Lộc Thần
        loc_than = self.LOC_THAN.get(nhat_can, "")
        if today_chi == loc_than:
            ket_qua["co_loc"] = True
            ket_qua["giai_thich"].append(f"📌 Có Lộc Thần: {today_chi}")
        
        # 3. Kết luận
        if ket_qua["co_tai"] and ket_qua["co_loc"]:
            ket_qua["ket_luan"] = "✅ ĐẠI LỘC - Có cả Tài và Lộc!"
            ket_qua["mau_sac"] = "#00ff88"
        elif ket_qua["co_tai"]:
            ket_qua["ket_luan"] = f"💰 Có {ket_qua['loai_tai']} - Cơ hội về tiền bạc!"
            ket_qua["mau_sac"] = "#ffaa00"
        elif ket_qua["co_loc"]:
            ket_qua["ket_luan"] = "🍀 Có Lộc - May mắn!"
            ket_qua["mau_sac"] = "#66ff66"
        else:
            ket_qua["ket_luan"] = "⚖️ Ngày thường"
            ket_qua["mau_sac"] = "#aaaaaa"
        
        return ket_qua
    
    # ==================== TIẾT KHÍ ====================
    def get_tiet_khi_info(self, date_obj):
        """
        Lấy thông tin tiết khí cho một ngày
        Args:
            date_obj: datetime object
        Returns:
            tuple: (tiet_khi, hanh_tiet_khi)
        """
        return get_tiet_khi_info(date_obj)

    def luan_ngay_loc(self, ngay_sinh, ngay_kiem_tra, gio_sinh=12):
        """Luận giải chi tiết một ngày có mang lại lộc hay hao tài"""
        from macro import DANH_SACH_CAN, DANH_SACH_CHI, SINH_MAP, KHAC_MAP, LUC_HOP, LUC_XUNG
        
        if not ngay_sinh or not ngay_kiem_tra:
            return None
        
        # 1. Lấy Tứ trụ bản thân
        tu_tru = self.tinh_tu_tru(ngay_sinh, gio_sinh)
        if not tu_tru:
            return None
        
        nhat_can = tu_tru["nhat_can"]
        nhat_chi = tu_tru["nhat_chi"]
        hanh_nhat = NGU_HANH.get(nhat_can, "")
        
        # 2. Lấy thông tin ngày kiểm tra
        today_can, today_chi = self.get_can_chi_from_date(ngay_kiem_tra)
        tiet_khi, hanh_tiet_khi = self.get_tiet_khi_info(ngay_kiem_tra)
        
        hanh_can = NGU_HANH.get(today_can, "")
        hanh_chi = NGU_HANH.get(today_chi, "")
        
        # 3. Các hành quan trọng
        hanh_tai = TAI_MAP.get(hanh_nhat, "")           # Tài của Nhật chủ
        hanh_sinh = SINH_MAP.get(hanh_nhat, "")         # Hành sinh cho Nhật chủ
        hanh_khac = KHAC_MAP.get(hanh_nhat, "")         # Hành khắc Nhật chủ
        
        # 4. Tra cứu nhanh
        can_tai, chi_tai = self.get_tai_can_chi(nhat_can)
        loc_than = LOC_THAN.get(nhat_can, "")
        
        # 5. Khởi tạo kết quả
        ket_qua = {
            "thong_tin_co_ban": {
                "nhat_can": nhat_can, "nhat_chi": nhat_chi, "hanh_nhat_chu": hanh_nhat,
                "ngay_xem": ngay_kiem_tra.strftime("%d/%m/%Y"),
                "can_chi_ngay": f"{today_can}{today_chi}", "tiet_khi": tiet_khi, "hanh_tiet_khi": hanh_tiet_khi
            },
            "diem_so": 0, "co_hoi": [], "canh_bao": [], "khuyen_nghi": []
        }
        
        # 6. Chấm điểm
        if today_can in can_tai or today_chi in chi_tai:
            loai = self.phan_biet_tai(nhat_can, today_can) if today_can in can_tai else "Thiên Tài"
            ket_qua["co_hoi"].append(f"💰 {loai} - Cơ hội tiền bạc")
            ket_qua["diem_so"] += 5
        
        if today_chi == loc_than:
            ket_qua["co_hoi"].append(f"🍀 Lộc Thần {today_chi} - May mắn")
            ket_qua["diem_so"] += 3
        
        # Can ngày
        if hanh_can == hanh_nhat:
            ket_qua["canh_bao"].append("⚠️ Tỷ Kiếp - Dễ bị tranh giành, hao tài")
            ket_qua["diem_so"] -= 3
        elif hanh_can == hanh_sinh:
            ket_qua["co_hoi"].append("📚 Ấn sinh - Được hỗ trợ, học hỏi")
            ket_qua["diem_so"] += 2
        elif hanh_can == hanh_khac:
            ket_qua["canh_bao"].append("⚠️ Quan Sát - Áp lực, dễ mất tiền oan")
            ket_qua["diem_so"] -= 4
        
        # Chi ngày
        if hanh_chi == hanh_nhat and today_chi not in chi_tai:
            ket_qua["canh_bao"].append("⚠️ Chi Tỷ Kiếp - Cạnh tranh lợi ích")
            ket_qua["diem_so"] -= 2
        elif hanh_chi == hanh_sinh:
            ket_qua["co_hoi"].append("🏠 Ấn chi - An cư, tài lộc bền")
            ket_qua["diem_so"] += 2
        elif hanh_chi == hanh_khac:
            ket_qua["canh_bao"].append("⚠️ Chi Quan Sát - Tai họa từ môi trường")
            ket_qua["diem_so"] -= 3
        
        # Tiết khí
        if hanh_tiet_khi == hanh_sinh:
            ket_qua["co_hoi"].append(f"🌿 Tiết khí {tiet_khi} sinh bản mệnh")
            ket_qua["diem_so"] += 1
        elif hanh_tiet_khi == hanh_khac:
            ket_qua["canh_bao"].append(f"🔥 Tiết khí {tiet_khi} khắc bản mệnh")
            ket_qua["diem_so"] -= 2
        elif hanh_tiet_khi == hanh_tai:
            ket_qua["co_hoi"].append(f"💰 Tiết khí {tiet_khi} là Tài tinh")
            ket_qua["diem_so"] += 1
        
        # Xung hợp nhật chi
        if LUC_HOP.get(today_chi) == nhat_chi:
            ket_qua["co_hoi"].append(f"🤝 Hợp với Nhật chi {nhat_chi}")
            ket_qua["diem_so"] += 2
        elif LUC_XUNG.get(today_chi) == nhat_chi:
            ket_qua["canh_bao"].append(f"💥 Xung với Nhật chi {nhat_chi}")
            ket_qua["diem_so"] -= 3
        
        # 7. Tổng kết
        ket_qua["diem_so"] = max(-10, min(10, ket_qua["diem_so"]))
        
        if ket_qua["diem_so"] >= 7:
            ket_qua["tong_ket"] = "🎉 ĐẠI LỘC - Ngày cực tốt cho tài lộc!"
        elif ket_qua["diem_so"] >= 4:
            ket_qua["tong_ket"] = "💰 CÓ LỘC - Nên hành động"
        elif ket_qua["diem_so"] >= 1:
            ket_qua["tong_ket"] = "🍀 TIỂU LỘC - Có cơ hội nhỏ"
        elif ket_qua["diem_so"] >= -2:
            ket_qua["tong_ket"] = "⚖️ NGÀY THƯỜNG"
        elif ket_qua["diem_so"] >= -5:
            ket_qua["tong_ket"] = "⚠️ TIỂU HAO - Cẩn thận chi tiêu"
        else:
            ket_qua["tong_ket"] = "💀 ĐẠI HAO - Hoãn việc quan trọng"
        
        # 8. Lời khuyên gọn
        if ket_qua["diem_so"] >= 4:
            ket_qua["khuyen_nghi"] = ["✅ Chủ động ký kết, thu tiền, bán hàng"]
        elif ket_qua["diem_so"] >= 1:
            ket_qua["khuyen_nghi"] = ["✅ Có thể làm việc nhỏ, không kỳ vọng lớn"]
        elif ket_qua["diem_so"] >= -2:
            ket_qua["khuyen_nghi"] = ["📌 Làm việc thường ngày, không đầu tư mới"]
        else:
            ket_qua["khuyen_nghi"] = ["❌ Nghỉ ngơi, tránh quyết định quan trọng"]
        
        return ket_qua


    # ==================== PHÂN TÍCH PNL + TỨ TRỤ ====================
    def analyze_pnl_tuvi(
        self,
        ngay_sinh,
        df_full: "pd.DataFrame",
        gio_sinh: int = 12,
        nguong: float = 10.0,
    ) -> dict:
        """
        Duyệt toàn bộ df_full, chạy luan_ngay_loc cho mỗi ngày pnl != 0.
 
        Args:
            ngay_sinh  : datetime – ngày sinh dương lịch
            df_full    : DataFrame có cột 'date' (datetime) và 'pnl' (float)
            gio_sinh   : giờ sinh (0-23)
            nguong     : ngưỡng |pnl| để phân nhóm "lớn" (mặc định 10)
 
        Returns:
            {
              "tat_ca"   : list[dict]  – kết quả mọi ngày pnl != 0
              "thang_lon": list[dict]  – ngày pnl >  nguong
              "lo_lon"   : list[dict]  – ngày pnl < -nguong
              "thong_ke" : dict        – tóm tắt thống kê tương quan
            }
        """
 
        df_pnl = df_full[df_full["pnl"] != 0].copy().sort_values("date")
 
        tat_ca: list[dict] = []
 
        for _, row in df_pnl.iterrows():
            ngay_kt = row["date"].to_pydatetime() if hasattr(row["date"], "to_pydatetime") else row["date"]
            pnl_val = float(row["pnl"])
 
            kq = self.luan_ngay_loc(ngay_sinh, ngay_kt, gio_sinh)
            if kq is None:
                continue
 
            kq["pnl"]     = pnl_val
            kq["nhom"]    = (
                "thang_lon" if pnl_val >  nguong else
                "lo_lon"    if pnl_val < -nguong else
                "nho"
            )
            tat_ca.append(kq)
 
        thang_lon = [r for r in tat_ca if r["nhom"] == "thang_lon"]
        lo_lon    = [r for r in tat_ca if r["nhom"] == "lo_lon"]
 
        # ── Thống kê tương quan điểm lộc vs PNL ──────────────────
        def _tb_diem(lst):
            return round(sum(r["diem_so"] for r in lst) / len(lst), 2) if lst else 0
 
        def _count_tong_ket(lst, keyword):
            return sum(1 for r in lst if keyword in r.get("tong_ket", ""))
 
        thong_ke = {
            "tong_ngay_pnl"       : len(tat_ca),
            "tong_thang_lon"      : len(thang_lon),
            "tong_lo_lon"         : len(lo_lon),
            "diem_tb_thang_lon"   : _tb_diem(thang_lon),
            "diem_tb_lo_lon"      : _tb_diem(lo_lon),
            "diem_tb_tat_ca"      : _tb_diem(tat_ca),
            # ngày thắng lớn có điểm lộc >= 1
            "thang_co_loc_pct"    : round(
                sum(1 for r in thang_lon if r["diem_so"] >= 1) / len(thang_lon) * 100, 1
            ) if thang_lon else 0,
            # ngày lỗ lớn có điểm cảnh báo (âm)
            "lo_co_canh_bao_pct"  : round(
                sum(1 for r in lo_lon if r["diem_so"] < 0) / len(lo_lon) * 100, 1
            ) if lo_lon else 0,
        }
 
        return {
            "tat_ca"   : tat_ca,
            "thang_lon": thang_lon,
            "lo_lon"   : lo_lon,
            "thong_ke" : thong_ke,
        }


    def in_ket_qua_luan_ngay(self, ket_qua):
        """In kết quả luan_ngay_loc ra terminal (dùng để test)"""
        if not ket_qua:
            print("Không có dữ liệu")
            return
        
        print("=" * 60)
        print(f"📅 NGÀY XEM: {ket_qua['thong_tin_co_ban']['ngay_xem']}")
        print(f"⭐ Nhật chủ: {ket_qua['thong_tin_co_ban']['nhat_can']} ({ket_qua['thong_tin_co_ban']['hanh_nhat_chu']})")
        print(f"📆 Can Chi ngày: {ket_qua['thong_tin_co_ban']['can_chi_ngay']}")
        print(f"🌾 Tiết khí: {ket_qua['thong_tin_co_ban']['tiet_khi']} ({ket_qua['thong_tin_co_ban']['hanh_tiet_khi']})")
        print("-" * 60)
        
        if ket_qua.get("co_hoi"):
            print("\n✅ CƠ HỘI:")
            for item in ket_qua["co_hoi"]:
                print(f"   {item}")
        
        if ket_qua.get("canh_bao"):
            print("\n⚠️ CẢNH BÁO:")
            for item in ket_qua["canh_bao"]:
                print(f"   {item}")
        
        print(f"\n🎯 ĐIỂM LỘC: {ket_qua['diem_so']}/10")
        print(f"   {ket_qua['tong_ket']}")
        
        if ket_qua.get("khuyen_nghi"):
            print("\n💡 LỜI KHUYÊN:")
            for item in ket_qua["khuyen_nghi"]:
                print(f"   {item}")
        
        print("=" * 60)










analyzer = TuViAnalyzer()

# Lấy tiết khí và hành cho ngày hôm nay
# today =  datetime(2026, 6, 4)  # Chỉ lấy phần ngày tháng năm
# tiet_khi, hanh = analyzer.get_tiet_khi_info(today)
# print(f"Hôm nay {today.strftime('%d/%m/%Y')}: {tiet_khi} - {hanh}")


 # Ví dụ: Người sinh 15/04/1990 (Nhật chủ Ất Mộc - yếu)
    # Xem ngày 20/04/2026
ngay_sinh = datetime(1990, 4, 15)
ngay_xem = datetime(2026, 4, 20)
    
ket_qua = analyzer.luan_ngay_loc(ngay_sinh, ngay_xem)
analyzer.in_ket_qua_luan_ngay(ket_qua)


# ==================== PHẦN XỬ LÝ TIẾT KHÍ CHO CALENDAR ====================
# (Để riêng hoặc có thể chuyển sang file khác nếu cần)
 
# import pandas as pd
# from datetime import timedelta
# from macro import get_element_for_date, MONTH_SCHEDULE
    
# CALENDAR_PATH = r"D:\Git\AstroFinance\blank-app\files\calendar_with_moon.csv"
# TIET_KHI_PATH = r"D:\Git\AstroFinance\blank-app\files\tietkhiTable.csv"
# OUTPUT_PATH = r"D:\Git\AstroFinance\blank-app\files\calendar_with_moon_tiet_khi.csv"

# # ==================== ĐỌC FILE TIẾT KHÍ ====================
# print("📂 Đang đọc file tietkhiTable.csv...")
# df_tietkhi = pd.read_csv(TIET_KHI_PATH)

# # Tạo danh sách các ngày bắt đầu tiết khí theo thứ tự
# term_list = []  # (ngày, tiết_khí, năm)

# for idx, row in df_tietkhi.iterrows():
#     for term in df_tietkhi.columns:
#         date_str = str(row[term]).strip()
#         if date_str and date_str != "nan":
#             # date_str có dạng mm/dd/yyyy
#             date_obj = datetime.strptime(date_str, "%m/%d/%Y")
#             term_list.append((date_obj, term))

# # Sắp xếp theo ngày
# term_list.sort(key=lambda x: x[0])

# print(f"✅ Đã đọc {len(term_list)} mốc tiết khí")

# # ==================== ĐỌC CALENDAR ====================
# print("\n📂 Đang đọc file calendar_with_moon.csv...")
# df_cal = pd.read_csv(CALENDAR_PATH)
# print(f"   Số dòng: {len(df_cal)}")

# # Chuyển cột date sang datetime
# df_cal['date_obj'] = pd.to_datetime(df_cal['date'], format="%m/%d/%Y")

# # ==================== FILL TIẾT KHÍ ====================
# print("\n⏳ Đang fill tiết khí cho tất cả các ngày...")

# # Tạo dictionary mapping date_obj -> tiết khí
# date_to_term = {}

# # Duyệt qua từng khoảng giữa các mốc tiết khí
# for i in range(len(term_list)):
#     current_date, current_term = term_list[i]
    
#     # Xác định ngày kết thúc của tiết khí này
#     if i + 1 < len(term_list):
#         next_date, _ = term_list[i + 1]
#         end_date = next_date - timedelta(days=1)
#     else:
#         # Tiết khí cuối cùng kéo dài đến hết năm
#         end_date = datetime(current_date.year, 12, 31)
    
#     # Fill từ current_date đến end_date
#     fill_date = current_date
#     while fill_date <= end_date:
#         date_to_term[fill_date] = current_term
#         fill_date += timedelta(days=1)

# # Gán vào dataframe
# df_cal['tiet_khi'] = df_cal['date_obj'].map(date_to_term).fillna("")

# # ==================== TÍNH HÀNH TIẾT KHÍ ====================

# def get_element_for_date(date_obj):
#     """Tính hành tiết khí"""
#     month, day = date_obj.month, date_obj.day
    
#     # Xác định tháng chi
#     if (month == 2 and day >= 4) or (month == 3 and day <= 4):
#         chi = "Dần"
#         start_date = datetime(date_obj.year, 2, 4)
#     elif (month == 3 and day >= 5) or (month == 4 and day <= 4):
#         chi = "Mão"
#         start_date = datetime(date_obj.year, 3, 5)
#     elif (month == 4 and day >= 5) or (month == 5 and day <= 4):
#         chi = "Thìn"
#         start_date = datetime(date_obj.year, 4, 4)
#     elif (month == 5 and day >= 5) or (month == 6 and day <= 4):
#         chi = "Tỵ"
#         start_date = datetime(date_obj.year, 5, 5)
#     elif (month == 6 and day >= 5) or (month == 7 and day <= 6):
#         chi = "Ngọ"
#         start_date = datetime(date_obj.year, 6, 5)
#     elif (month == 7 and day >= 7) or (month == 8 and day <= 6):
#         chi = "Mùi"
#         start_date = datetime(date_obj.year, 7, 7)
#     elif (month == 8 and day >= 7) or (month == 9 and day <= 6):
#         chi = "Thân"
#         start_date = datetime(date_obj.year, 8, 7)
#     elif (month == 9 and day >= 7) or (month == 10 and day <= 7):
#         chi = "Dậu"
#         start_date = datetime(date_obj.year, 9, 7)
#     elif (month == 10 and day >= 8) or (month == 11 and day <= 6):
#         chi = "Tuất"
#         start_date = datetime(date_obj.year, 10, 8)
#     elif (month == 11 and day >= 7) or (month == 12 and day <= 6):
#         chi = "Hợi"
#         start_date = datetime(date_obj.year, 11, 7)
#     elif (month == 12 and day >= 7) or (month == 1 and day <= 4):
#         chi = "Tý"
#         start_date = datetime(date_obj.year, 12, 7)
#     else:
#         chi = "Sửu"
#         start_date = datetime(date_obj.year, 1, 5)
    
#     days_since = (date_obj - start_date).days + 1
#     schedule = MONTH_SCHEDULE[chi]["schedule"]
    
#     total = 0
#     for can, days, hanh in schedule:
#         total += days
#         if days_since <= total:
#             return hanh
#     return schedule[-1][2]

# print("\n⏳ Đang tính hành tiết khí...")
# df_cal['hanh_tiet_khi'] = df_cal['date_obj'].apply(get_element_for_date)

# # ==================== LƯU FILE ====================
# df_cal = df_cal.drop(columns=['date_obj'])
# df_cal.to_csv(OUTPUT_PATH, index=False)
# print(f"\n✅ Đã lưu file {OUTPUT_PATH}")

# # ==================== KIỂM TRA KẾT QUẢ ====================
# print("\n📋 KIỂM TRA TIẾT KHÍ THÁNG TỴ (Lập Hạ - Tiểu Mãn) NĂM 2024:")
# # Lọc từ 5/5/2024 đến 5/6/2024
# check_df = df_cal[
#     (df_cal['date'] >= "5/5/2024") & 
#     (df_cal['date'] <= "6/4/2024")
# ]
# for _, row in check_df.iterrows():
#     print(f"   {row['date']}: {row['tiet_khi']} - {row['hanh_tiet_khi']}")

# print("\n📊 KIỂM TRA SỐ LƯỢNG NGÀY TRONG THÁNG TỴ 2024:")
# print(f"   Tổng số ngày: {len(check_df)}")
# print(f"   Mộc: {len(check_df[check_df['hanh_tiet_khi'] == 'Mộc'])}")
# print(f"   Hỏa: {len(check_df[check_df['hanh_tiet_khi'] == 'Hỏa'])}")
# print(f"   Thổ: {len(check_df[check_df['hanh_tiet_khi'] == 'Thổ'])}")
# print(f"   Kim: {len(check_df[check_df['hanh_tiet_khi'] == 'Kim'])}")
# print(f"   Thủy: {len(check_df[check_df['hanh_tiet_khi'] == 'Thủy'])}")