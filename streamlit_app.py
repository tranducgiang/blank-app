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