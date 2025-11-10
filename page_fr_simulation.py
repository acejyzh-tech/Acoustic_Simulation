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
st.dataframe(df) # , border="horizontal")

for mic_para in paras:
    pass

freqs = np.logspace(1, 5, 1000)  # 从 0.1Hz 到 100Hz
with st.sidebar:
    st.markdown(':material/Settings: 参数设置')

    D_AH = st.number_input("声孔直径（$mm$）", 0.1, 0.8, 0.3, 0.1,
                             label_visibility="visible",
                             help='麦克风进声孔直径。由于边界层与孔径数量级接近，这里将采用微孔管模型进行计算。$R_a=\eta$',
                          ) * 1e-3
    L_AH = st.number_input("声孔长度（$mm$）", 0.1, 0.8, 0.2, 0.1,
                             label_visibility="visible",
                             help='麦克风进声孔长度。由于边界层与孔径数量级接近，这里将采用微孔管模型进行计算。',
                          ) * 1e-3
    V_FC = st.number_input("前腔体积（$mm^3$）", 0.05, 2.0, 0.15, 0.05,
                             label_visibility="visible",
                             help='麦克风进声孔直径。由于边界层与孔径数量级接近，这里将采用微孔管模型进行计算。$R_a=\eta$',
                          ) * 1e-9
    V_BC = st.number_input("后腔体积（$mm^3$）", 0.05, 2.0, 1.3, 0.05,
                             label_visibility="visible",
                             help='麦克风进声孔长度。由于边界层与孔径数量级接近，这里将采用微孔管模型进行计算。',
                          ) * 1e-9
    C_SD = st.number_input("振膜声顺（$fF$）", 1.0, 4.0, 1.85, 0.1,
                             label_visibility="visible",
                             help='由振膜的面积、形状和张力决定。',
                          ) * 1e-15
    R_VH = st.number_input("泄气孔声阻尼（$G\Omega$）", 10.0, 8000.0, 180.0, 10.0,
                             label_visibility="visible",
                             help='由泄气通道的几何尺寸而定，通常可用毛细孔近似处理，其阻尼与频率无关。',
                          ) * 1e9
    R_BH = st.number_input("薄流层声阻尼（$M\Omega$）", 100.0, 500.0, 280.0, 20.0,
                             label_visibility="visible",
                             help='包括薄流层及背板孔贡献的声阻尼。由薄流层厚度、背板孔的尺寸与分布决定，通常可用毛细孔近似处理，与频率无关。',
                          ) * 1e6
    M_BH = st.number_input("薄流层声质量（$KH$）", 1.0, 10.0, 6.0, 1.0,
                             label_visibility="visible",
                             help='包括薄流层及背板孔贡献的声质量。由薄流层厚度、背板孔的尺寸与分布决定，通常可用毛细孔近似处理，与频率无关。',
                          ) * 1e3

mic1 = ac.MIC()   # 定义MIC类mic1
mic1.SD.C = C_SD
mic1.VH.R = R_VH
mic1.BH.R = R_BH
mic1.BH.M = M_BH
mic1.FC.C = ac.Ca(V_FC)
mic1.BC.C = ac.Ca(V_BC)

sens, N_AH, N_VH, N_BH, N_total = [], [], [], [], []  # 初始化数组
# 计算
for f in freqs:
    mic1.AH.R = ac.Ra(f=f, D=D_AH, L=L_AH)
    mic1.AH.M = ac.Ma(f=f, D=D_AH, L=L_AH)
    sens.append(ac.dB(mic1.Sens(f)))
    N_AH.append(ac.dB(mic1.N_AH(f)))
    N_VH.append(ac.dB(mic1.N_VH(f)))
    N_BH.append(ac.dB(mic1.N_BH(f)))
    N_total.append(ac.dB(mic1.N_total(f)))
    
# 绘制图形
df = pd.DataFrame({
    'Freq': freqs, 
    'Sensitivity': sens, 
    'Total Noise': N_total
})
chart = alt.Chart(df).mark_line().encode(
x=alt.X('Freq', scale=alt.Scale(type='log'), title='频率（Hz）'),
y=alt.Y('Sensitivity', title='dB')
) + alt.Chart(df).mark_line().encode(
x=alt.X('Freq', scale=alt.Scale(type='log'), title='频率（Hz）'),
y=alt.Y('Total Noise', title='dB')
)
st.altair_chart(chart)
