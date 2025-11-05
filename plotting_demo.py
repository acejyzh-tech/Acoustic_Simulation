import numpy as np
import pandas as pd
import streamlit as st
import altair as alt
import JYAcoustic as ac

# 正文

st.set_page_config(page_title="Plotting demo", page_icon=":material/show_chart:")
st.title("Plotting demo")
st.write(
    """
    This demo illustrates a combination of plotting and animation with
    Streamlit. We're generating a bunch of random numbers in a loop for around
    5 seconds. Enjoy!
    """
)

freqs = np.logspace(1, 5, 1000)  # 从 0.1Hz 到 100Hz
with st.sidebar:
    st.markdown(':material/Settings: 参数设置')

    D_AH = st.number_input("声孔直径（$mm$）", 0.1, 0.8, 0.3, 0.1,
                             label_visibility="visible",
                             help='麦克风进声孔直径。由于边界层与孔径数量级接近，这里将采用微孔管模型进行计算。$R_a=\eta$',
                          ) * 1e-15
    L_AH = st.number_input("声孔长度（$mm$）", 0.1, 0.8, 0.2, 0.1,
                             label_visibility="visible",
                             help='麦克风进声孔长度。由于边界层与孔径数量级接近，这里将采用微孔管模型进行计算。',
                          )
    C_SD = st.number_input("振膜声顺（$fF$）", 1.0, 4.0, 1.85, 0.1,
                             label_visibility="visible",
                             help='由振膜的面积、形状和张力决定。',
                          )
    R_VH = st.number_input("泄气孔声阻尼（$G\Omega$）", 10.0, 8000.0, 180.0, 10.0,
                             label_visibility="visible",
                             help='由泄气通道的几何尺寸而定，通常可用毛细孔近似处理，其阻尼与频率无关。',
                          )
    R_BH = st.number_input("薄流层声阻尼（$M\Omega$）", 100.0, 500.0, 280.0, 20.0,
                             label_visibility="visible",
                             help='包括薄流层及背板孔贡献的声阻尼。由薄流层厚度、背板孔的尺寸与分布决定，通常可用毛细孔近似处理，与频率无关。',
                          )
    M_BH = st.number_input("薄流层声质量（$KH$）", 1.0, 10.0, 6.0, 1.0,
                             label_visibility="visible",
                             help='包括薄流层及背板孔贡献的声质量。由薄流层厚度、背板孔的尺寸与分布决定，通常可用毛细孔近似处理，与频率无关。',
                          )

mic1 = ac.MIC()   # 定义MIC类mic1
mic1.SD.C = C_SD
mic1.VH.R = R_VH * 1e9
mic1.BH.R = R_BH * 1e6
mic1.BH.M = M_BH * 1e3

sens, N_AH, N_VH, N_BH, N_total = [], [], [], [], []  # 初始化数组
# 计算
for f in freqs:
    mic1.AH.R = ac.Ra(f=f, D=D_AH*1e-3, L=L_AH*1e-3)
    mic1.AH.M = ac.Ma(f=f, D=D_AH*1e-3, L=L_AH*1e-3)
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
