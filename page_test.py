import streamlit as st
import numpy as np
from scipy.io.wavfile import write
import scipy.signal
import io
import pandas as pd
import altair as alt

st.title("音频波形与频谱可视化工具（Altair）")

# 生成白噪声
def generate_white_noise(duration=5, sample_rate=44100):
    return np.random.randn(int(duration * sample_rate))

# 替代粉红噪声生成方法（兼容旧版 scipy）
def generate_pink_noise(duration=5, sample_rate=44100):
    white_noise = np.random.randn(int(duration * sample_rate))
    b, a = scipy.signal.butter(2, 0.1, btype='low')
    pink_noise = scipy.signal.lfilter(b, a, white_noise)
    return pink_noise / np.max(np.abs(pink_noise)) * 0.5

# 单频音
def generate_tone(frequency=440, duration=5, sample_rate=44100):
    t = np.linspace(0, duration, int(duration * sample_rate), endpoint=False)
    return 0.5 * np.sin(2 * np.pi * frequency * t)

# 扫频音
def generate_sweep(start_freq=20, end_freq=20000, duration=5, sample_rate=44100):
    t = np.linspace(0, duration, int(duration * sample_rate), endpoint=False)
    return 0.5 * np.sin(2 * np.pi * (start_freq + (end_freq - start_freq)/duration * t) * t)

# 音频转字节流（16位PCM格式）
def audio_to_bytes(audio_data, sample_rate):
    audio_data = np.int16(audio_data * 32767)
    byte_io = io.BytesIO()
    write(byte_io, sample_rate, audio_data)
    return byte_io.getvalue()

# 转换波形数据为 DataFrame
def waveform_to_df(audio_data, sample_rate):
    t = np.linspace(0, len(audio_data)/sample_rate, len(audio_data))
    df = pd.DataFrame({
        'time': t,
        'amplitude': audio_data
    })
    return df

# 转换频谱数据为 DataFrame
def spectrum_to_df(audio_data, sample_rate):
    n = len(audio_data)
    fft_result = np.fft.fft(audio_data)
    fft_magnitude = np.abs(fft_result)
    freqs = np.fft.fftfreq(n, 1/sample_rate)
    
    df = pd.DataFrame({
        'frequency': freqs[:n//2],
        'magnitude': fft_magnitude[:n//2]
    })
    return df

# 绘制波形图
def plot_waveform_altair(df):
    chart = alt.Chart(df).mark_line().encode(
        x='time:Q',
        y='amplitude:Q'
    ).properties(
        width=600,
        height=300,
        title='音频波形图'
    )
    return chart

# 绘制频谱图
def plot_spectrum_altair(df):
    chart = alt.Chart(df).mark_line().encode(
        x=alt.X('frequency:Q', scale=alt.Scale(type='log')),
        y='magnitude:Q'
    ).properties(
        width=600,
        height=300,
        title='音频频谱图'
    )
    return chart

# 按钮交互
if st.button("播放白噪声并显示波形与频谱"):
    audio_data = generate_white_noise()
    audio_bytes = audio_to_bytes(audio_data, 44100)
    st.audio(audio_bytes, format='audio/wav')
    
    df_wave = waveform_to_df(audio_data, 44100)
    df_spec = spectrum_to_df(audio_data, 44100)
    
    st.altair_chart(plot_waveform_altair(df_wave))
    st.altair_chart(plot_spectrum_altair(df_spec))

if st.button("播放粉红噪声并显示波形与频谱"):
    audio_data = generate_pink_noise()
    audio_bytes = audio_to_bytes(audio_data, 44100)
    st.audio(audio_bytes, format='audio/wav')
    
    df_wave = waveform_to_df(audio_data, 44100)
    df_spec = spectrum_to_df(audio_data, 44100)
    
    st.altair_chart(plot_waveform_altair(df_wave))
    st.altair_chart(plot_spectrum_altair(df_spec))

if st.button("播放单频音 (440Hz) 并显示波形与频谱"):
    audio_data = generate_tone(440)
    audio_bytes = audio_to_bytes(audio_data, 44100)
    st.audio(audio_bytes, format='audio/wav')
    
    df_wave = waveform_to_df(audio_data, 44100)
    df_spec = spectrum_to_df(audio_data, 44100)
    
    st.altair_chart(plot_waveform_altair(df_wave))
    st.altair_chart(plot_spectrum_altair(df_spec))

if st.button("播放扫频音 (20Hz-20kHz) 并显示波形与频谱"):
    audio_data = generate_sweep()
    audio_bytes = audio_to_bytes(audio_data, 44100)
    st.audio(audio_bytes, format='audio/wav')
    
    df_wave = waveform_to_df(audio_data, 44100)
    df_spec = spectrum_to_df(audio_data, 44100)
    
    st.altair_chart(plot_waveform_altair(df_wave))
    st.altair_chart(plot_spectrum_altair(df_spec))

# 使用说明
st.markdown("""
### 使用说明：
1. 点击对应按钮播放音频并查看波形与频谱图。
2. 波形图显示音频的时域信息，频谱图显示音频的频域信息。
3. Altair 图表支持交互式操作，如缩放、悬停查看数值等。
""")
