import streamlit as st
import numpy as np
import matplotlib.pyplot as plt
import librosa
import librosa.display
from scipy import signal
import soundfile as sf
from io import BytesIO, StringIO
import base64

# 设置页面配置
st.set_page_config(
    page_title="音频分析工具",
    page_icon="🎵",
    layout="wide",
    initial_sidebar_state="expanded"
)

# 全局变量初始化
if 'audio_data' not in st.session_state:
    st.session_state.audio_data = None
if 'sr' not in st.session_state:
    st.session_state.sr = None
if 'filtered_audio' not in st.session_state:
    st.session_state.filtered_audio = None
if 'play_position' not in st.session_state:
    st.session_state.play_position = 0
if 'is_playing' not in st.session_state:
    st.session_state.is_playing = False

# 定义滤波器函数
def apply_filter(audio_data, sr, filter_type, order, cutoff_freq):
    """
    应用数字滤波器
    :param audio_data: 原始音频数据
    :param sr: 采样率
    :param filter_type: 滤波器类型 ('highpass' 或 'lowpass')
    :param order: 滤波器阶数 (1 或 2)
    :param cutoff_freq: 截止频率 (Hz)
    :return: 滤波后的音频数据
    """
    # 计算归一化截止频率 (0 < Wn < 1)
    Wn = cutoff_freq / (sr / 2)
    if Wn <= 0 or Wn >= 1:
        st.warning("截止频率应在 (0, 采样率/2) 范围内！")
        return audio_data
    
    # 设计滤波器
    if order == 1:
        b, a = signal.butter(order, Wn, btype=filter_type, analog=False)
    elif order == 2:
        b, a = signal.butter(order, Wn, btype=filter_type, analog=False)
    else:
        st.warning("仅支持1阶和2阶滤波器！")
        return audio_data
    
    # 应用滤波器
    filtered_data = signal.lfilter(b, a, audio_data)
    return filtered_data.astype(np.float32)

# 音频转Base64（用于Streamlit播放）
def audio_to_base64(audio_data, sr):
    buffer = BytesIO()
    sf.write(buffer, audio_data, sr, format='WAV')
    buffer.seek(0)
    b64 = base64.b64encode(buffer.read()).decode()
    return f"data:audio/wav;base64,{b64}"

# 绘制声谱图
def plot_spectrogram(audio_data, sr, title, play_position=0):
    fig, ax = plt.subplots(figsize=(12, 4))
    
    # 计算声谱图
    D = librosa.amplitude_to_db(np.abs(librosa.stft(audio_data)), ref=np.max)
    
    # 绘制声谱图
    img = librosa.display.specshow(D, sr=sr, x_axis='time', y_axis='hz', ax=ax)
    fig.colorbar(img, ax=ax, format='%+2.0f dB')
    
    # 添加播放进度线
    if play_position > 0:
        ax.axvline(x=play_position, color='red', linestyle='--', linewidth=2, label=f'当前进度: {play_position:.2f}s')
        ax.legend(loc='upper right')
    
    ax.set_title(title, fontsize=14)
    ax.set_xlabel('时间 (s)', fontsize=12)
    ax.set_ylabel('频率 (Hz)', fontsize=12)
    plt.tight_layout()
    
    return fig

# 主界面设计
st.title("🎵 音频分析与滤波工具")
st.markdown("---")

# 侧边栏设置
with st.sidebar:
    st.header("参数设置")
    st.markdown("### 1. 上传音频文件")
    uploaded_file = st.file_uploader("支持WAV格式", type=['wav'])
    
    st.markdown("### 2. 滤波设置")
    filter_enabled = st.checkbox("启用滤波处理")
    if filter_enabled:
        filter_type = st.selectbox("滤波器类型", ['高通滤波', '低通滤波'])
        filter_order = st.selectbox("滤波器阶数", [1, 2])
        cutoff_freq = st.number_input("截止频率 (Hz)", min_value=10, max_value=10000, value=1000, step=100)
    else:
        filter_type = None
        filter_order = 1
        cutoff_freq = 1000

# 主功能区
col1, col2 = st.columns(2)

# 处理上传文件
if uploaded_file is not None:
    # 读取音频文件
    try:
        audio_data, sr = librosa.load(uploaded_file, sr=None, mono=True)
        st.session_state.audio_data = audio_data
        st.session_state.sr = sr
        
        # 计算音频时长
        duration = librosa.get_duration(y=audio_data, sr=sr)
        
        st.success(f"文件上传成功！")
        st.info(f"采样率: {sr} Hz | 时长: {duration:.2f} s | 数据长度: {len(audio_data)} 样本")
        
        # 滤波处理
        if filter_enabled:
            with st.spinner("正在应用滤波处理..."):
                filter_type_en = 'highpass' if filter_type == '高通滤波' else 'lowpass'
                filtered_audio = apply_filter(audio_data, sr, filter_type_en, filter_order, cutoff_freq)
                st.session_state.filtered_audio = filtered_audio
        else:
            st.session_state.filtered_audio = None
        
    except Exception as e:
        st.error(f"文件读取失败: {str(e)}")
else:
    st.info("请在左侧边栏上传WAV格式的音频文件")

# 显示原始音频分析
if st.session_state.audio_data is not None:
    st.markdown("---")
    st.header("原始音频分析")
    
    # 原始音频播放控制
    col1, col2, col3 = st.columns([3, 1, 1])
    with col1:
        st.subheader("音频播放")
    with col2:
        play_btn = st.button("▶️ 播放")
    with col3:
        pause_btn = st.button("⏸️ 暂停")
    
    # 播放进度条
    duration = librosa.get_duration(y=st.session_state.audio_data, sr=st.session_state.sr)
    play_position = st.slider("播放进度", min_value=0.0, max_value=duration, value=0.0, step=0.1, key="original_slider")
    st.session_state.play_position = play_position
    
    # 音频播放
    audio_base64 = audio_to_base64(st.session_state.audio_data, st.session_state.sr)
    st.audio(audio_base64, format='audio/wav')
    
    # 绘制原始声谱图
    st.subheader("原始音频声谱图")
    fig_original = plot_spectrogram(
        st.session_state.audio_data, 
        st.session_state.sr, 
        "原始音频声谱图",
        play_position=play_position
    )
    st.pyplot(fig_original)

# 显示滤波后音频分析
if st.session_state.filtered_audio is not None and filter_enabled:
    st.markdown("---")
    st.header("滤波后音频分析")
    
    # 滤波参数显示
    st.subheader(f"滤波参数: {filter_type} (第{filter_order}阶) | 截止频率: {cutoff_freq} Hz")
    
    # 滤波后音频播放控制
    col1, col2, col3 = st.columns([3, 1, 1])
    with col1:
        st.subheader("音频播放")
    with col2:
        play_filtered_btn = st.button("▶️ 播放滤波后", key="filtered_play")
    with col3:
        pause_filtered_btn = st.button("⏸️ 暂停滤波后", key="filtered_pause")
    
    # 滤波后播放进度条
    filtered_duration = librosa.get_duration(y=st.session_state.filtered_audio, sr=st.session_state.sr)
    filtered_play_position = st.slider("播放进度", min_value=0.0, max_value=filtered_duration, value=0.0, step=0.1, key="filtered_slider")
    
    # 滤波后音频播放
    filtered_audio_base64 = audio_to_base64(st.session_state.filtered_audio, st.session_state.sr)
    st.audio(filtered_audio_base64, format='audio/wav')
    
    # 绘制滤波后声谱图
    st.subheader("滤波后音频声谱图")
    fig_filtered = plot_spectrogram(
        st.session_state.filtered_audio, 
        st.session_state.sr, 
        f"{filter_type} (第{filter_order}阶, {cutoff_freq} Hz) 后声谱图",
        play_position=filtered_play_position
    )
    st.pyplot(fig_filtered)

# 下载功能
if st.session_state.filtered_audio is not None and filter_enabled:
    st.markdown("---")
    st.header("文件下载")
    
    # 生成下载文件
    filtered_buffer = BytesIO()
    sf.write(filtered_buffer, st.session_state.filtered_audio, st.session_state.sr, format='WAV')
    filtered_buffer.seek(0)
    
    st.download_button(
        label="下载滤波后音频",
        data=filtered_buffer,
        file_name=f"filtered_{filter_type}_{filter_order}阶_{cutoff_freq}Hz.wav",
        mime="audio/wav"
    )

# 页脚信息
st.markdown("---")
st.markdown("""
    <div style="text-align: center; color: #666;">
        <p>🎯 音频分析与滤波工具 | 支持WAV文件 | 声谱图可视化 | 数字滤波处理</p>
        <p>技术支持: librosa, scipy, streamlit, matplotlib</p>
    </div>
""", unsafe_allow_html=True)
