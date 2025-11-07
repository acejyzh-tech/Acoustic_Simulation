import streamlit as st
import librosa
import librosa.display
import numpy as np
import matplotlib.pyplot as plt
import soundfile as sf
import threading
import time
from matplotlib.colors import LinearSegmentedColormap

# 设置中文字体
plt.rcParams['font.sans-serif'] = ['SimHei', 'DejaVu Sans']
plt.rcParams['axes.unicode_minus'] = False

# 自定义颜色映射（可选）
def create_custom_cmap():
    colors = ['#000000', '#1a237e', '#3949ab', '#3f51b5', '#5c6bc0', 
              '#7986cb', '#9fa8da', '#c5cae9', '#e8eaf6', '#ffffff']
    return LinearSegmentedColormap.from_list('audio_cmap', colors, N=256)

custom_cmap = create_custom_cmap()

# 主应用
def main():
    st.title("🎵 WAV音频分析工具")
    st.markdown("---")
    
    # 初始化会话状态
    if 'audio_data' not in st.session_state:
        st.session_state.audio_data = None
    if 'sr' not in st.session_state:
        st.session_state.sr = None
    if 'duration' not in st.session_state:
        st.session_state.duration = 0.0
    if 'is_playing' not in st.session_state:
        st.session_state.is_playing = False
    if 'current_time' not in st.session_state:
        st.session_state.current_time = 0.0
    if 'spectrogram' not in st.session_state:
        st.session_state.spectrogram = None
    if 'freq_bins' not in st.session_state:
        st.session_state.freq_bins = None
    if 'time_bins' not in st.session_state:
        st.session_state.time_bins = None
    if 'lock' not in st.session_state:
        st.session_state.lock = threading.Lock()

    # 文件上传
    uploaded_file = st.file_uploader("选择WAV文件", type=["wav"])
    
    if uploaded_file is not None:
        # 读取音频文件
        with st.spinner("正在加载音频..."):
            y, sr = librosa.load(uploaded_file, sr=None, mono=True)
            st.session_state.audio_data = y
            st.session_state.sr = sr
            st.session_state.duration = librosa.get_duration(y=y, sr=sr)
            
            # 计算声谱图（STFT）
            n_fft = 2048
            hop_length = 512
            D = librosa.stft(y, n_fft=n_fft, hop_length=hop_length)
            S_db = librosa.amplitude_to_db(np.abs(D), ref=np.max)
            
            st.session_state.spectrogram = S_db
            st.session_state.freq_bins = librosa.fft_frequencies(n_fft=n_fft)
            st.session_state.time_bins = librosa.times_like(D, sr=sr, hop_length=hop_length)
        
        # 显示音频信息
        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric("采样率", f"{sr} Hz")
        with col2:
            st.metric("时长", f"{st.session_state.duration:.2f} 秒")
        with col3:
            st.metric("数据点数", f"{len(y):,}")
        
        st.markdown("---")
        
        # 音频播放控件
        st.audio(uploaded_file, format="audio/wav", start_time=0)
        
        # 播放控制按钮
        col_play, col_stop = st.columns(2)
        with col_play:
            play_btn = st.button("▶️ 播放", type="primary")
        with col_stop:
            stop_btn = st.button("⏹️ 停止")
        
        # 进度条
        progress_bar = st.progress(0.0)
        current_time_display = st.empty()
        
        # 创建双列布局：左侧声谱图，右侧实时频谱
        col_spectrogram, col_spectrum = st.columns(2)
        
        # 绘制声谱图（左侧）
        with col_spectrogram:
            st.subheader("声谱图（频率×时间）")
            spectrogram_fig, ax = plt.subplots(figsize=(10, 6))
            
            # 绘制声谱图
            im = ax.imshow(st.session_state.spectrogram, 
                          aspect='auto', 
                          origin='upper',  # 时间轴0点在左上角
                          cmap=custom_cmap,
                          extent=[st.session_state.time_bins[0], 
                                 st.session_state.time_bins[-1], 
                                 st.session_state.freq_bins[0], 
                                 st.session_state.freq_bins[-1]])
            
            # 设置标签
            ax.set_xlabel("时间 (秒)", fontsize=12)
            ax.set_ylabel("频率 (Hz)", fontsize=12)
            ax.set_title("音频声谱图", fontsize=14, fontweight='bold')
            
            # 添加颜色条
            cbar = plt.colorbar(im, ax=ax, label='强度 (dB)')
            
            # 初始时间线（红色虚线）
            time_line = ax.axvline(x=0, color='red', linestyle='--', linewidth=2, label='当前播放位置')
            ax.legend(loc='upper right')
            
            st.pyplot(spectrogram_fig, use_container_width=True)
        
        # 实时频谱图（右侧）
        with col_spectrum:
            st.subheader("实时频谱（dB值）")
            spectrum_fig, ax_spectrum = plt.subplots(figsize=(10, 6))
            
            # 初始化频谱图（全零）
            freq_range = st.session_state.freq_bins
            init_spectrum = np.zeros_like(freq_range)
            line, = ax_spectrum.plot(freq_range, init_spectrum, color='#2196F3', linewidth=2)
            
            # 设置标签和范围
            ax_spectrum.set_xlabel("频率 (Hz)", fontsize=12)
            ax_spectrum.set_ylabel("强度 (dB)", fontsize=12)
            ax_spectrum.set_title("当前播放音频频谱", fontsize=14, fontweight='bold')
            ax_spectrum.set_ylim(-100, 0)  # dB值范围
            ax_spectrum.grid(True, alpha=0.3)
            
            # 设置x轴范围（可根据实际需求调整）
            max_freq = min(8000, sr//2)  # 最大显示频率：8kHz或奈奎斯特频率
            ax_spectrum.set_xlim(0, max_freq)
            
            spectrum_placeholder = st.empty()
            spectrum_placeholder.pyplot(spectrum_fig, use_container_width=True)
        
        # 播放线程函数
        def play_audio():
            st.session_state.is_playing = True
            start_time = time.time()
            
            while st.session_state.is_playing:
                # 计算当前播放时间
                elapsed_time = time.time() - start_time
                current_time = min(elapsed_time, st.session_state.duration)
                
                # 更新会话状态
                with st.session_state.lock:
                    st.session_state.current_time = current_time
                
                # 更新进度条
                progress = current_time / st.session_state.duration if st.session_state.duration > 0 else 0.0
                progress_bar.progress(progress)
                
                # 更新时间显示
                current_time_display.markdown(f"当前播放时间: **{current_time:.2f} / {st.session_state.duration:.2f} 秒**")
                
                # 更新声谱图时间线
                time_line.set_xdata(current_time)
                
                # 计算当前时间点的频谱
                if st.session_state.audio_data is not None:
                    # 找到当前时间对应的音频帧
                    current_sample = int(current_time * st.session_state.sr)
                    
                    # 取当前帧附近的音频片段（用于频谱计算）
                    window_size = n_fft  # 与STFT保持一致
                    start_sample = max(0, current_sample - window_size // 2)
                    end_sample = min(len(st.session_state.audio_data), current_sample + window_size // 2)
                    
                    # 提取音频片段并补零（确保长度一致）
                    audio_segment = st.session_state.audio_data[start_sample:end_sample]
                    if len(audio_segment) < window_size:
                        audio_segment = np.pad(audio_segment, (0, window_size - len(audio_segment)), mode='constant')
                    
                    # 计算频谱
                    fft_result = np.fft.fft(audio_segment)
                    magnitude = np.abs(fft_result[:window_size//2])  # 取正频率部分
                    magnitude_db = librosa.amplitude_to_db(magnitude, ref=np.max)
                    
                    # 更新频谱图
                    line.set_ydata(magnitude_db)
                
                # 刷新图表
                with col_spectrogram:
                    st.pyplot(spectrogram_fig, use_container_width=True)
                with col_spectrum:
                    spectrum_placeholder.pyplot(spectrum_fig, use_container_width=True)
                
                # 检查是否播放完毕
                if current_time >= st.session_state.duration:
                    st.session_state.is_playing = False
                    break
                
                # 控制更新频率（避免过于频繁）
                time.sleep(0.05)  # 50ms更新一次
        
        # 播放按钮逻辑
        if play_btn and not st.session_state.is_playing:
            # 启动播放线程
            play_thread = threading.Thread(target=play_audio)
            play_thread.daemon = True
            play_thread.start()
        
        # 停止按钮逻辑
        if stop_btn:
            st.session_state.is_playing = False
            # 重置状态
            st.session_state.current_time = 0.0
            progress_bar.progress(0.0)
            current_time_display.markdown(f"当前播放时间: **0.00 / {st.session_state.duration:.2f} 秒**")
            time_line.set_xdata(0)
            
            # 重置频谱图
            line.set_ydata(np.zeros_like(freq_range))
            with col_spectrogram:
                st.pyplot(spectrogram_fig, use_container_width=True)
            with col_spectrum:
                spectrum_placeholder.pyplot(spectrum_fig, use_container_width=True)
    
    else:
        # 未上传文件时的提示
        st.info("请上传一个WAV格式的音频文件进行分析")
        # 显示示例图片（可选）
        col1, col2, col3 = st.columns(3)
        with col2:
            st.image("https://via.placeholder.com/400x300?text=等待音频文件上传", use_column_width=True)

if __name__ == "__main__":
    main()
