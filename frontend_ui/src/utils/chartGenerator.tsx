// utils/chartGenerator.ts
import { BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, Legend, RadarChart, PolarGrid, PolarAngleAxis, PolarRadiusAxis, Radar } from 'recharts';
import { createRoot } from 'react-dom/client';
import React from 'react';
import html2canvas from 'html2canvas';
import { ResultItem } from './localStorage';

// 伪随机数生成器 - 基于种子的线性同余生成器（与EEGVisualization.tsx一致）
class SeededRandom {
  private seed: number;

  constructor(seed: number) {
    this.seed = seed % 2147483647;
    if (this.seed <= 0) this.seed += 2147483646;
  }

  // 生成 0-1 之间的伪随机数
  next(): number {
    this.seed = (this.seed * 16807) % 2147483647;
    return (this.seed - 1) / 2147483646;
  }

  // 生成指定范围内的随机数
  range(min: number, max: number): number {
    return min + this.next() * (max - min);
  }

  // 生成指定范围内的随机整数
  rangeInt(min: number, max: number): number {
    return Math.floor(this.range(min, max + 1));
  }
}

// 生成基于resultId的确定性EEG数据
const generateRandomEEGData = (resultId: number) => {
  const channels = Array.from({ length: 16 }, (_, i) => `通道${i + 1}`);
  
  // 使用resultId作为基础种子
  const baseSeed = resultId * 1000;
  
  // 为不同的数据类型创建不同的随机数生成器
  const createRng = (offset: number) => new SeededRandom(baseSeed + offset);
  
  const generateChannelData = (min: number, max: number, decimals: number, seedOffset: number) => {
    const rng = createRng(seedOffset);
    return channels.map((_, index) => {
      const baseValue = min + (max - min) * (index / (channels.length - 1)) * 0.7;
      const randomVariation = (rng.next() - 0.5) * (max - min) * 0.15;
      const finalValue = Math.max(min, Math.min(max, baseValue + randomVariation));
      return parseFloat(finalValue.toFixed(decimals));
    });
  };
  
  const generateIntChannelData = (baseMin: number, _baseMax: number, step: number, seedOffset: number) => {
    const rng = createRng(seedOffset);
    return channels.map((_, index) => {
      const base = baseMin + index * step;
      const variation = rng.rangeInt(-5, 5);
      return Math.max(baseMin, base + variation);
    });
  };
  
  return {
    channels,
    // 功率特征数据 - 使用更真实的EEG功率范围
    thetaPower: generateChannelData(1.2, 4.8, 2, 100),
    alphaPower: generateChannelData(2.5, 8.5, 2, 200),
    betaPower: generateChannelData(0.8, 3.5, 2, 300),
    gammaPower: generateChannelData(0.3, 1.8, 2, 400),
    // 频带特征数据
    band1: generateChannelData(1.0, 4.5, 2, 500),
    band2: generateChannelData(1.8, 6.2, 2, 600),
    band3: generateChannelData(2.2, 7.8, 2, 700),
    band4: generateChannelData(1.5, 5.5, 2, 800),
    band5: generateChannelData(0.8, 3.2, 2, 900),
    // 时域特征数据
    zeroCrossings: generateIntChannelData(25, 85, 8, 1000),
    variance: generateChannelData(0.5, 2.5, 3, 1100),
    energy: generateIntChannelData(100, 500, 50, 1200),
    diff: generateChannelData(0.8, 3.5, 2, 1300),
    // 时频图（STFT）模拟数据
    timeFreq: {
      x: Array.from({ length: 100 }, (_, i) => i * 0.05), // 时间: 0-5秒
      y: Array.from({ length: 50 }, (_, i) => i),   // 频率: 0-50 Hz
      z: (() => {
        const rng = createRng(1500);
        return Array.from({ length: 50 }, (_, freqIdx) => {
          const baseEnergy = 30 - (freqIdx / 50) * 20; // 30降到10
          return Array.from({ length: 100 }, () => {
            const variation = rng.range(-5, 8);
            return Math.max(0, baseEnergy + variation);
          });
        });
      })(),
    },
  };
};

export class ChartGenerator {
  // 生成雷达图
  static async generateRadarChart(result: ResultItem): Promise<string> {
    const data = [
      {
        subject: '应激',
        A: result.stress_score,
        fullMark: 100
      },
      {
        subject: '抑郁',
        A: result.depression_score,
        fullMark: 100
      },
      {
        subject: '焦虑',
        A: result.anxiety_score,
        fullMark: 100
      },
      {
        subject: '社交孤立',
        A: result.social_isolation_score,
        fullMark: 100
      }
    ];
    
    const RadarChartComponent = () => (
      <RadarChart width={500} height={350} data={data}>
        <PolarGrid stroke="#e0e0e0" />
        <PolarAngleAxis dataKey="subject" tick={{ fill: '#333', fontSize: 14 }} />
        <PolarRadiusAxis angle={90} domain={[0, 100]} tick={{ fill: '#666' }} />
        <Radar name="评分" dataKey="A" stroke="#3498db" fill="#3498db" fillOpacity={0.6} strokeWidth={2} />
        <Legend />
      </RadarChart>
    );
    
    return await this.renderChartToBase64(RadarChartComponent);
  }
  
  // 生成综合脑电功率图
  static async generateEEGChart(result: ResultItem): Promise<string> {
    const eegData = generateRandomEEGData(result.id);
    const chartData = eegData.channels.map((channel, index) => ({
      name: channel,
      Theta: eegData.thetaPower[index],
      Alpha: eegData.alphaPower[index],
      Beta: eegData.betaPower[index],
      Gamma: eegData.gammaPower[index],
    }));
    
    const EEGChartComponent = () => (
      <BarChart width={700} height={350} data={chartData}>
        <CartesianGrid strokeDasharray="3 3" stroke="#e0e0e0" />
        <XAxis dataKey="name" tick={{ fill: '#333', fontSize: 12 }} />
        <YAxis tick={{ fill: '#666' }} label={{ value: '功率 (μV²)', angle: -90, position: 'insideLeft', style: { fill: '#333' } }} />
        <Tooltip 
          contentStyle={{ backgroundColor: '#fff', border: '1px solid #ccc', borderRadius: '4px' }}
          labelStyle={{ color: '#333', fontWeight: 'bold' }}
        />
        <Legend wrapperStyle={{ paddingTop: '10px' }} />
        <Bar dataKey="Theta" fill="#3498db" name="Theta波" />
        <Bar dataKey="Alpha" fill="#2ecc71" name="Alpha波" />
        <Bar dataKey="Beta" fill="#e74c3c" name="Beta波" />
        <Bar dataKey="Gamma" fill="#f39c12" name="Gamma波" />
      </BarChart>
    );
    
    return await this.renderChartToBase64(EEGChartComponent, 750, 400);
  }
  
  // 生成时域特征图（新增）
  static async generateTimeDomainChart(result: ResultItem): Promise<string> {
    const eegData = generateRandomEEGData(result.id);
    const chartData = eegData.channels.map((channel, index) => ({
      name: channel,
      过零率: eegData.zeroCrossings[index],
      方差: eegData.variance[index] * 50, // 缩放以便显示
      能量: eegData.energy[index] / 10, // 缩放以便显示
      差分: eegData.diff[index] * 30, // 缩放以便显示
    }));
    
    const TimeDomainComponent = () => (
      <BarChart width={700} height={350} data={chartData}>
        <CartesianGrid strokeDasharray="3 3" stroke="#e0e0e0" />
        <XAxis dataKey="name" tick={{ fill: '#333', fontSize: 12 }} />
        <YAxis tick={{ fill: '#666' }} />
        <Tooltip 
          contentStyle={{ backgroundColor: '#fff', border: '1px solid #ccc', borderRadius: '4px' }}
        />
        <Legend wrapperStyle={{ paddingTop: '10px' }} />
        <Bar dataKey="过零率" fill="#8e44ad" name="过零率" />
        <Bar dataKey="方差" fill="#d35400" name="方差(×50)" />
        <Bar dataKey="能量" fill="#27ae60" name="能量(÷10)" />
        <Bar dataKey="差分" fill="#1a535c" name="差分(×30)" />
      </BarChart>
    );
    
    return await this.renderChartToBase64(TimeDomainComponent, 750, 400);
  }
  
  // 生成频带特征图（新增）
  static async generateFrequencyBandChart(result: ResultItem): Promise<string> {
    const eegData = generateRandomEEGData(result.id);
    const chartData = eegData.channels.map((channel, index) => ({
      name: channel,
      Band1: eegData.band1[index],
      Band2: eegData.band2[index],
      Band3: eegData.band3[index],
      Band4: eegData.band4[index],
      Band5: eegData.band5[index],
    }));
    
    const FrequencyBandComponent = () => (
      <BarChart width={700} height={350} data={chartData}>
        <CartesianGrid strokeDasharray="3 3" stroke="#e0e0e0" />
        <XAxis dataKey="name" tick={{ fill: '#333', fontSize: 12 }} />
        <YAxis tick={{ fill: '#666' }} label={{ value: '功率', angle: -90, position: 'insideLeft', style: { fill: '#333' } }} />
        <Tooltip 
          contentStyle={{ backgroundColor: '#fff', border: '1px solid #ccc', borderRadius: '4px' }}
        />
        <Legend wrapperStyle={{ paddingTop: '10px' }} />
        <Bar dataKey="Band1" fill="#9b59b6" name="频带1" />
        <Bar dataKey="Band2" fill="#1abc9c" name="频带2" />
        <Bar dataKey="Band3" fill="#f1c40f" name="频带3" />
        <Bar dataKey="Band4" fill="#e67e22" name="频带4" />
        <Bar dataKey="Band5" fill="#34495e" name="频带5" />
      </BarChart>
    );
    
    return await this.renderChartToBase64(FrequencyBandComponent, 750, 400);
  }
  
  // 生成微分熵特征图（新增）
  static async generateDiffEntropyChart(result: ResultItem): Promise<string> {
    const eegData = generateRandomEEGData(result.id);
    const chartData = eegData.channels.map((channel, index) => ({
      name: channel,
      微分熵: eegData.diff[index],
    }));
    
    const DiffEntropyComponent = () => (
      <BarChart width={700} height={350} data={chartData}>
        <CartesianGrid strokeDasharray="3 3" stroke="#e0e0e0" />
        <XAxis dataKey="name" tick={{ fill: '#333', fontSize: 12 }} />
        <YAxis tick={{ fill: '#666' }} label={{ value: '微分熵值', angle: -90, position: 'insideLeft', style: { fill: '#333' } }} />
        <Tooltip 
          contentStyle={{ backgroundColor: '#fff', border: '1px solid #ccc', borderRadius: '4px' }}
        />
        <Legend wrapperStyle={{ paddingTop: '10px' }} />
        <Bar dataKey="微分熵" fill="#4ECDC4" name="微分熵特征" />
      </BarChart>
    );
    
    return await this.renderChartToBase64(DiffEntropyComponent, 750, 400);
  }
  
  // 生成血清图
  static async generateSerumChart(result: ResultItem): Promise<string> {
    // 使用result.id生成确定性的血清数据
    const rng = new SeededRandom(result.id * 1000 + 1400);
    const serumData = [
      { name: 'CRP', value: parseFloat(rng.range(0.5, 15.0).toFixed(1)), unit: 'mg/L' },
      { name: 'IL-6', value: parseFloat(rng.range(2.0, 50.0).toFixed(1)), unit: 'pg/mL' },
      { name: 'TNF-α', value: parseFloat(rng.range(5.0, 80.0).toFixed(1)), unit: 'pg/mL' },
      { name: 'LDH', value: parseFloat(rng.range(120.0, 350.0).toFixed(0)), unit: 'U/L' },
      { name: 'CK', value: parseFloat(rng.range(30.0, 250.0).toFixed(0)), unit: 'U/L' }
    ];
    
    const SerumChartComponent = () => (
      <BarChart width={700} height={350} data={serumData}>
        <CartesianGrid strokeDasharray="3 3" stroke="#e0e0e0" />
        <XAxis dataKey="name" tick={{ fill: '#333', fontSize: 12 }} />
        <YAxis tick={{ fill: '#666' }} label={{ value: '浓度', angle: -90, position: 'insideLeft', style: { fill: '#333' } }} />
        <Tooltip 
          contentStyle={{ backgroundColor: '#fff', border: '1px solid #ccc', borderRadius: '4px' }}
        />
        <Legend wrapperStyle={{ paddingTop: '10px' }} />
        <Bar dataKey="value" fill="#FF6B6B" name="血清指标" />
      </BarChart>
    );
    
    return await this.renderChartToBase64(SerumChartComponent, 750, 400);
  }
  
  // 生成时频域特征图（新增）
  static async generateTimeFreqChart(result: ResultItem): Promise<string> {
    const eegData = generateRandomEEGData(result.id);
    
    // 创建一个Canvas来绘制时频域热图
    const TimeFreqComponent = () => {
      const canvasRef = React.useRef<HTMLCanvasElement>(null);
      
      React.useEffect(() => {
        if (canvasRef.current) {
          const canvas = canvasRef.current;
          const ctx = canvas.getContext('2d');
          if (!ctx) return;
          
          const width = 700;
          const height = 350;
          const padding = 60;
          const plotWidth = width - 2 * padding;
          const plotHeight = height - 2 * padding;
          
          // 清空画布
          ctx.fillStyle = 'white';
          ctx.fillRect(0, 0, width, height);
          
          // 绘制时频域热图数据
          const timeSteps = eegData.timeFreq.x.length;
          const freqSteps = eegData.timeFreq.y.length;
          const cellWidth = plotWidth / timeSteps;
          const cellHeight = plotHeight / freqSteps;
          
          // 找到最大最小值用于归一化
          const allValues = eegData.timeFreq.z.flat();
          const minVal = Math.min(...allValues);
          const maxVal = Math.max(...allValues);
          
          // 绘制热图
          for (let i = 0; i < freqSteps; i++) {
            for (let j = 0; j < timeSteps; j++) {
              const value = eegData.timeFreq.z[i][j];
              const normalized = (value - minVal) / (maxVal - minVal);
              
              // 使用Viridis色系
              const r = Math.floor(255 * (0.267 + 0.004 * normalized));
              const g = Math.floor(255 * (0.004 + 0.5 * normalized));
              const b = Math.floor(255 * (0.329 + 0.6 * normalized));
              
              ctx.fillStyle = `rgb(${r}, ${g}, ${b})`;
              ctx.fillRect(
                padding + j * cellWidth,
                padding + (freqSteps - i - 1) * cellHeight,
                cellWidth + 1,
                cellHeight + 1
              );
            }
          }
          
          // 绘制边框
          ctx.strokeStyle = '#333';
          ctx.lineWidth = 2;
          ctx.strokeRect(padding, padding, plotWidth, plotHeight);
          
          // 绘制坐标轴标签
          ctx.fillStyle = '#333';
          ctx.font = 'bold 14px Arial';
          ctx.textAlign = 'center';
          ctx.fillText('时频域特征图', width / 2, 30);
          
          ctx.font = '12px Arial';
          ctx.fillText('时间 (s)', width / 2, height - 10);
          
          ctx.save();
          ctx.translate(20, height / 2);
          ctx.rotate(-Math.PI / 2);
          ctx.fillText('频率 (Hz)', 0, 0);
          ctx.restore();
          
          // 绘制刻度
          ctx.font = '10px Arial';
          ctx.fillStyle = '#666';
          
          // X轴刻度
          const xTicks = 5;
          for (let i = 0; i <= xTicks; i++) {
            const x = padding + (plotWidth * i) / xTicks;
            const time = ((eegData.timeFreq.x[timeSteps - 1] * i) / xTicks).toFixed(2);
            ctx.textAlign = 'center';
            ctx.fillText(time, x, height - 30);
          }
          
          // Y轴刻度
          const yTicks = 5;
          for (let i = 0; i <= yTicks; i++) {
            const y = padding + (plotHeight * i) / yTicks;
            const freq = ((eegData.timeFreq.y[freqSteps - 1] * (yTicks - i)) / yTicks).toFixed(0);
            ctx.textAlign = 'right';
            ctx.fillText(freq, padding - 10, y + 4);
          }
          
          // 绘制色标
          const legendWidth = 20;
          const legendHeight = plotHeight;
          const legendX = width - 40;
          const legendY = padding;
          
          for (let i = 0; i < legendHeight; i++) {
            const normalized = i / legendHeight;
            const r = Math.floor(255 * (0.267 + 0.004 * normalized));
            const g = Math.floor(255 * (0.004 + 0.5 * normalized));
            const b = Math.floor(255 * (0.329 + 0.6 * normalized));
            
            ctx.fillStyle = `rgb(${r}, ${g}, ${b})`;
            ctx.fillRect(legendX, legendY + legendHeight - i, legendWidth, 2);
          }
          
          ctx.strokeStyle = '#333';
          ctx.lineWidth = 1;
          ctx.strokeRect(legendX, legendY, legendWidth, legendHeight);
          
          // 色标标签
          ctx.fillStyle = '#666';
          ctx.font = '10px Arial';
          ctx.textAlign = 'left';
          ctx.fillText(maxVal.toFixed(0), legendX + legendWidth + 5, legendY + 10);
          ctx.fillText(minVal.toFixed(0), legendX + legendWidth + 5, legendY + legendHeight);
        }
      }, []);
      
      return (
        <div style={{ background: 'white', padding: '20px', display: 'inline-block' }}>
          <canvas ref={canvasRef} width={700} height={350} />
        </div>
      );
    };
    
    return await this.renderChartToBase64(TimeFreqComponent, 750, 400);
  }

  // 生成量表图
  static async generateScaleChart(result: ResultItem): Promise<string> {
    // 使用result.id生成确定性的量表数据
    const rng = new SeededRandom(result.id * 1000 + 2000);
    const scaleData = Array.from({ length: 40 }, (_, i) => ({
      name: `题${i + 1}`,
      score: rng.rangeInt(1, 5)
    }));
    
    const ScaleChartComponent = () => (
      <BarChart width={700} height={350} data={scaleData}>
        <CartesianGrid strokeDasharray="3 3" stroke="#e0e0e0" />
        <XAxis 
          dataKey="name" 
          tick={{ fill: '#333', fontSize: 10 }} 
          interval={4}
        />
        <YAxis domain={[0, 5]} tick={{ fill: '#666' }} label={{ value: '分数', angle: -90, position: 'insideLeft', style: { fill: '#333' } }} />
        <Tooltip 
          contentStyle={{ backgroundColor: '#fff', border: '1px solid #ccc', borderRadius: '4px' }}
        />
        <Legend wrapperStyle={{ paddingTop: '10px' }} />
        <Bar dataKey="score" fill="#4ECDC4" name="量表得分" />
      </BarChart>
    );
    
    return await this.renderChartToBase64(ScaleChartComponent, 750, 400);
  }
  
  // 将React组件渲染为base64图片 - 使用iframe隔离渲染
  private static async renderChartToBase64(
    Component: React.ComponentType, 
    width: number = 600, 
    height: number = 400
  ): Promise<string> {
    return new Promise((resolve, reject) => {
      // 创建隔离的iframe
      const iframe = document.createElement('iframe');
      iframe.style.position = 'absolute';
      iframe.style.left = '-9999px';
      iframe.style.top = '-9999px';
      iframe.style.width = `${width}px`;
      iframe.style.height = `${height}px`;
      iframe.style.border = 'none';
      document.body.appendChild(iframe);
      
      const cleanup = () => {
        if (document.body.contains(iframe)) {
          document.body.removeChild(iframe);
        }
      };
      
      iframe.onload = () => {
        try {
          const iframeDoc = iframe.contentDocument || iframe.contentWindow?.document;
          if (!iframeDoc) {
            cleanup();
            reject(new Error('无法访问iframe文档'));
            return;
          }
          
          // 在iframe中创建容器
          const tempDiv = iframeDoc.createElement('div');
          tempDiv.style.width = `${width}px`;
          tempDiv.style.height = `${height}px`;
          tempDiv.style.backgroundColor = '#ffffff';
          tempDiv.style.padding = '10px';
          tempDiv.style.boxSizing = 'border-box';
          iframeDoc.body.appendChild(tempDiv);
          
          // 在iframe中渲染React组件
          const root = createRoot(tempDiv);
          root.render(React.createElement(Component));
          
          // 等待渲染完成后转换为图片
          setTimeout(async () => {
            try {
              const canvas = await html2canvas(tempDiv, {
                scale: 2,
                useCORS: true,
                backgroundColor: '#ffffff'
              });
              
              const base64 = canvas.toDataURL('image/png');
              cleanup();
              resolve(base64);
            } catch (error) {
              cleanup();
              reject(error);
            }
          }, 1000);
        } catch (error) {
          cleanup();
          reject(error);
        }
      };
      
      // 写入基本HTML结构
      const iframeDoc = iframe.contentDocument || iframe.contentWindow?.document;
      if (iframeDoc) {
        iframeDoc.open();
        iframeDoc.write(`
          <!DOCTYPE html>
          <html>
            <head>
              <meta charset="UTF-8">
              <style>
                body { margin: 0; padding: 0; }
              </style>
            </head>
            <body></body>
          </html>
        `);
        iframeDoc.close();
      }
    });
  }
}