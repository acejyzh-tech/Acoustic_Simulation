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



def plotting_demo() -> None:

    
    # 添加交互控件：截止频率滑块
    fc = st.sidebar.slider("截止频率（Hz）", 0.1, 100.0, 1.0, 0.1)
    
    # 生成频率数据（对数刻度）
    f = np.logspace(-1, 2, 500)  # 从 0.1Hz 到 100Hz
    
    # 计算一阶高通滤波器幅值响应（归一化为分贝）
    H = f / np.sqrt(f**2 + fc**2)
    H_dB = 20 * np.log10(H)
    
    # 绘制图形
    fig, ax = plt.subplots(figsize=(10, 6))
    ax.semilogx(f, H_dB, label="幅值响应")  # 对数频率轴
    ax.set_title("一阶高通滤波器幅值响应")
    ax.set_xlabel("频率 (Hz)")
    ax.set_ylabel("幅值 (dB)")
    ax.grid(True, which="both", linestyle="--", linewidth=0.5)
    ax.legend()
    
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
show_code(plotting_demo)
