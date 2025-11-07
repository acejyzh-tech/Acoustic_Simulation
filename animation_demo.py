import streamlit as st
import numpy as np
import scipy.signal as signal
from scipy.io import wavfile
import io

# 设置页面标题
st.title("音频滤波处理工具")

# 上传音频文件
uploaded_file = st.file_uploader("上传WAV音频文件", type=["wav"])

# 频率选择器
filter_options = {
    "无滤波": None,
    "100Hz高通": 100,
    "200Hz高通": 200,
    "500Hz高通": 500
}
selected_filter = st.selectbox("选择滤波器", list(filter_options.keys()))

# 缓存音频数据
@st.cache_data
def load_audio(file):
    # 读取WAV文件
    sample_rate, data = wavfile.read(file)
    
    # 转换为单声道
    if len(data.shape) > 1:
        data = data[:, 0]
    
    # 标准化音频数据
    data = data / np.max(np.abs(data))
    return sample_rate, data

# 滤波处理函数
def apply_filter(sample_rate, data, cutoff):
    if cutoff is None:
        return data
    
    # 设计Butterworth高通滤波器
    nyquist = 0.5 * sample_rate
    normal_cutoff = cutoff / nyquist
    b, a = signal.butter(4, normal_cutoff, btype='high', analog=False)
    
    # 应用滤波器
    filtered = signal.lfilter(b, a, data)
    return filtered

# 主程序逻辑
if uploaded_file is not None:
    # 加载音频数据
    sample_rate, audio_data = load_audio(uploaded_file)
    
    # 缓存处理后的音频数据
    @st.cache_data
    def get_processed_audio(cutoff):
        return apply_filter(sample_rate, audio_data, cutoff)
    
    # 获取处理后的音频
    processed_audio = get_processed_audio(filter_options[selected_filter])
    
    # 显示原始音频
    st.subheader("原始音频")
    st.audio(uploaded_file, format='audio/wav')
    
    # 显示处理后音频
    st.subheader("处理后音频")
    st.audio(io.BytesIO(wavfile.write(io.BytesIO(), sample_rate, (processed_audio * 32767).astype(np.int16))), format='audio/wav')
    
    # 显示音频信息
    st.sidebar.markdown("### 音频信息")
    st.sidebar.write(f"采样率: {sample_rate} Hz")
    st.sidebar.write(f"时长: {len(audio_data)/sample_rate:.2f} 秒")
    st.sidebar.write(f"通道数: {1 if len(audio_data.shape) == 1 else audio_data.shape[1]}")
    
else:
    st.info("请上传WAV音频文件以开始处理")
