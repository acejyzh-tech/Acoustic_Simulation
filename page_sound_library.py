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
    return pink_noise *0.5

def generate_red_noise(duration=5, sample_rate=44100):
    num_samples = int(sample_rate * duration)
    white_noise = np.random.normal(0, 1, num_samples)
    X = rfft(white_noise)
    S = np.zeros_like(X)
    freqs = np.fft.rfftfreq(num_samples, d=1/sample_rate)
    S[1:] = 1 /freqs[1:]
    red_fft = X * S
    red_noise = irfft(red_fft)
    red_noise = red_noise / np.max(np.abs(red_noise))
    return red_noise *0.5

# 单频音和扫频音
def generate_tone(frequency=440, duration=5, sample_rate=44100):
    t = np.linspace(0, duration, int(duration * sample_rate), endpoint=False)
    return 0.5 * np.sin(2 * np.pi * frequency * t)

def generate_sweep(start_freq=20, end_freq=20000, duration=10, sample_rate=44100):
    t = np.linspace(0, duration, int(duration * sample_rate), endpoint=False)
    return 0.5 * np.sin(2 * np.pi * (start_freq + (end_freq - start_freq)/duration * t) * t)

# 音频转字节流函数
def audio_to_bytes(audio_data, sample_rate):
    audio_data = np.int16(audio_data * 32767)
    byte_io = io.BytesIO()
    write(byte_io, sample_rate, audio_data)
    return byte_io.getvalue()

st.caption("常用的声音库，点击按钮播放。注意：由于您的播放设备的频响特性差异，实际听到的音频会被“染色”。")
# 按钮交互
st.divider()
with st.container(horizontal=True):
    if st.button("白噪声", icon=":material/earthquake:"):
        audio_data = generate_white_noise()
        audio_bytes = audio_to_bytes(audio_data, 44100)
        st.audio(audio_bytes, format='audio/wav', autoplay=True)
    
    if st.button("粉红噪声", icon=":material/earthquake:"):
        audio_data = generate_pink_noise()
        audio_bytes = audio_to_bytes(audio_data, 44100)
        st.audio(audio_bytes, format='audio/wav', autoplay=True)
        
st.divider()
with st.container(horizontal=True):
    if st.button("440 Hz", icon=":material/earthquake:"):
        audio_data = generate_tone(440)
        audio_bytes = audio_to_bytes(audio_data, 44100)
        st.audio(audio_bytes, format='audio/wav', autoplay=True)
        
    if st.button("100 Hz", icon=":material/earthquake:"):
        audio_data = generate_tone(100)
        audio_bytes = audio_to_bytes(audio_data, 44100)
        st.audio(audio_bytes, format='audio/wav', autoplay=True)
        
    if st.button("250 Hz", icon=":material/earthquake:"):
        audio_data = generate_tone(250)
        audio_bytes = audio_to_bytes(audio_data, 44100)
        st.audio(audio_bytes, format='audio/wav', autoplay=True)
        
    if st.button("500 Hz", icon=":material/earthquake:"):
        audio_data = generate_tone(500)
        audio_bytes = audio_to_bytes(audio_data, 44100)
        st.audio(audio_bytes, format='audio/wav', autoplay=True)
        
    if st.button("1,000 Hz", icon=":material/earthquake:"):
        audio_data = generate_tone(1000)
        audio_bytes = audio_to_bytes(audio_data, 44100)
        st.audio(audio_bytes, format='audio/wav', autoplay=True)
        
    if st.button("2,000 Hz", icon=":material/earthquake:"):
        audio_data = generate_tone(2000)
        audio_bytes = audio_to_bytes(audio_data, 44100)
        st.audio(audio_bytes, format='audio/wav', autoplay=True)
        
    if st.button("5,000 Hz", icon=":material/earthquake:"):
        audio_data = generate_tone(5000)
        audio_bytes = audio_to_bytes(audio_data, 44100)
        st.audio(audio_bytes, format='audio/wav', autoplay=True)
        
    if st.button("10,000 Hz", icon=":material/earthquake:"):
        audio_data = generate_tone(10000)
        audio_bytes = audio_to_bytes(audio_data, 44100)
        st.audio(audio_bytes, format='audio/wav', autoplay=True)

st.divider()
with st.container(horizontal=True):
    if st.button("20 Hz to 20 kHz 线性扫频", icon=":material/earthquake:"):
        audio_data = generate_sweep()
        audio_bytes = audio_to_bytes(audio_data, 44100)
        st.audio(audio_bytes, format='audio/wav', autoplay=True)


