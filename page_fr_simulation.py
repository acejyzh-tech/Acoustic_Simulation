import numpy as np
import pandas as pd
import streamlit as st
import altair as alt
import JYAcoustic as ac

input_para = st.text_area(
    ":material/Settings: 请输入麦克风的参数：", 
    "0.3,0.2,0.15,1.3,1.85,180,280,6.0")
rows = input_para.split('\n')
paras = [row.split(',') for row in rows]
paras = [[float(item) if isinstance(item, str) and item.replace('.', '', 1).isdigit() else None for item in row] for row in paras]
paras = [row for row in paras if all(cell is not None for cell in row) and len(row)==8]
df = pd.DataFrame(paras, columns=
                  ["声孔直径", "声孔长度", "前腔体积", "后腔体积", 
                   "振膜声顺", "泄气孔声阻尼", "薄流层声阻尼", "薄流层声质量"])
st.dataframe(df) 

freqs = np.logspace(1, 5, 1000)  # 从 0.1Hz 到 100Hz
Sensitivity = pd.DataFrame({'Freq': freqs, })
Noise = pd.DataFrame({'Freq': freqs, })

MICS = []    # 建立麦克风组
for mic_para in paras:
    MICS.append(ac.MIC())

for i, mic in enumerate(MICS):
    mic.SD.C = paras[i][4]
    mic.VH.R = paras[i][5]
    mic.BH.R = paras[i][6]
    mic.BH.M = paras[i][7]
    mic.FC.C = ac.Ca(paras[i][2])
    mic.BC.C = ac.Ca(paras[i][3])
    sens, noise = [], []  # 初始化数组
    for f in freqs:
        mic.AH.R = ac.Ra(f=f, D=paras[i][0], L=paras[i][1])
        mic.AH.M = ac.Ma(f=f, D=paras[i][0], L=paras[i][1])
        sens.append(ac.dB(mic.Sens(f)))
        noise.append(ac.dB(mic.N_total(f)))
    Sensitivity[str(i)] = sens
    Noise[str(i)] = noise
st.dataframe(Sensitivity) 


chart = alt.Chart(Sensitivity).mark_line().encode(
x=alt.X('Freq', scale=alt.Scale(type='log'), title='频率（Hz）'),
y=alt.Y('0', title='dB')
) + alt.Chart(Sensitivity).mark_line().encode(
x=alt.X('Freq', scale=alt.Scale(type='log'), title='频率（Hz）'),
y=alt.Y('1', title='dB')
)
st.altair_chart(chart)
