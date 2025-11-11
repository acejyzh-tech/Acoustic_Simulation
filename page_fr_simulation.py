import time
import numpy as np
import pandas as pd
import streamlit as st
import altair as alt
import JYAcoustic as ac

debug_logs = f"初始化完成..."+time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())+"\n"

input_para = st.text_area(
    ":material/Settings: 请输入麦克风的参数：", 
    "0.3,0.2,0.15,1.3,1.85,180,280,6.0")
rows = input_para.split('\n')
paras = [row.split(',') for row in rows]
paras = [[float(item) if isinstance(item, str) and item.replace('.', '', 1).isdigit() else None for item in row] for row in paras]
paras = [row for row in paras if all(cell is not None for cell in row) and len(row)==8]
names = [str(i+1)+"#" for i in range(len(paras))]
df = pd.DataFrame(paras, columns=
                  ["声孔直径", "声孔长度", "前腔体积", "后腔体积", 
                   "振膜声顺", "泄气孔声阻尼", "薄流层声阻尼", "薄流层声质量"],
                 index = names)
st.dataframe(df) 

freqs = np.logspace(1, 5, 1000)  # 从 0.1Hz 到 100Hz
Sensitivity = pd.DataFrame({'Freq': freqs, })
Noise = pd.DataFrame({'Freq': freqs, })
log_debug(df)
log_debug(Sensitivity)
log_debug(Noise)


MICS = []    # 建立麦克风组
for mic_para in paras:
    MICS.append(ac.MIC())
# 计算麦克风频响
for i, mic in enumerate(MICS):
    mic.FC.C = ac.Ca(paras[i][2])*1e-9
    mic.BC.C = ac.Ca(paras[i][3])*1e-9
    mic.SD.C = paras[i][4]*1e-15
    mic.VH.R = paras[i][5]*1e9
    mic.BH.R = paras[i][6]*1e6
    mic.BH.M = paras[i][7]*1e3
    sens, noise = [], []  # 初始化数组
    for f in freqs:
        mic.AH.R = ac.Ra(f=f, D=paras[i][0]*1e-3, L=paras[i][1]*1e-3)
        mic.AH.M = ac.Ma(f=f, D=paras[i][0]*1e-3, L=paras[i][1]*1e-3)
        sens.append(ac.dB(mic.Sens(f)))
        noise.append(ac.dB(mic.N_total(f)))
    Sensitivity[names[i]] = sens
    Noise[names[i]] = noise

# 绘制频响曲线
charts_sens, charts_noise = [], []
colors = ["#3b6291", "#943c39", "#779043", "#624c7c", "#388498", "#bf7334", "#3f689", "#9c403d", "#7d9847", "#675083", "#3b8ba1", "#c97937"]
for i, col in enumerate(names):
    chart1 = alt.Chart(Sensitivity).mark_line().encode(
        x=alt.X("Freq:Q", scale=alt.Scale(type='log'), title='频率（Hz）'),
        y=alt.Y(f"{col}:Q", title="灵敏度（dB）"),
        color=alt.value(colors[i])
    )
    chart2 = alt.Chart(Noise).mark_line().encode(
        x=alt.X("Freq:Q", scale=alt.Scale(type='log'), title='频率（Hz）'),
        y=alt.Y(f"{col}:Q", title="噪声谱（dB）"),
        color=alt.value(colors[i])
    )
    charts_sens.append(chart1)
    charts_noise.append(chart2)

# 绘制曲线
tab1, tab2, tab3 = st.tabs(["灵敏度频响曲线", "噪声频谱曲线", "相位频响曲线"])
with tab1:
    st.altair_chart(alt.layer(*charts_sens))
with tab2:
    st.altair_chart(alt.layer(*charts_noise))
with tab3:
    st.altair_chart(alt.layer(*charts_noise))
st.toast("计算完成!")

