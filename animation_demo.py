import streamlit as st
import numpy as np
import matplotlib.pyplot as plt
import librosa
import librosa.display
from scipy import signal
import soundfile as sf
from io import BytesIO
import base64
from functools import lru_cache

# 设置页面配置
st.set_page_config(
    page_title="🎵 音频分析与平滑滤波工具",
    page_icon="🎵",
    layout="wide",
    initial_sidebar_state="expanded"
)

# 全局配置
FILTER_PRESETS = {
    "无滤波": {"type": None, "order": 2, "cutoff": 0},
    "100Hz高通滤波": {"type": "highpass", "order": 2, "cutoff": 100},
    "200Hz高通滤波": {"type": "highpass", "order": 2, "cutoff": 200},
    "500Hz高通滤波": {"type": "highpass", "order": 2, "cutoff": 500}
}
FILTER_NAMES = list(FILTER_PRESETS.keys())

# 全局状态初始化
if 'initialized' not in st.session_state:
    st.session_state.initialized = False
    st.session_state.audio_data = None
    st.session_state.sr = None
    st.session_state.duration = 0.0
    st.session_state.play_position = 0.0
    st.session_state.selected_filter = FILTER_NAMES[0]
    # 预计算缓存
    st.session_state.filtered_audio_cache = {}
    st.session_state.audio_base64_cache = {}
    st.session_state.spectrogram_cache = {}
    st.session_state.filter_version = 0  # 用于触发音频组件更新

# ---------------------- 核心优化：缓存与预计算 ----------------------
@lru_cache(maxsize=4)
def cached_apply_filter(audio_data_tuple, sr, filter_type, filter_order, cutoff_freq):
    """
    带缓存的滤波函数，避免重复计算
    """
    audio_data = np.array(audio_data_tuple)
    if filter_type is None:
        return audio_data.astype(np.float32)
    
    # 归一化截止频率
    Wn = cutoff_freq / (sr / 2)
    if Wn <= 0 or Wn >= 1:
        return audio_data.astype(np.float32)
    
    # 2阶Butterworth滤波器（预设计算）
    b, a = signal.butter(filter_order, Wn, btype=filter_type, analog=False)
    filtered_data = signal.lfilter(b, a, audio_data)
    return filtered_data.astype(np.float32)

def precompute_all_filters(audio_data, sr):
    """
    预计算所有滤波模式的音频数据
    """
    audio_tuple = tuple(audio_data)  # 可哈希化用于缓存
    filtered_cache = {}
    
    with st.spinner("预处理所有滤波模式（确保平滑切换）..."):
        for filter_name, config in FILTER_PRESETS.items():
            filtered_audio = cached_apply_filter(
                audio_tuple,
                sr,
                config["type"],
                config["order"],
                config["cutoff"]
            )
            filtered_cache[filter_name] = filtered_audio
            
            # 预生成Base64编码
            buffer = BytesIO()
            sf.write(buffer, filtered_audio, sr, format='WAV')
            buffer.seek(0)
            b64 = base64.b64encode(buffer.read()).decode()
            st.session_state.audio_base64_cache[filter_name] = f"data:audio/wav;base64,{b64}"
    
    return filtered_cache

@lru_cache(maxsize=32)
def cached_spectrogram(audio_data_tuple, sr, play_position, filter_name):
    """
    缓存声谱图计算结果（添加filter_name作为缓存键）
    """
    audio_data = np.array(audio_data_tuple)
    fig, ax = plt.subplots(figsize=(14, 5))
    
    # 优化的STFT参数（平衡速度和精度）
    n_fft = 1024
    hop_length = 256
    D = librosa.amplitude_to_db(np.abs(librosa.stft(audio_data, n_fft=n_fft, hop_length=hop_length)), ref=np.max)
    
    # 绘制声谱图
    img = librosa.display.specshow(
        D, 
        sr=sr, 
        hop_length=hop_length,
        x_axis='time', 
        y_axis='hz', 
        ax=ax,
        fmin=20,
        fmax=sr/2,
        cmap='viridis'
    )
    fig.colorbar(img, ax=ax, format='%+2.0f dB', label='音量')
    
    # 播放进度线
    if play_position > 0:
        ax.axvline(
            x=play_position, 
            color='red', 
            linestyle='--', 
            linewidth=3, 
            alpha=0.9,
            label=f'进度: {play_position:.2f}s'
        )
        ax.legend(loc='upper right', fontsize=10)
    
    ax.set_title(f"{filter_name} - 声谱图", fontsize=16, fontweight='bold')
    ax.set_xlabel('时间 (s)', fontsize=12)
    ax.set_ylabel('频率 (Hz)', fontsize=12)
    ax.grid(True, alpha=0.3)
    plt.tight_layout()
    
    return fig

# ---------------------- 界面与逻辑 ----------------------
def render_audio_player(filter_name):
    """
    渲染音频播放器（修复key参数问题）
    """
    # 直接从缓存获取Base64编码
    audio_base64 = st.session_state.audio_base64_cache[filter_name]
    
    # 移除不支持的key参数，通过filter_version触发更新
    st.audio(
        audio_base64,
        format='audio/wav',
        start_time=st.session_state.play_position
    )

def render_spectrogram(filter_name):
    """
    渲染声谱图（从缓存获取）
    """
    audio_data = st.session_state.filtered_audio_cache[filter_name]
    audio_tuple = tuple(audio_data)
    
    # 从缓存获取或计算声谱图
    fig = cached_spectrogram(
        audio_tuple,
        st.session_state.sr,
        round(st.session_state.play_position, 1),  # 四舍五入减少缓存键数量
        filter_name  # 添加滤波名称作为缓存键
    )
    
    st.pyplot(fig, use_container_width=True)

# 主界面设计
st.title("🎵 音频分析与平滑滤波工具")
st.markdown("---")

# 侧边栏
with st.sidebar:
    st.header("📌 功能设置")
    
    # 1. 文件上传
    st.markdown("### 1. 上传音频文件")
    uploaded_file = st.file_uploader("支持WAV格式", type=['wav'])
    
    # 2. 平滑滤波切换（核心交互）
    st.markdown("### 2. 滤波模式切换")
    st.success("✅ 切换无延迟，实时生效")
    selected_filter = st.radio(
        "选择滤波模式",
        options=FILTER_NAMES,
        index=0,
        key="filter_radio",
        label_visibility="collapsed"  # 隐藏默认标签，使用自定义标题
    )

# 主功能区
col1, col2 = st.columns([1, 3])

with col1:
    st.markdown("### 🎧 播放控制")
    st.markdown("---")
    
    # 文件上传处理
    if uploaded_file is not None:
        try:
            # 首次上传时初始化
            if not st.session_state.initialized:
                # 读取音频文件
                audio_data, sr = librosa.load(uploaded_file, sr=None, mono=True)
                duration = librosa.get_duration(y=audio_data, sr=sr)
                
                # 保存基础数据
                st.session_state.audio_data = audio_data
                st.session_state.sr = sr
                st.session_state.duration = duration
                st.session_state.initialized = True
                
                # 预计算所有滤波和编码（关键优化）
                st.session_state.filtered_audio_cache = precompute_all_filters(audio_data, sr)
            
            # 显示文件信息
            st.info(f"采样率: {st.session_state.sr} Hz")
            st.info(f"时长: {st.session_state.duration:.2f} s")
            st.info(f"当前模式: {selected_filter}")
            
            # 播放进度条（核心控制）
            play_position = st.slider(
                "播放进度",
                min_value=0.0,
                max_value=st.session_state.duration,
                value=st.session_state.play_position,
                step=0.1,
                key="play_slider",
                format="%.1f s"
            )
            st.session_state.play_position = play_position
            
            # 实时更新选中的滤波模式（触发音频更新）
            if selected_filter != st.session_state.selected_filter:
                st.session_state.selected_filter = selected_filter
                st.session_state.filter_version += 1  # 递增版本号触发更新
            
            # 音频播放器（修复key参数问题）
            st.markdown("---")
            st.subheader(f"当前音频: {selected_filter}")
            # 使用空容器和版本号确保更新
            audio_container = st.container()
            with audio_container:
                render_audio_player(selected_filter)
            
            # 下载功能
            st.markdown("---")
            st.subheader("📥 下载")
            
            # 下载当前滤波音频
            current_audio_b64 = st.session_state.audio_base64_cache[selected_filter]
            filter_suffix = selected_filter.replace("Hz", "").replace("高通滤波", "").replace("无", "no").strip()
            st.download_button(
                label=f"下载{selected_filter}",
                data=base64.b64decode(current_audio_b64.split(",")[1]),  # 正确解码Base64数据
                file_name=f"filtered_{filter_suffix}.wav",
                mime="audio/wav",
                key=f"download_{selected_filter}"
            )
            
            # 下载原始音频
            original_b64 = st.session_state.audio_base64_cache["无滤波"]
            st.download_button(
                label="下载原始音频",
                data=base64.b64decode(original_b64.split(",")[1]),
                file_name="original_audio.wav",
                mime="audio/wav",
                key="download_original"
            )
            
            # 滤波效果说明
            st.markdown("---")
            st.subheader("ℹ️ 效果说明")
            filter_descriptions = {
                "无滤波": "保留所有频率成分，原始音频效果",
                "100Hz高通滤波": "过滤100Hz以下低频噪声（如电流声、隆隆声）",
                "200Hz高通滤波": "适合语音信号去噪，保留主要语音频率",
                "500Hz高通滤波": "突出高频细节，过滤更多低频成分"
            }
            st.info(filter_descriptions[selected_filter])
        
        except Exception as e:
            st.error(f"处理失败: {str(e)}")
            st.exception(e)
            st.session_state.initialized = False  # 重置状态
    else:
        # 未上传文件时的提示
        st.markdown("""
            <div style="text-align: center; padding: 30px; background-color: #f8f9fa; border-radius: 8px; margin-top: 50px;">
                <h4>📤 请上传WAV文件</h4>
                <p style="color: #666; margin-top: 10px;">上传后自动预处理所有滤波模式</p>
            </div>
        """, unsafe_allow_html=True)

with col2:
    st.markdown("### 📊 实时声谱图")
    st.markdown("---")
    
    # 显示声谱图（无延迟更新）
    if st.session_state.initialized:
        # 直接从缓存渲染声谱图
        render_spectrogram(st.session_state.selected_filter)
    else:
        # 未上传文件时的占位图
        st.markdown("""
            <div style="text-align: center; padding: 100px; background-color: #f8f9fa; border-radius: 8px; height: 400px; display: flex; align-items: center; justify-content: center;">
                <h3>🎵 上传文件后显示声谱图</h3>
            </div>
        """, unsafe_allow_html=True)

# 页脚信息
st.markdown("---")
st.markdown("""
    <div style="text-align: center; color: #666;">
        <p>⚡ 平滑切换技术 | 预计算优化 | 无延迟交互</p>
        <p>支持: 无滤波/100Hz/200Hz/500Hz高通滤波 | 实时声谱图更新</p>
    </div>
""", unsafe_allow_html=True)
