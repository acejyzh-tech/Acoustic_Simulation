import streamlit as st
import numpy as np
import matplotlib.pyplot as plt
import librosa
import librosa.display
from scipy import signal
import soundfile as sf
from io import BytesIO
import base64

# 设置页面配置
st.set_page_config(
    page_title="音频分析与实时滤波工具",
    page_icon="🎵",
    layout="wide",
    initial_sidebar_state="expanded"
)

# 全局变量初始化
if 'audio_data' not in st.session_state:
    st.session_state.audio_data = None
if 'sr' not in st.session_state:
    st.session_state.sr = None
if 'current_filtered_audio' not in st.session_state:
    st.session_state.current_filtered_audio = None
if 'play_position' not in st.session_state:
    st.session_state.play_position = 0
if 'selected_filter' not in st.session_state:
    st.session_state.selected_filter = "无滤波"
if 'filter_params' not in st.session_state:
    # 定义预设滤波参数
    st.session_state.filter_params = {
        "无滤波": {"type": None, "order": 2, "cutoff": 0},
        "100Hz高通滤波": {"type": "highpass", "order": 2, "cutoff": 100},
        "200Hz高通滤波": {"type": "highpass", "order": 2, "cutoff": 200},
        "500Hz高通滤波": {"type": "highpass", "order": 2, "cutoff": 500}
    }

# 定义滤波器函数
def apply_filter(audio_data, sr, filter_config):
    """
    应用指定的滤波器
    :param audio_data: 原始音频数据
    :param sr: 采样率
    :param filter_config: 滤波配置字典
    :return: 处理后的音频数据
    """
    if filter_config["type"] is None:  # 无滤波
        return audio_data.astype(np.float32)
    
    # 计算归一化截止频率 (0 < Wn < 1)
    Wn = filter_config["cutoff"] / (sr / 2)
    if Wn <= 0 or Wn >= 1:
        st.warning(f"截止频率 {filter_config['cutoff']}Hz 超出有效范围，将使用无滤波")
        return audio_data.astype(np.float32)
    
    # 设计2阶Butterworth滤波器
    b, a = signal.butter(
        filter_config["order"], 
        Wn, 
        btype=filter_config["type"], 
        analog=False
    )
    
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

# 绘制声谱图（支持实时更新）
def plot_spectrogram(audio_data, sr, title, play_position=0):
    fig, ax = plt.subplots(figsize=(14, 5))
    
    # 计算声谱图（使用更精细的参数）
    n_fft = 2048
    hop_length = 512
    D = librosa.amplitude_to_db(np.abs(librosa.stft(audio_data, n_fft=n_fft, hop_length=hop_length)), ref=np.max)
    
    # 绘制声谱图
    img = librosa.display.specshow(
        D, 
        sr=sr, 
        hop_length=hop_length,
        x_axis='time', 
        y_axis='hz', 
        ax=ax,
        fmin=20,  # 最小显示频率
        fmax=sr/2  # 最大显示频率
    )
    fig.colorbar(img, ax=ax, format='%+2.0f dB', label='音量')
    
    # 添加播放进度线（实时更新）
    if play_position > 0:
        ax.axvline(
            x=play_position, 
            color='red', 
            linestyle='--', 
            linewidth=3, 
            alpha=0.8,
            label=f'当前进度: {play_position:.2f}s'
        )
        ax.legend(loc='upper right', fontsize=10)
    
    ax.set_title(title, fontsize=16, fontweight='bold')
    ax.set_xlabel('时间 (s)', fontsize=12)
    ax.set_ylabel('频率 (Hz)', fontsize=12)
    ax.grid(True, alpha=0.3)
    plt.tight_layout()
    
    return fig

# 主界面设计
st.title("🎵 音频分析与实时滤波工具")
st.markdown("---")

# 侧边栏设置
with st.sidebar:
    st.header("📌 功能设置")
    st.markdown("### 1. 上传音频文件")
    uploaded_file = st.file_uploader("支持WAV格式", type=['wav'])
    
    st.markdown("### 2. 实时滤波切换")
    st.info("选择滤波模式后实时生效，无需重新加载")
    # 单选按钮组 - 实时切换滤波模式
    selected_filter = st.radio(
        "选择滤波模式",
        options=["无滤波", "100Hz高通滤波", "200Hz高通滤波", "500Hz高通滤波"],
        index=0,
        key="filter_radio"
    )
    
    # 保存当前选中的滤波模式
    if selected_filter != st.session_state.selected_filter:
        st.session_state.selected_filter = selected_filter
        # 标记需要更新滤波
        st.session_state.update_filter = True

# 主功能区
st.markdown("### 🎧 音频播放与可视化")
st.markdown("---")

# 处理上传文件
if uploaded_file is not None:
    # 读取音频文件
    try:
        audio_data, sr = librosa.load(uploaded_file, sr=None, mono=True)
        st.session_state.audio_data = audio_data
        st.session_state.sr = sr
        
        # 计算音频时长
        duration = librosa.get_duration(y=audio_data, sr=sr)
        
        # 显示文件信息
        col1, col2, col3, col4 = st.columns(4)
        with col1:
            st.success("✅ 文件上传成功")
        with col2:
            st.info(f"采样率: {sr} Hz")
        with col3:
            st.info(f"时长: {duration:.2f} s")
        with col4:
            st.info(f"当前模式: {selected_filter}")
        
        # 实时应用滤波
        filter_config = st.session_state.filter_params[selected_filter]
        with st.spinner(f"正在应用 {selected_filter}..."):
            current_audio = apply_filter(audio_data, sr, filter_config)
            st.session_state.current_filtered_audio = current_audio
        
        # 音频播放控制区
        st.markdown("---")
        st.subheader("🎚️ 播放控制")
        
        # 播放进度条（支持拖拽定位）
        play_position = st.slider(
            "播放进度",
            min_value=0.0,
            max_value=duration,
            value=st.session_state.play_position,
            step=0.1,
            key="play_slider",
            format="%.1f s"
        )
        st.session_state.play_position = play_position
        
        # 播放按钮和音频组件
        col_play, col_download = st.columns([1, 8])
        with col_play:
            st.markdown("### 播放:")
        with col_download:
            # 生成当前音频的Base64编码（实时更新）
            current_audio_base64 = audio_to_base64(current_audio, sr)
            st.audio(current_audio_base64, format='audio/wav', start_time=play_position)
        
        # 下载当前音频（根据选中的滤波模式）
        st.markdown("---")
        col_download1, col_download2 = st.columns(2)
        with col_download1:
            # 原始音频下载
            original_audio_base64 = audio_to_base64(audio_data, sr)
            st.download_button(
                label="📥 下载原始音频",
                data=original_audio_base64,
                file_name="original_audio.wav",
                mime="audio/wav"
            )
        with col_download2:
            # 当前滤波音频下载
            filter_suffix = selected_filter.replace("Hz", "").replace("高通滤波", "").replace("无", "no").strip()
            download_filename = f"filtered_audio_{filter_suffix}.wav"
            st.download_button(
                label=f"📥 下载{selected_filter}音频",
                data=current_audio_base64,
                file_name=download_filename,
                mime="audio/wav"
            )
        
        # 声谱图显示区
        st.markdown("---")
        st.subheader("📊 实时声谱图")
        
        # 绘制当前音频的声谱图（带进度指示）
        fig = plot_spectrogram(
            current_audio,
            sr,
            title=f"{selected_filter} - 声谱图",
            play_position=play_position
        )
        st.pyplot(fig, use_container_width=True)
        
        # 滤波效果说明
        st.markdown("---")
        st.subheader("ℹ️ 滤波效果说明")
        filter_descriptions = {
            "无滤波": "保留所有频率成分，原始音频效果",
            "100Hz高通滤波": "过滤掉100Hz以下的低频噪声（如电流声、隆隆声）",
            "200Hz高通滤波": "过滤掉200Hz以下的低频成分，适合语音信号去噪",
            "500Hz高通滤波": "过滤掉500Hz以下的低频成分，突出高频细节"
        }
        st.info(filter_descriptions[selected_filter])
        
    except Exception as e:
        st.error(f"文件处理失败: {str(e)}")
        st.exception(e)
else:
    # 未上传文件时的提示
    st.markdown("""
        <div style="text-align: center; padding: 50px; background-color: #f8f9fa; border-radius: 10px;">
            <h3>📤 请先上传WAV格式音频文件</h3>
            <p style="color: #666; margin-top: 20px;">支持各种采样率的WAV文件，上传后即可实时切换滤波模式</p>
        </div>
    """, unsafe_allow_html=True)

# 页脚信息
st.markdown("---")
st.markdown("""
    <div style="text-align: center; color: #666; margin-top: 20px;">
        <p>🎯 实时滤波功能 | 支持无滤波/100Hz/200Hz/500Hz高通滤波 | 声谱图实时更新</p>
        <p>技术支持: librosa, scipy, streamlit, matplotlib | 设计优化: 实时切换无刷新</p>
    </div>
""", unsafe_allow_html=True)
