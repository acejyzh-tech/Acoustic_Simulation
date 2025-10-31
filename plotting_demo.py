# Copyright (c) Streamlit Inc. (2018-2022) Snowflake Inc. (2022-2025)
import time
import numpy as np
import pandas as pd
import streamlit as st
import matplotlib.pyplot as plt
import JYAcoustic as ac

def plotting_curve() -> None:
    freqs = np.logspace(1, 5, 1000)  # 从 0.1Hz 到 100Hz
    # 侧边参数输入栏
    with st.expander("麦克风参数"):
        st.write('''
            The chart above shows some numbers I picked for you.
            I rolled actual dice for these, so they're *guaranteed* to
            be random.
        ''')
        col1, col2 = st.columns(2)
        with col1:
            C_SD = st.number_input("振膜声顺", 1.0, 4.0, 1.85, 0.1,
                                     label_visibility="visible",
                                     help='''
                                     单位$fF$（$10^{-15}F$），由振膜的面积、形状和张力决定
                                     ''',
                                  )
            R_VH = st.number_input("泄气孔阻尼", 10.0, 8000.0, 180.0, 10.0,
                                     label_visibility="visible",
                                     help='''
                                     单位$G\Omega$（$10^{9}\Omega$），由振膜的面积、形状和张力决定
                                     ''',
                                  )
            R_BH = st.number_input("背板阻尼",
                                     label_visibility="visible",
                                     help='''
                                     单位$fF$（$10^{-15}F$），由振膜的面积、形状和张力决定
                                     ''',
                                  )
        with col2:
            st.write('test')


    mic1 = ac.MIC()   # 定义MIC类mic1
    mic1.SD.C = C_SD * 1e-15
    sens, N_AH, N_VH, N_BH, N_total = [], [], [], [], []  # 初始化数组
    # 计算
    for f in freqs:
        sens.append(mic1.Sens(f))
        N_AH.append(mic1.N_AH(f))
        N_VH.append(mic1.N_VH(f))
        N_BH.append(mic1.N_BH(f))
        N_total.append(mic1.N_total(f))
        
    # 绘制图形
    fig = plt.figure(figsize=(8,6))
    ax = plt.subplot()
    ax.semilogx(freqs, ac.dB(sens), '-k', label='Sensitivity') 
    ax.semilogx(freqs, ac.dB(N_AH), '-C0', label='Acoustic Inlet')
    ax.semilogx(freqs, ac.dB(N_VH), '-C1', label='Vent Hole')
    ax.semilogx(freqs, ac.dB(N_BH), '-C2', label='Backplete Hole')
    ax.semilogx(freqs, ac.dB(N_total), '-k', label='Total Noise')
    ax.grid()
    ax.legend(loc='best')
    
    # 显示图形
    st.pyplot(fig)

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
plotting_curve()
