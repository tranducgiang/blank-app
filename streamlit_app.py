import streamlit as st
import pandas as pd
import numpy as np

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


df = pd.read_csv("files/btc_2021.csv", parse_dates=["datetime"])
fig_dict = {
  "data": [
    {
      "type": "candlestick",
      "x": df["datetime"].astype(str).tolist(),
      "open": df["open"].tolist(),
      "high": df["high"].tolist(),
      "low": df["low"].tolist(),
      "close": df["close"].tolist()
    }
  ],
  "layout": {"title": "BTC Candlestick (dict)"}
}
st.plotly_chart(fig_dict)