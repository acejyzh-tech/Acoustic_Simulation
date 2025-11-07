import streamlit as st
import librosa
import librosa.display
import numpy as np
from scipy.signal import butter, filtfilt
import soundfile as sf
from io import BytesIO

# 设置页面配置
st.set_page_config(
    page_title="音频高通滤波工具",
    page_icon="🎵",
    layout="centered",
    initial_sidebar_state="collapsed"
)

# 页面标题和说明
st.title("🎵 音频高通滤波处理工具")
st.markdown("""
支持WAV文件上传、播放和多种高通滤波处理，切换滤波模式无迟滞。
""", unsafe_allow_html=True)

# ---------------------- 核心函数定义 ----------------------

@st.cache_data(show_spinner="正在预处理音频...")
def load_and_preprocess_audio(file_bytes):
    """
    加载音频并预计算所有滤波版本
    返回格式：{滤波类型: (音频数据, 采样率)}
    """
    # 加载原始音频
    y, sr = librosa.load(BytesIO(file_bytes), sr=None)
    
    # 存储所有处理后的音频
    processed_audio = {
        "无滤波": (y, sr)
    }
    
    # 定义高通滤波函数
    def butter_highpass(cutoff, fs, order=4):
        nyquist = 0.5 * fs
        normal_cutoff = cutoff / nyquist
        b, a = butter(order, normal_cutoff, btype='high', analog=False)
        return b, a
    
    def apply_highpass(y, cutoff, fs, order=4):
        b, a = butter_highpass(cutoff, fs, order=order)
        filtered_y = filtfilt(b, a, y)  # 零相位滤波，避免失真
        return filtered_y
    
    # 预计算各频率高通滤波
    for cutoff in [100, 200, 500]:
        filtered_y = apply_highpass(y, cutoff, sr)
        processed_audio[f"{cutoff}Hz高通滤波"] = (filtered_y, sr)
    
    return processed_audio

def audio_to_bytes(y, sr):
    """将音频数据转换为可播放的字节流"""
    buffer = BytesIO()
    sf.write(buffer, y, sr, format='WAV')
    buffer.seek(0)
    return buffer

# ---------------------- 界面布局 ----------------------

# 文件上传区域
uploaded_file = st.file_uploader("选择WAV音频文件", type=["wav"])

if uploaded_file is not None:
    # 读取文件字节（用于缓存）
    file_bytes = uploaded_file.getvalue()
    
    # 预计算所有滤波版本（使用缓存）
    processed_audio = load_and_preprocess_audio(file_bytes)
    
    # 显示音频信息
    y_original, sr = processed_audio["无滤波"]
    duration = librosa.get_duration(y=y_original, sr=sr)
    st.info(f"""
    音频信息：
    - 采样率：{sr} Hz
    - 时长：{duration:.2f} 秒
    - 通道数：{1 if y_original.ndim == 1 else y_original.shape[1]}
    """)
    
    # 滤波模式选择（单选按钮）
    st.subheader("选择滤波模式")
    filter_option = st.radio(
        label="",
        options=["无滤波", "100Hz高通滤波", "200Hz高通滤波", "500Hz高通滤波"],
        index=0,
        horizontal=True  # 水平排列，更简洁
    )
    
    # 获取当前选择的音频数据
    y_filtered, sr = processed_audio[filter_option]
    
    # 音频播放区域
    st.subheader("播放音频")
    audio_bytes = audio_to_bytes(y_filtered, sr)
    st.audio(audio_bytes, format="audio/wav", start_time=0)
    
    # 下载选项
    st.subheader("下载处理后音频")
    col1, col2 = st.columns(2)
    with col1:
        st.download_button(
            label=f"下载{filter_option}音频",
            data=audio_bytes,
            file_name=f"{uploaded_file.name[:-4]}_{filter_option.replace(' ', '_')}.wav",
            mime="audio/wav"
        )
    with col2:
        # 原始音频下载
        original_audio_bytes = audio_to_bytes(y_original, sr)
        st.download_button(
            label="下载原始音频",
            data=original_audio_bytes,
            file_name=f"{uploaded_file.name[:-4]}_原始音频.wav",
            mime="audio/wav"
        )

else:
    # 未上传文件时的提示
    st.empty()  # 清空占位
    with st.container():
        st.markdown("""
        <div style="text-align: center; padding: 50px; background-color: #f8f9fa; border-radius: 10px; margin-top: 50px;">
            <h3>👆 请上传WAV格式的音频文件</h3>
            <p style="color: #666; margin-top: 20px;">支持的格式：.wav</p>
        </div>
        """, unsafe_allow_html=True)

# 页脚信息
st.markdown("""
---
<div style="text-align: center; color: #666; font-size: 12px;">
    音频处理工具 | 基于Streamlit + Librosa构建 | 高通滤波采用4阶巴特沃斯滤波器
</div>
""", unsafe_allow_html=True)
