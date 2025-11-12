import streamlit as st
import pandas as pd

st.header("常用声学参数", divider=True)
with st.container(horizontal=True):
  temperature = st.number_input("Temperature (°C)", value=20)
  pressure = st.number_input("Pressure (Pa)", value=101325)
data = {
  "名称":[],
  "符号":[]
}
df = pd.DataFrame(data)

st.dataframe(df)
