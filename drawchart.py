# drawchart.py
import plotly.graph_objects as go
from macro import get_24_tiet_khi
import macro
from pnlUtils import canchi_color, get_hanh, SEASON_COLORS, get_solar_terms
import pandas as pd
import numpy as np
import datetime as dt  # thêm alias để tránh conflict
 

# drawchart.py - cập nhật hàm draw_tiet_khi_circle_with_pnl

def draw_tiet_khi_circle_with_pnl(year: int = None, df_filtered: pd.DataFrame = None, ngay_sinh=None):
    """
    Vẽ vòng tròn 24 tiết khí, đánh dấu ngày sinh, ngày hiện tại và vẽ các đường PNL
    - Đường màu xanh lá: PNL dương
    - Đường màu đỏ: PNL âm
    - Đường màu vàng: Ngày hiện tại (today)
    - Đường màu cam/đậm: Ngày sinh
    - Bán kính ngắn hơn, nằm trong vòng tròn (từ tâm đến bán kính 0.4~0.7)
    - Độ dày mỏng (width=1.5)
    """
    if year is None:
        year = dt.datetime.now().year
    
    # Vẽ vòng tròn cơ bản
    fig = draw_tiet_khi_circle(year)
    
    # Lọc dữ liệu PNL trong năm
    if df_filtered is not None:
        df_year = df_filtered[df_filtered['date'].dt.year == year].copy()
        df_year = df_year[df_year['pnl'] != 0].copy()  # chỉ lấy ngày có PNL
        
        # Tìm max |PNL| để scale bán kính
        max_abs_pnl = max(abs(df_year['pnl'].max()), abs(df_year['pnl'].min())) if not df_year.empty else 1
        # Tránh division by zero
        if max_abs_pnl == 0:
            max_abs_pnl = 1
        
        # Dictionary để lưu tổng PNL theo tiết khí
        tiet_khi_pnl = {}
        
        for _, row in df_year.iterrows():
            date_obj = row['date'].to_pydatetime() if hasattr(row['date'], 'to_pydatetime') else row['date']
            pnl_val = float(row['pnl'])
            
            # Lấy tiết khí của ngày này
            from tuvi import TuViAnalyzer
            analyzer = TuViAnalyzer()
            tiet_khi, _ = analyzer.get_tiet_khi_info(date_obj)
            
            if tiet_khi not in tiet_khi_pnl:
                tiet_khi_pnl[tiet_khi] = {'total': 0, 'list': []}
            tiet_khi_pnl[tiet_khi]['total'] += pnl_val
            tiet_khi_pnl[tiet_khi]['list'].append(pnl_val)
        
        # Bán kính tối thiểu và tối đa cho đường PNL (nằm trong vòng tròn)
        MIN_RADIUS = 0.15  # bán kính nhỏ nhất (PNL = 0)
        MAX_RADIUS = 0.75  # bán kính lớn nhất (PNL max) - nằm trong vòng tròn bán kính 1
        
        # Vẽ đường cho mỗi tiết khí có PNL
        for tiet_khi, data in tiet_khi_pnl.items():
            total_pnl = data['total']
            pnl_list = data['list']
            
            # Lấy thông tin tiết khí từ macro
            tk_info = macro.get_tiet_khi_info_by_name(tiet_khi)
            
            if tk_info:
                goc = tk_info['goc']
                mau = "#00e676" if total_pnl > 0 else "#ff1744"  # Xanh cho dương, đỏ cho âm
                
                # Tính bán kính dựa trên |PNL| (scale tuyến tính)
                abs_pnl = abs(total_pnl)
                # Scale: PNL=0 -> MIN_RADIUS, PNL=max -> MAX_RADIUS
                radius = MIN_RADIUS + (abs_pnl / max_abs_pnl) * (MAX_RADIUS - MIN_RADIUS)
                radius = min(MAX_RADIUS, max(MIN_RADIUS, radius))  # giới hạn trong khoảng
                
                # Tính tọa độ điểm trên vòng tròn bán kính `radius`
                rad = np.radians(90 - goc)
                x_point = radius * np.cos(rad)
                y_point = radius * np.sin(rad)
                
                # Vẽ đường nối từ tâm đến điểm (bán kính ngắn hơn)
                fig.add_trace(go.Scatter(
                    x=[0, x_point], 
                    y=[0, y_point],
                    mode='lines',
                    line=dict(color=mau, width=1.5, dash='solid'),
                    showlegend=False,
                    hoverinfo='text',
                    hovertext=f"📊 {tiet_khi}\n"
                              f"Tổng PNL: {total_pnl:+,.2f} USD\n"
                              f"Số ngày GD: {len(pnl_list)}\n"
                              f"Max: {max(pnl_list):+,.2f}\n"
                              f"Min: {min(pnl_list):+,.2f}\n"
                              f"Bán kính: {radius:.2f}"
                ))
                
                # Thêm chấm tròn nhỏ tại điểm cuối
                fig.add_trace(go.Scatter(
                    x=[x_point], y=[y_point],
                    mode='markers',
                    marker=dict(size=6, color=mau, symbol='circle',
                               line=dict(width=0.5, color='white')),
                    showlegend=False,
                    hoverinfo='none'
                ))
                
                # Thêm annotation nhỏ hiển thị tổng PNL (nếu |total_pnl| > 30)
                if abs(total_pnl) > 30:
                    # Vị trí label ở bán kính lớn hơn một chút
                    x_label = (radius + 0.05) * np.cos(rad)
                    y_label = (radius + 0.05) * np.sin(rad)
                    
                    # Xác định vị trí anchor
                    if -0.2 < x_label < 0.2:
                        xanchor = 'center'
                    elif x_label > 0:
                        xanchor = 'left'
                    else:
                        xanchor = 'right'
                    
                    if -0.2 < y_label < 0.2:
                        yanchor = 'middle'
                    elif y_label > 0:
                        yanchor = 'bottom'
                    else:
                        yanchor = 'top'
                    
                    # Định dạng số ngắn gọn (K, M)
                    if abs(total_pnl) >= 1000:
                        pnl_text = f"{total_pnl/1000:+.1f}K"
                    else:
                        pnl_text = f"{total_pnl:+.0f}"
                    
                    fig.add_annotation(
                        x=x_label,
                        y=y_label,
                        text=pnl_text,
                        showarrow=False,
                        font=dict(size=7, color=mau, weight='bold'),
                        bgcolor='rgba(15,17,32,0.7)',
                        bordercolor=mau,
                        borderwidth=0.5,
                        borderpad=1,
                        xanchor=xanchor,
                        yanchor=yanchor
                    )
    
    # ==================== THÊM ĐƯỜNG NGÀY HIỆN TẠI (TODAY) ====================
    today = dt.datetime.now()
    today_year = today.year
    
    # Chỉ vẽ nếu năm được chọn là năm hiện tại (hoặc có thể vẽ cho mọi năm)
    # Nếu muốn vẽ cho mọi năm, bỏ comment dòng dưới và comment if
    # if True:
    if year == today_year or year == today_year - 1 or year == today_year + 1:
        from tuvi import TuViAnalyzer
        analyzer = TuViAnalyzer()
        
        # Tạo datetime object cho ngày hiện tại trong năm được chọn
        try:
            today_in_year = dt.datetime(year, today.month, today.day)
        except:
            today_in_year = dt.datetime(year, today.month, 28)
        
        # Lấy tiết khí của ngày hiện tại
        tiet_khi_today, hanh_tiet_khi_today = analyzer.get_tiet_khi_info(today_in_year)
        
        # Lấy thông tin từ macro
        tk_info_today = macro.get_tiet_khi_info_by_name(tiet_khi_today)
        
        if tk_info_today:
            goc_today = tk_info_today['goc']
            icon_today = tk_info_today['icon']
            mau_today = "#FFD700"  # Màu vàng cho ngày hiện tại
            
            # Bán kính: chạy đến viền (1.0) để nổi bật, nhưng có thể hơi ngắn hơn để phân biệt với ngày sinh
            # Dùng bán kính 0.9 để phân biệt với đường ngày sinh (1.0)
            radius_today = 0.9
            
            rad_today = np.radians(90 - goc_today)
            x_point_today = radius_today * np.cos(rad_today)
            y_point_today = radius_today * np.sin(rad_today)
            
            # Vẽ đường nối từ tâm đến điểm (bán kính 0.9) - MÀU VÀNG
            fig.add_trace(go.Scatter(
                x=[0, x_point_today], 
                y=[0, y_point_today],
                mode='lines',
                line=dict(color=mau_today, width=2.5, dash='dot'),  # dash='dot' để phân biệt
                showlegend=False,
                hoverinfo='text',
                hovertext=f"📅 Hôm nay: {today.strftime('%d/%m/%Y')}\n"
                          f"Tiết khí: {tiet_khi_today} {icon_today}\n"
                          f"Hành tiết khí: {hanh_tiet_khi_today}\n"
                          f"Góc: {goc_today}°"
            ))
            
            # Vẽ chấm tròn màu vàng tại điểm cuối
            fig.add_trace(go.Scatter(
                x=[x_point_today], y=[y_point_today],
                mode='markers',
                marker=dict(size=10, color=mau_today, symbol='circle',
                           line=dict(width=1, color='white')),
                showlegend=False,
                hoverinfo='none'
            ))
            
            # Thêm annotation cho ngày hiện tại (ở bán kính 1.05)
            x_label_today = 1.05 * np.cos(rad_today)
            y_label_today = 1.05 * np.sin(rad_today)
            
            # Xác định vị trí anchor
            if -0.2 < x_label_today < 0.2:
                xanchor_today = 'center'
            elif x_label_today > 0:
                xanchor_today = 'left'
            else:
                xanchor_today = 'right'
            
            if -0.2 < y_label_today < 0.2:
                yanchor_today = 'middle'
            elif y_label_today > 0:
                yanchor_today = 'bottom'
            else:
                yanchor_today = 'top'
            
            fig.add_annotation(
                x=x_label_today,
                y=y_label_today,
                text=f"📅 <b>{tiet_khi_today}</b> {icon_today}<br>"
                     f"<span style='font-size:10px'>{today.strftime('%d/%m')}</span>",
                showarrow=True,
                arrowhead=2,
                arrowwidth=2,
                arrowcolor=mau_today,
                ax=0.1 * np.cos(rad_today),
                ay=0.1 * np.sin(rad_today),
                font=dict(size=9, color=mau_today, weight='bold'),
                bgcolor='rgba(15,17,32,0.9)',
                bordercolor=mau_today,
                borderwidth=1,
                borderpad=3,
                xanchor=xanchor_today,
                yanchor=yanchor_today
            )
            
            # Thêm chú thích góc
            fig.add_annotation(
                x=0.45 * np.cos(rad_today),
                y=0.45 * np.sin(rad_today),
                text=f"{goc_today}°",
                showarrow=False,
                font=dict(size=18, color=mau_today, weight='bold'),
                bgcolor='rgba(0,0,0,0.4)',
                borderpad=1
            )
    
    # Nếu có ngày sinh, vẽ đường đậm (chạy từ tâm ra đến viền - bán kính 1.0)
    if ngay_sinh is not None:
        from tuvi import TuViAnalyzer
        analyzer = TuViAnalyzer()
        
        # Tạo datetime object cho ngày sinh trong năm được chọn
        try:
            ngay_sinh_trong_nam = dt.datetime(year, ngay_sinh.month, ngay_sinh.day)
        except:
            ngay_sinh_trong_nam = dt.datetime(year, ngay_sinh.month, 28)
        
        # Dùng hàm có sẵn get_tiet_khi_info
        tiet_khi_sinh, hanh_tiet_khi_sinh = analyzer.get_tiet_khi_info(ngay_sinh_trong_nam)
        
        # Lấy thông tin từ macro
        tk_info_sinh = macro.get_tiet_khi_info_by_name(tiet_khi_sinh)
        
        if tk_info_sinh:
            goc_sinh = tk_info_sinh['goc']
            icon_sinh = tk_info_sinh['icon']
            mau_sinh = tk_info_sinh['mau']
            mua_sinh = tk_info_sinh['mua']
            
            # Đường ngày sinh chạy đến viền (bán kính 1.0)
            rad_sinh = np.radians(90 - goc_sinh)
            x_point_sinh_full = 1.0 * np.cos(rad_sinh)
            y_point_sinh_full = 1.0 * np.sin(rad_sinh)
            
            # 1. Vẽ đường nối từ tâm đến viền - ĐƯỜNG ĐẬM
            fig.add_trace(go.Scatter(
                x=[0, x_point_sinh_full], 
                y=[0, y_point_sinh_full],
                mode='lines',
                line=dict(color=mau_sinh, width=4, dash='solid'),
                showlegend=False,
                hoverinfo='text',
                hovertext=f"🎂 Ngày sinh: {ngay_sinh.strftime('%d/%m/%Y')}<br>"
                          f"Tiết khí: {tiet_khi_sinh} {icon_sinh}<br>"
                          f"Hành tiết khí: {hanh_tiet_khi_sinh}<br>"
                          f"Góc: {goc_sinh}°<br>Mùa: {mua_sinh}"
            ))
            
            # 2. Vẽ chấm tròn tại điểm đầu (tâm)
            fig.add_trace(go.Scatter(
                x=[0], y=[0],
                mode='markers',
                marker=dict(size=12, color=mau_sinh, symbol='circle', 
                           line=dict(width=2, color='white')),
                showlegend=False,
                hoverinfo='none'
            ))
            
            # 3. Vẽ chấm sao tại điểm cuối (trên viền)
            fig.add_trace(go.Scatter(
                x=[x_point_sinh_full], y=[y_point_sinh_full],
                mode='markers',
                marker=dict(size=16, color=mau_sinh, symbol='star-diamond',
                           line=dict(width=1.5, color='gold')),
                showlegend=False,
                hoverinfo='text',
                hovertext=f"🎂 {tiet_khi_sinh} {icon_sinh}"
            ))
            
            # 4. Thêm annotation nổi bật (ở bán kính 1.15)
            x_label_sinh = 1.15 * np.cos(rad_sinh)
            y_label_sinh = 1.15 * np.sin(rad_sinh)
            
            # Xác định vị trí anchor
            if -0.2 < x_label_sinh < 0.2:
                xanchor_sinh = 'center'
            elif x_label_sinh > 0:
                xanchor_sinh = 'left'
            else:
                xanchor_sinh = 'right'
            
            if -0.2 < y_label_sinh < 0.2:
                yanchor_sinh = 'middle'
            elif y_label_sinh > 0:
                yanchor_sinh = 'bottom'
            else:
                yanchor_sinh = 'top'
            
            fig.add_annotation(
                x=x_label_sinh,
                y=y_label_sinh,
                text=f"🎂 <b>{tiet_khi_sinh}</b> {icon_sinh}<br>"
                     f"<span style='font-size:10px'>{ngay_sinh.strftime('%d/%m')}</span><br>"
                     f"<span style='font-size:9px'>{hanh_tiet_khi_sinh}</span>",
                showarrow=True,
                arrowhead=2,
                arrowwidth=2,
                arrowcolor=mau_sinh,
                ax=0.12 * np.cos(rad_sinh),
                ay=0.12 * np.sin(rad_sinh),
                font=dict(size=10, color=mau_sinh, weight='bold'),
                bgcolor='rgba(15,17,32,0.9)',
                bordercolor=mau_sinh,
                borderwidth=1.5,
                borderpad=4,
                xanchor=xanchor_sinh,
                yanchor=yanchor_sinh
            )
    
    # Thêm chú thích cho các đường
    fig.add_annotation(
        x=1.38, y=-1.35,
        text="<span style='color:#00e676'>🟢 PNL dương</span>  |  "
             "<span style='color:#ff1744'>🔴 PNL âm</span>  |  "
             "<span style='color:#FFD700'>📅 Hôm nay</span>  |  "
             "<span style='color:#ffaa00'>⭐ Ngày sinh</span><br>"
             "<span style='font-size:9px'>Độ dài đường tỉ lệ với |PNL|</span>",
        showarrow=False,
        font=dict(size=12),
        bgcolor='rgba(15,17,32,0.85)',
        bordercolor='#555',
        borderwidth=1,
        borderpad=4,
        xanchor='right',
        yanchor='top'
    )
    
    return fig

# drawchart.py - cập nhật hàm draw_tiet_khi_circle (giữ lại tia và đường 4 trục)

def draw_tiet_khi_circle(year: int = None):
    """
    Vẽ vòng tròn 24 Tiết Khí theo Âm Dương Lịch
    Dùng mapping từ macro.py
    - GIỮ LẠI 24 đường tia từ tâm ra
    - GIỮ LẠI đường kẻ đậm cho 4 trục chính
    - Bỏ các đường bôi đỏ (đường chấm đỏ viền quanh)
    - Tăng kích thước font chữ
    - Biểu đồ to hơn
    """
    if year is None:
        year = dt.datetime.now().year
    
    # Lấy danh sách tiết khí từ macro
    from macro import DANH_SACH_24_TIET_KHI, get_tiet_khi_info_by_name
    
    # Tạo list dữ liệu với góc và màu
    tiet_khi_data = []
    for ten in DANH_SACH_24_TIET_KHI:
        info = get_tiet_khi_info_by_name(ten)
        if info:
            tiet_khi_data.append((
                info['goc'], 
                info['ten'], 
                info['icon'], 
                info['mau']
            ))
    
    # Tính tọa độ
    angles = np.array([data[0] for data in tiet_khi_data])
    radius = 1
    
    # Chuyển đổi góc: 0° = phía trên (12 giờ)
    rad = np.radians(90 - angles)
    x = radius * np.cos(rad)
    y = radius * np.sin(rad)
    
    fig = go.Figure()
    
    # 1. Vẽ vòng tròn ngoài (đậm hơn)
    theta = np.linspace(0, 2*np.pi, 100)
    fig.add_trace(go.Scatter(
        x=np.cos(theta), y=np.sin(theta),
        mode='lines',
        line=dict(color='#ffaa00', width=3.5),
        fill='toself',
        fillcolor='rgba(255,170,0,0.03)',
        showlegend=False,
        hoverinfo='none'
    ))
    
    # 2. Vẽ vòng tròn trong (bán kính 0.7)
    fig.add_trace(go.Scatter(
        x=0.7*np.cos(theta), y=0.7*np.sin(theta),
        mode='lines',
        line=dict(color='rgba(255,255,255,0.2)', width=1.5, dash='dash'),
        showlegend=False,
        hoverinfo='none'
    ))
    
    # 3. GIỮ LẠI 24 đường tia (từ tâm ra ngoài) - ĐÃ GIỮ
    for rad_i in rad:
        fig.add_trace(go.Scatter(
            x=[0, np.cos(rad_i)], y=[0, np.sin(rad_i)],
            mode='lines',
            line=dict(color='rgba(255,255,255,0.12)', width=0.8),
            showlegend=False,
            hoverinfo='none'
        ))
    
    # ==================== NGÀY THÁNG CHO CÁC TIẾT KHÍ ====================
    tiet_khi_dates = [
        # Mùa Xuân
        (315, 4, 2, "Lập Xuân"), (330, 19, 2, "Vũ Thủy"), (345, 5, 3, "Kinh Trập"),
        (0, 20, 3, "Xuân Phân"), (15, 4, 4, "Thanh Minh"), (30, 20, 4, "Cốc Vũ"),
        # Mùa Hè
        (45, 5, 5, "Lập Hạ"), (60, 21, 5, "Tiểu Mãn"), (75, 5, 6, "Mang Chủng"),
        (90, 21, 6, "Hạ Chí"), (105, 7, 7, "Tiểu Thử"), (120, 23, 7, "Đại Thử"),
        # Mùa Thu
        (135, 7, 8, "Lập Thu"), (150, 23, 8, "Xử Thử"), (165, 7, 9, "Bạch Lộ"),
        (180, 23, 9, "Thu Phân"), (195, 8, 10, "Hàn Lộ"), (210, 23, 10, "Sương Giáng"),
        # Mùa Đông
        (225, 7, 11, "Lập Đông"), (240, 22, 11, "Tiểu Tuyết"), (255, 7, 12, "Đại Tuyết"),
        (270, 21, 12, "Đông Chí"), (285, 5, 1, "Tiểu Hàn"), (300, 20, 1, "Đại Hàn"),
    ]
    
    # 4. GIỮ LẠI 4 trục chính - CÓ ĐƯỜNG KẺ ĐẬM
    chinh_goc = [0, 90, 180, 270]
    chinh_ten = ["Xuân Phân", "Hạ Chí", "Thu Phân", "Đông Chí"]
    chinh_icon = ["🌸", "☀️", "🍂", "❄️"]
    
    for goc, ten, icon in zip(chinh_goc, chinh_ten, chinh_icon):
        rad_chinh = np.radians(90 - goc)
        
        # Tìm ngày tháng
        ngay_str = ""
        for g, ngay, thang, ten_tk in tiet_khi_dates:
            if g == goc:
                ngay_str = f"{ngay:02d}/{thang:02d}"
                break
        
        # VẼ ĐƯỜNG KẺ ĐẬM cho 4 trục chính
        fig.add_trace(go.Scatter(
            x=[0, 1.18*np.cos(rad_chinh)], y=[0, 1.18*np.sin(rad_chinh)],
            mode='lines',
            line=dict(color='#ffaa00', width=3, dash='solid'),
            showlegend=False,
            hoverinfo='none'
        ))
        
        # Thêm label
        fig.add_annotation(
            x=1.28*np.cos(rad_chinh),
            y=1.28*np.sin(rad_chinh),
            text=f"{icon}<b style='font-size:16px'>{ten}</b><br><span style='font-size:13px'>{ngay_str}</span>",
            showarrow=False,
            font=dict(size=14, color='#ffaa00', weight='bold'),
            xanchor='center',
            yanchor='middle',
            bgcolor='rgba(15,17,32,0.85)',
            borderwidth=1.5,
            bordercolor='#ffaa00',
            borderpad=6
        )
    
    # 5. Đánh dấu các điểm tiết khí
    for i, (goc, ten, icon, mau) in enumerate(tiet_khi_data):
        rad_i = rad[i]
        
        # Tìm ngày tháng
        ngay_str = ""
        for g, ngay, thang, ten_tk in tiet_khi_dates:
            if g == goc and ten_tk == ten:
                ngay_str = f"{ngay:02d}/{thang:02d}"
                break
        
        # Chấm tròn tại vị trí
        fig.add_trace(go.Scatter(
            x=[x[i]], y=[y[i]],
            mode='markers+text',
            marker=dict(size=14, color=mau, symbol='circle', 
                       line=dict(width=1.5, color='white')),
            text=[icon],
            textposition='middle center',
            textfont=dict(size=18, color='white'),
            showlegend=False,
            hoverinfo='text',
            hovertext=f"<b>{ten}</b><br>📅 {ngay_str}<br>🎯 Góc: {goc}°"
        ))
        
        # Thêm label cho các tiết khí
        if goc not in chinh_goc:
            x_label = 1.15 * np.cos(rad_i)
            y_label = 1.15 * np.sin(rad_i)
            
            if abs(x_label) > 0.85 or abs(y_label) > 0.85:
                x_label = 1.25 * np.cos(rad_i)
                y_label = 1.25 * np.sin(rad_i)
            
            fig.add_annotation(
                x=x_label,
                y=y_label,
                text=f"<b>{ten}</b><br><span style='font-size:11px'>{ngay_str}</span>",
                showarrow=False,
                font=dict(size=11, color=mau, weight='bold'),
                xanchor='center' if abs(x_label) < 0.8 else ('left' if x_label > 0 else 'right'),
                yanchor='middle',
                bgcolor='rgba(15,17,32,0.75)',
                borderpad=4,
                borderwidth=0.5,
                bordercolor=mau
            )
    
    # 6. Vẽ 12 cung địa chi
    dia_chi = ["Tý", "Sửu", "Dần", "Mão", "Thìn", "Tỵ", "Ngọ", "Mùi", "Thân", "Dậu", "Tuất", "Hợi"]
    dc_goc = np.linspace(0, 330, 12)
    
    for i, (goc, dc) in enumerate(zip(dc_goc, dia_chi)):
        rad_dc = np.radians(90 - goc)
        x_dc = 0.82 * np.cos(rad_dc)
        y_dc = 0.82 * np.sin(rad_dc)
        
        fig.add_annotation(
            x=x_dc, y=y_dc,
            text=f"<b>{dc}</b>",
            showarrow=False,
            font=dict(size=14, color='#aaaaff', weight='bold'),
            xanchor='center',
            yanchor='middle',
            bgcolor='rgba(136,136,204,0.12)',
            borderwidth=0.8,
            bordercolor='#aaaaff',
            borderpad=4
        )
    
    # 7. Thêm tâm vòng tròn
    fig.add_trace(go.Scatter(
        x=[0], y=[0],
        mode='markers',
        marker=dict(size=10, color='#ffaa00', symbol='circle',
                   line=dict(width=2, color='white')),
        showlegend=False,
        hoverinfo='none'
    ))
    
    # 8. Thêm 4 mùa
    mua_data = [
        (45, "XUÂN", "#4caf50"),
        (135, "HẠ", "#ff5252"),
        (225, "THU", "#ffb300"),
        (315, "ĐÔNG", "#29b6f6"),
    ]
    
    for goc, ten, mau in mua_data:
        rad_mua = np.radians(90 - goc)
        x_mua = 0.58 * np.cos(rad_mua)
        y_mua = 0.58 * np.sin(rad_mua)
        
        fig.add_annotation(
            x=x_mua, y=y_mua,
            text=f"<b>{ten}</b>",
            showarrow=False,
            font=dict(size=20, color=mau, weight='bold'),
            xanchor='center',
            yanchor='middle',
            opacity=0.8
        )
    
    # 9. Thêm chú thích
    fig.add_annotation(
        x=1.45, y=-1.42,
        text="📅 Ngày tháng theo Dương lịch (gần đúng)",
        showarrow=False,
        font=dict(size=10, color='#888'),
        bgcolor='rgba(15,17,32,0.7)',
        borderpad=3,
        xanchor='right',
        yanchor='top'
    )
    
    # Cập nhật layout - KÍCH THƯỚC TO HƠN
    fig.update_layout(
        title=dict(
            text=f"<b>🌞 Vòng Tròn 24 Tiết Khí Năm {year}</b><br>" +
                 "<span style='font-size:14px;color:#aaa'>" +
                 "Mỗi cung 15° kinh độ mặt trời · 4 mùa Xuân-Hạ-Thu-Đông</span>",
            x=0.5,
            xanchor='center',
            font=dict(size=20, color='#ffaa00')
        ),
        width=1000,
        height=1000,
        xaxis=dict(
            visible=False,
            range=[-1.6, 1.6],
            showgrid=False,
            zeroline=False
        ),
        yaxis=dict(
            visible=False,
            range=[-1.6, 1.6],
            showgrid=False,
            zeroline=False,
            scaleanchor="x",
            scaleratio=1
        ),
        plot_bgcolor='#0f1120',
        paper_bgcolor='#0d0d1a',
        hovermode='closest',
        margin=dict(l=80, r=80, t=120, b=80),
        showlegend=False,
        annotations=fig.layout.annotations if hasattr(fig.layout, 'annotations') else []
    )
    
    return fig

def draw_tiet_khi_timeline(df_filtered: pd.DataFrame, year: int):
    """
    Vẽ 24 tiết khí dạng timeline trên biểu đồ PNL
    """
    # Cần tính ngày cụ thể của 24 tiết khí trong năm
    # Tạm thời dùng ngày trung bình (cần cập nhật chính xác sau)
    tiet_khi_ngay = [
        (2, 4, "Lập Xuân"), (2, 19, "Vũ Thủy"), (3, 5, "Kinh Trập"),
        (3, 20, "Xuân Phân"), (4, 4, "Thanh Minh"), (4, 20, "Cốc Vũ"),
        (5, 5, "Lập Hạ"), (5, 21, "Tiểu Mãn"), (6, 5, "Mang Chủng"),
        (6, 21, "Hạ Chí"), (7, 7, "Tiểu Thử"), (7, 23, "Đại Thử"),
        (8, 7, "Lập Thu"), (8, 23, "Xử Thử"), (9, 7, "Bạch Lộ"),
        (9, 23, "Thu Phân"), (10, 8, "Hàn Lộ"), (10, 23, "Sương Giáng"),
        (11, 7, "Lập Đông"), (11, 22, "Tiểu Tuyết"), (12, 7, "Đại Tuyết"),
        (12, 21, "Đông Chí"), (1, 5, "Tiểu Hàn"), (1, 20, "Đại Hàn"),
    ]
    
    fig = go.Figure()
    colors = ['#4caf50'] * 6 + ['#ff5252'] * 6 + ['#ffb300'] * 6 + ['#29b6f6'] * 6
    
    for i, (thang, ngay, ten) in enumerate(tiet_khi_ngay):
        try:
            date_obj = pd.Timestamp(f'{year}-{thang:02d}-{ngay:02d}')
            if thang == 1 and year > 2000:
                date_obj = pd.Timestamp(f'{year+1}-01-{ngay:02d}')
        except:
            continue
            
        fig.add_vline(
            x=date_obj,
            line_width=1.5,
            line_dash="dash",
            line_color=colors[i],
            opacity=0.7,
            annotation_text=f"  {ten[:2]}",
            annotation_position="top left" if i % 2 == 0 else "bottom left",
            annotation_font=dict(size=12, color=colors[i])
        )
    
    return fig

def draw_tiet_khi_circle_with_birthday(year: int = None, ngay_sinh=None):
    """
    Vẽ vòng tròn 24 tiết khí có đánh dấu ngày sinh và đường nối đậm
    Sử dụng mapping từ macro.py
    """
    if year is None:
        year = datetime.now().year
    
    # Vẽ vòng tròn cơ bản
    fig = draw_tiet_khi_circle(year)
    
    # Nếu có ngày sinh, vẽ đường nối đậm
    if ngay_sinh is not None:
        from tuvi import TuViAnalyzer
        analyzer = TuViAnalyzer()
        
        # Tạo datetime object cho ngày sinh trong năm được chọn
        try:
            ngay_sinh_trong_nam = dt.datetime(year, ngay_sinh.month, ngay_sinh.day)
        except:
            # Xử lý ngày 29/2
            ngay_sinh_trong_nam = dt.datetime(year, ngay_sinh.month, 28)
        
        # Dùng hàm có sẵn get_tiet_khi_info
        tiet_khi, hanh_tiet_khi = analyzer.get_tiet_khi_info(ngay_sinh_trong_nam)
        
        # Lấy thông tin từ macro
        tk_info = macro.get_tiet_khi_info_by_name(tiet_khi)
        
        if tk_info:
            goc = tk_info['goc']
            icon = tk_info['icon']
            mau = tk_info['mau']
            mua = tk_info['mua']
            
            # Tính tọa độ điểm trên vòng tròn
            rad = np.radians(90 - goc)
            x_point = 1.0 * np.cos(rad)
            y_point = 1.0 * np.sin(rad)
            
            # 1. Vẽ đường nối từ tâm (0,0) đến điểm trên vòng tròn - ĐƯỜNG ĐẬM
            fig.add_trace(go.Scatter(
                x=[0, x_point], 
                y=[0, y_point],
                mode='lines',
                line=dict(color=mau, width=5, dash='solid'),
                showlegend=False,
                hoverinfo='text',
                hovertext=f"🎂 Ngày sinh: {ngay_sinh.strftime('%d/%m/%Y')}<br>"
                          f"Tiết khí: {tiet_khi} {icon}<br>"
                          f"Hành tiết khí: {hanh_tiet_khi}<br>"
                          f"Góc: {goc}°<br>Mùa: {mua}"
            ))
            
            # 2. Vẽ chấm tròn lớn tại điểm đầu (tâm)
            fig.add_trace(go.Scatter(
                x=[0], y=[0],
                mode='markers',
                marker=dict(size=14, color=mau, symbol='circle', 
                           line=dict(width=2, color='white')),
                showlegend=False,
                hoverinfo='none'
            ))
            
            # 3. Vẽ chấm sao tại điểm cuối
            fig.add_trace(go.Scatter(
                x=[x_point], y=[y_point],
                mode='markers',
                marker=dict(size=18, color=mau, symbol='star-diamond',
                           line=dict(width=2, color='gold')),
                showlegend=False,
                hoverinfo='text',
                hovertext=f"🎂 {tiet_khi} {icon}"
            ))
            
            # 4. Thêm annotation nổi bật
            x_label = 1.4 * np.cos(rad)
            y_label = 1.4 * np.sin(rad)
            
            # Xác định vị trí anchor
            if -0.2 < x_label < 0.2:
                xanchor = 'center'
            elif x_label > 0:
                xanchor = 'left'
            else:
                xanchor = 'right'
            
            if -0.2 < y_label < 0.2:
                yanchor = 'middle'
            elif y_label > 0:
                yanchor = 'bottom'
            else:
                yanchor = 'top'
            
            fig.add_annotation(
                x=x_label,
                y=y_label,
                text=f"🎂 <b>{tiet_khi}</b> {icon}<br>"
                     f"<span style='font-size:11px'>{ngay_sinh.strftime('%d/%m')}</span><br>"
                     f"<span style='font-size:10px'>{hanh_tiet_khi}</span>",
                showarrow=True,
                arrowhead=2,
                arrowwidth=3,
                arrowcolor=mau,
                ax=0.15 * np.cos(rad),
                ay=0.15 * np.sin(rad),
                font=dict(size=11, color=mau, weight='bold'),
                bgcolor='rgba(15,17,32,0.95)',
                bordercolor=mau,
                borderwidth=2,
                borderpad=6,
                xanchor=xanchor,
                yanchor=yanchor
            )
            
            # 5. Thêm chú thích góc
            fig.add_annotation(
                x=0.55 * np.cos(rad),
                y=0.55 * np.sin(rad),
                text=f"{goc}°",
                showarrow=False,
                font=dict(size=10, color=mau, weight='bold'),
                bgcolor='rgba(0,0,0,0.5)',
                borderpad=2
            )
    
    return fig

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