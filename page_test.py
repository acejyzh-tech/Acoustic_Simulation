import streamlit as st
import numpy as np
from scipy.io.wavfile import write
import scipy.signal
import io
import pandas as pd
import matplotlib.pyplot as plt
import plotly.graph_objects as go
from functools import lru_cache

st.title("音频波形与频谱可视化工具（优化版）")

# 缓存音频生成函数，避免重复计算
@lru_cache(maxsize=10)
def generate_audio(audio_type, duration=5, sample_rate=44100):
    if audio_type == "white_noise":
        return np.random.randn(int(duration * sample_rate))
    elif audio_type == "pink_noise":
        white_noise = np.random.randn(int(duration * sample_rate))
        b, a = scipy.signal.butter(2, 0.1, btype='low')
        pink_noise = scipy.signal.lfilter(b, a, white_noise)
        return pink_noise / np.max(np.abs(pink_noise)) * 0.5
    elif audio_type == "tone":
        t = np.linspace(0, duration, int(duration * sample_rate), endpoint=False)
        return 0.5 * np.sin(2 * np.pi * 440 * t)
    elif audio_type == "sweep":
        t = np.linspace(0, duration, int(duration * sample_rate), endpoint=False)
        return 0.5 * np.sin(2 * np.pi * (20 + (20000 - 20)/duration * t) * t)
    else:
        raise ValueError("未知音频类型")

# 音频转字节流（16位PCM格式）
def audio_to_bytes(audio_data, sample_rate):
    audio_data = np.int16(audio_data * 32767)
    byte_io = io.BytesIO()
    write(byte_io, sample_rate, audio_data)
    return byte_io.getvalue()

# 数据下采样（减少数据点）
def downsample_data(data, factor=10):
    return data[::factor]

# 转换波形数据为 DataFrame
def waveform_to_df(audio_data, sample_rate, downsample_factor=10):
    t = np.linspace(0, len(audio_data)/sample_rate, len(audio_data))
    data = downsample_data(audio_data, downsample_factor)
    t = downsample_data(t, downsample_factor)
    df = pd.DataFrame({
        'time': t,
        'amplitude': data
    })
    return df

# 转换频谱数据为 DataFrame
def spectrum_to_df(audio_data, sample_rate, downsample_factor=10):
    n = len(audio_data)
    fft_result = np.fft.fft(audio_data)
    fft_magnitude = np.abs(fft_result)
    freqs = np.fft.fftfreq(n, 1/sample_rate)
    
    # 只保留低频部分（避免高频冗余）
    freqs = freqs[:n//2]
    fft_magnitude = fft_magnitude[:n//2]
    data = downsample_data(fft_magnitude, downsample_factor)
    freqs = downsample_data(freqs, downsample_factor)
    
    df = pd.DataFrame({
        'frequency': freqs,
        'magnitude': data
    })
    return df

# 绘制波形图（使用 Plotly）
def plot_waveform_plotly(df):
    fig = go.Figure()
    fig.add_trace(go.Scatter(x=df['time'], y=df['amplitude'], mode='lines', name='波形'))
    fig.update_layout(title='音频波形图', xaxis_title='时间 (s)', yaxis_title='振幅')
    return fig

# 绘制频谱图（使用 Plotly）
def plot_spectrum_plotly(df):
    fig = go.Figure()
    fig.add_trace(go.Scatter(x=df['frequency'], y=df['magnitude'], mode='lines', name='频谱'))
    fig.update_layout(title='音频频谱图', xaxis_type='log', xaxis_title='频率 (Hz)', yaxis_title='幅度')
    return fig

# 按钮交互
audio_types = {
    "白噪声": "white_noise",
    "粉红噪声": "pink_noise",
    "单频音 (440Hz)": "tone",
    "扫频音 (20Hz-20kHz)": "sweep"
}

for label, audio_type in audio_types.items():
    if st.button(f"播放 {label} 并显示波形与频谱"):
        audio_data = generate_audio(audio_type)
        audio_bytes = audio_to_bytes(audio_data, 44100)
        st.audio(audio_bytes, format='audio/wav')
        
        df_wave = waveform_to_df(audio_data, 44100, downsample_factor=10)
        df_spec = spectrum_to_df(audio_data, 44100, downsample_factor=10)
        
        st.plotly_chart(plot_waveform_plotly(df_wave))
        st.plotly_chart(plot_spectrum_plotly(df_spec))

# 使用说明
st.markdown("""
### 使用说明：
1. 点击对应按钮播放音频并查看波形与频谱图。
2. 使用 Plotly 绘制图表，支持交互式操作（缩放、悬停等）。
3. 通过数据下采样和缓存机制，显著提升性能。
""")
