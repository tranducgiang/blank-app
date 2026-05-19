import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go
import plotly.express as px
from datetime import timedelta
import os
from glob import glob
from functools import lru_cache

class MoonCalendarApp:
    CSV_PATH = "files/calendar_with_moon.csv"
    BTC_PATH = "files/btc_2021.csv"
    PASSWORD = "astro123"
    PHASE_MAP = {
        0.0: "new moon",
        90.0: "first-moon",
        180.0: "full-moon",
        270.0: "half-moon",
    }
    HIGHLIGHT_VALUES = {"ram", "m1"}
    WINDOW_SIZE = 100  # Số ngày hiển thị mỗi lần
    
    # Màu sắc theo mùa
    SEASON_COLORS = {
        'spring': 'rgba(255, 105, 180, 0.10)',
        'summer': 'rgba(255, 100, 30, 0.10)',
        'autumn': 'rgba(255, 165, 0, 0.10)',
        'winter': 'rgba(30, 170, 255, 0.10)',
    }
    
    # Ngũ hành
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

    def __init__(self):
        st.set_page_config(layout="wide", page_title="PNL & Moon Calendar")
        st.title("🌙 PNL Trading Dashboard với Lịch Âm Dương")
        self.load_all_data()
        self.run()

    def load_calendar_data(self):
        """Đọc dữ liệu lịch"""
        df = pd.read_csv(self.CSV_PATH)
        df["date"] = pd.to_datetime(df["date"], errors="coerce")
        df["moon_numeric"] = pd.to_numeric(df["moon"], errors="coerce")
        df["moon_phase"] = df["moon_numeric"].map(self.PHASE_MAP)
        df["highlight"] = (
            df["specdate"].astype(str).str.strip().str.lower().isin(self.HIGHLIGHT_VALUES)
        )
        return df

    def load_pnl_data(self):
        """Đọc dữ liệu PNL từ các file Excel"""
        script_dir = os.path.dirname(os.path.abspath(__file__))
        all_pnl = []
        
        # Đọc file Excel từ thư mục files
        files = glob(os.path.join(script_dir, "files/*.xlsx"))
        if files:
            with st.spinner("Đang đọc dữ liệu PNL..."):
                for file in files:
                    try:
                        df_excel = pd.read_excel(file)
                        if 'closeTime(UTC+8)' in df_excel.columns and 'Realized PNL' in df_excel.columns:
                            df_s = df_excel[['closeTime(UTC+8)', 'Realized PNL']].copy()
                            df_s['closeTime(UTC+8)'] = pd.to_datetime(
                                df_s['closeTime(UTC+8)'], format='%Y-%m-%d %H:%M:%S', errors='coerce')
                            df_s['Realized PNL'] = pd.to_numeric(df_s['Realized PNL'], errors='coerce')
                            df_s = df_s.dropna()
                            df_s['date'] = df_s['closeTime(UTC+8)'].dt.floor('D')
                            all_pnl.append(df_s[['date', 'Realized PNL']])
                    except Exception as e:
                        st.warning(f"Lỗi đọc {os.path.basename(file)}: {e}")
        
        # Đọc file Excel Binance
        files_binance = glob(os.path.join(script_dir, "filesbinance/*.xlsx"))
        if files_binance:
            for file in files_binance:
                try:
                    df_binance = pd.read_excel(file, header=9)
                    
                    time_col = None
                    pnl_col = None
                    
                    for col in df_binance.columns:
                        col_str = str(col).strip()
                        if 'Thời gian' in col_str:
                            time_col = col
                        if 'Lợi nhuận đã thực hiện' in col_str:
                            pnl_col = col
                    
                    if time_col is None or pnl_col is None:
                        continue
                    
                    df_s = df_binance[[time_col, pnl_col]].copy()
                    df_s = df_s.dropna(subset=[time_col, pnl_col])
                    df_s[time_col] = pd.to_datetime(df_s[time_col], format='%y-%m-%d %H:%M:%S', errors='coerce')
                    df_s[pnl_col] = pd.to_numeric(df_s[pnl_col], errors='coerce')
                    df_s = df_s.dropna()
                    
                    df_s = df_s.rename(columns={time_col: 'closeTime(UTC+8)', pnl_col: 'Realized PNL'})
                    df_s['date'] = df_s['closeTime(UTC+8)'].dt.date
                    all_pnl.append(df_s[['date', 'Realized PNL']])
                    
                except Exception as e:
                    st.warning(f"Lỗi đọc Binance file: {e}")
        
        return all_pnl

    def load_all_data(self):
        """Tải và gộp tất cả dữ liệu"""
        self.calendar_df = self.load_calendar_data()
        
        all_pnl = self.load_pnl_data()
        
        if all_pnl:
            df_all_pnl = pd.concat(all_pnl, ignore_index=True)
            df_all_pnl['date'] = pd.to_datetime(df_all_pnl['date'])
            daily_pnl = df_all_pnl.groupby('date')['Realized PNL'].sum().reset_index()
            daily_pnl = daily_pnl.sort_values('date')
            
            # Gộp vào calendar_df
            self.calendar_df['date_for_merge'] = pd.to_datetime(self.calendar_df['date']).dt.date
            daily_pnl['date_for_merge'] = daily_pnl['date'].dt.date
            pnl_dict = dict(zip(daily_pnl['date_for_merge'], daily_pnl['Realized PNL']))
            self.calendar_df['pnl'] = self.calendar_df['date_for_merge'].map(pnl_dict).fillna(0)
            self.calendar_df = self.calendar_df.drop(columns=['date_for_merge'])
            
            # Thông tin thống kê
            st.sidebar.success(f"✅ Tổng PNL: {daily_pnl['Realized PNL'].sum():,.2f} USD")
            st.sidebar.info(f"📊 Số ngày giao dịch: {len(daily_pnl)}")
        else:
            self.calendar_df['pnl'] = 0
            st.sidebar.warning("⚠️ Không có dữ liệu PNL")
        
        # Lọc các ngày đặc biệt
        self.calendar_df["specdate_clean"] = self.calendar_df["specdate"].astype(str).str.strip().str.lower()
        self.calendar_df["is_moon_phase"] = self.calendar_df["moon_numeric"].isin([0, 90, 180, 270])
        self.calendar_df["is_specdate"] = self.calendar_df["specdate_clean"].isin(["ram", "rằm", "m1", "mùng 1"])
        self.calendar_df["is_solar_term"] = self.calendar_df["date"].isin(self.get_all_solar_dates())
        self.calendar_df["has_pnl"] = self.calendar_df["pnl"] != 0
        
        self.df_filtered = self.calendar_df[
            self.calendar_df["is_moon_phase"] | self.calendar_df["is_specdate"] |
            self.calendar_df["is_solar_term"] | self.calendar_df["has_pnl"]
        ].copy().sort_values("date").reset_index(drop=True)
        
        self.total_rows = len(self.df_filtered)

    @lru_cache(maxsize=50)
    def get_solar_terms(self, year):
        """Lấy thông tin tứ khí"""
        return {
            'Xuân phân': {'date': pd.Timestamp(f'{year}-03-20'), 'icon': '🌸', 'color': '#FF69B4'},
            'Hạ chí': {'date': pd.Timestamp(f'{year}-06-21'), 'icon': '☀️', 'color': '#FF6B35'},
            'Thu phân': {'date': pd.Timestamp(f'{year}-09-22'), 'icon': '🍂', 'color': '#FFA500'},
            'Đông chí': {'date': pd.Timestamp(f'{year}-12-21'), 'icon': '❄️', 'color': '#4FC3F7'},
        }

    def get_all_solar_dates(self):
        """Lấy tất cả ngày tứ khí"""
        all_solar_dates = set()
        for y in self.calendar_df["date"].dt.year.dropna().unique():
            for info in self.get_solar_terms(int(y)).values():
                all_solar_dates.add(info['date'])
        return all_solar_dates

    def canchi_color(self, can: str, chi: str) -> tuple:
        """Trả về màu theo ngũ hành"""
        cc = self.HANH_COLOR.get(self.CAN_HANH.get(str(can).strip(), ""), "#aaaaaa")
        hc = self.HANH_COLOR.get(self.CHI_HANH.get(str(chi).strip(), ""), "#aaaaaa")
        return cc, hc

    def build_figure(self, offset: int):
        """Xây dựng biểu đồ PNL với các annotation"""
        start_idx = max(0, offset)
        end_idx = min(self.total_rows, start_idx + self.WINDOW_SIZE)
        df_view = self.df_filtered.iloc[start_idx:end_idx].copy()

        if df_view.empty:
            return go.Figure()

        start_date = df_view['date'].iloc[0]
        end_date = df_view['date'].iloc[-1]
        df_pnl = df_view[df_view['pnl'] != 0].copy()

        # Xác định range cho y-axis
        if not df_pnl.empty:
            peak = max(abs(df_pnl['pnl'].max()), abs(df_pnl['pnl'].min()), 50) * 1.35
            pnl_max, pnl_min = peak, -peak * 0.55
        else:
            pnl_min, pnl_max = -50, 50

        fig = go.Figure()

        # Thêm nền 4 mùa
        years = range(start_date.year, end_date.year + 1)
        bounds = []
        for year in years:
            terms = self.get_solar_terms(year)
            bounds += [
                {'date': terms['Xuân phân']['date'], 'color': self.SEASON_COLORS['spring']},
                {'date': terms['Hạ chí']['date'], 'color': self.SEASON_COLORS['summer']},
                {'date': terms['Thu phân']['date'], 'color': self.SEASON_COLORS['autumn']},
                {'date': terms['Đông chí']['date'], 'color': self.SEASON_COLORS['winter']},
            ]
        bounds.sort(key=lambda x: x['date'])
        
        for i, b in enumerate(bounds):
            s = b['date']
            e = bounds[i+1]['date'] if i+1 < len(bounds) else pd.Timestamp(f'{s.year+1}-03-20')
            if e >= start_date and s <= end_date:
                fig.add_vrect(
                    x0=s, x1=e,
                    fillcolor=b['color'], opacity=0.45,
                    layer="below", line_width=0,
                )

        # Thêm PNL Bars
        if not df_pnl.empty:
            bar_colors = ['#00e676' if x >= 0 else '#ff1744' for x in df_pnl['pnl']]
            
            fig.add_trace(go.Bar(
                x=df_pnl['date'],
                y=df_pnl['pnl'],
                name="PNL",
                marker_color=bar_colors,
                marker_line_width=0,
                opacity=0.88,
                text=df_pnl['pnl'].apply(lambda x: f'{x:+,.0f}'),
                textposition='outside',
                textfont=dict(size=9, color='rgba(220,220,220,0.9)'),
                hovertemplate="<b>%{x|%d/%m/%Y}</b><br>PNL: %{y:+,.2f} USD<extra></extra>",
            ))

        # Thêm annotations cho moon phase và specdate
        pnl_by_date = {row['date'].normalize(): row['pnl'] for _, row in df_view.iterrows()}
        phase_labels = {0: "🌑", 90: "🌓", 180: "🌕", 270: "🌗"}
        phase_rows = df_view[df_view["moon_numeric"].isin([0, 90, 180, 270])]
        
        spec_map = {"ram": "Rằm", "rằm": "Rằm", "m1": "Mùng 1", "mùng 1": "Mùng 1"}
        spec_rows = df_view[df_view["specdate_clean"].isin(["ram", "rằm", "m1", "mùng 1"])]

        annotations = []

        for _, row in phase_rows.iterrows():
            d = row['date'].normalize()
            pnl_val = pnl_by_date.get(d, 0)
            icon = phase_labels.get(row['moon_numeric'], "🌙")
            ay = -22 if pnl_val >= 0 else 22
            annotations.append(dict(
                x=d, y=pnl_val,
                xref="x", yref="y",
                text=icon,
                showarrow=True,
                arrowhead=0, arrowwidth=1, arrowcolor="rgba(255,215,0,0.4)",
                ax=0, ay=ay,
                font=dict(size=18, color="#FFD700"),
            ))

        for _, row in spec_rows.iterrows():
            d = row['date'].normalize()
            pnl_val = pnl_by_date.get(d, 0)
            sv = row['specdate_clean']
            label = spec_map.get(sv, sv)
            is_ram = sv in ("ram", "rằm")
            color = "#FFD700" if is_ram else "#9b9bff"
            ay = -44 if pnl_val >= 0 else 44
            annotations.append(dict(
                x=d, y=pnl_val,
                xref="x", yref="y",
                text=label,
                showarrow=True,
                arrowhead=0, arrowwidth=1,
                arrowcolor=f"{'rgba(255,215,0,0.35)' if is_ram else 'rgba(155,155,255,0.35)'}",
                ax=0, ay=ay,
                font=dict(size=10, color=color),
                bgcolor="rgba(5,5,18,0.75)",
                bordercolor=color, borderwidth=1, borderpad=3,
            ))

        # Thêm tứ khí
        for year in years:
            for term_name, info in self.get_solar_terms(year).items():
                td = info['date']
                if start_date <= td <= end_date:
                    fig.add_vline(
                        x=td,
                        line_width=2,
                        line_dash="dash",
                        line_color=info['color'],
                        opacity=0.85,
                        annotation_text=f"  {info['icon']} {term_name}",
                        annotation_position="top left",
                        annotation_font=dict(size=12, color=info['color']),
                        annotation_bgcolor="rgba(5, 5, 18, 0.82)",
                        annotation_bordercolor=info['color'],
                        annotation_borderwidth=1,
                        annotation_borderpad=5,
                    )

        # Đường zero line
        fig.add_hline(y=0, line_dash="solid", line_color="rgba(255,255,255,0.2)", line_width=1)

        # Title và layout
        m0, m1 = start_date.strftime('%m/%Y'), end_date.strftime('%m/%Y')
        month_range_str = m0 if m0 == m1 else f"{m0} – {m1}"
        pnl_days = len(df_pnl)
        total_pnl = df_pnl['pnl'].sum() if not df_pnl.empty else 0
        sign_icon = "▲" if total_pnl >= 0 else "▼"

        fig.update_layout(
            template='plotly_dark',
            paper_bgcolor='#0d0d1a',
            plot_bgcolor='#0f1120',
            title=dict(
                text=f"<b>📅 {month_range_str}</b>  ·  Ngày {start_idx+1}–{end_idx} / {self.total_rows}  ·  {pnl_days} GD  ·  {sign_icon} {total_pnl:+,.0f} USD",
                font=dict(size=12, color='#cccccc'),
                x=0.01, xanchor='left', y=0.98,
            ),
            xaxis=dict(
                type='date',
                range=[start_date - timedelta(hours=12), end_date + timedelta(hours=12)],
                tickformat="%d/%m",
                dtick="D3",
                tickangle=-45,
                tickfont=dict(size=9),
                gridcolor='rgba(255,255,255,0.05)',
            ),
            yaxis=dict(
                title=dict(text="PNL (USD)", font=dict(size=10)),
                side="left",
                range=[pnl_min, pnl_max],
                tickformat="+,.0f",
                tickfont=dict(size=9),
                gridcolor='rgba(255,255,255,0.05)',
                zerolinecolor='rgba(255,255,255,0.25)',
            ),
            hovermode='x unified',
            bargap=0.22,
            annotations=annotations,
            height=600,
            margin=dict(l=60, r=20, t=50, b=55),
        )

        return fig

    def show_moon_calendar(self):
        """Hiển thị biểu đồ PNL chính"""
        st.divider()
        st.subheader("📈 PNL theo ngày với Lịch Âm Dương")
        
        # Điều khiển điều hướng
        col1, col2, col3, col4, col5 = st.columns([1, 1, 1, 1, 3])
        
        if 'offset' not in st.session_state:
            st.session_state.offset = max(0, self.total_rows - self.WINDOW_SIZE)
        
        with col1:
            if st.button("⏮ Đầu"):
                st.session_state.offset = 0
        with col2:
            if st.button("◀ Trước"):
                st.session_state.offset = max(0, st.session_state.offset - self.WINDOW_SIZE)
        with col3:
            if st.button("Sau ▶"):
                st.session_state.offset = min(max(0, self.total_rows - self.WINDOW_SIZE), 
                                              st.session_state.offset + self.WINDOW_SIZE)
        with col4:
            if st.button("Cuối ⏭"):
                st.session_state.offset = max(0, self.total_rows - self.WINDOW_SIZE)
        
        # Hiển thị thông tin
        start_idx = st.session_state.offset
        end_idx = min(self.total_rows, start_idx + self.WINDOW_SIZE)
        st.caption(f"Hiển thị ngày {start_idx + 1} - {end_idx} / {self.total_rows}")
        
        # Hiển thị biểu đồ
        fig = self.build_figure(st.session_state.offset)
        st.plotly_chart(fig, use_container_width=True)

    def show_random_charts(self):
        """Hiển thị chart ngẫu nhiên"""
        st.divider()
        st.subheader("📊 Chart Ngẫu Nhiên")

        np.random.seed(42)
        data = pd.DataFrame(
            {
                "Ngày": pd.date_range("2026-01-01", periods=30),
                "Giá Trị A": np.random.randn(30).cumsum(),
                "Giá Trị B": np.random.randn(30).cumsum(),
                "Giá Trị C": np.random.randn(30).cumsum(),
            }
        )

        col1, col2 = st.columns(2)
        with col1:
            st.line_chart(data.set_index("Ngày")[["Giá Trị A", "Giá Trị B"]])
        with col2:
            st.bar_chart(data.set_index("Ngày")["Giá Trị C"])

    def show_btc_section(self):
        """Hiển thị BTC charts"""
        st.divider()
        st.subheader("🔒 BTC Charts (Protected)")

        password = st.text_input("Nhập mật khẩu để xem dữ liệu BTC", type="password")
        if not password:
            return

        if password != self.PASSWORD:
            st.error("Mật khẩu không đúng. Vui lòng thử lại.")
            return

        try:
            df = pd.read_csv(self.BTC_PATH, parse_dates=["datetime"])
            st.success("Xác thực thành công — hiển thị dữ liệu BTC.")
            st.dataframe(df.head())

            btc_fig = go.Figure(
                data=[
                    go.Candlestick(
                        x=df["datetime"],
                        open=df["open"],
                        high=df["high"],
                        low=df["low"],
                        close=df["close"],
                    )
                ]
            )
            btc_fig.update_layout(
                title="BTC Candlestick Chart",
                xaxis_rangeslider_visible=False,
                height=500
            )
            st.plotly_chart(btc_fig, use_container_width=True)
        except FileNotFoundError:
            st.error(f"Không tìm thấy file {self.BTC_PATH}")

    def run(self):
        """Chạy ứng dụng"""
        # Sidebar thông tin
        st.sidebar.header("📊 Dashboard Info")
        st.sidebar.info(f"Tổng số ngày đặc biệt: {self.total_rows}")
        st.sidebar.markdown("---")
        st.sidebar.markdown("### Chú thích:")
        st.sidebar.markdown("🌑🌓🌕🌗 - Các pha Mặt Trăng")
        st.sidebar.markdown("🌸☀️🍂❄️ - Tứ khí")
        st.sidebar.markdown("🟢 - PNL dương")
        st.sidebar.markdown("🔴 - PNL âm")
        
        # Hiển thị các phần
        self.show_random_charts()
        self.show_moon_calendar()
        self.show_btc_section()


if __name__ == "__main__":
    MoonCalendarApp()