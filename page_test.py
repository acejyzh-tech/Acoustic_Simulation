import streamlit as st
import numpy as np
from scipy.io.wavfile import write
import scipy.signal
import io

st.title("音频生成与播放工具（兼容旧版scipy）")

# 生成白噪声
def generate_white_noise(duration=5, sample_rate=44100):
    return np.random.randn(int(duration * sample_rate))

# 替代粉红噪声生成方法（使用滤波白噪声）
def generate_pink_noise(duration=5, sample_rate=44100):
    # 生成白噪声
    white_noise = np.random.randn(int(duration * sample_rate))
    # 使用滤波器近似粉红噪声（1/f特性）
    b, a = scipy.signal.butter(2, 0.1, btype='low')  # 低通滤波器
    pink_noise = scipy.signal.lfilter(b, a, white_noise)
    # 归一化
    return pink_noise / np.max(np.abs(pink_noise)) * 0.5

# 单频音和扫频音的函数保持不变
def generate_tone(frequency=440, duration=5, sample_rate=44100):
    t = np.linspace(0, duration, int(duration * sample_rate), endpoint=False)
    return 0.5 * np.sin(2 * np.pi * frequency * t)

def generate_sweep(start_freq=20, end_freq=20000, duration=5, sample_rate=44100):
    t = np.linspace(0, duration, int(duration * sample_rate), endpoint=False)
    return 0.5 * np.sin(2 * np.pi * (start_freq + (end_freq - start_freq)/duration * t) * t)

# 音频转字节流函数不变
def audio_to_bytes(audio_data, sample_rate):
    audio_data = np.int16(audio_data * 32767)
    byte_io = io.BytesIO()
    write(byte_io, sample_rate, audio_data)
    return byte_io.getvalue()

# 按钮交互
if st.button("播放白噪声"):
    audio_data = generate_white_noise()
    audio_bytes = audio_to_bytes(audio_data, 44100)
    st.audio(audio_bytes, format='audio/wav')

if st.button("播放粉红噪声（旧版兼容）"):
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

st.markdown("""
### 使用说明：
1. 安装依赖：
```bash
pip install streamlit numpy scipy
