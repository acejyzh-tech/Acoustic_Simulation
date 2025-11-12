import streamlit as st
import numpy as np
from scipy.io.wavfile import write
import scipy.signal
import io

# 页面标题
st.title("音频生成与播放工具（无sounddevice依赖）")

# 生成白噪声（均匀分布的随机信号）
def generate_white_noise(duration=5, sample_rate=44100):
    return np.random.randn(int(duration * sample_rate))

# 生成粉红噪声（1/f特性，需scipy 1.10+）
def generate_pink_noise(duration=5, sample_rate=44100):
    return scipy.signal.pinknoise(int(duration * sample_rate))

# 生成单频正弦波（可调整频率）
def generate_tone(frequency=440, duration=5, sample_rate=44100):
    t = np.linspace(0, duration, int(duration * sample_rate), endpoint=False)
    return 0.5 * np.sin(2 * np.pi * frequency * t)

# 生成扫频信号（线性扫频，从start_freq到end_freq）
def generate_sweep(start_freq=20, end_freq=20000, duration=5, sample_rate=44100):
    t = np.linspace(0, duration, int(duration * sample_rate), endpoint=False)
    # 线性扫频公式：f(t) = start_freq + (end_freq - start_freq) * t / duration
    return 0.5 * np.sin(2 * np.pi * (start_freq + (end_freq - start_freq)/duration * t) * t)

# 将音频数据转换为字节流（16位PCM格式）
def audio_to_bytes(audio_data, sample_rate):
    # 归一化到-32767到32767范围并转换为16位整数
    audio_data = np.int16(audio_data * 32767)
    # 使用io.BytesIO创建内存文件
    byte_io = io.BytesIO()
    write(byte_io, sample_rate, audio_data)
    return byte_io.getvalue()

# 按钮交互
if st.button("播放白噪声"):
    audio_data = generate_white_noise()
    audio_bytes = audio_to_bytes(audio_data, 44100)
    st.audio(audio_bytes, format='audio/wav')

if st.button("播放粉红噪声"):
    audio_data = generate_pink_noise()
    audio_bytes = audio_to_bytes(audio_data, 44100)
    st.audio(audio_bytes, format='audio/wav')

if st.button("播放单频音 (440Hz)"):
    audio_data = generate_tone(440)
    audio_bytes = audio_to_bytes(audio_data, 44100)
    st.audio(audio_bytes, format='audio/wav')

if st.button("播放扫频音 (20Hz-20kHz)"):
    audio_data = generate_sweep()
    audio_bytes = audio_to_bytes(audio_data, 44100)
    st.audio(audio_bytes, format='audio/wav')
