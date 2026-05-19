# import dash
# from dash import dcc, html, Input, Output, State, ctx
# import plotly.graph_objects as go
# import pandas as pd
# from datetime import timedelta
# import os
# from glob import glob
# from functools import lru_cache

# app = dash.Dash(__name__)

# # ==================== CẤU HÌNH ====================
# WINDOW_SIZE  = 100    # Số ngày hiển thị mỗi lần

# # ==================== ĐỌC DỮ LIỆU ====================
# print("📂 Đang đọc dữ liệu...")

# CSV_PATH = "files/calendar_with_moon.csv"
# df_full = pd.read_csv(CSV_PATH)
# df_full["date"] = pd.to_datetime(df_full["date"], errors="coerce")
# df_full["moon_numeric"] = pd.to_numeric(df_full["moon"], errors="coerce")

# script_dir = os.path.dirname(os.path.abspath(__file__))

# # ==================== ĐỌC FILE EXCEL TỪ THƯ MỤC files (cũ) ====================
# files = glob(os.path.join(script_dir, "files/*.xlsx"))

# all_pnl = []
# if files:
#     for file in files:
#         try:
#             df_excel = pd.read_excel(file)
#             if 'closeTime(UTC+8)' in df_excel.columns and 'Realized PNL' in df_excel.columns:
#                 df_s = df_excel[['closeTime(UTC+8)', 'Realized PNL']].copy()
#                 df_s['closeTime(UTC+8)'] = pd.to_datetime(
#                     df_s['closeTime(UTC+8)'], format='%Y-%m-%d %H:%M:%S', errors='coerce')
#                 df_s['Realized PNL'] = pd.to_numeric(df_s['Realized PNL'], errors='coerce')
#                 df_s = df_s.dropna()
#                 df_s['date'] = df_s['closeTime(UTC+8)'].dt.floor('D')
#                 all_pnl.append(df_s[['date', 'Realized PNL']])
#                 print(f"✅ Đã đọc {os.path.basename(file)}: {len(df_s)} giao dịch")
#         except Exception as e:
#             print(f"Lỗi đọc {file}: {e}")



# # ==================== ĐỌC FILE EXCEL BINANCE (SỬA ĐỊNH DẠNG NGÀY) ====================
# files_binance = glob(os.path.join(script_dir, "filesbinance/*.xlsx"))

# if files_binance:
#     print(f"\n📂 Tìm thấy {len(files_binance)} file Binance:")
#     for file in files_binance:
#         try:
#             print(f"\n   📄 Đang xử lý: {os.path.basename(file)}")
            
#             # Đọc file với header ở dòng 10
#             df_binance = pd.read_excel(file, header=9)
            
#             # Tìm cột Thời gian và Lợi nhuận
#             time_col = None
#             pnl_col = None
            
#             for col in df_binance.columns:
#                 col_str = str(col).strip()
#                 if 'Thời gian' in col_str:
#                     time_col = col
#                 if 'Lợi nhuận đã thực hiện' in col_str:
#                     pnl_col = col
            
#             if time_col is None or pnl_col is None:
#                 print(f"   ⚠️ Không tìm thấy cột cần thiết!")
#                 continue
            
#             print(f"   📅 Cột thời gian: '{time_col}'")
#             print(f"   💰 Cột PNL: '{pnl_col}'")
            
#             # Lấy dữ liệu
#             df_s = df_binance[[time_col, pnl_col]].copy()
            
#             # Xóa dòng trống
#             df_s = df_s.dropna(subset=[time_col, pnl_col])
            
#             # ✅ SỬA: Chuyển đổi thời gian từ định dạng "25-05-26 21:35:51"
#             # Ý nghĩa: 25-05-26 = năm 2025, tháng 05, ngày 26
#             df_s[time_col] = pd.to_datetime(
#                 df_s[time_col], 
#                 format='%y-%m-%d %H:%M:%S',  # 25-05-26 -> 2025-05-26
#                 errors='coerce'
#             )
            
#             # Chuyển PNL sang số
#             df_s[pnl_col] = pd.to_numeric(df_s[pnl_col], errors='coerce')
            
#             # Xóa dòng lỗi
#             before = len(df_s)
#             df_s = df_s.dropna()
#             print(f"   📊 Số dòng hợp lệ: {len(df_s)} / {before}")
            
#             if len(df_s) == 0:
#                 print(f"   ⚠️ Không có dòng dữ liệu hợp lệ!")
#                 continue
            
#             # Đổi tên cột
#             df_s = df_s.rename(columns={time_col: 'closeTime(UTC+8)', pnl_col: 'Realized PNL'})
            
#             # Tạo cột date (chỉ lấy phần ngày)
#             df_s['date'] = df_s['closeTime(UTC+8)'].dt.date
            
#             # Hiển thị mẫu dữ liệu
#             print(f"   📋 Mẫu dữ liệu (3 dòng đầu):")
#             for i in range(min(3, len(df_s))):
#                 print(f"      {df_s['date'].iloc[i]} - PNL: {df_s['Realized PNL'].iloc[i]:.4f}")
            
#             all_pnl.append(df_s[['date', 'Realized PNL']])
#             print(f"   ✅ Đã đọc {len(df_s)} giao dịch từ Binance")
#             print(f"   💰 Tổng PNL file này: {df_s['Realized PNL'].sum():,.2f} USD")
            
#         except Exception as e:
#             print(f"   ❌ Lỗi đọc {file}: {e}")
#             import traceback
#             traceback.print_exc()


# # ==================== GỘP TẤT CẢ PNL ====================
# if all_pnl:
#     # Gộp tất cả
#     df_all_pnl = pd.concat(all_pnl, ignore_index=True)
    
#     # Đảm bảo cột date là datetime
#     df_all_pnl['date'] = pd.to_datetime(df_all_pnl['date'])
    
#     # Tổng hợp theo ngày
#     daily_pnl = df_all_pnl.groupby('date')['Realized PNL'].sum().reset_index()
#     daily_pnl = daily_pnl.sort_values('date')
    
#     # Tạo dictionary để map vào df_full
#     pnl_dict = dict(zip(daily_pnl['date'], daily_pnl['Realized PNL']))
    
#     # Gộp vào df_full (đảm bảo cùng kiểu dữ liệu)
#     df_full['date_for_merge'] = pd.to_datetime(df_full['date']).dt.date
#     daily_pnl['date_for_merge'] = daily_pnl['date'].dt.date
    
#     pnl_dict_by_date = dict(zip(daily_pnl['date_for_merge'], daily_pnl['Realized PNL']))
#     df_full['pnl'] = df_full['date_for_merge'].map(pnl_dict_by_date).fillna(0)
    
#     # Xóa cột tạm
#     df_full = df_full.drop(columns=['date_for_merge'])
    
#     print(f"\n✅ TỔNG HỢP:")
#     print(f"   📊 Tổng số giao dịch: {len(df_all_pnl)}")
#     print(f"   📅 Số ngày có giao dịch: {len(daily_pnl)}")
#     print(f"   💰 Tổng PNL: {daily_pnl['Realized PNL'].sum():,.2f} USD")
#     print(f"   📈 PNL Max: {daily_pnl['Realized PNL'].max():.2f}")
#     print(f"   📉 PNL Min: {daily_pnl['Realized PNL'].min():.2f}")
    
#     # Hiển thị 10 ngày đầu có PNL
#     print(f"\n📋 10 ngày đầu có PNL:")
#     print(daily_pnl.head(10).to_string())
    
# else:
#     df_full['pnl'] = 0
#     print("\n⚠️ Không có dữ liệu PNL nào được đọc!")
    

# # ==================== TỨ KHÍ ====================
# @lru_cache(maxsize=50)
# def get_solar_terms(year):
#     return {
#         'Xuân phân': {'date': pd.Timestamp(f'{year}-03-20'), 'icon': '🌸', 'color': '#FF69B4'},
#         'Hạ chí':    {'date': pd.Timestamp(f'{year}-06-21'), 'icon': '☀️', 'color': '#FF6B35'},
#         'Thu phân':  {'date': pd.Timestamp(f'{year}-09-22'), 'icon': '🍂', 'color': '#FFA500'},
#         'Đông chí':  {'date': pd.Timestamp(f'{year}-12-21'), 'icon': '❄️', 'color': '#4FC3F7'},
#     }

# all_solar_dates = set()
# for y in df_full["date"].dt.year.dropna().unique():
#     for info in get_solar_terms(int(y)).values():
#         all_solar_dates.add(info['date'])

# # ==================== LỌC NGÀY ĐẶC BIỆT ====================
# df_full["specdate_clean"] = df_full["specdate"].astype(str).str.strip().str.lower()
# df_full["is_moon_phase"]  = df_full["moon_numeric"].isin([0, 90, 180, 270])
# df_full["is_specdate"]    = df_full["specdate_clean"].isin(["ram", "rằm", "m1", "mùng 1"])
# df_full["is_solar_term"]  = df_full["date"].isin(all_solar_dates)
# df_full["has_pnl"]        = df_full["pnl"] != 0

# df_filtered = df_full[
#     df_full["is_moon_phase"] | df_full["is_specdate"] |
#     df_full["is_solar_term"] | df_full["has_pnl"]
# ].copy().sort_values("date").reset_index(drop=True)

# total_rows = len(df_filtered)
# print(f"📅 Sau lọc: {total_rows} ngày (từ {len(df_full)})")


# SEASON_COLORS = {
#     'spring': 'rgba(255, 105, 180, 0.10)',
#     'summer': 'rgba(255, 100,  30, 0.10)',
#     'autumn': 'rgba(255, 165,   0, 0.10)',
#     'winter': 'rgba( 30, 170, 255, 0.10)',
# }



# # ==================== NGŨ HÀNH MÀU SẮC ====================
# # Can: Giáp Ất=Mộc, Bính Đinh=Hỏa, Mậu Kỷ=Thổ, Canh Tân=Kim, Nhâm Quý=Thủy
# CAN_HANH = {
#     "Giáp": "Mộc", "Ất":  "Mộc",
#     "Bính": "Hỏa", "Đinh":"Hỏa",
#     "Mậu":  "Thổ", "Kỷ":  "Thổ",
#     "Canh": "Kim",  "Tân": "Kim",
#     "Nhâm": "Thủy","Quý": "Thủy",
# }
# # Chi: Tý Hợi=Thủy, Dần Mão=Mộc, Tỵ Ngọ=Hỏa, Thân Dậu=Kim, Thìn Tuất Sửu Mùi=Thổ
# CHI_HANH = {
#     "Tý":   "Thủy","Hợi":  "Thủy",
#     "Dần":  "Mộc", "Mão":  "Mộc",
#     "Tỵ":   "Hỏa", "Ngọ":  "Hỏa",
#     "Thân": "Kim",  "Dậu":  "Kim",
#     "Thìn": "Thổ", "Tuất": "Thổ","Sửu":"Thổ","Mùi":"Thổ",
# }
# # Màu ngũ hành (sáng, đọc được trên nền tối)
# HANH_COLOR = {
#     "Mộc":  "#4caf50",   # xanh lá
#     "Hỏa":  "#ff5252",   # đỏ
#     "Thổ":  "#ffb300",   # vàng đất
#     "Kim":  "#b0bec5",   # trắng bạc
#     "Thủy": "#29b6f6",   # xanh nước
# }

# def canchi_color(can: str, chi: str) -> tuple:
#     """Trả về (can_color, chi_color) theo ngũ hành."""
#     cc = HANH_COLOR.get(CAN_HANH.get(str(can).strip(), ""), "#aaaaaa")
#     hc = HANH_COLOR.get(CHI_HANH.get(str(chi).strip(), ""), "#aaaaaa")
#     return cc, hc

# # ==================== HÀM VẼ CHART ====================
# def build_figure(offset: int):
#     start_idx = max(0, offset)
#     end_idx   = min(total_rows, start_idx + WINDOW_SIZE)
#     df_view   = df_filtered.iloc[start_idx:end_idx].copy()

#     if df_view.empty:
#         return go.Figure(), ""

#     start_date = df_view['date'].iloc[0]
#     end_date   = df_view['date'].iloc[-1]
#     df_pnl     = df_view[df_view['pnl'] != 0].copy()

#     if not df_pnl.empty:
#         peak = max(abs(df_pnl['pnl'].max()), abs(df_pnl['pnl'].min()), 50) * 1.35
#         pnl_max, pnl_min = peak, -peak * 0.55
#     else:
#         pnl_min, pnl_max = -50, 50

#     fig = go.Figure()

#     # ── Nền 4 mùa ──────────────────────────────────────────────────────────────
#     years = range(start_date.year, end_date.year + 1)
#     bounds = []
#     for year in years:
#         terms = get_solar_terms(year)
#         bounds += [
#             {'date': terms['Xuân phân']['date'], 'color': SEASON_COLORS['spring']},
#             {'date': terms['Hạ chí']['date'],    'color': SEASON_COLORS['summer']},
#             {'date': terms['Thu phân']['date'],   'color': SEASON_COLORS['autumn']},
#             {'date': terms['Đông chí']['date'],   'color': SEASON_COLORS['winter']},
#         ]
#     bounds.sort(key=lambda x: x['date'])
#     for i, b in enumerate(bounds):
#         s = b['date']
#         e = bounds[i+1]['date'] if i+1 < len(bounds) else pd.Timestamp(f'{s.year+1}-03-20')
#         if e >= start_date and s <= end_date:
#             fig.add_vrect(
#                 x0=max(s, start_date).timestamp() * 1000,
#                 x1=min(e, end_date).timestamp() * 1000,
#                 fillcolor=b['color'], opacity=0.45,
#                 layer="below", line_width=0,
#             )

#     # ── PNL Bars ────────────────────────────────────────────────────────────────
#     if not df_pnl.empty:
#         bar_colors = ['#00e676' if x >= 0 else '#ff1744' for x in df_pnl['pnl']]

#         # Build customdata: [can, chi, hanh_can, hanh_chi] cho mỗi bar
#         def _hanh(can, chi):
#             hc = CAN_HANH.get(str(can).strip(), "?")
#             hh = CHI_HANH.get(str(chi).strip(), "?")
#             return hc, hh

#         customdata = []
#         for _, r in df_pnl.iterrows():
#             can_s = str(r.get('can', '')).strip()
#             chi_s = str(r.get('chi', '')).strip()
#             hc, hh = _hanh(can_s, chi_s)
#             customdata.append([can_s, chi_s, hc, hh])

#         fig.add_trace(go.Bar(
#             x=df_pnl['date'],
#             y=df_pnl['pnl'],
#             name="PNL",
#             marker_color=bar_colors,
#             marker_line_width=0,
#             opacity=0.88,
#             yaxis="y",
#             text=df_pnl['pnl'].apply(lambda x: f'{x:+,.0f}'),
#             textposition='outside',
#             textfont=dict(size=9, color='rgba(220,220,220,0.9)'),
#             customdata=customdata,
#             hovertemplate=(
#                 "<b>%{x|%d/%m/%Y}</b><br>"
#                 "PNL: %{y:+,.2f} USD<br>"
#                 "Can Chi: %{customdata[0]} %{customdata[1]}<br>"
#                 "Ngũ hành: %{customdata[2]} · %{customdata[3]}"
#                 "<extra></extra>"
#             ),
#             cliponaxis=False,
#         ))

#     # ── Moon Phase + Specdate – annotation trên đỉnh bar ──────────────────────
#     # lookup pnl theo ngày để biết đỉnh bar
#     pnl_by_date = {row['date'].normalize(): row['pnl'] for _, row in df_view.iterrows()}

#     phase_labels = {0: "🌑", 90: "🌓", 180: "🌕", 270: "🌗"}
#     phase_rows = df_view[df_view["moon_numeric"].isin([0, 90, 180, 270])]

#     df_view["_spec"] = df_view["specdate"].astype(str).str.strip().str.lower()
#     spec_map = {"ram": "Rằm", "rằm": "Rằm", "m1": "Mùng 1", "mùng 1": "Mùng 1"}
#     spec_rows = df_view[df_view["_spec"].isin(["ram", "rằm", "m1", "mùng 1"])]

#     annotations = []

#     for _, row in phase_rows.iterrows():
#         d = row['date'].normalize()
#         pnl_val = pnl_by_date.get(d, 0)
#         icon = phase_labels.get(row['moon_numeric'], "🌙")
#         # icon nằm sát đỉnh bar: ay âm = lên trên (bar dương), ay dương = xuống dưới (bar âm)
#         ay = -22 if pnl_val >= 0 else 22
#         annotations.append(dict(
#             x=d, y=pnl_val,
#             xref="x", yref="y",
#             text=icon,
#             showarrow=True,
#             arrowhead=0, arrowwidth=1, arrowcolor="rgba(255,215,0,0.4)",
#             ax=0, ay=ay,
#             font=dict(size=18, color="#FFD700"),
#             bgcolor="rgba(0,0,0,0)", borderwidth=0,
#         ))

#     for _, row in spec_rows.iterrows():
#         d = row['date'].normalize()
#         pnl_val = pnl_by_date.get(d, 0)
#         sv = row['_spec']
#         label = spec_map.get(sv, sv)
#         is_ram = sv in ("ram", "rằm")
#         color  = "#FFD700" if is_ram else "#9b9bff"
#         # tầng 2: cách thêm 22px so với moon phase icon
#         ay = -44 if pnl_val >= 0 else 44
#         annotations.append(dict(
#             x=d, y=pnl_val,
#             xref="x", yref="y",
#             text=label,
#             showarrow=True,
#             arrowhead=0, arrowwidth=1,
#             arrowcolor=f"{'rgba(255,215,0,0.35)' if is_ram else 'rgba(155,155,255,0.35)'}",
#             ax=0, ay=ay,
#             font=dict(size=10, color=color),
#             bgcolor="rgba(5,5,18,0.75)",
#             bordercolor=color, borderwidth=1, borderpad=3,
#         ))

#     # ── Can Chi – ngày có |PNL| > 10, tầng 3 trên đỉnh bar ───────────────────
#     df_big = df_pnl[df_pnl['pnl'].abs() > 10].copy()
#     for _, row in df_big.iterrows():
#         d       = row['date'].normalize()
#         pnl_val = row['pnl']
#         can_str = str(row.get('can', '')).strip()
#         chi_str = str(row.get('chi', '')).strip()
#         if not can_str or can_str == 'nan':
#             continue
#         cc, hc = canchi_color(can_str, chi_str)
#         label  = f"<b>{can_str}</b> <b>{chi_str}</b>"
#         # tầng 3: ay = -66 (trên spec/moon), +66 nếu bar âm
#         ay = -66 if pnl_val >= 0 else 66
#         annotations.append(dict(
#             x=d, y=pnl_val,
#             xref="x", yref="y",
#             text=f'<span style="color:{cc}">{can_str}</span> <span style="color:{hc}">{chi_str}</span>',
#             showarrow=True,
#             arrowhead=0, arrowwidth=1,
#             arrowcolor="rgba(180,180,180,0.25)",
#             ax=0, ay=ay,
#             font=dict(size=11),
#             bgcolor="rgba(5,5,18,0.80)",
#             bordercolor="rgba(120,120,120,0.5)",
#             borderwidth=1, borderpad=4,
#         ))

#     # ── Tứ Khí – TO HƠN (size 12), CAO HƠN (top left), NỀN SẪM ───────────────
#     for year in years:
#         for term_name, info in get_solar_terms(year).items():
#             td = info['date']
#             if start_date <= td <= end_date:
#                 fig.add_vline(
#                     x=td.timestamp() * 1000,
#                     line_width=2,
#                     line_dash="dash",
#                     line_color=info['color'],
#                     opacity=0.85,
#                     annotation_text=f"  {info['icon']} {term_name}",
#                     annotation_position="top left",
#                     annotation_font=dict(size=12, color=info['color']),
#                     annotation_bgcolor="rgba(5, 5, 18, 0.82)",
#                     annotation_bordercolor=info['color'],
#                     annotation_borderwidth=1,
#                     annotation_borderpad=5,
#                 )

#     # ── Zero line ───────────────────────────────────────────────────────────────
#     fig.add_hline(y=0, line_dash="solid", line_color="rgba(255,255,255,0.2)", line_width=1)

#     # ── Nhãn tháng/năm ─────────────────────────────────────────────────────────
#     m0, m1 = start_date.strftime('%m/%Y'), end_date.strftime('%m/%Y')
#     month_range_str = m0 if m0 == m1 else f"{m0} – {m1}"

#     pnl_days  = len(df_pnl)
#     total_pnl = df_pnl['pnl'].sum() if not df_pnl.empty else 0
#     sign_icon = "▲" if total_pnl >= 0 else "▼"

#     title_str = (
#         f"<b>📅 {month_range_str}</b>"
#         f"  ·  Ngày {start_idx+1}–{end_idx} / {total_rows}"
#         f"  ·  {pnl_days} GD"
#         f"  ·  {sign_icon} {total_pnl:+,.0f} USD"
#     )

#     # ── Layout ──────────────────────────────────────────────────────────────────
#     fig.update_layout(
#         template='plotly_dark',
#         paper_bgcolor='#0d0d1a',
#         plot_bgcolor='#0f1120',
#         dragmode='pan',
#         title=dict(
#             text=title_str,
#             font=dict(size=12, color='#cccccc'),
#             x=0.01, xanchor='left', y=0.98,
#         ),
#         xaxis=dict(
#             type='date',
#             range=[start_date - timedelta(hours=12), end_date + timedelta(hours=12)],
#             tickformat="%d/%m",
#             dtick="D3",
#             tickangle=-45,
#             tickfont=dict(size=9),
#             gridcolor='rgba(255,255,255,0.05)',
#             # fixedrange=True → drag/scroll không trigger rebuild figure
#             # (bỏ nếu muốn zoom bằng scroll, nhưng sẽ lag hơn)
#             fixedrange=True,
#         ),
#         yaxis=dict(
#             title=dict(text="PNL (USD)", font=dict(size=10)),
#             side="left",
#             range=[pnl_min, pnl_max],
#             tickformat="+,.0f",
#             tickfont=dict(size=9),
#             gridcolor='rgba(255,255,255,0.05)',
#             zerolinecolor='rgba(255,255,255,0.25)',
#             fixedrange=False,
#         ),

#         legend=dict(
#             orientation="h", yanchor="bottom", y=1.01,
#             xanchor="right", x=1,
#             font=dict(size=9), bgcolor='rgba(0,0,0,0)',
#         ),
#         margin=dict(l=60, r=20, t=50, b=55),
#         hovermode='x unified',
#         bargap=0.22,
#         annotations=annotations,
#         uirevision=str(offset),
#     )

#     fig.update_xaxes(
#         showspikes=True, spikecolor="rgba(160,160,160,0.4)",
#         spikemode="toaxis+across", spikesnap="cursor",  
#     )
#     fig.update_yaxes(
#         showspikes=True, spikecolor="rgba(160,160,160,0.4)",
#         spikemode="toaxis+across", spikesnap="cursor",  
#     )

#     info = (
#         f"📅 {month_range_str}  "
#         f"| {start_idx+1}–{end_idx}/{total_rows}  "
#         f"| {pnl_days} GD  "
#         f"| {sign_icon} {total_pnl:+,.0f} USD"
#     )
#     return fig, info


# # ==================== LAYOUT ====================
# _btn_nav = {
#     "fontSize": "12px", "padding": "3px 10px",
#     "backgroundColor": "#1e1e30", "color": "#aaaacc",
#     "border": "1px solid #333", "borderRadius": "5px",
#     "cursor": "pointer", "margin": "3px",
# }
# _btn_reload = {
#     "fontSize": "12px", "padding": "3px 12px",
#     "backgroundColor": "#5a009a", "color": "white",
#     "border": "none", "borderRadius": "5px",
#     "cursor": "pointer", "margin": "3px",
# }

# app.layout = html.Div([
#     html.Div([
#         html.Button("🔄 Reload", id="btn-reload", n_clicks=0, style=_btn_reload),
#         html.Button("⏮ Đầu",   id="btn-first",  n_clicks=0, style=_btn_nav),
#         html.Button("◀ Trước",  id="btn-prev",   n_clicks=0, style=_btn_nav),
#         html.Button("Sau ▶",    id="btn-next",   n_clicks=0, style=_btn_nav),
#         html.Button("Cuối ⏭",  id="btn-last",   n_clicks=0, style=_btn_nav),
#         html.Span(id="info-text",
#                   style={"color": "#7fff7f", "marginLeft": "14px", "fontSize": "11px"}),
#     ], style={
#         "display": "flex", "alignItems": "center", "flexWrap": "wrap",
#         "backgroundColor": "#0d0d1a", "padding": "5px 8px",
#         "borderBottom": "1px solid #1a1a2e",
#     }),

#     dcc.Graph(
#         id='moon-chart',
#         style={'height': 'calc(100vh - 46px)'},
#         config={
#             # scrollZoom=False và fixedrange=True ở xaxis
#             # → drag không fire relayoutData liên tục → KHÔNG LAG
#             'scrollZoom': False,
#             'displaylogo': False,
#             'modeBarButtonsToRemove': [
#                 'zoom2d', 'zoomIn2d', 'zoomOut2d', 'autoScale2d', 'select2d', 'lasso2d'
#             ],
#         },
#     ),

#     dcc.Store(id='window-offset', data=max(0, total_rows - WINDOW_SIZE)),
# ], style={"backgroundColor": "#0d0d1a"})


# # ==================== CALLBACK (chỉ nút, không có relayoutData) ====================
# @app.callback(
#     [Output('moon-chart',    'figure'),
#      Output('info-text',     'children'),
#      Output('window-offset', 'data')],
#     [Input('btn-first',  'n_clicks'),
#      Input('btn-prev',   'n_clicks'),
#      Input('btn-next',   'n_clicks'),
#      Input('btn-last',   'n_clicks'),
#      Input('btn-reload', 'n_clicks')],
#     State('window-offset', 'data'),
#     prevent_initial_call=False,
# )
# def navigate(n_first, n_prev, n_next, n_last, n_reload, current_offset):
#     triggered = ctx.triggered_id
#     offset = current_offset if current_offset is not None else max(0, total_rows - WINDOW_SIZE)

#     if   triggered == 'btn-first': offset = 0
#     elif triggered == 'btn-last':  offset = max(0, total_rows - WINDOW_SIZE)
#     elif triggered == 'btn-prev':  offset = max(0, offset - WINDOW_SIZE)
#     elif triggered == 'btn-next':  offset = min(max(0, total_rows - WINDOW_SIZE), offset + WINDOW_SIZE)

#     fig, info = build_figure(offset)
#     return fig, info, offset


# if __name__ == "__main__":
#     print("=" * 58)
#     print("🚀 PNL + LỊCH – KHÔNG LAG, NHÃN TO, NỀN SẪM")
#     print("=" * 58)
#     print(f"✅ {total_rows} ngày sau lọc  |  Window {WINDOW_SIZE} ngày")
#     print("✅ FIX LAG: xaxis fixedrange=True + bỏ relayoutData callback")
#     print("✅ Nhãn tháng/năm trên title (ví dụ: 03/2025 – 04/2025)")
#     print("✅ Tứ khí: font 12, position top-left, nền rgba(5,5,18,0.82)")
#     print("✅ Moon Phase & Specdate neo top cố định qua y2")
#     app.run(debug=True, port=8050)




 