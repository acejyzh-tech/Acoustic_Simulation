import streamlit as st
import numpy as np
import pandas as pd
import altair as alt
import JYAcoustic as ac

st.header("绘制频响及失真曲线", divider=True)
init_fr = "35.0, 15000.0, 8.0, 25000.0, 6.0, 60000.0, 11.0\n"
fr_para = st.text_area("请输入频响曲线参数", init_fr)
fr_paras = [line.strip() for line in fr_para.splitlines() if line.strip()]
st.dataframe(fr_paras)

freqs = np.logspace(1, 5, 1000)  # 从 0.1Hz 到 100Hz
As = []
for data in fr_paras:
  As.append(1/np.sqrt(1+(50/freqs)**2))
