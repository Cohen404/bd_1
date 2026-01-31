import React, { useState, useEffect } from 'react';
import Plot from 'react-plotly.js';

interface EEGVisualizationProps {
  dataId?: number;
  personnelId?: string;
}

interface ExcelRecord {
  序号: number;
  脑电采集时间: string;
  文件名: string;
}

interface EEGData {
  channels: string[];
  fftData: {
    frequencies: number[];
    magnitudes: number[][];
  };
}

const EEGVisualization: React.FC<EEGVisualizationProps> = ({ dataId, personnelId }) => {
  const [eegData, setEEGData] = useState<EEGData | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const computeFFT = (data: number[]): number[] => {
    const N = data.length;
    const result: number[] = new Array(N * 2).fill(0);
    
    for (let k = 0; k < N; k++) {
      let realSum = 0;
      let imagSum = 0;
      
      for (let n = 0; n < N; n++) {
        const angle = (2 * Math.PI * k * n) / N;
        const cos = Math.cos(angle);
        const sin = Math.sin(angle);
        
        realSum += data[n] * cos;
        imagSum -= data[n] * sin;
      }
      
      result[k * 2] = realSum;
      result[k * 2 + 1] = imagSum;
    }
    
    return result;
  };

  useEffect(() => {
    const loadEEGData = async () => {
      if (!personnelId) {
        setEEGData(null);
        return;
      }

      try {
        setLoading(true);
        setError(null);

        const excelResponse = await fetch('/api/eegs/excel');
        const excelData = await excelResponse.json();
        
        const matchedRecord = excelData.find((record: ExcelRecord) => record.序号 === parseInt(personnelId));
        
        if (!matchedRecord) {
          setError(`未找到人员编号为${personnelId}的采集记录`);
          setLoading(false);
          return;
        }

        const filename = matchedRecord.文件名;

        const txtResponse = await fetch(`/api/eegs/txt?filename=${encodeURIComponent(filename)}`);
        const txtContent = await txtResponse.text();
        
        const lines = txtContent.replace(/\\n/g, '\n').split('\n');
        const channels = Array.from({ length: 16 }, (_, i) => `EXG Channel ${i}`);
        
        const channelData: number[][] = Array.from({ length: 16 }, () => []);
        
        let sampleCount = 0;
        for (let i = 5; i < lines.length; i++) {
          const line = lines[i].trim();
          if (!line || line.startsWith('%')) continue;
          
          const parts = line.split(',').map(p => p.trim());
          if (parts.length < 17) continue;
          
          for (let channel = 0; channel < 16; channel++) {
            const value = parseFloat(parts[channel + 1]);
            if (!isNaN(value)) {
              channelData[channel].push(value);
            }
          }
          
          sampleCount++;
          if (sampleCount >= 10000) break;
        }

        console.log('每个通道的数据量:', channelData.map(d => d.length));

        const fftSize = 1024;
        const sampleRate = 1000;
        
        const frequencies: number[] = [];
        const magnitudes: number[][] = Array.from({ length: 16 }, () => []);
        
        for (let channel = 0; channel < 16; channel++) {
          const data = channelData[channel];
          
          const mean = data.reduce((sum, val) => sum + val, 0) / data.length;
          const detrendedData = data.map(val => val - mean);
          
          const paddedData = new Array(fftSize).fill(0);
          for (let i = 0; i < Math.min(detrendedData.length, fftSize); i++) {
            const window = 0.5 * (1 - Math.cos(2 * Math.PI * i / fftSize));
            paddedData[i] = detrendedData[i] * window;
          }
          
          const fftResult = computeFFT(paddedData);
          const channelMagnitudes: number[] = [];
          
          for (let i = 0; i < fftSize / 2; i++) {
            const freq = (i * sampleRate) / fftSize;
            frequencies.push(freq);
            
            const magnitude = Math.sqrt(fftResult[i * 2] ** 2 + fftResult[i * 2 + 1] ** 2);
            const normalizedMagnitude = magnitude / (fftSize / 2);
            const dbMagnitude = 20 * Math.log10(normalizedMagnitude + 1e-10);
            channelMagnitudes.push(dbMagnitude);
          }
          
          magnitudes[channel] = channelMagnitudes;
        }

        const uniqueFrequencies = [...new Set(frequencies)].sort((a, b) => a - b).slice(0, fftSize / 2);

        setEEGData({
          channels,
          fftData: {
            frequencies: uniqueFrequencies,
            magnitudes: magnitudes
          }
        });
      } catch (err) {
        console.error('加载EEG数据失败:', err);
        setError('加载数据失败，请重试');
      } finally {
        setLoading(false);
      }
    };

    loadEEGData();
  }, [personnelId]);

  if (loading) {
    return (
      <div className="flex items-center justify-center py-8">
        <div className="text-gray-500">加载中...</div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="flex items-center justify-center py-8">
        <div className="text-red-500">{error}</div>
      </div>
    );
  }

  if (!eegData) {
    return (
      <div className="flex items-center justify-center py-8">
        <div className="text-gray-500">请选择数据</div>
      </div>
    );
  }

  const traces = eegData.channels.map((channel, index) => ({
    x: eegData.fftData.frequencies,
    y: eegData.fftData.magnitudes[index],
    name: channel,
    mode: 'lines',
    line: { width: 1 },
  }));

  const layout = {
    title: 'FFT频谱图 (0-15通道)',
    xaxis: { 
      title: '频率 (Hz)',
      type: 'log',
      autorange: true
    },
    yaxis: { 
      title: '幅度 (dB)',
      autorange: true
    },
    hovermode: 'closest',
    showlegend: true,
    legend: { 
      x: 0.02, 
      y: 1,
      bgcolor: 'rgba(255, 255, 255, 0.8)',
      bordercolor: '#444',
      borderwidth: 1
    },
    autosize: true,
    margin: { l: 80, r: 30, t: 50, b: 60 },
  };

  const config = {
    responsive: true,
    displayModeBar: true,
    displaylogo: false,
  };

  return (
    <div className="w-full h-full">
      <Plot
        data={traces}
        layout={layout}
        config={config}
        style={{ width: '100%', height: '100%' }}
      />
    </div>
  );
};

export default EEGVisualization;
