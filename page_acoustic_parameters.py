import streamlit as st
import pandas as pd

st.header("常用声学参数", divider=True)
with st.container(horizontal=True):
  temperature = st.number_input("Temperature (°C)", value=20)
  pressure = st.number_input("Pressure (Pa)", value=101325)
data = {
  "名称":["玻尔兹曼常数"],
  "英文":["Boltzmann constant"],
  "符号":["$k_B$"],
  "数值":[8.31446261815324 ],
  "单位":["$J K^{-1}mol^{-1}$"],
  "量纲":[""],
  "公式":[""],
  "说明":["定义国际单位制 SI 的七个固定常数之一"]
}
df = pd.DataFrame(data)

st.table(df)
