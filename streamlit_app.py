import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go
from datetime import timedelta
import os
from glob import glob

# ==================== CẤU HÌNH ====================
st.set_page_config(layout="wide", page_title="PNL + Lịch Âm Dương", initial_sidebar_state="collapsed")

WINDOW_SIZE = 100  # Số ngày hiển thị mỗi lần

# ==================== ĐỌC DỮ LIỆU ====================
@st.cache_data
def load_data():
    print("📂 Đang đọc dữ liệu...")
    
    CSV_PATH = "files/calendar_with_moon.csv"
    df_full = pd.read_csv(CSV_PATH)
    df_full["date"] = pd.to_datetime(df_full["date"], errors="coerce")
    df_full["moon_numeric"] = pd.to_numeric(df_full["moon"], errors="coerce")
    
    script_dir = os.path.dirname(os.path.abspath(__file__))
    
    # Đọc file Excel từ thư mục files
    files = glob(os.path.join(script_dir, "files/*.xlsx"))
    all_pnl = []
    
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
            except Exception as e:
                pass
    
    # Đọc file Excel Binance
    files_binance = glob(os.path.join(script_dir, "filesbinance/*.xlsx"))
    
    if files_binance:
        for file in files_binance:
            try:
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
                pass
    
    # Gộp tất cả PNL
    if all_pnl:
        df_all_pnl = pd.concat(all_pnl, ignore_index=True)
        df_all_pnl['date'] = pd.to_datetime(df_all_pnl['date'])
        daily_pnl = df_all_pnl.groupby('date')['Realized PNL'].sum().reset_index()
        daily_pnl = daily_pnl.sort_values('date')
        
        pnl_dict = dict(zip(daily_pnl['date'], daily_pnl['Realized PNL']))
        df_full['pnl'] = df_full['date'].map(pnl_dict).fillna(0)
    else:
        df_full['pnl'] = 0
    
    return df_full

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

def canchi_color(can: str, chi: str) -> tuple:
    """Trả về (can_color, chi_color) theo ngũ hành."""
    cc = HANH_COLOR.get(CAN_HANH.get(str(can).strip(), ""), "#aaaaaa")
    hc = HANH_COLOR.get(CHI_HANH.get(str(chi).strip(), ""), "#aaaaaa")
    return cc, hc

# ==================== HÀM VẼ CHART ====================
def build_figure(df_filtered, offset, total_rows):
    start_idx = max(0, offset)
    end_idx = min(total_rows, start_idx + WINDOW_SIZE)
    df_view = df_filtered.iloc[start_idx:end_idx].copy()

    if df_view.empty:
        return go.Figure(), ""

    start_date = df_view['date'].iloc[0]
    end_date = df_view['date'].iloc[-1]
    df_pnl = df_view[df_view['pnl'] != 0].copy()

    if not df_pnl.empty:
        peak = max(abs(df_pnl['pnl'].max()), abs(df_pnl['pnl'].min()), 50) * 1.35
        pnl_max, pnl_min = peak, -peak * 0.55
    else:
        pnl_min, pnl_max = -50, 50

    fig = go.Figure()

    # ── PNL Bars ────────────────────────────────────────────────────────────────
    if not df_pnl.empty:
        bar_colors = ['#00e676' if x >= 0 else '#ff1744' for x in df_pnl['pnl']]

        # Build customdata: [can, chi, hanh_can, hanh_chi] cho mỗi bar
        def _hanh(can, chi):
            hc = CAN_HANH.get(str(can).strip(), "?")
            hh = CHI_HANH.get(str(chi).strip(), "?")
            return hc, hh

        customdata = []
        for _, r in df_pnl.iterrows():
            can_s = str(r.get('can', '')).strip()
            chi_s = str(r.get('chi', '')).strip()
            hc, hh = _hanh(can_s, chi_s)
            customdata.append([can_s, chi_s, hc, hh])

        fig.add_trace(go.Bar(
            x=df_pnl['date'],
            y=df_pnl['pnl'],
            name="PNL",
            marker_color=bar_colors,
            marker_line_width=0,
            opacity=0.88,
            yaxis="y",
            text=df_pnl['pnl'].apply(lambda x: f'{x:+,.0f}'),
            textposition='outside',
            textfont=dict(size=9, color='rgba(220,220,220,0.9)'),
            customdata=customdata,
            hovertemplate=(
                "<b>%{x|%d/%m/%Y}</b><br>"
                "PNL: %{y:+,.2f} USD<br>"
                "Can Chi: %{customdata[0]} %{customdata[1]}<br>"
                "Ngũ hành: %{customdata[2]} · %{customdata[3]}"
                "<extra></extra>"
            ),
            cliponaxis=False,
        ))

    # ── Moon Phase + Specdate – annotation trên đỉnh bar ──────────────────────
    pnl_by_date = {row['date'].normalize(): row['pnl'] for _, row in df_view.iterrows()}
    phase_labels = {0: "🌑", 90: "🌓", 180: "🌕", 270: "🌗"}
    phase_rows = df_view[df_view["moon_numeric"].isin([0, 90, 180, 270])]

    df_view["_spec"] = df_view["specdate"].astype(str).str.strip().str.lower()
    spec_map = {"ram": "Rằm", "rằm": "Rằm", "m1": "Mùng 1", "mùng 1": "Mùng 1"}
    spec_rows = df_view[df_view["_spec"].isin(["ram", "rằm", "m1", "mùng 1"])]

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
            bgcolor="rgba(0,0,0,0)", borderwidth=0,
        ))

    for _, row in spec_rows.iterrows():
        d = row['date'].normalize()
        pnl_val = pnl_by_date.get(d, 0)
        sv = row['_spec']
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

    # ── Can Chi – ngày có |PNL| > 10, tầng 3 trên đỉnh bar ───────────────────
    df_big = df_pnl[df_pnl['pnl'].abs() > 10].copy()
    for _, row in df_big.iterrows():
        d = row['date'].normalize()
        pnl_val = row['pnl']
        can_str = str(row.get('can', '')).strip()
        chi_str = str(row.get('chi', '')).strip()
        if not can_str or can_str == 'nan':
            continue
        cc, hc = canchi_color(can_str, chi_str)
        # tầng 3: ay = -66 (trên spec/moon), +66 nếu bar âm
        ay = -66 if pnl_val >= 0 else 66
        annotations.append(dict(
            x=d, y=pnl_val,
            xref="x", yref="y",
            text=f'<span style="color:{cc}">{can_str}</span> <span style="color:{hc}">{chi_str}</span>',
            showarrow=True,
            arrowhead=0, arrowwidth=1,
            arrowcolor="rgba(180,180,180,0.25)",
            ax=0, ay=ay,
            font=dict(size=11),
            bgcolor="rgba(5,5,18,0.80)",
            bordercolor="rgba(120,120,120,0.5)",
            borderwidth=1, borderpad=4,
        ))

    # ── Zero line ───────────────────────────────────────────────────────────────
    fig.add_hline(y=0, line_dash="solid", line_color="rgba(255,255,255,0.2)", line_width=1)

    # ── Nhãn tháng/năm ─────────────────────────────────────────────────────────
    m0, m1 = start_date.strftime('%m/%Y'), end_date.strftime('%m/%Y')
    month_range_str = m0 if m0 == m1 else f"{m0} – {m1}"

    pnl_days = len(df_pnl)
    total_pnl = df_pnl['pnl'].sum() if not df_pnl.empty else 0
    sign_icon = "▲" if total_pnl >= 0 else "▼"

    title_str = (
        f"<b>📅 {month_range_str}</b>"
        f"  ·  Ngày {start_idx+1}–{end_idx} / {total_rows}"
        f"  ·  {pnl_days} GD"
        f"  ·  {sign_icon} {total_pnl:+,.0f} USD"
    )

    # ── Layout ──────────────────────────────────────────────────────────────────
    fig.update_layout(
        template='plotly_dark',
        paper_bgcolor='#0d0d1a',
        plot_bgcolor='#0f1120',
        dragmode='pan',
        title=dict(
            text=title_str,
            font=dict(size=12, color='#cccccc'),
            x=0.01, xanchor='left', y=0.98,
        ),
        xaxis=dict(
            type='date',
            tickformat="%d/%m",
            dtick="D3",
            tickangle=-45,
            tickfont=dict(size=9),
            gridcolor='rgba(255,255,255,0.05)',
            fixedrange=True,
        ),
        yaxis=dict(
            title=dict(text="PNL (USD)", font=dict(size=10)),
            side="left",
            range=[pnl_min, pnl_max],
            tickformat="+,.0f",
            tickfont=dict(size=9),
            gridcolor='rgba(255,255,255,0.05)',
            zerolinecolor='rgba(255,255,255,0.25)',
            fixedrange=False,
        ),
        legend=dict(
            orientation="h", yanchor="bottom", y=1.01,
            xanchor="right", x=1,
            font=dict(size=9), bgcolor='rgba(0,0,0,0)',
        ),
        margin=dict(l=60, r=20, t=50, b=55),
        hovermode='x unified',
        bargap=0.22,
        annotations=annotations,
    )

    fig.update_xaxes(
        showspikes=True, spikecolor="rgba(160,160,160,0.4)",
        spikemode="toaxis+across", spikesnap="cursor",  
    )
    fig.update_yaxes(
        showspikes=True, spikecolor="rgba(160,160,160,0.4)",
        spikemode="toaxis+across", spikesnap="cursor",  
    )

    info = (
        f"📅 {month_range_str}  "
        f"| {start_idx+1}–{end_idx}/{total_rows}  "
        f"| {pnl_days} GD  "
        f"| {sign_icon} {total_pnl:+,.0f} USD"
    )
    return fig, info

# ==================== MAIN ====================
def main():
    # Load dữ liệu
    df_full = load_data()
    
    # Lọc ngày đặc biệt (bỏ tứ khí tạm thời)
    df_full["specdate_clean"] = df_full["specdate"].astype(str).str.strip().str.lower()
    df_full["is_moon_phase"] = df_full["moon_numeric"].isin([0, 90, 180, 270])
    df_full["is_specdate"] = df_full["specdate_clean"].isin(["ram", "rằm", "m1", "mùng 1"])
    df_full["has_pnl"] = df_full["pnl"] != 0
    
    df_filtered = df_full[
        df_full["is_moon_phase"] | df_full["is_specdate"] | df_full["has_pnl"]
    ].copy().sort_values("date").reset_index(drop=True)
    
    total_rows = len(df_filtered)
    
    # CSS để tạo giao diện giống runtemp
    st.markdown("""
        <style>
        .stApp {
            background-color: #0d0d1a;
        }
        .stButton button {
            font-size: 12px;
            padding: 3px 10px;
            background-color: #1e1e30;
            color: #aaaacc;
            border: 1px solid #333;
            border-radius: 5px;
            margin: 3px;
            cursor: pointer;
        }
        .stButton button:hover {
            background-color: #2a2a40;
            color: white;
        }
        .reload-btn button {
            background-color: #5a009a;
            color: white;
            border: none;
        }
        .info-text {
            color: #7fff7f;
            margin-left: 14px;
            font-size: 11px;
        }
        div[data-testid="stVerticalBlock"] {
            gap: 0rem;
        }
        </style>
    """, unsafe_allow_html=True)
    
    # Khởi tạo session state
    if 'offset' not in st.session_state:
        st.session_state.offset = max(0, total_rows - WINDOW_SIZE)
    
    # Header với các nút điều khiển
    col1 = st.columns([1, 1, 1, 1, 1, 4])
    
    with col1[0]:
        if st.button("🔄 Reload", key="reload"):
            st.cache_data.clear()
            st.rerun()
    
    with col1[1]:
        if st.button("⏮ Đầu", key="first"):
            st.session_state.offset = 0
            st.rerun()
    
    with col1[2]:
        if st.button("◀ Trước", key="prev"):
            st.session_state.offset = max(0, st.session_state.offset - WINDOW_SIZE)
            st.rerun()
    
    with col1[3]:
        if st.button("Sau ▶", key="next"):
            st.session_state.offset = min(max(0, total_rows - WINDOW_SIZE), st.session_state.offset + WINDOW_SIZE)
            st.rerun()
    
    with col1[4]:
        if st.button("Cuối ⏭", key="last"):
            st.session_state.offset = max(0, total_rows - WINDOW_SIZE)
            st.rerun()
    
    with col1[5]:
        fig, info = build_figure(df_filtered, st.session_state.offset, total_rows)
        st.markdown(f'<span class="info-text">{info}</span>', unsafe_allow_html=True)
    
    # Hiển thị chart
    st.plotly_chart(fig, use_container_width=True, config={
        'scrollZoom': False,
        'displaylogo': False,
        'modeBarButtonsToRemove': ['zoom2d', 'zoomIn2d', 'zoomOut2d', 'autoScale2d', 'select2d', 'lasso2d']
    })

if __name__ == "__main__":
    print("=" * 58)
    print("🚀 PNL + LỊCH – KHÔNG LAG, NHÃN TO, NỀN SẪM")
    print("=" * 58)
    # print(f"✅ {total_rows if 'total_rows' in dir() else 'Đang load'} ngày sau lọc  |  Window {WINDOW_SIZE} ngày")
    main()