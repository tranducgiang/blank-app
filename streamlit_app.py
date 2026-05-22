# streamlit_app.py
"""
App chính: PNL + Lịch Âm Dương + Tứ Trụ
"""

import datetime
import streamlit as st
import pandas as pd

import macro
from pnlUtils import (
    load_all_data,
    build_full_data,
    process_multiple_uploads,
    get_data_summary,
)
from drawchart import build_figure
from tuvi import TuViAnalyzer
import datetime as dt  # thêm alias để tránh conflict


# ──────────────────────────────────────────────────────────────
# SESSION STATE helpers
# ──────────────────────────────────────────────────────────────
def _init_session_state():
    """Khởi tạo session state lần đầu."""
    if 'data_loaded' not in st.session_state:
        df_filtered, df_full, daily_pnl = load_all_data()
        st.session_state.df_filtered    = df_filtered
        st.session_state.df_full        = df_full
        st.session_state.daily_pnl      = daily_pnl
        st.session_state.available_years = _years_from(df_filtered)
        st.session_state.data_loaded    = True
        st.session_state.using_default  = True
        st.session_state.bingx_files    = []
        st.session_state.binance_files  = []
        # Toggle defaults — chỉ set 1 lần, không bị override khi rerun
        st.session_state.tog_moon       = True
        st.session_state.tog_canchi     = True
        st.session_state.tog_pnl_label  = True
        st.session_state.tog_solar      = True


def _years_from(df_filtered: pd.DataFrame) -> list[int]:
    return sorted(df_filtered['date'].dt.year.dropna().unique().astype(int))


# ──────────────────────────────────────────────────────────────
# SIDEBAR: upload + START + RESET
# ──────────────────────────────────────────────────────────────
def _render_sidebar_upload():
    """Sidebar phần upload file."""
    st.sidebar.markdown("## 📂 Tải dữ liệu PNL")
    st.sidebar.markdown("*Chọn file Excel từ BingX và/hoặc Binance*")

    bingx_files = st.sidebar.file_uploader(
        "📊 BingX Files",
        type=['xlsx'],
        accept_multiple_files=True,
        key="bingx_upload",
        help="File Excel BingX (cột closeTime(UTC+8) và Realized PNL)",
    )
    if bingx_files:
        st.session_state.bingx_files = bingx_files
        st.sidebar.success(f"✅ {len(bingx_files)} file BingX đã chọn")

    binance_files = st.sidebar.file_uploader(
        "📈 Binance Files",
        type=['xlsx'],
        accept_multiple_files=True,
        key="binance_upload",
        help="File Excel Binance (header dòng 9, cột Thời gian & Lợi nhuận đã thực hiện)",
    )
    if binance_files:
        st.session_state.binance_files = binance_files
        st.sidebar.success(f"✅ {len(binance_files)} file Binance đã chọn")

    st.sidebar.markdown("---")


def _handle_start_button():
    """Xử lý nút START."""
    st.sidebar.markdown('<div class="start-btn">', unsafe_allow_html=True)
    clicked = st.sidebar.button("🚀 START - Load toàn bộ dữ liệu", key="start_btn", use_container_width=True)
    st.sidebar.markdown('</div>', unsafe_allow_html=True)

    if not clicked:
        return

    bingx   = st.session_state.bingx_files
    binance = st.session_state.binance_files

    if not bingx and not binance:
        st.sidebar.error("❌ Vui lòng chọn ít nhất 1 file BingX hoặc Binance!")
        return

    with st.spinner("🔄 Đang xử lý dữ liệu..."):
        pnl_list, errors = process_multiple_uploads({"BingX": bingx, "Binance": binance})

        for err in errors:
            st.sidebar.warning(f"⚠️ {err}")

        if not pnl_list:
            st.sidebar.error("❌ Không có dữ liệu PNL hợp lệ nào được tìm thấy!")
            return

        df_filtered, df_full, daily_pnl = build_full_data(
            pnl_list, st.session_state.get('df_full')
        )

        if df_filtered is None:
            st.sidebar.error("❌ Không thể xây dựng dữ liệu từ các file đã chọn!")
            return

        st.session_state.df_filtered     = df_filtered
        st.session_state.df_full         = df_full
        st.session_state.daily_pnl       = daily_pnl
        st.session_state.available_years = _years_from(df_filtered)
        st.session_state.data_loaded     = True
        st.session_state.using_default   = False

        summary = get_data_summary(df_filtered, daily_pnl)
        st.sidebar.success("✅ Load thành công!")
        st.sidebar.info(f"📊 {summary.get('total_trading_days', 0)} ngày giao dịch")
        st.sidebar.info(f"💰 Tổng PNL: {summary.get('total_pnl', 0):+,.2f} USD")

    st.rerun()


def _handle_reset_button():
    """Xử lý nút RESET."""
    if not st.sidebar.button("🔄 Reset về dữ liệu mặc định", key="reset_btn", use_container_width=True):
        return

    with st.spinner("Đang reset..."):
        df_filtered, df_full, daily_pnl = load_all_data()
        st.session_state.df_filtered     = df_filtered
        st.session_state.df_full         = df_full
        st.session_state.daily_pnl       = daily_pnl
        st.session_state.available_years = _years_from(df_filtered)
        st.session_state.using_default   = True
        st.session_state.bingx_files     = []
        st.session_state.binance_files   = []
        st.sidebar.success("✅ Đã reset về dữ liệu mặc định")

    st.rerun()


def _render_sidebar_status():
    """Hiển thị trạng thái dữ liệu hiện tại."""
    if st.session_state.using_default:
        st.sidebar.info("📌 Đang dùng: Dữ liệu mặc định")
    else:
        st.sidebar.success("📌 Đang dùng: Dữ liệu custom đã upload")


# ──────────────────────────────────────────────────────────────
# SIDEBAR: thống kê năm
# ──────────────────────────────────────────────────────────────
def _render_sidebar_stats(df_filtered: pd.DataFrame, daily_pnl: pd.DataFrame, current_year: int):
    """Sidebar phần thống kê."""
    st.sidebar.markdown("---")
    st.sidebar.header(f"📊 Thống kê năm {current_year}")

    df_year = df_filtered[
        (df_filtered['date'].dt.year == current_year) & (df_filtered['pnl'] != 0)
    ]
    if not df_year.empty:
        st.sidebar.success(f"💰 Tổng PNL: {df_year['pnl'].sum():+,.2f} USD")
        st.sidebar.info(f"📊 Ngày GD: {len(df_year)}")
        st.sidebar.info(f"📈 Max: {df_year['pnl'].max():+,.2f} USD")
        st.sidebar.info(f"📉 Min: {df_year['pnl'].min():+,.2f} USD")

    if daily_pnl is not None:
        st.sidebar.markdown("---")
        st.sidebar.markdown("**📊 Tổng tất cả:**")
        st.sidebar.success(f"💰 {daily_pnl['Realized PNL'].sum():+,.2f} USD")
        st.sidebar.info(f"📅 Tổng ngày GD: {len(daily_pnl)}")

    st.sidebar.markdown("---")
    st.sidebar.markdown("### Chú thích:")
    st.sidebar.markdown("🌑🌓🌕🌗 – Pha Mặt Trăng (ngày có GD)")
    st.sidebar.markdown("🌸☀️🍂❄️ – Tứ khí")
    st.sidebar.markdown("🟢 PNL dương  |  🔴 PNL âm")


# ──────────────────────────────────────────────────────────────
# CHART + điều hướng năm
# ──────────────────────────────────────────────────────────────
def _render_chart_section(df_filtered: pd.DataFrame, available_years: list[int]):
    """Thanh điều hướng năm + plotly chart."""
    if not available_years:
        st.error("Không có dữ liệu! Hãy upload file hoặc kiểm tra lại.")
        return None

    if 'selected_year' not in st.session_state:
        st.session_state.selected_year = (
            2021 if 2021 in available_years else available_years[0]
        )

    current_year = st.session_state.selected_year
    year_idx     = available_years.index(current_year) if current_year in available_years else 0

    # ── Hàng 1: điều hướng năm ─────────────────────────────────
    nav_cols = st.columns([1, 1] + [0.8] * len(available_years) + [1, 4])

    with nav_cols[0]:
        if st.button("🔄 ", key="reload"):
            st.rerun()

    with nav_cols[1]:
        if st.button("◀ Prev", key="prev", disabled=(year_idx == 0)):
            st.session_state.selected_year = available_years[year_idx - 1]
            for k in ["tog_moon", "tog_canchi", "tog_pnl_label", "tog_solar"]:
                st.session_state.pop(k, None)
            st.rerun()

    for i, yr in enumerate(available_years):
        with nav_cols[2 + i]:
            is_active = (yr == current_year)
            if is_active:
                st.markdown('<div class="year-btn-active">', unsafe_allow_html=True)
            if st.button(str(yr), key=f"year_{yr}"):
                st.session_state.selected_year = yr
                for k in ["tog_moon", "tog_canchi", "tog_pnl_label", "tog_solar"]:
                    st.session_state.pop(k, None)
                st.rerun()
            if is_active:
                st.markdown('</div>', unsafe_allow_html=True)

    with nav_cols[2 + len(available_years)]:
        if st.button(" ▶", key="next", disabled=(year_idx == len(available_years) - 1)):
            st.session_state.selected_year = available_years[year_idx + 1]
            for k in ["tog_moon", "tog_canchi", "tog_pnl_label", "tog_solar"]:
                st.session_state.pop(k, None)
            st.rerun()

    with nav_cols[2 + len(available_years) + 1]:
        pass  # info text sẽ render sau

    # ── Hàng 2: toggle hiển thị ────────────────────────────────
    st.markdown('<div class="toggle-row">', unsafe_allow_html=True)
    tog_cols = st.columns([1, 1, 1, 1, 6])
    with tog_cols[0]:
        show_moon = st.toggle("🌙 Moon / Specdate", key="tog_moon",
                              value=st.session_state.get("_tog_moon_val", True))
        st.session_state["_tog_moon_val"] = show_moon
    with tog_cols[1]:
        show_canchi = st.toggle("☯ Can Chi", key="tog_canchi",
                                value=st.session_state.get("_tog_canchi_val", True))
        st.session_state["_tog_canchi_val"] = show_canchi
    with tog_cols[2]:
        show_pnl_label = st.toggle("🔢 Nhãn PNL", key="tog_pnl_label",
                                   value=st.session_state.get("_tog_pnl_label_val", True))
        st.session_state["_tog_pnl_label_val"] = show_pnl_label
    with tog_cols[3]:
        show_solar = st.toggle("🌸 Tứ khí", key="tog_solar",
                               value=st.session_state.get("_tog_solar_val", True))
        st.session_state["_tog_solar_val"] = show_solar
    st.markdown('</div>', unsafe_allow_html=True)

    # ── Build + render chart ────────────────────────────────────
    ngay_sinh_dt = st.session_state.get('ngay_sinh_dt', None)
    gio_sinh_so  = st.session_state.get('gio_sinh_so', 12)

    chart_opts = {
        "show_moon":      show_moon,
        "show_canchi":    show_canchi,
        "show_pnl_label": show_pnl_label,
        "show_solar":     show_solar,
    }

    fig, info = build_figure(df_filtered, current_year, ngay_sinh_dt, gio_sinh_so, chart_opts)

    # Render info text vào cột cuối hàng năm
    with nav_cols[2 + len(available_years) + 1]:
        st.markdown(f'<span class="info-text">{info}</span>', unsafe_allow_html=True)

    st.plotly_chart(fig, use_container_width=True, height=768, config={
        'scrollZoom': True,
        'displaylogo': False,
        'modeBarButtonsToRemove': ['select2d', 'lasso2d'],
        'modeBarButtonsToAdd': ['resetScale2d'],
    })

    return current_year


# ──────────────────────────────────────────────────────────────
# TỨ TRỤ / XEM LỘC
# ──────────────────────────────────────────────────────────────

def _render_tuvi_input(col):
    """Form nhập liệu Tứ Trụ — lấy ngày sinh từ session state toàn cục."""
    with col:
        st.markdown("### 📝 Thông tin của bạn")

        ns_dt  = st.session_state.get("ngay_sinh_dt")
        gio_so = st.session_state.get("gio_sinh_so", 12)

        if ns_dt is None:
            st.warning("⚠️ Chưa lưu ngày sinh. Hãy điền và nhấn **💾 Lưu ngày sinh** ở trên.")
            return

        sinh_ngay = ns_dt.date()
        st.markdown(
            f"<div style='color:#aaaacc;font-size:13px;margin-bottom:8px;'>"
            f"Ngày sinh: <b style='color:#ffcc44;'>{sinh_ngay.strftime('%d/%m/%Y')}</b></div>",
            unsafe_allow_html=True,
        )

        if st.button("🔮 Xem lộc hôm nay", type="primary", use_container_width=True):
            with st.spinner("Đang tính toán..."):
                analyzer = TuViAnalyzer()
                tu_tru   = analyzer.tinh_tu_tru(sinh_ngay, gio_so)
                if tu_tru:
                    st.session_state['tuvi_result'] = analyzer.xem_loc_ngay(
                        tu_tru, datetime.datetime.now()
                    )
                    st.session_state['tu_tru'] = tu_tru
                    st.rerun()
                else:
                    st.error("Không thể tính Tứ Trụ!")


def _render_tuvi_result(col):
    """Hiển thị kết quả Tứ Trụ — toàn bộ bằng tiếng Việt."""
    with col:
        if 'tuvi_result' not in st.session_state:
            st.info("👈 Nhập thông tin và nhấn 'Xem lộc hôm nay'")
            return

        kq = st.session_state['tuvi_result']
        tt = st.session_state.get('tu_tru', {})

        # ── Bảng Tứ Trụ ──────────────────────────────────────
        st.markdown(f"""
        <div style="background:#0f1120;border-radius:12px;padding:16px;
                    margin-top:12px;border-left:4px solid #ffaa00;">
            <div style="font-size:16px;font-weight:bold;color:#ffaa00;
                        margin-bottom:12px;letter-spacing:.5px;">
                📜 Tứ Trụ của bạn
            </div>
            <table style="width:100%;border-collapse:collapse;font-size:13px;">
                <thead>
                    <tr style="border-bottom:1px solid #333;">
                        <th style="color:#888;font-weight:500;padding:5px 8px;text-align:left;width:25%">Trụ</th>
                        <th style="color:#888;font-weight:500;padding:5px 8px;text-align:left;width:30%">Can Chi</th>
                        <th style="color:#888;font-weight:500;padding:5px 8px;text-align:left">Ngũ hành</th>
                    </tr>
                </thead>
                <tbody>
                    <tr style="border-bottom:1px solid #1e1e30;">
                        <td style="color:#aaa;padding:6px 8px;">⛰ Năm</td>
                        <td style="color:#e0e0ff;padding:6px 8px;font-weight:bold;">{tt.get('nam','?')}</td>
                        <td style="color:#888;padding:6px 8px;font-size:12px;">—</td>
                    </tr>
                    <tr style="border-bottom:1px solid #1e1e30;">
                        <td style="color:#aaa;padding:6px 8px;">🌿 Tháng</td>
                        <td style="color:#e0e0ff;padding:6px 8px;font-weight:bold;">{tt.get('thang','?')}</td>
                        <td style="color:#888;padding:6px 8px;font-size:12px;">—</td>
                    </tr>
                    <tr style="border-bottom:1px solid #1e1e30;background:#151530;">
                        <td style="color:#ffaa00;padding:6px 8px;font-weight:bold;">🌟 Ngày (Nhật Trụ)</td>
                        <td style="color:#ffdd88;padding:6px 8px;font-weight:bold;font-size:15px;">{tt.get('ngay','?')}</td>
                        <td style="color:#ffaa00;padding:6px 8px;font-size:12px;">Nhật Can: <b>{kq['nhat_can']}</b> · {kq.get('ngu_hanh_nhat','')}</td>
                    </tr>
                    <tr>
                        <td style="color:#aaa;padding:6px 8px;">⏰ Giờ</td>
                        <td style="color:#e0e0ff;padding:6px 8px;font-weight:bold;">{tt.get('gio','?')}</td>
                        <td style="color:#888;padding:6px 8px;font-size:12px;">—</td>
                    </tr>
                </tbody>
            </table>
        </div>
        """, unsafe_allow_html=True)

        # ── Bảng ngày xem ─────────────────────────────────────
        st.markdown(f"""
        <div style="background:#0f1120;border-radius:12px;padding:16px;margin-top:10px;">
            <div style="font-size:14px;font-weight:bold;color:#88bbff;margin-bottom:10px;">
                📅 Ngày xem: {kq['ngay_xem']}
            </div>
            <table style="width:100%;border-collapse:collapse;font-size:13px;">
                <thead>
                    <tr style="border-bottom:1px solid #333;">
                        <th style="color:#888;font-weight:500;padding:5px 8px;text-align:left">Thành phần</th>
                        <th style="color:#888;font-weight:500;padding:5px 8px;text-align:left">Tên</th>
                        <th style="color:#888;font-weight:500;padding:5px 8px;text-align:left">Ngũ hành</th>
                        <th style="color:#888;font-weight:500;padding:5px 8px;text-align:left">Ghi chú</th>
                    </tr>
                </thead>
                <tbody>
                    <tr style="border-bottom:1px solid #1e1e30;">
                        <td style="color:#aaa;padding:6px 8px;">Thiên Can ngày</td>
                        <td style="color:#e0e0ff;padding:6px 8px;font-weight:bold;">{kq['today_can']}</td>
                        <td style="color:#7ec8e3;padding:6px 8px;">{kq.get('today_can_hanh','')}</td>
                        <td style="color:#666;padding:6px 8px;font-size:11px;">
                            {'✅ Tài Tinh' if kq['co_tai'] else ''}
                        </td>
                    </tr>
                    <tr>
                        <td style="color:#aaa;padding:6px 8px;">Địa Chi ngày</td>
                        <td style="color:#e0e0ff;padding:6px 8px;font-weight:bold;">{kq['today_chi']}</td>
                        <td style="color:#7ec8e3;padding:6px 8px;">{kq.get('today_chi_hanh','')}</td>
                        <td style="color:#666;padding:6px 8px;font-size:11px;">
                            {'🍀 Lộc Thần' if kq['co_loc'] else ''}
                        </td>
                    </tr>
                </tbody>
            </table>
            <div style="margin-top:10px;font-size:12px;color:#666;">
                Tài Tinh của bạn (Nhật Can <b style="color:#ffaa00">{kq['nhat_can']}</b>):
                hành <b style="color:#88ddaa">{kq.get('tai_hanh','?')}</b>
                &nbsp;·&nbsp;
                Lộc Thần: Chi <b style="color:#88ddaa">{kq.get('loc_than','?')}</b>
            </div>
        </div>
        """, unsafe_allow_html=True)

        # ── Kết luận ──────────────────────────────────────────
        st.markdown(f"""
        <div style="background-color:{kq['mau_sac']}18;
                    border:1px solid {kq['mau_sac']}88;
                    border-radius:8px;padding:12px 16px;
                    text-align:center;margin-top:10px;
                    font-size:15px;font-weight:bold;color:{kq['mau_sac']};">
            {kq['ket_luan']}
        </div>
        """, unsafe_allow_html=True)

        # ── Chi tiết lý giải ──────────────────────────────────
        if kq["giai_thich"]:
            st.markdown(
                "<div style='margin-top:10px;font-size:13px;color:#aaa;"
                "font-weight:bold;'>📖 Lý giải:</div>",
                unsafe_allow_html=True,
            )
            for g in kq["giai_thich"]:
                st.markdown(
                    f"<div style='font-size:13px;color:#cccccc;"
                    f"padding:4px 0 4px 12px;border-left:2px solid #333;'>{g}</div>",
                    unsafe_allow_html=True,
                )

        st.markdown("<div style='height:8px'></div>", unsafe_allow_html=True)
        if st.button("🗑 Xóa kết quả"):
            st.session_state.pop('tuvi_result', None)
            st.session_state.pop('tu_tru', None)
            st.rerun()




# ──────────────────────────────────────────────────────────────
# NGÀY SINH TOÀN CỤC
# ──────────────────────────────────────────────────────────────

def _save_ngay_sinh(sinh_ngay, gio_sinh_key: str):
    """Lưu ngày sinh + giờ sinh vào session state toàn cục."""
    gio_so = macro._GIO_MAP[gio_sinh_key]
    ns_dt  = datetime.datetime(sinh_ngay.year, sinh_ngay.month, sinh_ngay.day)
    st.session_state["ngay_sinh_dt"]           = ns_dt
    st.session_state["gio_sinh_so"]            = gio_so
    st.session_state["_global_gio_sinh_label"] = gio_sinh_key
    # Invalidate kết quả cũ khi đổi ngày sinh
    st.session_state.pop("pnl_tuvi_result", None)


def _render_ngay_sinh_global():
    """Widget ngày sinh + giờ sinh dùng chung toàn bộ app."""
    st.markdown("---")
    st.markdown(
        "<div style='background:#0f1120;border-radius:10px;"
        "padding:12px 18px;border:1px solid #2a2a40;margin-bottom:8px;'>"
        "<span style='color:#ffaa00;font-weight:bold;font-size:15px;'>🎂 Ngày Sinh</span>"
        " <span style='color:#666;font-size:12px;'>"
        "— dùng chung cho Chart Hover, Xem Lộc và Phân Tích PNL</span></div>",
        unsafe_allow_html=True,
    )
    c1, c2, c3 = st.columns([2, 2, 1])
    with c1:
        default_date = st.session_state.get("ngay_sinh_dt")
        default_date = default_date.date() if default_date else datetime.date(1990, 1, 1)
        sinh_ngay = st.date_input(
            "Ngày sinh (Dương lịch)",
            value=default_date,
            key="_global_sinh_ngay_input",
        )
    with c2:
        saved_gio = st.session_state.get("_global_gio_sinh_label", list(macro._GIO_MAP.keys())[6])
        gio_options = list(macro._GIO_MAP.keys())
        gio_idx = gio_options.index(saved_gio) if saved_gio in gio_options else 6
        gio_sinh_key = st.selectbox(
            "Giờ sinh",
            options=gio_options,
            index=gio_idx,
            key="_global_gio_sinh_input",
        )
    with c3:
        st.markdown("<div style='height:28px'></div>", unsafe_allow_html=True)
        if st.button("💾 Lưu", use_container_width=True, key="save_ngay_sinh_btn", type="primary"):
            _save_ngay_sinh(sinh_ngay, gio_sinh_key)
            st.success("✅ Đã lưu!")
            st.rerun()

    # Trạng thái đã lưu
    if st.session_state.get("ngay_sinh_dt"):
        ns  = st.session_state["ngay_sinh_dt"]
        lbl = st.session_state.get("_global_gio_sinh_label", "")
        st.markdown(
            f"<div style='color:#888;font-size:12px;margin-top:2px;'>"
            f"Đang dùng: <b style='color:#ffcc44;'>{ns.strftime('%d/%m/%Y')}</b>"
            f" · Giờ <b style='color:#ffcc44;'>{lbl}</b></div>",
            unsafe_allow_html=True,
        )
    st.markdown("---")

def _render_tuvi_section():
    """Khung Tứ Trụ đầy đủ."""
    st.markdown("---")
    st.markdown("## 🎋 Xem Lộc Ngày Hôm Nay Theo Tứ Trụ")
    col_left, col_right = st.columns(2)
    _render_tuvi_input(col_left)
    _render_tuvi_result(col_right)


# ──────────────────────────────────────────────────────────────
# PHÂN TÍCH PNL × TỨ TRỤ
# ──────────────────────────────────────────────────────────────

def _pnl_card_html(r: dict, show_detail: bool = True) -> str:
    """Trả về HTML hoàn chỉnh cho 1 card. Dùng với st.components.v1.html."""
    from pnlUtils import CAN_HANH, CHI_HANH, HANH_COLOR

    pnl         = r["pnl"]
    pnl_color   = "#00e676" if pnl > 0 else "#ff1744"
    diem        = r["diem_so"]
    tong_ket    = r.get("tong_ket", "")
    co_hoi      = r.get("co_hoi", [])
    canh_bao    = r.get("canh_bao", [])
    khuyen_nghi = r.get("khuyen_nghi", [])
    info        = r["thong_tin_co_ban"]
    diem_color  = (
        "#00e676" if diem >= 4 else
        "#ffaa00" if diem >= 1 else
        "#ff7043" if diem >= -2 else
        "#ff1744"
    )

    # Tách Can / Chi từ can_chi_ngay bằng startswith (tránh lỗi cắt Unicode)
    can_chi_str = info.get("can_chi_ngay", "")
    today_can   = ""
    for can_test in CAN_HANH:          # duyệt toàn bộ 10 Can
        if can_chi_str.startswith(can_test):
            if len(can_test) > len(today_can):
                today_can = can_test   # lấy Can khớp dài nhất
    chi_str   = can_chi_str[len(today_can):]
    hanh_can  = CAN_HANH.get(today_can, "")
    hanh_chi  = CHI_HANH.get(chi_str, "")

    # Màu border = ngũ hành của Can ngày
    border_color = HANH_COLOR.get(hanh_can, "#555577")
    can_color    = HANH_COLOR.get(hanh_can, "#e0e0ff")
    chi_color    = HANH_COLOR.get(hanh_chi, "#e0e0ff")

    can_chi_html = (
        f'<span style="color:{can_color};font-weight:bold;font-size:14px;">{today_can}</span>'
        f'<span style="color:{chi_color};font-weight:bold;font-size:14px;">{chi_str}</span>'
    )

    detail_rows = ""
    if show_detail:
        for x in co_hoi:
            detail_rows += f'<div style="color:#88ddaa;font-size:12px;padding:2px 0">{x}</div>'
        for x in canh_bao:
            detail_rows += f'<div style="color:#ffaa55;font-size:12px;padding:2px 0">{x}</div>'
        kn_rows = "".join(
            f'<div style="color:#aaaacc;font-size:12px;padding:2px 0">{x}</div>'
            for x in khuyen_nghi
        )
        detail_rows += f'<div style="margin-top:6px;">{kn_rows}</div>'
        detail_rows = f'<div style="margin-top:8px;border-top:1px solid #1e1e30;padding-top:8px;">{detail_rows}</div>'

    tiet_khi  = info.get("tiet_khi", "?")
    hanh_tiet = info.get("hanh_tiet_khi", "?")
    ngay_xem  = info.get("ngay_xem", "")

    return f"""<!DOCTYPE html>
<html>
<head>
<meta charset="utf-8">
<style>
  @import url('https://fonts.googleapis.com/css2?family=Be+Vietnam+Pro:wght@400;700&display=swap');
  body {{ margin:0; padding:0; background:transparent;
         font-family:'Be Vietnam Pro', Arial, sans-serif; }}
</style>
</head>
<body>
<div style="background:#0f1120;border-radius:10px;padding:14px 16px;
            border-left:4px solid {border_color};">
  <div style="display:flex;justify-content:space-between;align-items:center;flex-wrap:wrap;gap:6px;">
    <div>
      <span style="color:#aaaacc;font-size:13px;">&#128197; {ngay_xem}</span>&nbsp;
      {can_chi_html}&nbsp;
      <span style="color:#888;font-size:12px;">&#183; {tiet_khi} ({hanh_tiet})</span>
    </div>
    <div style="display:flex;align-items:center;gap:12px;">
      <span style="color:{pnl_color};font-weight:bold;font-size:16px;">{pnl:+,.2f} USD</span>
      <span style="background:{diem_color}22;border:1px solid {diem_color}66;
                   border-radius:6px;padding:2px 10px;
                   color:{diem_color};font-size:13px;font-weight:bold;">&#11088; {diem:+d}</span>
    </div>
  </div>
  <div style="margin-top:6px;font-size:13px;color:#cccccc;">{tong_ket}</div>
  {detail_rows}
</div>
</body></html>"""


def _render_thong_ke_box(tk: dict, nguong: float):
    """Hiển thị box thống kê tóm tắt."""
    st.markdown(f"""
    <div style='background:#0f1120;border-radius:12px;padding:18px 20px;
                border:1px solid #1e1e30;margin-bottom:16px;'>
        <div style='font-size:15px;font-weight:bold;color:#ffaa00;margin-bottom:14px;'>
            📊 Tương quan Điểm Lộc ↔ PNL
        </div>
        <div style='display:grid;grid-template-columns:repeat(auto-fill,minmax(160px,1fr));gap:12px;'>
            <div style='text-align:center;background:#0d0d1a;border-radius:8px;padding:10px;'>
                <div style='color:#888;font-size:11px;'>Tổng ngày GD</div>
                <div style='color:#e0e0ff;font-size:22px;font-weight:bold;'>{tk["tong_ngay_pnl"]}</div>
            </div>
            <div style='text-align:center;background:#0d0d1a;border-radius:8px;padding:10px;'>
                <div style='color:#888;font-size:11px;'>Thắng lớn (>{nguong:.0f}$)</div>
                <div style='color:#00e676;font-size:22px;font-weight:bold;'>{tk["tong_thang_lon"]}</div>
                <div style='color:#555;font-size:11px;'>ĐTB lộc: <b style="color:#00e676">{tk["diem_tb_thang_lon"]:+.1f}</b></div>
            </div>
            <div style='text-align:center;background:#0d0d1a;border-radius:8px;padding:10px;'>
                <div style='color:#888;font-size:11px;'>Lỗ lớn (&lt;-{nguong:.0f}$)</div>
                <div style='color:#ff1744;font-size:22px;font-weight:bold;'>{tk["tong_lo_lon"]}</div>
                <div style='color:#555;font-size:11px;'>ĐTB lộc: <b style="color:#ff7043">{tk["diem_tb_lo_lon"]:+.1f}</b></div>
            </div>
            <div style='text-align:center;background:#0d0d1a;border-radius:8px;padding:10px;'>
                <div style='color:#888;font-size:11px;'>ĐTB lộc toàn bộ</div>
                <div style='color:#88bbff;font-size:22px;font-weight:bold;'>{tk["diem_tb_tat_ca"]:+.1f}</div>
            </div>
            <div style='text-align:center;background:#0d0d1a;border-radius:8px;padding:10px;'>
                <div style='color:#888;font-size:11px;'>Thắng lớn có lộc</div>
                <div style='color:#00e676;font-size:22px;font-weight:bold;'>{tk["thang_co_loc_pct"]}%</div>
            </div>
            <div style='text-align:center;background:#0d0d1a;border-radius:8px;padding:10px;'>
                <div style='color:#888;font-size:11px;'>Lỗ lớn có cảnh báo</div>
                <div style='color:#ff7043;font-size:22px;font-weight:bold;'>{tk["lo_co_canh_bao_pct"]}%</div>
            </div>
        </div>
    </div>
    """, unsafe_allow_html=True)


def _render_pnl_tuvi_section():
    """Section phân tích toàn bộ PNL theo Tứ Trụ."""
    st.markdown("---")
    st.markdown("## 🔮 Phân Tích PNL × Tứ Trụ")

    df_full    = st.session_state.get("df_full")
    if df_full is None or df_full[df_full["pnl"] != 0].empty:
        st.info("📭 Chưa có dữ liệu PNL. Hãy upload file rồi nhấn START.")
        return

    # ── Lấy ngày sinh từ session state toàn cục ───────────────
    ngay_sinh_dt = st.session_state.get("ngay_sinh_dt")
    gio_so       = st.session_state.get("gio_sinh_so", 12)

    if ngay_sinh_dt is None:
        st.warning("⚠️ Chưa lưu ngày sinh. Hãy điền và nhấn **💾 Lưu ngày sinh** ở trên.")
        return

    with st.expander("⚙️ Cài đặt phân tích", expanded=True):
        st.markdown(
            f"<span style='color:#aaaacc;font-size:13px;'>Ngày sinh đang dùng: "
            f"<b style='color:#ffcc44;'>{ngay_sinh_dt.strftime('%d/%m/%Y')}</b></span>",
            unsafe_allow_html=True,
        )
        nguong = st.number_input(
            "Ngưỡng PNL lớn ($)",
            min_value=1.0, max_value=10000.0,
            value=st.session_state.get("pnl_tuvi_nguong", 10.0),
            step=5.0,
            key="pnl_tuvi_nguong",
        )
        run_btn = st.button("🚀 Phân tích ngay", type="primary", use_container_width=True, key="pnl_tuvi_run")

    if run_btn:
        with st.spinner("⏳ Đang phân tích toàn bộ ngày PNL..."):
            analyzer = TuViAnalyzer()
            result   = analyzer.analyze_pnl_tuvi(ngay_sinh_dt, df_full, gio_so, nguong)
        st.session_state["pnl_tuvi_result"]      = result
        st.session_state["pnl_tuvi_nguong_used"] = nguong

    if "pnl_tuvi_result" not in st.session_state:
        return

    result  = st.session_state["pnl_tuvi_result"]
    nguong  = st.session_state.get("pnl_tuvi_nguong_used", 10.0)
    tk      = result["thong_ke"]

    # ── Thống kê ───────────────────────────────────────────────
    _render_thong_ke_box(tk, nguong)

    # ── Tabs: Thắng lớn / Lỗ lớn / Tất cả ────────────────────
    tab_thang, tab_lo, tab_tat_ca = st.tabs([
        f"🟢 Thắng lớn ({tk['tong_thang_lon']})",
        f"🔴 Lỗ lớn ({tk['tong_lo_lon']})",
        f"📋 Tất cả ({tk['tong_ngay_pnl']})",
    ])

    import streamlit.components.v1 as components
    PAGE_SIZE = 10

    def _render_list(tab, rows: list, page_key: str, show_detail: bool = True):
        with tab:
            if not rows:
                st.info("Không có ngày nào trong nhóm này.")
                return

            rows_sorted = sorted(rows, key=lambda r: abs(r["pnl"]), reverse=True)
            total       = len(rows_sorted)
            total_pages = max(1, (total + PAGE_SIZE - 1) // PAGE_SIZE)

            # Khởi tạo page nếu chưa có
            if page_key not in st.session_state:
                st.session_state[page_key] = 1
            page = st.session_state[page_key]

            # Slice trang hiện tại
            start = (page - 1) * PAGE_SIZE
            end   = min(start + PAGE_SIZE, total)
            page_rows = rows_sorted[start:end]

            # Info + điều hướng trang trên
            col_info, col_nav = st.columns([3, 2])
            with col_info:
                st.markdown(
                    f"<span style='color:#888;font-size:12px;'>"
                    f"Hiển thị {start+1}–{end} / {total} kết quả</span>",
                    unsafe_allow_html=True,
                )
            with col_nav:
                nav_cols = st.columns(4)
                if nav_cols[0].button("⏮", key=f"{page_key}_first",  disabled=(page == 1)):
                    st.session_state[page_key] = 1; st.rerun()
                if nav_cols[1].button("◀",  key=f"{page_key}_prev",   disabled=(page == 1)):
                    st.session_state[page_key] = page - 1; st.rerun()
                if nav_cols[2].button("▶",  key=f"{page_key}_next",   disabled=(page == total_pages)):
                    st.session_state[page_key] = page + 1; st.rerun()
                if nav_cols[3].button("⏭", key=f"{page_key}_last",  disabled=(page == total_pages)):
                    st.session_state[page_key] = total_pages; st.rerun()

            # Render cards trang hiện tại
            for r in page_rows:
                detail_lines = len(r.get("co_hoi", [])) + len(r.get("canh_bao", [])) + len(r.get("khuyen_nghi", []))
                height = 90 + (detail_lines * 22 if show_detail else 0)
                components.html(_pnl_card_html(r, show_detail), height=height, scrolling=False)

            # Điều hướng trang dưới
            st.markdown(
                f"<div style='text-align:center;color:#666;font-size:12px;margin-top:4px;'>"
                f"Trang {page} / {total_pages}</div>",
                unsafe_allow_html=True,
            )

    _render_list(tab_thang, result["thang_lon"], "page_thang", show_detail=True)
    _render_list(tab_lo,    result["lo_lon"],    "page_lo",    show_detail=True)
    _render_list(tab_tat_ca, result["tat_ca"],   "page_all",   show_detail=False)

    if st.button("🗑 Xóa kết quả phân tích", key="pnl_tuvi_clear"):
        st.session_state.pop("pnl_tuvi_result", None)
        st.rerun()


# streamlit_app.py - cập nhật hàm _render_tiet_khi_circle_section()

def _render_tiet_khi_circle_section():
    """Section hiển thị vòng tròn 24 tiết khí và đánh dấu ngày sinh"""
    st.markdown("---")
    st.markdown("## 🌞 Vòng Tròn 24 Tiết Khí & Ngày Sinh")
    
    # Chọn năm để hiển thị
    col1, col2, col3 = st.columns([2, 1, 1])
    with col1:
        nam_hien_tai = dt.datetime.now().year
        nam_chon = st.number_input(
            "Chọn năm",
            min_value=2000,
            max_value=2030,
            value=nam_hien_tai,
            step=1,
            key="tiet_khi_nam"
        )
    
    with col2:
        st.markdown("<div style='height:28px'></div>", unsafe_allow_html=True)
        if st.button("🔄 Vẽ lại", key="ve_tiet_khi_btn", use_container_width=True):
            st.rerun()
    
    # Lấy ngày sinh từ session state
    ngay_sinh = st.session_state.get("ngay_sinh_dt")
    
    if ngay_sinh is None:
        st.warning("⚠️ Vui lòng nhập ngày sinh ở phần trên để xem tiết khí tương ứng!")
        from drawchart import draw_tiet_khi_circle
        fig = draw_tiet_khi_circle(nam_chon)
    else:
        # Vẽ vòng tròn có đánh dấu ngày sinh
        from drawchart import draw_tiet_khi_circle_with_birthday
        fig = draw_tiet_khi_circle_with_birthday(nam_chon, ngay_sinh)
        
        # Hiển thị thông tin ngày sinh
        from tuvi import TuViAnalyzer
        analyzer = TuViAnalyzer()
        
        # Tạo datetime cho năm đang xem
        try:
            ngay_sinh_trong_nam = dt.datetime(nam_chon, ngay_sinh.month, ngay_sinh.day)
        except:
            ngay_sinh_trong_nam = dt.datetime(nam_chon, ngay_sinh.month, 28)
        
        tiet_khi, hanh_tiet_khi = analyzer.get_tiet_khi_info(ngay_sinh_trong_nam)
        
        # Hiển thị thông tin dạng card đẹp
        st.markdown(f"""
        <div style='background:linear-gradient(135deg, #1a1a2e 0%, #0f1120 100%);
                    border-radius:12px;padding:16px 20px;margin-bottom:16px;
                    border-left:4px solid #ffaa00;'>
            <div style='display:flex;align-items:center;gap:15px;flex-wrap:wrap;'>
                <div style='font-size:48px;'>{'🎂'}</div>
                <div>
                    <div style='color:#aaa;font-size:13px;'>Ngày sinh của bạn</div>
                    <div style='color:#ffcc44;font-size:18px;font-weight:bold;'>
                        {ngay_sinh.strftime('%d/%m/%Y')}
                    </div>
                </div>
                <div style='width:1px;height:40px;background:#333;'></div>
                <div>
                    <div style='color:#aaa;font-size:13px;'>Rơi vào tiết khí</div>
                    <div style='color:#4caf50;font-size:18px;font-weight:bold;'>
                        {tiet_khi} 
                    </div>
                </div>
                <div>
                    <div style='color:#aaa;font-size:13px;'>Hành tiết khí</div>
                    <div style='color:#29b6f6;font-size:16px;font-weight:bold;'>
                        {hanh_tiet_khi}
                    </div>
                </div>
            </div>
        </div>
        """, unsafe_allow_html=True)
    
    st.plotly_chart(fig, use_container_width=True, config={
        'displaylogo': False,
        'modeBarButtonsToRemove': ['select2d', 'lasso2d'],
    })

# streamlit_app.py - thêm hàm mới

def _render_tiet_khi_pnl_section():
    """Section hiển thị vòng tròn 24 tiết khí với các đường PNL"""
    st.markdown("---")
    st.markdown("## 📊 Vòng Tròn Tiết Khí & PNL")
    st.markdown(
        "<span style='color:#888;font-size:13px;'>"
        "Mỗi đường nối từ tâm đến tiết khí thể hiện tổng PNL của tất cả giao dịch trong tiết khí đó. "
        "🟢 Xanh = PNL dương, 🔴 Đỏ = PNL âm, ⭐ Vàng = Ngày sinh"
        "</span>",
        unsafe_allow_html=True
    )
    
    # Kiểm tra có dữ liệu PNL không
    df_filtered = st.session_state.get("df_filtered")
    if df_filtered is None or df_filtered[df_filtered["pnl"] != 0].empty:
        st.warning("⚠️ Chưa có dữ liệu PNL. Hãy upload file và nhấn START!")
        return
    
    # Chọn năm
    col1, col2, col3 = st.columns([2, 1, 1])
    with col1:
        available_years = sorted(df_filtered['date'].dt.year.unique())
        if available_years:
            nam_chon = st.selectbox(
                "Chọn năm",
                options=available_years,
                index=len(available_years) - 1 if available_years else 0,
                key="tiet_khi_pnl_nam"
            )
        else:
            nam_chon = dt.datetime.now().year
    
    with col2:
        st.markdown("<div style='height:28px'></div>", unsafe_allow_html=True)
        if st.button("🔄 Vẽ lại", key="ve_tiet_khi_pnl_btn", use_container_width=True):
            st.rerun()
    
    # Lấy ngày sinh
    ngay_sinh = st.session_state.get("ngay_sinh_dt")
    
    # Vẽ biểu đồ
    from drawchart import draw_tiet_khi_circle_with_pnl
    fig = draw_tiet_khi_circle_with_pnl(nam_chon, df_filtered, ngay_sinh)
    
    st.plotly_chart(fig, use_container_width=True, config={
        'displaylogo': False,
        'modeBarButtonsToRemove': ['select2d', 'lasso2d'],
    })
    
    # Hiển thị bảng thống kê PNL theo tiết khí
    with st.expander("📋 Thống kê PNL theo từng tiết khí", expanded=False):
        # Tính toán thống kê
        df_year = df_filtered[df_filtered['date'].dt.year == nam_chon].copy()
        df_year = df_year[df_year['pnl'] != 0].copy()
        
        from tuvi import TuViAnalyzer
        analyzer = TuViAnalyzer()
        
        tiet_khi_stats = {}
        for _, row in df_year.iterrows():
            date_obj = row['date'].to_pydatetime() if hasattr(row['date'], 'to_pydatetime') else row['date']
            pnl_val = float(row['pnl'])
            tiet_khi, _ = analyzer.get_tiet_khi_info(date_obj)
            
            if tiet_khi not in tiet_khi_stats:
                tiet_khi_stats[tiet_khi] = {'pnl_list': [], 'total': 0, 'count': 0}
            tiet_khi_stats[tiet_khi]['pnl_list'].append(pnl_val)
            tiet_khi_stats[tiet_khi]['total'] += pnl_val
            tiet_khi_stats[tiet_khi]['count'] += 1
        
        # Tạo bảng dữ liệu
        stats_data = []
        for tiet_khi, stats in tiet_khi_stats.items():
            tk_info = macro.get_tiet_khi_info_by_name(tiet_khi)
            stats_data.append({
                "Tiết khí": f"{tk_info['icon'] if tk_info else ''} {tiet_khi}",
                "Mùa": tk_info['mua'] if tk_info else '?',
                "Tổng PNL": f"{stats['total']:+,.2f} USD",
                "Số ngày GD": stats['count'],
                "PNL TB/ngày": f"{stats['total']/stats['count']:+,.2f} USD",
                "Max": f"{max(stats['pnl_list']):+,.2f} USD",
                "Min": f"{min(stats['pnl_list']):+,.2f} USD"
            })
        
        df_stats = pd.DataFrame(stats_data)
        df_stats = df_stats.sort_values("Tổng PNL", ascending=False)
        
        st.dataframe(df_stats, use_container_width=True, hide_index=True)

# ──────────────────────────────────────────────────────────────
# MAIN
# ──────────────────────────────────────────────────────────────
def main():
    st.set_page_config(
        layout="wide",
        page_title="PNL + Lịch Âm Dương",
        initial_sidebar_state="collapsed",
    )
    st.markdown(macro.APP_CSS, unsafe_allow_html=True)

    _init_session_state()

    # Sidebar
    _render_sidebar_upload()
    _handle_start_button()
    _handle_reset_button()
    _render_sidebar_status()

    # Main area — ngày sinh lên đầu
    _render_ngay_sinh_global()

    current_year = _render_chart_section(
        st.session_state.df_filtered,
        st.session_state.available_years,
    )
    if current_year:
        _render_sidebar_stats(
            st.session_state.df_filtered,
            st.session_state.daily_pnl,
            current_year,
        )

    _render_tuvi_section()
    _render_pnl_tuvi_section()

     # ========== THÊM SECTION VÒNG TRÒN 24 TIẾT KHÍ ==========
    _render_tiet_khi_circle_section()
    # Section vòng tròn tiết khí với PNL (THÊM MỚI)
    _render_tiet_khi_pnl_section()
    
if __name__ == "__main__":
    main()