import streamlit as st
import numpy as np
from scipy.io.wavfile import write
import scipy.signal
from scipy.fft import rfft, irfft
import io

# 生成白噪声
def generate_white_noise(duration=5, sample_rate=44100, mean=0, std=1):
    num_samples = int(sample_rate * duration)
    noise = np.random.normal(mean, std, num_samples)
    noise = noise / np.max(np.abs(noise))
    return noise *0.5

def generate_pink_noise(duration=5, sample_rate=44100):
    num_samples = int(sample_rate * duration)
    white_noise = np.random.normal(0, 1, num_samples)
    X = rfft(white_noise)
    S = np.zeros_like(X)
    freqs = np.fft.rfftfreq(num_samples, d=1/sample_rate)
    S[1:] = 1 / np.sqrt(freqs[1:])
    pink_fft = X * S
    pink_noise = irfft(pink_fft)
    pink_noise = pink_noise / np.max(np.abs(pink_noise))
    return pink_noise

# 替代粉红噪声生成方法（使用滤波白噪声）
def generate_pink_noise1(duration=5, sample_rate=44100):
    # 生成白噪声
    white_noise = generate_white_noise(duration, sample_rate)
    # 使用滤波器近似粉红噪声（1/f特性）
    b, a = scipy.signal.butter(0.5, 10.0, btype='lowpass', fs=sample_rate)  # 低通滤波器
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

def generate_babble_noise(sample_rate=44100, duration=5, num_sinusoids=20):
    t = np.linspace(0, duration, int(sample_rate * duration), endpoint=False)
    frequencies = np.random.uniform(100, 3000, num_sinusoids)
    amplitudes = np.random.uniform(0.1, 0.5, num_sinusoids)
    babble = np.zeros_like(t)
    for f, a in zip(frequencies, amplitudes):
        babble += a * np.sin(2 * np.pi * f * t)
    babble = np.int16(babble / np.max(np.abs(babble)) * 32767)
    return babble

# 音频转字节流函数
def audio_to_bytes(audio_data, sample_rate):
    audio_data = np.int16(audio_data * 32767)
    byte_io = io.BytesIO()
    write(byte_io, sample_rate, audio_data)
    return byte_io.getvalue()

st.caption("常用的声音库，点击按钮播放。注意：由于您的播放设备的频响特性差异，实际听到的音频会被“染色”。")
# 按钮交互
with st.container(horizontal=True):
    if st.button("白噪声", icon=":material/earthquake:"):
        audio_data = generate_white_noise()
        audio_bytes = audio_to_bytes(audio_data, 44100)
        st.audio(audio_bytes, format='audio/wav', autoplay=True)
    
    if st.button("粉红噪声", icon=":material/earthquake:"):
        audio_data = generate_pink_noise()
        audio_bytes = audio_to_bytes(audio_data, 44100)
        st.audio(audio_bytes, format='audio/wav', autoplay=True)
    
    if st.button("Babble 噪声", icon=":material/earthquake:"):
        audio_data = generate_babble_noise()
        audio_bytes = audio_to_bytes(audio_data, 44100)
        st.audio(audio_bytes, format='audio/wav', autoplay=True)
    
with st.container(horizontal=True):
    if st.button("单频音 (440Hz)", icon=":material/earthquake:"):
        audio_data = generate_tone(440)
        audio_bytes = audio_to_bytes(audio_data, 44100)
        st.audio(audio_bytes, format='audio/wav', autoplay=True)
        
    if st.button("单频音 (100Hz)", icon=":material/earthquake:"):
        audio_data = generate_tone(100)
        audio_bytes = audio_to_bytes(audio_data, 44100)
        st.audio(audio_bytes, format='audio/wav', autoplay=True)
        
    if st.button("单频音 (250Hz)", icon=":material/earthquake:"):
        audio_data = generate_tone(250)
        audio_bytes = audio_to_bytes(audio_data, 44100)
        st.audio(audio_bytes, format='audio/wav', autoplay=True)
        
    if st.button("单频音 (500Hz)", icon=":material/earthquake:"):
        audio_data = generate_tone(500)
        audio_bytes = audio_to_bytes(audio_data, 44100)
        st.audio(audio_bytes, format='audio/wav', autoplay=True)
        
    if st.button("单频音 (1000Hz)", icon=":material/earthquake:"):
        audio_data = generate_tone(1000)
        audio_bytes = audio_to_bytes(audio_data, 44100)
        st.audio(audio_bytes, format='audio/wav', autoplay=True)
        
    if st.button("单频音 (2000Hz)", icon=":material/earthquake:"):
        audio_data = generate_tone(2000)
        audio_bytes = audio_to_bytes(audio_data, 44100)
        st.audio(audio_bytes, format='audio/wav', autoplay=True)
        
    if st.button("单频音 (5000Hz)", icon=":material/earthquake:"):
        audio_data = generate_tone(5000)
        audio_bytes = audio_to_bytes(audio_data, 44100)
        st.audio(audio_bytes, format='audio/wav', autoplay=True)
        
    if st.button("单频音 (10000Hz)", icon=":material/earthquake:"):
        audio_data = generate_tone(10000)
        audio_bytes = audio_to_bytes(audio_data, 44100)
        st.audio(audio_bytes, format='audio/wav', autoplay=True)
        
with st.container(horizontal=True):
    if st.button("扫频音 (20Hz-20kHz)", icon=":material/earthquake:"):
        audio_data = generate_sweep()
        audio_bytes = audio_to_bytes(audio_data, 44100)
        st.audio(audio_bytes, format='audio/wav', autoplay=True)



