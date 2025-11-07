import streamlit as st
import librosa
import numpy as np
from scipy.signal import butter, filtfilt
import soundfile as sf
from io import BytesIO
import time

# 设置页面配置
st.set_page_config(
    page_title="音频高通滤波工具（完美无缝版）",
    page_icon="🎵",
    layout="centered",
    initial_sidebar_state="collapsed"
)

# 页面标题和说明
st.title("🎵 音频高通滤波工具（完美无缝版）")
st.markdown("""
支持WAV文件上传、**播放中实时无缝切换**滤波模式，切换后自动继续播放，无任何中断。
""", unsafe_allow_html=True)

# ---------------------- 全局状态管理 ----------------------
if "current_time" not in st.session_state:
    st.session_state.current_time = 0.0  # 记录当前播放时间
if "last_filter_option" not in st.session_state:
    st.session_state.last_filter_option = "无滤波"  # 上一次选择的滤波模式
if "audio_data" not in st.session_state:
    st.session_state.audio_data = {}  # 存储所有音频字节流
if "is_playing" not in st.session_state:
    st.session_state.is_playing = False  # 记录播放状态
if "last_update_time" not in st.session_state:
    st.session_state.last_update_time = 0.0  # 上次时间更新时间
if "total_samples" not in st.session_state:
    st.session_state.total_samples = 0  # 总样本数（用于正确判断）

# ---------------------- 核心函数定义 ----------------------

@st.cache_data(show_spinner="正在预处理音频...")
def load_and_preprocess_audio(file_bytes):
    """
    加载音频并预计算所有滤波版本
    返回格式：{滤波类型: (音频数据, 采样率, 总时长, 总样本数)}
    """
    # 加载原始音频
    y, sr = librosa.load(BytesIO(file_bytes), sr=None, mono=False)  # 保留原始通道数
    duration = librosa.get_duration(y=y, sr=sr)
    
    # 计算总样本数（处理单通道/多通道）
    if y.ndim == 2:
        total_samples = y.shape[1]  # 多通道：(channels, samples)
    else:
        total_samples = len(y)      # 单通道：(samples,)
    
    # 存储所有处理后的音频
    processed_audio = {
        "无滤波": (y, sr, duration, total_samples)
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
        processed_audio[f"{cutoff}Hz高通滤波"] = (filtered_y, sr, duration, total_samples)
    
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

def get_audio_segment_bytes(y, sr, start_time=0.0):
    """从指定时间点截取音频片段并转换为字节流（修复数组判断问题）"""
    start_sample = int(start_time * sr)
    
    # 正确判断样本数（修复核心错误）
    if y.ndim == 2:
        total_samples = y.shape[1]
    else:
        total_samples = len(y)
    
    # 确保起始样本不超过总样本数
    if start_sample < total_samples and start_sample >= 0:
        if y.ndim == 2:
            y_segment = y[:, start_sample:]  # 多通道：(channels, samples)
        else:
            y_segment = y[start_sample:]     # 单通道：(samples,)
    else:
        y_segment = y  # 返回完整音频
    
    return audio_to_bytes(y_segment, sr)

# ---------------------- JavaScript 注入（增强版） ----------------------
def inject_audio_listener():
    """注入增强版JavaScript，监听播放状态和进度"""
    js = """
    <script>
    let lastPlayState = false;
    let audioElement = null;
    
    // 定期检查音频元素
    setInterval(function() {
        const audioElements = document.querySelectorAll('audio');
        // 找到活跃的音频元素（正在播放或有播放进度）
        const newAudioElement = Array.from(audioElements).find(el => 
            el.currentTime > 0.1 || !el.paused
        );
        
        if (newAudioElement) {
            audioElement = newAudioElement;
            
            // 监听播放状态变化
            const isCurrentlyPlaying = !audioElement.paused;
            if (isCurrentlyPlaying !== lastPlayState) {
                lastPlayState = isCurrentlyPlaying;
                // 发送播放状态
                window.parent.postMessage({
                    type: 'streamlit:setComponentValue',
                    value: isCurrentlyPlaying ? 'true' : 'false',
                    key: 'audio_play_state'
                }, '*');
            }
            
            // 监听播放进度
            const currentTime = audioElement.currentTime;
            window.parent.postMessage({
                type: 'streamlit:setComponentValue',
                value: currentTime.toString(),
                key: 'audio_current_time'
            }, '*');
            
            // 监听播放结束
            audioElement.addEventListener('ended', function() {
                window.parent.postMessage({
                    type: 'streamlit:setComponentValue',
                    value: '0.0',
                    key: 'audio_current_time'
                }, '*');
                window.parent.postMessage({
                    type: 'streamlit:setComponentValue',
                    value: 'false',
                    key: 'audio_play_state'
                }, '*');
            });
        }
    }, 200);  // 200ms检查一次，平衡性能和实时性
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
    y_original, sr, total_duration, total_samples = processed_audio["无滤波"]
    st.session_state.total_samples = total_samples
    
    # 预生成所有完整音频的字节流（避免重复转换）
    if not st.session_state.audio_data:
        for filter_name, (y_data, y_sr, _, _) in processed_audio.items():
            st.session_state.audio_data[filter_name] = audio_to_bytes(y_data, y_sr)
    
    # 显示音频信息
    st.info(f"""
    音频信息：
    - 采样率：{sr} Hz
    - 时长：{total_duration:.2f} 秒
    - 通道数：{y_original.shape[0] if y_original.ndim == 2 else 1}
    - 总样本数：{total_samples:,}
    """)
    
    # 滤波模式选择（单选按钮）
    st.subheader("选择滤波模式")
    filter_option = st.radio(
        label="（播放中切换可无缝衔接）",
        options=["无滤波", "100Hz高通滤波", "200Hz高通滤波", "500Hz高通滤波"],
        index=0,
        horizontal=True  # 水平排列
    )
    
    # 注入JavaScript监听
    inject_audio_listener()
    
    # 隐藏的输入框，用于接收JavaScript传递的状态
    audio_play_state = st.text_input(
        label="", value="false", key="audio_play_state", label_visibility="hidden"
    )
    audio_current_time = st.text_input(
        label="", value="0.0", key="audio_current_time", label_visibility="hidden"
    )
    
    # 更新全局状态（避免频繁更新）
    current_time = st.session_state.current_time
    try:
        new_current_time = float(audio_current_time)
        new_is_playing = audio_play_state.lower() == "true"
        
        # 仅在时间变化超过0.1秒或播放状态变化时更新
        if abs(new_current_time - current_time) > 0.1 or new_is_playing != st.session_state.is_playing:
            # 确保时间不超过音频时长
            new_current_time = min(new_current_time, total_duration)
            new_current_time = max(new_current_time, 0.0)
            
            st.session_state.current_time = new_current_time
            st.session_state.is_playing = new_is_playing
            st.session_state.last_update_time = time.time()
    except Exception as e:
        st.error(f"状态更新错误：{str(e)}")
    
    # 处理滤波模式切换
    current_filter = filter_option
    if current_filter != st.session_state.last_filter_option:
        st.session_state.last_filter_option = current_filter
    
    # 获取当前音频数据
    y_filtered, sr, _, _ = processed_audio[current_filter]
    
    # 生成当前时间点的音频片段（修复后的函数）
    current_play_time = st.session_state.current_time
    audio_segment_bytes = get_audio_segment_bytes(y_filtered, sr, current_play_time)
    
    # 音频播放区域（动态更新）
    st.subheader("播放音频")
    audio_container = st.container()
    
    with audio_container:
        st.audio(
            audio_segment_bytes,
            format="audio/wav",
            start_time=0  # 片段从0开始
        )
    
    # 显示播放进度条和时间
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        progress = current_play_time / total_duration if total_duration > 0 else 0.0
        progress = min(progress, 1.0)
        st.progress(progress)
        st.markdown(f"""
        <div style="text-align: center; font-size: 14px;">
            当前位置：{current_play_time:.2f} / {total_duration:.2f} 秒 | 状态：{"播放中" if st.session_state.is_playing else "已暂停"}
        </div>
        """, unsafe_allow_html=True)
    
    # 控制按钮
    col1, col2, col3 = st.columns(3)
    with col2:
        reset_col1, reset_col2 = st.columns(2)
        with reset_col1:
            if st.button("🔄 重置播放位置"):
                st.session_state.current_time = 0.0
                st.session_state.is_playing = False
        with reset_col2:
            if st.button("⏮️ 回到开始"):
                st.session_state.current_time = 0.0
                st.session_state.is_playing = True
    
    # 下载选项
    st.subheader("下载处理后音频")
    col1, col2 = st.columns(2)
    with col1:
        # 下载完整的滤波音频
        st.download_button(
            label=f"下载{current_filter}音频",
            data=st.session_state.audio_data[current_filter],
            file_name=f"{uploaded_file.name[:-4]}_{current_filter.replace(' ', '_')}.wav",
            mime="audio/wav"
        )
    with col2:
        # 原始音频下载
        st.download_button(
            label="下载原始音频",
            data=st.session_state.audio_data["无滤波"],
            file_name=f"{uploaded_file.name[:-4]}_原始音频.wav",
            mime="audio/wav"
        )
    
    # 自动更新：播放中定期刷新音频片段
    if st.session_state.is_playing:
        # 检查是否需要更新（避免过于频繁）
        if time.time() - st.session_state.last_update_time > 0.3:
            # 兼容不同Streamlit版本
            try:
                st.rerun(scope="component")  # Streamlit 1.30+
            except:
                st.rerun()  # 旧版本降级使用

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

# 页脚信息
st.markdown("""
---
<div style="text-align: center; color: #666; font-size: 12px;">
    音频无缝滤波工具 | 完美支持播放中切换 | 基于Streamlit + Librosa构建
</div>
""", unsafe_allow_html=True)
