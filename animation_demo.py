import streamlit as st
import librosa
import numpy as np
from scipy.signal import butter, filtfilt
import soundfile as sf
from io import BytesIO
import base64

# 设置页面配置
st.set_page_config(
    page_title="音频高通滤波工具（无缝切换版）",
    page_icon="🎵",
    layout="centered",
    initial_sidebar_state="collapsed"
)

# 页面标题和说明
st.title("🎵 音频高通滤波工具（无缝切换版）")
st.markdown("""
支持WAV文件上传、**播放中实时无缝切换**滤波模式，无中断无迟滞。
""", unsafe_allow_html=True)

# ---------------------- 全局状态管理 ----------------------
if "current_time" not in st.session_state:
    st.session_state.current_time = 0.0  # 记录当前播放时间
if "audio_key" not in st.session_state:
    st.session_state.audio_key = 0  # 用于强制刷新音频组件
if "active_audio" not in st.session_state:
    st.session_state.active_audio = None  # 当前激活的音频数据

# ---------------------- 核心函数定义 ----------------------

@st.cache_data(show_spinner="正在预处理音频...")
def load_and_preprocess_audio(file_bytes):
    """
    加载音频并预计算所有滤波版本
    返回格式：{滤波类型: (音频数据, 采样率, 总时长)}
    """
    # 加载原始音频
    y, sr = librosa.load(BytesIO(file_bytes), sr=None, mono=False)  # 保留原始通道数
    duration = librosa.get_duration(y=y, sr=sr)
    
    # 存储所有处理后的音频
    processed_audio = {
        "无滤波": (y, sr, duration)
    }
    
    # 定义高通滤波函数（支持多通道）
    def butter_highpass(cutoff, fs, order=4):
        nyquist = 0.5 * fs
        normal_cutoff = cutoff / nyquist
        b, a = butter(order, normal_cutoff, btype='high', analog=False)
        return b, a
    
    def apply_highpass(y, cutoff, fs, order=4):
        b, a = butter_highpass(cutoff, fs, order=order)
        # 处理多通道音频
        if y.ndim == 2:
            filtered_y = np.array([filtfilt(b, a, channel) for channel in y])
        else:
            filtered_y = filtfilt(b, a, y)
        return filtered_y
    
    # 预计算各频率高通滤波
    for cutoff in [100, 200, 500]:
        filtered_y = apply_highpass(y, cutoff, sr)
        processed_audio[f"{cutoff}Hz高通滤波"] = (filtered_y, sr, duration)
    
    return processed_audio

def audio_to_bytes(y, sr):
    """将音频数据转换为可播放的字节流"""
    buffer = BytesIO()
    # 处理多通道数据（确保维度正确）
    if y.ndim == 2:
        y = y.T  # 转换为 (samples, channels) 格式
    sf.write(buffer, y, sr, format='WAV')
    buffer.seek(0)
    return buffer

def get_audio_segment(y, sr, start_time=0.0):
    """从指定时间点截取音频片段"""
    start_sample = int(start_time * sr)
    if start_sample < len(y):
        if y.ndim == 2:
            return y[:, start_sample:]  # 多通道：(channels, samples)
        else:
            return y[start_sample:]     # 单通道：(samples,)
    return y

# ---------------------- JavaScript 注入（监听播放进度） ----------------------
def inject_audio_listener():
    """注入JavaScript监听音频播放进度，更新session state"""
    js = """
    <script>
    // 等待页面加载完成
    document.addEventListener('DOMContentLoaded', function() {
        // 获取音频元素
        const audioElement = document.querySelector('audio');
        if (audioElement) {
            // 监听timeupdate事件（播放进度更新）
            audioElement.addEventListener('timeupdate', function() {
                const currentTime = this.currentTime;
                // 通过Streamlit的API更新session state
                window.parent.postMessage({
                    type: 'streamlit:setComponentValue',
                    value: currentTime,
                    key: 'current_audio_time'
                }, '*');
            });
            
            // 监听播放结束事件
            audioElement.addEventListener('ended', function() {
                window.parent.postMessage({
                    type: 'streamlit:setComponentValue',
                    value: 0.0,
                    key: 'current_audio_time'
                }, '*');
            });
        }
    });
    </script>
    """
    st.markdown(js, unsafe_allow_html=True)

# ---------------------- 界面布局 ----------------------

# 文件上传区域
uploaded_file = st.file_uploader("选择WAV音频文件", type=["wav"])

if uploaded_file is not None:
    # 读取文件字节（用于缓存）
    file_bytes = uploaded_file.getvalue()
    
    # 预计算所有滤波版本（使用缓存）
    processed_audio = load_and_preprocess_audio(file_bytes)
    y_original, sr, total_duration = processed_audio["无滤波"]
    
    # 显示音频信息
    st.info(f"""
    音频信息：
    - 采样率：{sr} Hz
    - 时长：{total_duration:.2f} 秒
    - 通道数：{y_original.shape[0] if y_original.ndim == 2 else 1}
    """)
    
    # 滤波模式选择（单选按钮）
    st.subheader("选择滤波模式")
    filter_option = st.radio(
        label="（播放中切换可无缝衔接）",
        options=["无滤波", "100Hz高通滤波", "200Hz高通滤波", "500Hz高通滤波"],
        index=0,
        horizontal=True  # 水平排列
    )
    
    # 注入JavaScript监听播放进度
    inject_audio_listener()
    
    # 接收JavaScript传递的当前播放时间
    current_time = st.session_state.get("current_time", 0.0)
    
    # 获取当前选择的音频数据，并从当前时间点截取
    y_filtered, sr, _ = processed_audio[filter_option]
    y_segment = get_audio_segment(y_filtered, sr, current_time)
    audio_bytes = audio_to_bytes(y_segment, sr)
    
    # 音频播放区域（使用动态key确保切换时刷新）
    st.subheader("播放音频")
    st.audio(
        audio_bytes,
        format="audio/wav",
        start_time=0,  # 片段从0开始（因为已经截取了前面的部分）
        key=f"audio_player_{st.session_state.audio_key}"
    )
    
    # 显示当前播放位置（增强用户体验）
    col1, col2, col3 = st.columns(3)
    with col2:
        st.progress(current_time / total_duration if total_duration > 0 else 0.0)
        st.markdown(f"""
        <div style="text-align: center; font-size: 14px;">
            当前位置：{current_time:.2f} / {total_duration:.2f} 秒
        </div>
        """, unsafe_allow_html=True)
    
    # 重置播放位置按钮
    if st.button("🔄 重置播放位置", type="secondary"):
        st.session_state.current_time = 0.0
        st.session_state.audio_key += 1  # 强制刷新播放器
        st.rerun()
    
    # 下载选项
    st.subheader("下载处理后音频")
    col1, col2 = st.columns(2)
    with col1:
        # 完整的滤波音频（不是片段）
        full_filtered_audio = audio_to_bytes(y_filtered, sr)
        st.download_button(
            label=f"下载{filter_option}音频",
            data=full_filtered_audio,
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
    
    # 监听滤波选项变化，更新播放器（保持播放位置）
    if st.session_state.get("last_filter_option") != filter_option:
        st.session_state.last_filter_option = filter_option
        st.session_state.audio_key += 1  # 强制刷新播放器
        # 不需要rerun，Streamlit会自动更新
    
else:
    # 未上传文件时的提示
    st.empty()
    with st.container():
        st.markdown("""
        <div style="text-align: center; padding: 50px; background-color: #f8f9fa; border-radius: 10px; margin-top: 50px;">
            <h3>👆 请上传WAV格式的音频文件</h3>
            <p style="color: #666; margin-top: 20px;">支持的格式：.wav</p>
        </div>
        """, unsafe_allow_html=True)

# ---------------------- 接收JavaScript的时间更新 ----------------------
# 使用隐藏的text_input接收JavaScript传递的值
current_audio_time = st.text_input(
    label="",
    value=str(st.session_state.current_time),
    key="current_audio_time",
    label_visibility="hidden"
)

# 更新session state中的当前时间
try:
    st.session_state.current_time = float(current_audio_time)
except:
    st.session_state.current_time = 0.0

# 页脚信息
st.markdown("""
---
<div style="text-align: center; color: #666; font-size: 12px;">
    音频无缝滤波工具 | 支持播放中实时切换 | 基于Streamlit + Librosa构建
</div>
""", unsafe_allow_html=True)
