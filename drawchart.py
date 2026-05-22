# drawchart.py
import plotly.graph_objects as go
from pnlUtils import canchi_color, get_hanh, SEASON_COLORS, get_solar_terms
import pandas as pd


def build_figure(df_filtered, year, ngay_sinh=None, gio_sinh=12, chart_opts=None):
    """Xây dựng biểu đồ PNL cho toàn bộ 1 năm, hỗ trợ drag/zoom tự do"""

    if chart_opts is None:
        chart_opts = {}
    show_moon      = chart_opts.get("show_moon",      True)
    show_canchi    = chart_opts.get("show_canchi",     True)
    show_pnl_label = chart_opts.get("show_pnl_label", True)
    show_solar     = chart_opts.get("show_solar",      True)

    # Lọc data theo năm
    df_view = df_filtered[df_filtered['date'].dt.year == year].copy()

    if df_view.empty:
        return go.Figure(), f"Không có dữ liệu năm {year}"

    start_date = df_view['date'].iloc[0]
    end_date   = df_view['date'].iloc[-1]
    df_pnl     = df_view[df_view['pnl'] != 0].copy()
    total_rows  = len(df_filtered)

    # ── Y-axis range ────────────────────────────────────────────────────────────
    if not df_pnl.empty:
        peak = max(abs(df_pnl['pnl'].max()), abs(df_pnl['pnl'].min()), 50) * 1.35
        pnl_max, pnl_min = peak, -peak * 0.55
    else:
        pnl_min, pnl_max = -50, 50

    fig = go.Figure()

    # ── Nền 4 mùa ──────────────────────────────────────────────────────────────
    terms = get_solar_terms(year)
    bounds = [
        {'date': terms['Xuân phân']['date'], 'color': SEASON_COLORS['spring']},
        {'date': terms['Hạ chí']['date'],    'color': SEASON_COLORS['summer']},
        {'date': terms['Thu phân']['date'],   'color': SEASON_COLORS['autumn']},
        {'date': terms['Đông chí']['date'],   'color': SEASON_COLORS['winter']},
    ]
    # Thêm bound đầu năm và cuối năm để bao phủ toàn bộ
    prev_terms = get_solar_terms(year - 1)
    bounds_full = [
        {'date': prev_terms['Đông chí']['date'], 'color': SEASON_COLORS['winter']},
    ] + bounds + [
        {'date': pd.Timestamp(f'{year + 1}-03-20'), 'color': SEASON_COLORS['spring']},
    ]
    bounds_full.sort(key=lambda x: x['date'])

    for i, b in enumerate(bounds_full):
        s = b['date']
        e = bounds_full[i + 1]['date'] if i + 1 < len(bounds_full) else pd.Timestamp(f'{year + 1}-03-21')
        if e >= start_date and s <= end_date:
            fig.add_vrect(
                x0=max(s, start_date), x1=min(e, end_date),
                fillcolor=b['color'], opacity=0.45,
                layer="below", line_width=0,
            )

    # ── PNL Bars ────────────────────────────────────────────────────────────────
    if not df_pnl.empty:
        bar_colors = ['#00e676' if x >= 0 else '#ff1744' for x in df_pnl['pnl']]

        # Khởi tạo TuViAnalyzer nếu có ngày sinh
        _analyzer = None
        if ngay_sinh is not None:
            try:
                from tuvi import TuViAnalyzer
                _analyzer = TuViAnalyzer()
            except Exception:
                pass

        customdata = []
        for _, r in df_pnl.iterrows():
            can_s = str(r.get('can', '')).strip()
            chi_s = str(r.get('chi', '')).strip()
            hc, hh = get_hanh(can_s, chi_s)

            # Lộc ngày
            tiet_khi_str  = str(r.get('tiet_khi', '')).strip()   if 'tiet_khi'      in r.index else ''
            hanh_tiet_str = str(r.get('hanh_tiet_khi', '')).strip() if 'hanh_tiet_khi' in r.index else ''
            loc_str = ''
            if _analyzer is not None:
                try:
                    kq = _analyzer.luan_ngay_loc(ngay_sinh, r['date'].to_pydatetime(), gio_sinh)
                    if kq:
                        tiet_khi_str  = kq['thong_tin_co_ban'].get('tiet_khi', tiet_khi_str)
                        hanh_tiet_str = kq['thong_tin_co_ban'].get('hanh_tiet_khi', hanh_tiet_str)
                        loc_str = kq.get('tong_ket', '')
                except Exception:
                    pass

            customdata.append([can_s, chi_s, hc, hh, tiet_khi_str, hanh_tiet_str, loc_str])

        fig.add_trace(go.Bar(
            x=df_pnl['date'],
            y=df_pnl['pnl'],
            name="PNL",
            marker_color=bar_colors,
            marker_line_width=0,
            opacity=0.88,
            yaxis="y",
            text=df_pnl['pnl'].apply(lambda x: f'{x:+,.0f}') if show_pnl_label else None,
            textposition='outside',
            textfont=dict(size=9, color='rgba(220,220,220,0.9)'),
            customdata=customdata,
            hovertemplate=(
                "<b>%{x|%d/%m/%Y}</b><br>"
                "PNL: %{y:+,.2f} USD<br>"
                "Can Chi: %{customdata[0]} %{customdata[1]}<br>"
                "Ngũ hành: %{customdata[2]} · %{customdata[3]}<br>"
                "Tiết khí: %{customdata[4]} (%{customdata[5]})<br>"
                "%{customdata[6]}"
                "<extra></extra>"
            ),
            cliponaxis=False,
        ))

    # ── Moon Phase + Specdate annotations ──────────────────────────────────────
    # Chỉ hiển thị moon annotation cho ngày có PNL != 0
    pnl_by_date = {row['date'].normalize(): row['pnl'] for _, row in df_view.iterrows()}
    phase_labels = {0: "🌑", 90: "🌓", 180: "🌕", 270: "🌗"}

    # Moon phase: chỉ trên ngày có PNL
    phase_rows = df_view[
        df_view["moon_numeric"].isin([0, 90, 180, 270]) &
        (df_view["pnl"] != 0)   # ← loại bỏ ngày PNL = 0
    ]

    df_view["_spec"] = df_view["specdate"].astype(str).str.strip().str.lower()
    spec_map = {"ram": "Rằm", "rằm": "Rằm", "m1": "Mùng 1", "mùng 1": "Mùng 1"}
    spec_rows = df_view[
        df_view["_spec"].isin(["ram", "rằm", "m1", "mùng 1"]) &
        (df_view["pnl"] != 0)   # ← chỉ hiển thị khi có PNL
    ]

    annotations = []

    if show_moon:
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

    # ── Can Chi – ngày có |PNL| > 10 ──────────────────────────────────────────
    if show_canchi:
        df_big = df_pnl[df_pnl['pnl'].abs() > 10].copy()
        for _, row in df_big.iterrows():
            d = row['date'].normalize()
            pnl_val = row['pnl']
            can_str = str(row.get('can', '')).strip()
            chi_str = str(row.get('chi', '')).strip()
            if not can_str or can_str == 'nan':
                continue
            cc, hc = canchi_color(can_str, chi_str)
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

    # ── Tứ Khí vlines ──────────────────────────────────────────────────────────
    if show_solar:
        for term_name, info in get_solar_terms(year).items():
            td = info['date']
            td_ms = td.timestamp() * 1000
            start_ms = start_date.timestamp() * 1000
            end_ms   = end_date.timestamp() * 1000
            if start_ms <= td_ms <= end_ms:
                fig.add_vline(
                    x=td_ms,
                    line_width=2, line_dash="dash",
                    line_color=info['color'], opacity=0.85,
                    annotation_text=f"  {info['icon']} {term_name}",
                    annotation_position="top left",
                    annotation_font=dict(size=12, color=info['color']),
                    annotation_bgcolor="rgba(5,5,18,0.82)",
                    annotation_bordercolor=info['color'],
                    annotation_borderwidth=1,
                    annotation_borderpad=5,
                )

    # ── Zero line ───────────────────────────────────────────────────────────────
    fig.add_hline(y=0, line_dash="solid", line_color="rgba(255,255,255,0.2)", line_width=1)

    # ── Title ───────────────────────────────────────────────────────────────────
    pnl_days  = len(df_pnl)
    total_pnl = df_pnl['pnl'].sum() if not df_pnl.empty else 0
    sign_icon = "▲" if total_pnl >= 0 else "▼"
    title_str = (
        f"<b>📅 Năm {year}</b>"
        f"  ·  {pnl_days} GD"
        f"  ·  {sign_icon} {total_pnl:+,.0f} USD"
    )

    # ── Layout – zoom/drag hoàn toàn tự do ─────────────────────────────────────
    fig.update_layout(
        height=768,
        template='plotly_dark',
        paper_bgcolor='#0d0d1a',
        plot_bgcolor='#0f1120',
        dragmode='pan',           # drag để pan
        title=dict(
            text=title_str,
            font=dict(size=12, color='#cccccc'),
            x=0.01, xanchor='left', y=0.98,
        ),
        xaxis=dict(
            type='date',
            range=[f'{year}-01-01', f'{year}-12-31'],
            tickformat="%d/%m",
            dtick="M1",           # mỗi tháng 1 tick khi xem cả năm
            tickangle=0,          # nằm ngang
            tickfont=dict(size=9),
            gridcolor='rgba(255,255,255,0.05)',
            fixedrange=False,     # ← cho phép zoom/pan trên trục X
            rangeslider=dict(visible=True, thickness=0.04),  # mini range slider
        ),
        yaxis=dict(
            title=dict(text="PNL (USD)", font=dict(size=10)),
            side="left",
            range=[pnl_min, pnl_max],
            tickformat="+,.0f",
            tickfont=dict(size=9),
            gridcolor='rgba(255,255,255,0.05)',
            zerolinecolor='rgba(255,255,255,0.25)',
            fixedrange=False,     # ← cho phép zoom trục Y
        ),
        legend=dict(
            orientation="h", yanchor="bottom", y=1.01,
            xanchor="right", x=1,
            font=dict(size=9), bgcolor='rgba(0,0,0,0)',
        ),
        margin=dict(l=60, r=20, t=50, b=60),
        hovermode='x unified',
        bargap=0.15,
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
        f"📅 Năm {year}  "
        f"| {pnl_days} GD  "
        f"| {sign_icon} {total_pnl:+,.0f} USD"
    )
    return fig, info