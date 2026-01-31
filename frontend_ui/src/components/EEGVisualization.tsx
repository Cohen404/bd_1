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
  time: number[];
  exgData: number[][];
}

const EEGVisualization: React.FC<EEGVisualizationProps> = ({ dataId, personnelId }) => {
  const [eegData, setEEGData] = useState<EEGData | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    const loadEEGData = async () => {
      if (!personnelId) {
        setEEGData(null);
        return;
      }

      try {
        setLoading(true);
        setError(null);

        const md5Response = await fetch(`/api/data/${dataId}`);
        const dataInfo = await md5Response.json();

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
        
        console.log('原始TXT内容长度:', txtContent.length);
        console.log('原始TXT内容前200字符:', txtContent.substring(0, 200));
        
        const lines = txtContent.replace(/\\n/g, '\n').split('\n');
        const channels = Array.from({ length: 16 }, (_, i) => `EXG Channel ${i}`);
        
        const exgData: number[] = [];
        const timeData: number[] = [];
        
        console.log('TXT总行数:', lines.length);
        console.log('前6行:', lines.slice(0, 6));
        
        let sampleCount = 0;
        for (let i = 29; i < lines.length; i++) {
          const line = lines[i].trim();
          console.log(`第${i}行原始内容:`, line);
          
          if (!line || line.startsWith('%')) {
            console.log('跳过空行或注释行');
            continue;
          }
          
          const parts = line.split(',').map(p => p.trim());
          console.log(`第${i}行分割后数量:`, parts.length);
          
          if (parts.length < 17) {
            console.log('分割后数量不足17，跳过');
            continue;
          }
          
          const sampleIndex = parseFloat(parts[0]);
          timeData.push(sampleIndex);
          
          for (let channel = 0; channel < 16; channel++) {
            const value = parseFloat(parts[channel + 1]);
            console.log(`通道${channel}值:`, value, '是否NaN:', isNaN(value));
            if (!isNaN(value)) {
              exgData.push(value);
            }
          }
          
          sampleCount++;
          
          if (sampleCount >= 1) break;
        }

        console.log('提取的数据:', exgData);
        console.log('数据长度:', exgData.length);

        if (exgData.length === 0) {
          setError('未找到有效的数据');
          setLoading(false);
          return;
        }

        const minValue = Math.min(...exgData);
        const maxValue = Math.max(...exgData);
        const normalizedData = exgData.map(value => 
          (value - minValue) / (maxValue - minValue)
        );

        console.log('归一化后的数据:', normalizedData);

        setEEGData({
          channels,
          time: timeData,
          exgData: [normalizedData]
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

  const traces = [{
    x: eegData.channels,
    y: eegData.exgData[0],
    name: '脑电数据',
    mode: 'markers+lines',
    line: { width: 2, color: '#3b82f6' },
    marker: { size: 8, color: '#3b82f6' },
  }];

  const layout = {
    title: '脑电波形图',
    xaxis: { 
      title: '通道',
      tickmode: 'array',
      tickvals: eegData.channels,
      ticktext: eegData.channels
    },
    yaxis: { title: '归一化值', range: [0, 1] },
    hovermode: 'closest',
    showlegend: false,
    autosize: true,
    margin: { l: 60, r: 30, t: 50, b: 60 },
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