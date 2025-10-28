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
    C_SD = st.sidebar.number_input("振膜顺性（fF）", 1.0, 4.0, 1.85, 0.05)
    R_AH = st.sidebar.number_input("声孔声阻（Mo）", 10.0, 500.0, 110.0, 1.0)
    M_AH = st.sidebar.number_input("声孔惯性（KH）", 10.0, 200.0, 40.0, 5.0)

    mic1 = ac.MIC()   # 定义MIC类mic1
    mic1.SD.C = C_SD * 1e-15
    mic1.AH.R = R_AH * 1e6
    mic1.AH.M = M_AH * 1e3
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
    st.set_page_config(page_title="Plotting demo", page_icon=":material/show_chart:")
    st.title("Plotting demo")
    st.write(
        """
        This demo illustrates a combination of plotting and animation with
        Streamlit. We're generating a bunch of random numbers in a loop for around
        5 seconds. Enjoy!
        """
    )
    df = pd.DataFrame(
        [
            {"Label": "1#", "振膜顺性": 1.85, "声孔惯性": 40},
        ]
    )
    para = st.table(df)

    st.markdown(f"DF is **{para}**")


    

    st.table(
        pd.DataFrame(
            {
                "Frequency (Hz)": freqs,
                "Sensitivity (dB)": ac.dB(sens),
                "Acoustic Inlet Noise (dB)": ac.dB(N_AH),
                "Vent Hole (dB)": ac.dB(N_VH),
                "Backplete Hole (dB)": ac.dB(N_BH),
                "Total Noise (dB)": ac.dB(N_total),
            }
        )
    )
    
    st.pyplot(fig)

# 正文
plotting_curve()
