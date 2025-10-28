'''
by J.Y.Zhang
用于进行常用的声学计算
（1）声速、空气体积模量等常用参数的计算和调用
（2）低衰和谐振特性的计算
（3）非线性失真计算
（4）等效电路的基尔霍夫方法求解
'''

import numpy as np
import matplotlib.pyplot as plt

# 物理常数
PI = np.pi  # 圆周率
KB = 1.38064853e-23  # 玻尔兹曼常数 KB
NA = 6.022140857e23   # 阿弗加德罗常数 NA
Ru = KB * NA  # 气体常数 R

# 物理条件
p0 = 101325  # 大气压强，单位 Pa
T0 = 293.15  # 绝对温度，单位 K

# 空气的热力学参数
GAMMA = 1.4  # 空气绝热指数 or 比热比
M0 = 0.0289652  # 空气摩尔质量，单位 kg/mol
Cvm = Ru / (GAMMA - 1) / M0  # 空气的定容比热
Cpm = GAMMA * Cvm  # 空气的定压比热

# 与温度和压强有关的空气参数
rho0 = p0 * M0 / Ru / T0 # 特定温度和气压下的空气密度
k0 = -0.00039333 + 0.00010184*T0 - 4.8574E-8*T0**2 + 1.5207E-11*T0**3  # 空气热导率
KAPPA = k0 / rho0 / Cpm  # 特定温度下空气的热扩散率
ETA = 2.791e-7 * T0 ** 0.7355  # 特定温度下空气的运动粘滞系数
NIU = ETA / rho0  # 特定温度下空气的动力粘滞系数
K0 = GAMMA * p0  # 特定气压下空气的绝热体积模量，单位 Pa
c0 = np.sqrt(GAMMA * Ru * T0 / M0)  # 特定温度下空气中的声速
Z0 = rho0 * c0  # 空气的特性阻抗

def print_air_para(): # 输出物理参数
    print('-'*20)
    print('计算条件:')
    print(f'温度：{T0} K')
    print(f'气压：{p0} Pa；')
    print(f'空气密度：{rho0:.3f} kg/m3')
    print(f'空气热导率：{k0:.3g} W/(m K)')
    print(f'空气运动粘滞系数：{ETA:.3g} Pa s')
    print(f'空气声速：{c0:.1f} m/s')
    print(f'空气特性阻抗：{Z0:.1f} N s/m3')
    print('-'*20)

# 常用声学公式
def dB(x): return 20*np.log10(x)  # 计算dB值
def dBsum(x, coh=False):  # dB信号的叠加
    if coh==True:  # 相干信号的叠加
        return 20*np.log10(np.sum(10**(x/20)))
    else:  # 非相干信号的叠加
        return 10*np.log10(np.sum(10**(x/10)))
def SPL(p): return dB(p/20e-6)  # 有声压级（Pa）计算声压级（dB）
def parallel(R1,R2): return R1*R2/(R1+R2) 
def omg(f): return 2 * PI * f  # 计算圆频率（Hz）
def beta(f): return np.sqrt(NIU/omg(f))  # 计算某个频率声音的边界层厚度
def A_ro(f, f_ro): return 1/np.sqrt(1+(f_ro/f)**2)  # 低衰频率为f_ro，频率f时的低衰值
def f0(C, M): return 1/2/PI/np.sqrt(C*M)   # 由顺性和惯性计算系统固有频率
def Qm(C, M, R): return np.sqrt(M/C)/R  # 计算振动系统的品质因数
def fr(C, M, R): return f0(C, M) * np.sqrt(1-1/2/Qm(C,M,R)**2)   # 计算谐振频率
def Ar(C, M, R): return 2*Qm(C,M,R)**2/np.sqrt(4*Qm(C,M,R)**2-1)  # 计算谐振峰高度
def A_hr(z, Qm): return Qm/np.sqrt(z**2+(z**2-1)**2*Qm**2)  # 由频率比和品质因数，计算幅频谐响应
def JN(R): return np.sqrt(4*KB*T0*R)  # 计算阻值下的 J-N 噪声密度

'''
A 计权计算
参考 GB/T 3785.1-2010 / IEC 61672-1:2002
'''
def A_weight(f):
    D = np.sqrt(1/2)
    fr = 10**3   # 中心参考频率，该频率处计权值为0
    fL = 10**1.5   # C计权的低频截止频率
    fH = 10**3.9   # C计权的高频截止频率
    fA = 10**2.45  # A计权耦合高通滤波器截止频率
    
    c = fL**2*fH**2  # 公式12
    b = 1/(1-D) * (fr**2 + c/fr**2 - D*(fL**2+fH**2))  # 公式11
    
    f1 = np.sqrt((-b-np.sqrt(b**2-4*c))/2)
    f2 = (3-np.sqrt(5))/2*fA
    f3 = (3+np.sqrt(5))/2*fA
    f4 = np.sqrt((-b+np.sqrt(b**2-4*c))/2)
    
    def CW(f): return dB(f4**2*f**2/(f**2+f1**2)/(f**2+f4**2))   # 公式6
    def AW(f): return CW(f) + dB(f**2/np.sqrt((f**2+f2**2)*(f**2+f3**2)))   # 公式7
    
    return AW(f)-AW(fr)

'''
非线性失真处理
'''
def RMS(x): return np.sqrt(np.sum(x**2)/len(x))   # 计算RMS值
def DC(x): return np.sum(x)/len(x)  # 计算直流分量
def Af(x):  # 计算基频分量
    T = len(x)
    t = np.linspace(0, 1, T, endpoint=False)
    a = np.sum(x*np.cos(2*PI*t))*2/T
    b = np.sum(x*np.sin(2*PI*t))*2/T
    return np.sqrt(a**2 + b**2)
# 计算x的总谐波失真，x为一个完整周期内的等时间间隔离散信号
def THD(x): return np.sqrt(2*RMS(x)**2-2*DC(x)**2-Af(x)**2)/Af(x)

# 对周期为T的时域数列进行重新插值采样，转化成一个完整周期内的等时间间隔离散信号
def interp(x, y, T): 
    for i in range(len(x)):
        x[i] = x[i] - np.floor(x[i]/T)*T  # 时间戳平移到一个周期内
    indices = sorted(range(len(x)), key=lambda i: x[i]) # 建立排序索引
    x, y = [x[i] for i in indices], [y[i] for i in indices] # 根据排序后的索引重新排列 x 和 y
    # 在序列末尾补尾值
    x.append(T)
    y.append(y[0])
    # 进行插值处理
    x1 = np.linspace(0, T, 100, endpoint=False)
    y1 = np.interp(x1, x, y)
    return y1

'''
麦克风频响及噪声特性求解 V1.0
'''
class AC:  # 定义阻抗类
    # 初始化阻抗类，参数R（声阻）、M（声质量）、C（声顺）
    def __init__(self, R=0, M=0, C=None):
        self.R, self.M, self.C = R, M, C
        self.K = None
        
    # 计算特定频率f时的声学阻抗
    def Z(self, f):
        if self.C==None: self.K = 0
        else: self.K = 1/self.C
        return complex(self.R, omg(f)*self.M - self.K/omg(f))

class MIC:  # 麦克风参数类
    # 麦克风初始化，振膜SD / 进声孔AH / 泄气孔VH / 背板孔BH / 前腔FC / 后腔BC
    def __init__(self,
                 SD=AC(0, 0, 1.84e-15),
                 AH=AC(110e6, 40e3), VH=AC(275000e6), BH=AC(286e6, 5.826e3),
                 FC=AC(0,0,0.98e-15), BC=AC(0,0,9.2e-15)):
        self.SD = SD
        self.AH, self.VH, self.BH = AH, VH, BH
        self.FC, self.BC = FC, BC
    # 计算频率响应，返回灵敏度（复值）和进声孔、泄气孔、背板孔激发的噪声
    def Z0(self, f): return self.SD.Z(f)+self.BH.Z(f)
    def Z1(self, f): return parallel(self.AH.Z(f), self.FC.Z(f))
    def Z2(self, f): return self.Z1(f) + self.BC.Z(f)
    def Z3(self, f): return self.Z2(f) + self.VH.Z(f)
    def Zm(self, f): return complex(0,omg(f)*parallel(self.SD.C, self.BC.C))*(self.Z0(f)*self.Z3(f)+self.Z2(f)*self.VH.Z(f))
    def Sens(self, f): return np.abs(self.Z1(f)*self.VH.Z(f)/self.AH.Z(f)/self.Zm(f))
    def phase(self, f): return np.angle(self.Z1(f)*self.VH.Z(f)/self.AH.Z(f)/self.Zm(f))
    def N_AH(self, f): return np.abs(self.Sens(f) * JN(self.AH.R))
    def N_VH(self, f): return np.abs(self.Z2(f)/self.Zm(f) * JN(self.VH.R))
    def N_BH(self, f): return np.abs(self.Z3(f)/self.Zm(f) * JN(self.BH.R))
    def N_total(self, f): return np.sqrt(self.N_AH(f)**2 + self.N_VH(f)**2 + self.N_BH(f)**2)


''''''''''''''''''''''''''''''''''''
def main():
    def eg01():
    # Example 01: 绘制频响及噪声谱曲线
        mic1 = MIC()   # 定义MIC类mic1
        freqs = 10**np.linspace(1, 5, 2000)
        sens, N_AH, N_VH, N_BH, N_total = [], [], [], [], []  # 初始化数组
        # 计算
        for f in freqs:
            sens.append(mic1.Sens(f))
            N_AH.append(mic1.N_AH(f))
            N_VH.append(mic1.N_VH(f))
            N_BH.append(mic1.N_BH(f))
            N_total.append(mic1.N_total(f))
        # 绘制图形
        plt.figure(figsize=(8,6))
        ax = plt.subplot()
        ax.semilogx(freqs, dB(sens), '-k', label='Sensitivity') 
        ax.semilogx(freqs, dB(N_AH), '-C0', label='Acoustic Inlet')
        ax.semilogx(freqs, dB(N_VH), '-C1', label='Vent Hole')
        ax.semilogx(freqs, dB(N_BH), '-C2', label='Backplete Hole')
        ax.semilogx(freqs, dB(N_total), '-k', label='Total Noise')
        ax.grid()
        ax.legend(loc='best')
        plt.show()
    
    # print_air_para()
    eg01()

if __name__ == '__main__':
    main()