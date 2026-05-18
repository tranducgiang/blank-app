import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go

st.title("🎈 My new app")
st.write(
    "Let's start building! For help and inspiration, head over to [docs.streamlit.io](https://docs.streamlit.io/)."
)

# Tạo dữ liệu ngẫu nhiên
st.divider()
st.subheader("📊 Chart Ngẫu Nhiên")

# Tạo dataframe với dữ liệu ngẫu nhiên
np.random.seed(42)
data = pd.DataFrame({
    'Ngày': pd.date_range('2026-01-01', periods=30),
    'Giá Trị A': np.random.randn(30).cumsum(),
    'Giá Trị B': np.random.randn(30).cumsum(),
    'Giá Trị C': np.random.randn(30).cumsum()
})

# Hiển thị chart
col1, col2 = st.columns(2)

with col1:
    st.line_chart(data.set_index('Ngày')[['Giá Trị A', 'Giá Trị B']])

with col2:
    st.bar_chart(data.set_index('Ngày')['Giá Trị C'])


st.divider()
st.subheader("🌙 Moon Calendar Chart")

calendar_df = pd.read_csv("files/calendar_with_moon.csv")
calendar_df['date'] = pd.to_datetime(calendar_df['date'], dayfirst=False, errors='coerce')
calendar_df['moon_numeric'] = pd.to_numeric(calendar_df['moon'], errors='coerce')
phase_map = {
    0.0: 'new moon',
    90.0: 'first-moon',
    180.0: 'full-moon',
    270.0: 'half-moon'
}
calendar_df['moon_phase'] = calendar_df['moon_numeric'].map(phase_map)
calendar_df['highlight'] = calendar_df['specdate'].astype(str).str.strip().str.lower().isin(['ram', 'm1'])
calendar_df['highlight_y'] = calendar_df['moon_numeric'].fillna(-10)

st.write("Đọc file `files/calendar_with_moon.csv` và vẽ các pha mặt trăng.")

fig = go.Figure()
fig.add_trace(go.Scatter(
    x=calendar_df['date'],
    y=calendar_df['moon_numeric'],
    mode='markers+lines',
    name='Moon angle',
    marker=dict(color='royalblue', size=6),
    hovertemplate='Date: %{x}<br>Moon angle: %{y}<extra></extra>'
))
phase_points = calendar_df.dropna(subset=['moon_phase'])
fig.add_trace(go.Scatter(
    x=phase_points['date'],
    y=phase_points['moon_numeric'],
    mode='markers+text',
    text=phase_points['moon_phase'],
    textposition='top center',
    marker=dict(symbol='diamond', size=12, color='green'),
    name='Moon phases'
))
highlight_points = calendar_df[calendar_df['highlight']]
fig.add_trace(go.Scatter(
    x=highlight_points['date'],
    y=highlight_points['highlight_y'],
    mode='markers',
    marker=dict(color='red', size=12, symbol='circle'),
    name='ram / m1'
))
fig.update_layout(
    title='Moon phase chart from calendar_with_moon.csv',
    xaxis_title='Date',
    yaxis_title='Moon angle',
    legend_title='Legend',
    hovermode='closest'
)
st.plotly_chart(fig)

st.dataframe(calendar_df.head(20))

st.divider()
st.subheader("🔒 BTC Charts (Protected)")

# Simple password protection (change PASSWORD as needed)
PASSWORD = "astro123"
password = st.text_input("Nhập mật khẩu để xem dữ liệu BTC", type="password")

if password:
    if password == PASSWORD:
        # Load and display BTC data and candlestick only after correct password
        df = pd.read_csv("files/btc_2021.csv", parse_dates=["datetime"])
        st.success("Xác thực thành công — hiển thị dữ liệu BTC.")
        st.dataframe(df.head())

        # 1. Candlestick Chart (tốt nhất cho OHLC)
        fig = go.Figure(data=[go.Candlestick(
            x=df['datetime'],
            open=df['open'],
            high=df['high'],
            low=df['low'],
            close=df['close']
        )])
        fig.update_layout(title="BTC Candlestick Chart", xaxis_rangeslider_visible=False)
        st.plotly_chart(fig)
    else:
        st.error("Mật khẩu không đúng. Vui lòng thử lại.")