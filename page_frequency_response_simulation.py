import time
import numpy as np
import pandas as pd
import streamlit as st
import altair as alt
import JYAcoustic as ac

st.caption("基于Kirchhoff Law和微孔管理论的麦克风集中参数仿真工具。输入声孔尺寸（直径、深度）、前后腔容积、振膜顺性、泄气通道声阻尼、薄流层声阻和声质量，求解Kirchhoff方程组计算麦克风的灵敏度频响、噪声谱、以及相位频响。")

parabox = st.empty()
curvebox = st.empty()
log_key = "debug_log"
log_area = st.empty()

def log_debug(msg):
    if log_key not in st.session_state:
        st.session_state[log_key] = ""
    else:
        st.session_state[log_key] += f"{msg}\n"
        log_area.text_area("程序信息", value=st.session_state[log_key], height=300)
st.session_state[log_key] = ""
log_debug(f"更新数据..."+time.strftime("%Y-%m-%d %H:%M:%S", time.localtime()))

# 参数输入区
with parabox.container():
    input_para = st.text_area(
        ":material/Settings: 请输入麦克风的参数：", 
        "0.2,0.2,0.15,1.3,1.85,180,280,6.0\n"
    +"0.25,0.2,0.15,1.3,1.85,180,280,6.0\n"
    +"0.3,0.2,0.15,1.3,1.85,180,280,6.0\n"
    +"0.35,0.2,0.15,1.3,1.85,180,280,6.0\n")
    rows = input_para.split('\n')
    paras = [row.split(',') for row in rows]
    paras = [[float(item) if isinstance(item, str) and item.replace('.', '', 1).isdigit() else None for item in row] for row in paras]
    paras = [row for row in paras if all(cell is not None for cell in row) and len(row)==8]
    names = [str(i+1)+"#" for i in range(len(paras))]
    df = pd.DataFrame(paras, columns=
                      ["声孔直径", "声孔长度", "前腔体积", "后腔体积", 
                       "振膜声顺", "泄气孔声阻尼", "薄流层声阻尼", "薄流层声质量"],
                     index = names)
    st.caption("依次输入声孔直径$(mm)$，声孔长度$(mm)$，前腔体积$(mm^3)$，后腔体积$(mm^3)$，振膜声顺$(fF)$，泄气孔声阻尼$(G\Omega)$，薄流层声阻尼$(M\Omega)$，薄流层声质量$(KH)$，数据之间用英文逗号连接。无效数据不会被读取。")
    st.button("计算", type="primary")
    st.markdown("麦克风的参数列表") 
    st.dataframe(df) 
    log_debug(df.to_string(header=False))
    log_debug(f"计算中...")

with curvebox.container():
    freqs = np.logspace(1, 5, 1000)  # 从 0.1Hz 到 100Hz
    Sensitivity = pd.DataFrame({'Freq': freqs, })
    Noise = pd.DataFrame({'Freq': freqs, })
    Phase = pd.DataFrame({'Freq': freqs, })

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
        sens, noise, phase = [], [], []  # 初始化数组
        for f in freqs:
            mic.AH.R = ac.Ra(f=f, D=paras[i][0]*1e-3, L=paras[i][1]*1e-3)
            mic.AH.M = ac.Ma(f=f, D=paras[i][0]*1e-3, L=paras[i][1]*1e-3)
            sens.append(ac.dB(mic.Sens(f)))
            noise.append(ac.dB(mic.N_total(f)))
            phase.append(mic.phase(f))
        Sensitivity[names[i]] = sens
        Noise[names[i]] = noise
        Phase[names[i]] = phase
    log_debug(Sensitivity)
    log_debug(Noise)
    log_debug(Phase)

    # 绘制频响曲线
    charts_sens, charts_noise, charts_phase = [], [], []
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
        chart3 = alt.Chart(Phase).mark_line().encode(
            x=alt.X("Freq:Q", scale=alt.Scale(type='log'), title='频率（Hz）'),
            y=alt.Y(f"{col}:Q", title="相位（rad）"),
            color=alt.value(colors[i])
        )
        charts_sens.append(chart1)
        charts_noise.append(chart2)
        charts_phase.append(chart3)

    
    # 绘制曲线
    tab1, tab2, tab3 = st.tabs(["灵敏度频响曲线", "噪声频谱曲线", "相位频响曲线"])
    with tab1:
        st.altair_chart(alt.layer(*charts_sens))
    with tab2:
        st.altair_chart(alt.layer(*charts_noise))
    with tab3:
        st.altair_chart(alt.layer(*charts_phase))
    log_debug(f"计算中完成"+time.strftime("%Y-%m-%d %H:%M:%S", time.localtime()))
