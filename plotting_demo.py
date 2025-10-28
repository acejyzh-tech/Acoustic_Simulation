# Copyright (c) Streamlit Inc. (2018-2022) Snowflake Inc. (2022-2025)
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

import time
import numpy as np
import streamlit as st
from streamlit.hello.utils import show_code
import matplotlib.pyplot as plt
import JYAcoustic as ac

def plotting_demo() -> None:
    fo = st.sidebar.slider("低衰截止频率（Hz）", 10.0, 500.0, 20.0, 1.0)
    freqs = np.logspace(1, 5, 1000)  # 从 0.1Hz 到 100Hz
    
    mic1 = ac.MIC()   # 定义MIC类mic1
    sens, N_AH, N_VH, N_BH, N_total = [], [], [], [], []  # 初始化数组
    # 计算
    for f in freqs:
        sens.append(mic1.Sens(f))
        N_AH.append(mic1.N_AH(f))
        N_VH.append(mic1.N_VH(f))
        N_BH.append(mic1.N_BH(f))
        N_total.append(mic1.N_total(f))
    # 绘制图形
    plt.figure(figsize=(8,6))
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

st.set_page_config(page_title="Plotting demo", page_icon=":material/show_chart:")
st.title("Plotting demo")
st.write(
    """
    This demo illustrates a combination of plotting and animation with
    Streamlit. We're generating a bunch of random numbers in a loop for around
    5 seconds. Enjoy!
    """
)
plotting_demo()
# show_code(plotting_demo) # 显示源代码
