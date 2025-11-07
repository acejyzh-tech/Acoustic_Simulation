import streamlit as st
import numpy as np
import scipy.signal as signal
import scipy.io.wavfile as wavfile
import io
import matplotlib.pyplot as plt

# 设置页面配置
st.set_page_config(page_title="音频滤波器", layout="centered")

# 缓存音频数据
@st.cache_data
def load_audio(file):
    # 使用 scipy 读取 WAV 文件
    sample_rate, samples = wavfile.read(file)
    
    # 处理多通道音频（仅保留单通道）
    if len(samples.shape) > 1:
        samples = samples[:, 0]  # 取第一个通道
    
    # 确保数据类型为 int16（16 位 PCM）
    samples = samples.astype(np.int16)
    
    return sample_rate, samples

# 缓存滤波器处理结果
@st.cache_data
def apply_filter(sample_rate, samples, cutoff):
    # 设计高通滤波器
    nyquist = 0.5 * sample_rate
    normal_cutoff = cutoff / nyquist
    b, a = signal.butter(4, normal_cutoff, btype='high', analog=False)
    
    # 应用滤波器
    filtered = signal.lfilter(b, a, samples)
    return filtered.astype(samples.dtype)

# 主程序
st.title("🎵 音频滤波处理工具")

# 文件上传
uploaded_file = st.file_uploader("请选择WAV音频文件", type=["wav"])

if uploaded_file:
    # 加载音频
    sample_rate, samples = load_audio(uploaded_file)
    
    # 显示音频信息
    st.sidebar.markdown("### 📁 音频信息")
    st.sidebar.write(f"采样率: {sample_rate} Hz")
    st.sidebar.write(f"时长: {len(samples)/sample_rate:.2f} 秒")
    
    # 滤波器选择
    filter_options = {
        "无滤波": 0,
        "100Hz高通": 100,
        "200Hz高通": 200,
        "500Hz高通": 500
    }
    
    selected_filter = st.sidebar.radio(
        "⚙️ 选择滤波器",
        list(filter_options.keys()),
        index=0
    )
    
    # 获取滤波器参数
    cutoff = filter_options[selected_filter]
    
    # 预计算滤波结果（缓存）
    if cutoff > 0:
        filtered_samples = apply_filter(sample_rate, samples, cutoff)
    else:
        filtered_samples = samples
    
    # 播放音频
    st.markdown("### 🎧 音频播放")
    # 将 numpy 数组转换为字节流
    audio_data = filtered_samples.tobytes()
    st.audio(audio_data, format='audio/wav', sample_rate=sample_rate)
    
    # 显示原始和处理后音频对比
    st.markdown("### 📊 音频对比")
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("原始音频")
        st.audio(samples.tobytes(), format='audio/wav', sample_rate=sample_rate)
    
    with col2:
        st.subheader("处理后音频")
        st.audio(audio_data, format='audio/wav', sample_rate=sample_rate)
    
    # 频谱分析（可选）
    if st.checkbox("📊 显示频谱分析"):
        st.markdown("### 📈 频谱图")
        import matplotlib.pyplot as plt
        from scipy.fft import fft
        
        n = len(samples)
        yf = fft(samples)
        xf = np.linspace(0, sample_rate, n)
        
        fig, ax = plt.subplots()
        ax.plot(xf[:n//2], 20 * np.log10(np.abs(yf[:n//2])))
        ax.set_xlabel('频率 (Hz)')
        ax.set_ylabel('幅度 (dB)')
        st.pyplot(fig)

else:
    st.info("请上传WAV音频文件以开始处理")
