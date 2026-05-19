# streamlit_app.py
import streamlit as st
import pandas as pd
from pnlUtils import load_all_data
from drawchart import build_figure

# ==================== CẤU HÌNH ====================
st.set_page_config(layout="wide", page_title="PNL + Lịch Âm Dương", initial_sidebar_state="collapsed")


def main():
    # Load dữ liệu
    df_filtered, df_full, daily_pnl = load_all_data()

    # Lấy danh sách các năm có dữ liệu
    available_years = sorted(df_filtered['date'].dt.year.dropna().unique().astype(int))
    if not available_years:
        st.error("Không có dữ liệu!")
        return

    # CSS
    st.markdown("""
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
        .year-btn button {
            font-size: 14px;
            font-weight: bold;
            padding: 5px 18px;
            background-color: #1a1a35;
            color: #ffffffcc;
            border: 1px solid #4444aa;
            border-radius: 7px;
        }
        .year-btn button:hover {
            background-color: #28286a;
            color: #ffffff;
        }
        .info-text {
            color: #7fff7f;
            margin-left: 14px;
            font-size: 11px;
        }
        div[data-testid="stVerticalBlock"] { gap: 0rem; }
        </style>
    """, unsafe_allow_html=True)

    # ── Session state ────────────────────────────────────────────────────────────
    if 'selected_year' not in st.session_state:
        st.session_state.selected_year = available_years[-1]  # mặc định năm mới nhất

    current_year = st.session_state.selected_year
    year_idx = available_years.index(current_year) if current_year in available_years else len(available_years) - 1

    # ── Header controls ──────────────────────────────────────────────────────────
    n_years = len(available_years)
    # Cột: Reload | ◀ | [năm 1] [năm 2] ... | ▶ | info
    nav_cols = st.columns([1, 1] + [1] * n_years + [1, 4])

    with nav_cols[0]:
        if st.button("🔄 Reload", key="reload"):
            st.cache_data.clear()
            st.rerun()

    with nav_cols[1]:
        prev_disabled = (year_idx == 0)
        if st.button("◀ Prev", key="prev", disabled=prev_disabled):
            st.session_state.selected_year = available_years[year_idx - 1]
            st.rerun()

    for i, yr in enumerate(available_years):
        with nav_cols[2 + i]:
            is_active = (yr == current_year)
            label = f"**{yr}**" if is_active else str(yr)
            if st.button(label, key=f"year_{yr}"):
                st.session_state.selected_year = yr
                st.rerun()

    with nav_cols[2 + n_years]:
        next_disabled = (year_idx == n_years - 1)
        if st.button("Next ▶", key="next", disabled=next_disabled):
            st.session_state.selected_year = available_years[year_idx + 1]
            st.rerun()

    # ── Build & render chart ─────────────────────────────────────────────────────
    fig, info = build_figure(df_filtered, current_year)

    with nav_cols[2 + n_years + 1]:
        st.markdown(f'<span class="info-text">{info}</span>', unsafe_allow_html=True)

    st.plotly_chart(fig, use_container_width=True, config={
        'scrollZoom': True,          # cuộn chuột để zoom
        'displaylogo': False,
        'modeBarButtonsToRemove': ['select2d', 'lasso2d'],
        'modeBarButtonsToAdd': ['resetScale2d'],
        'toImageButtonOptions': {'format': 'png', 'width': 1800, 'height': 700},
    })

    # ── Sidebar thống kê ─────────────────────────────────────────────────────────
    st.sidebar.header(f"📊 Thống kê năm {current_year}")

    df_year_pnl = df_filtered[
        (df_filtered['date'].dt.year == current_year) & (df_filtered['pnl'] != 0)
    ]
    if not df_year_pnl.empty:
        year_total = df_year_pnl['pnl'].sum()
        st.sidebar.success(f"💰 Tổng PNL: {year_total:+,.2f} USD")
        st.sidebar.info(f"📊 Ngày GD: {len(df_year_pnl)}")
        st.sidebar.info(f"📈 Max: {df_year_pnl['pnl'].max():+,.2f} USD")
        st.sidebar.info(f"📉 Min: {df_year_pnl['pnl'].min():+,.2f} USD")
    else:
        st.sidebar.warning("Không có giao dịch trong năm này.")

    if daily_pnl is not None:
        st.sidebar.markdown("---")
        st.sidebar.markdown("**📊 Tổng tất cả:**")
        st.sidebar.success(f"💰 {daily_pnl['Realized PNL'].sum():+,.2f} USD")
        st.sidebar.info(f"📅 Tổng ngày GD: {len(daily_pnl)}")

    st.sidebar.markdown("---")
    st.sidebar.markdown("### Chú thích:")
    st.sidebar.markdown("🌑🌓🌕🌗 - Pha Mặt Trăng (chỉ ngày có GD)")
    st.sidebar.markdown("🌸☀️🍂❄️ - Tứ khí")
    st.sidebar.markdown("🟢 PNL dương  |  🔴 PNL âm")
    st.sidebar.markdown("---")
    st.sidebar.markdown("**💡 Zoom/Pan:**")
    st.sidebar.markdown("- 🖱️ Cuộn chuột: zoom trục X")
    st.sidebar.markdown("- 🖱️ Drag trên chart: chọn vùng zoom")
    st.sidebar.markdown("- Double-click: reset về toàn năm")
    st.sidebar.markdown("- Range slider dưới biểu đồ: kéo để pan")


if __name__ == "__main__":
    print("=" * 58)
    print("🚀 PNL + LỊCH – ĐIỀU HƯỚNG THEO NĂM")
    print("=" * 58)
    main()