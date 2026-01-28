// utils/reportGenerator.ts
import jsPDF from 'jspdf';
import html2canvas from 'html2canvas';
import { ResultItem } from './localStorage';

export interface ReportData {
  result: ResultItem;
  user: {
    username: string;
    user_type: string;
  };
  charts: {
    eeg: string;             // 脑电功率图base64
    timeDomain: string;      // 时域特征图base64
    frequencyBand: string;   // 频带特征图base64
    diffEntropy: string;     // 微分熵特征图base64
    timeFreq: string;        // 时频域特征图base64
    serum: string;           // 血清图base64
  };
}

export class ReportGenerator {
  // 生成报告HTML模板
  static createReportHTML(data: ReportData): string {
    const { result, user, charts } = data;
    
    return `
      <!DOCTYPE html>
      <html>
      <head>
        <meta charset="UTF-8">
        <style>
          * { 
            margin: 0; 
            padding: 0; 
            box-sizing: border-box; 
          }
          
          body { 
            font-family: 'Microsoft YaHei', 'SimHei', Arial, sans-serif; 
            line-height: 1.6;
            color: #333;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            padding: 40px;
          }
          
          .report-container {
            max-width: 1200px;
            margin: 0 auto;
            background: white;
            border-radius: 20px;
            box-shadow: 0 20px 60px rgba(0, 0, 0, 0.3);
            overflow: hidden;
          }
          
          .header { 
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            text-align: center; 
            padding: 50px 40px;
            position: relative;
          }
          
          .header::after {
            content: '';
            position: absolute;
            bottom: 0;
            left: 0;
            right: 0;
            height: 4px;
            background: linear-gradient(90deg, #ffd700, #ff6b6b, #4ecdc4, #45b7d1);
          }
          
          .header h1 {
            font-size: 42px;
            font-weight: bold;
            margin-bottom: 15px;
            text-shadow: 2px 2px 4px rgba(0, 0, 0, 0.2);
          }
          
          .header .subtitle {
            font-size: 16px;
            opacity: 0.95;
            margin-top: 10px;
          }
          
          .content {
            padding: 40px;
          }
          
          .section { 
            background: white;
            padding: 40px;
            box-sizing: border-box;
            position: relative;
          }
          
          .section-content {
            background: #f8f9fa;
            border-radius: 15px;
            padding: 30px;
            box-shadow: 0 2px 10px rgba(0, 0, 0, 0.05);
          }
          
          .section-title {
            font-size: 26px;
            font-weight: bold;
            color: #667eea;
            margin-bottom: 25px;
            padding-bottom: 15px;
            border-bottom: 3px solid #667eea;
            display: flex;
            align-items: center;
          }
          
          .section-title::before {
            content: '';
            display: inline-block;
            width: 8px;
            height: 30px;
            background: linear-gradient(135deg, #667eea, #764ba2);
            margin-right: 15px;
            border-radius: 4px;
          }
          
          .info-grid {
            display: grid;
            grid-template-columns: repeat(2, 1fr);
            gap: 20px;
            margin-top: 20px;
          }
          
          .info-item {
            background: white;
            padding: 15px 20px;
            border-radius: 10px;
            border-left: 4px solid #667eea;
            box-shadow: 0 2px 5px rgba(0, 0, 0, 0.05);
          }
          
          .info-item label {
            font-weight: bold;
            color: #666;
            font-size: 14px;
            display: block;
            margin-bottom: 5px;
          }
          
          .info-item value {
            font-size: 16px;
            color: #333;
            font-weight: 500;
          }
          
          .score-grid {
            display: grid;
            grid-template-columns: repeat(2, 1fr);
            gap: 20px;
            margin-top: 20px;
          }
          
          .score-card {
            background: white;
            padding: 25px;
            border-radius: 12px;
            box-shadow: 0 4px 15px rgba(0, 0, 0, 0.08);
            transition: transform 0.3s ease;
          }
          
          .score-card:hover {
            transform: translateY(-5px);
          }
          
          .score-card-title {
            font-size: 16px;
            color: #666;
            margin-bottom: 12px;
            font-weight: 500;
          }
          
          .score-value {
            font-size: 36px;
            font-weight: bold;
            margin-bottom: 8px;
          }
          
          .score-label {
            font-size: 14px;
            padding: 5px 15px;
            border-radius: 20px;
            display: inline-block;
            font-weight: 500;
          }
          
          .risk-high { 
            color: #e74c3c;
          }
          
          .risk-high .score-label {
            background: #fee;
            color: #e74c3c;
          }
          
          .risk-medium { 
            color: #f39c12;
          }
          
          .risk-medium .score-label {
            background: #fff3e0;
            color: #f39c12;
          }
          
          .risk-low { 
            color: #27ae60;
          }
          
          .risk-low .score-label {
            background: #e8f5e9;
            color: #27ae60;
          }
          
          .chart-container { 
            text-align: center; 
            margin: 30px 0;
            background: white;
            padding: 25px;
            border-radius: 12px;
            box-shadow: 0 2px 10px rgba(0, 0, 0, 0.05);
            page-break-inside: avoid;
            break-inside: avoid;
          }
          
          .chart-title {
            font-size: 18px;
            font-weight: 600;
            color: #444;
            margin-bottom: 20px;
            padding-bottom: 10px;
            border-bottom: 2px solid #e0e0e0;
          }
          
          .chart-container img { 
            max-width: 100%; 
            height: auto;
            border-radius: 8px;
            page-break-inside: avoid;
            break-inside: avoid;
            display: block;
            margin: 0 auto;
          }
          
          .charts-grid {
            display: grid;
            grid-template-columns: 1fr;
            gap: 25px;
          }
          
          .recommendation-box {
            background: linear-gradient(135deg, #667eea15, #764ba215);
            border-left: 5px solid #667eea;
            padding: 25px;
            border-radius: 10px;
            margin-top: 20px;
          }
          
          .recommendation-box h3 {
            color: #667eea;
            font-size: 18px;
            margin-bottom: 15px;
          }
          
          .recommendation-box p {
            color: #555;
            line-height: 1.8;
            font-size: 15px;
          }
          
          .footer {
            background: #f8f9fa;
            padding: 30px;
            text-align: center;
            color: #666;
            font-size: 14px;
            border-top: 1px solid #e0e0e0;
          }
          
          .divider {
            height: 3px;
            background: linear-gradient(90deg, #667eea, #764ba2);
            margin: 40px 0;
            border-radius: 2px;
          }
          
          @media print {
            body { 
              background: white;
              padding: 0;
            }
            .report-container {
              box-shadow: none;
            }
          }
        </style>
      </head>
      <body>
        <div class="report-container">
          <div class="header">
            <h1>🧠 心理健康评估报告</h1>
            <div class="subtitle">Mental Health Assessment Report</div>
            <div class="subtitle">报告生成时间：${new Date().toLocaleString('zh-CN', { 
              year: 'numeric', 
              month: 'long', 
              day: 'numeric', 
              hour: '2-digit', 
              minute: '2-digit' 
            })}</div>
          </div>
          
          <div class="content">
            <!-- 第1页：基本信息 + 评估结果 -->
            <div class="section">
              <div class="section-content">
                <h2 class="section-title">📋 基本信息</h2>
                <div class="info-grid">
                  <div class="info-item">
                    <label>姓名</label>
                    <value>${result.personnel_name || '未知'}</value>
                  </div>
                  <div class="info-item">
                    <label>人员编号</label>
                    <value>${result.personnel_id || '未知'}</value>
                  </div>
                  <div class="info-item">
                    <label>用户账号</label>
                    <value>${user?.username || '未知'}</value>
                  </div>
                  <div class="info-item">
                    <label>评估时间</label>
                    <value>${new Date(result.result_time).toLocaleString('zh-CN')}</value>
                  </div>
                </div>
              </div>
              
              <div class="section-content" style="margin-top: 30px;">
                <h2 class="section-title">📊 评估结果</h2>
                <div class="score-grid">
                  <div class="score-card ${this.getRiskClass(result.stress_score)}">
                    <div class="score-card-title">应激评分</div>
                    <div class="score-value">${result.stress_score.toFixed(1)}</div>
                    <span class="score-label">${this.getRiskLevel(result.stress_score)}</span>
                  </div>
                  <div class="score-card ${this.getRiskClass(result.depression_score)}">
                    <div class="score-card-title">抑郁评分</div>
                    <div class="score-value">${result.depression_score.toFixed(1)}</div>
                    <span class="score-label">${this.getRiskLevel(result.depression_score)}</span>
                  </div>
                  <div class="score-card ${this.getRiskClass(result.anxiety_score)}">
                    <div class="score-card-title">焦虑评分</div>
                    <div class="score-value">${result.anxiety_score.toFixed(1)}</div>
                    <span class="score-label">${this.getRiskLevel(result.anxiety_score)}</span>
                  </div>
                  <div class="score-card ${this.getRiskClass(result.social_isolation_score)}">
                    <div class="score-card-title">社交孤立评分</div>
                    <div class="score-value">${result.social_isolation_score.toFixed(1)}</div>
                    <span class="score-label">${this.getRiskLevel(result.social_isolation_score)}</span>
                  </div>
                </div>
              </div>
            </div>
            
            <!-- 第2页：脑电信号分析（脑电功率频谱 + 时域特征） -->
            <div class="section">
              <div class="section-content" style="padding: 20px;">
                <h2 class="section-title" style="margin-bottom: 15px;">🧠 脑电信号（EEG）分析</h2>
                <div class="charts-grid" style="gap: 15px;">
                  <div class="chart-container" style="margin: 10px 0; padding: 15px;">
                    <div class="chart-title" style="margin-bottom: 10px; font-size: 16px;">脑电功率频谱分析</div>
                    <img src="${charts.eeg}" alt="脑电功率图" style="max-height: 380px; object-fit: contain;" />
                    <p style="color: #666; font-size: 12px; margin-top: 8px;">
                      展示各通道的Theta、Alpha、Beta、Gamma波功率分布
                    </p>
                  </div>
                  
                  <div class="chart-container" style="margin: 10px 0; padding: 15px;">
                    <div class="chart-title" style="margin-bottom: 10px; font-size: 16px;">时域特征分析</div>
                    <img src="${charts.timeDomain}" alt="时域特征图" style="max-height: 380px; object-fit: contain;" />
                    <p style="color: #666; font-size: 12px; margin-top: 8px;">
                      包括过零率、方差、能量、差分等时域特征指标
                    </p>
                  </div>
                </div>
              </div>
            </div>
            
            <!-- 第3页：脑电信号分析（频带特征 + 微分熵） -->
            <div class="section">
              <div class="section-content" style="padding: 20px;">
                <h2 class="section-title" style="margin-bottom: 15px;">🧠 脑电信号（EEG）分析（续）</h2>
                <div class="charts-grid" style="gap: 15px;">
                  <div class="chart-container" style="margin: 10px 0; padding: 15px;">
                    <div class="chart-title" style="margin-bottom: 10px; font-size: 16px;">频带特征分析</div>
                    <img src="${charts.frequencyBand}" alt="频带特征图" style="max-height: 380px; object-fit: contain;" />
                    <p style="color: #666; font-size: 12px; margin-top: 8px;">
                      展示各频带的能量分布情况
                    </p>
                  </div>
                  
                  <div class="chart-container" style="margin: 10px 0; padding: 15px;">
                    <div class="chart-title" style="margin-bottom: 10px; font-size: 16px;">微分熵特征分析</div>
                    <img src="${charts.diffEntropy}" alt="微分熵图" style="max-height: 380px; object-fit: contain;" />
                    <p style="color: #666; font-size: 12px; margin-top: 8px;">
                      微分熵反映信号的复杂度和不确定性
                    </p>
                  </div>
                </div>
              </div>
            </div>
            
            <!-- 第4页：时频域特征分析 -->
            <div class="section">
              <div class="section-content">
                <h2 class="section-title">🧠 脑电信号（EEG）分析（续）</h2>
                <div class="charts-grid">
                  <div class="chart-container">
                    <div class="chart-title">时频域特征分析</div>
                    <img src="${charts.timeFreq}" alt="时频域特征图" style="max-height: 600px; object-fit: contain;" />
                    <p style="color: #666; font-size: 13px; margin-top: 10px;">
                      展示信号在时间和频率域的联合分布特征
                    </p>
                  </div>
                </div>
              </div>
            </div>
            
            <!-- 第5页：血清指标分析 -->
            <div class="section">
              <div class="section-content">
                <h2 class="section-title">🔬 血清指标分析</h2>
                <div class="chart-container">
                  <div class="chart-title">炎症标志物检测</div>
                  <img src="${charts.serum}" alt="血清图" style="max-height: 600px; object-fit: contain;" />
                  <p style="color: #666; font-size: 13px; margin-top: 10px;">
                    包括CRP、IL-6、TNF-α、LDH、CK等炎症相关指标
                  </p>
                </div>
              </div>
            </div>
            
            <!-- 第6页：综合评估与建议 -->
            <div class="section">
              <div class="section-content">
                <h2 class="section-title">💡 综合评估与建议</h2>
                <div class="recommendation-box">
                  <h3>总体风险等级</h3>
                  <p><strong style="font-size: 18px; color: #667eea;">${this.calculateOverallRiskLevel(result)}</strong></p>
                </div>
                <div class="recommendation-box" style="margin-top: 20px;">
                  <h3>专业建议</h3>
                  <p>${result.recommendations || '建议定期进行心理健康评估，保持良好的生活作息，如有需要请咨询专业心理医生。'}</p>
                </div>
              </div>
            </div>
          </div>
          
          <div class="footer">
            <p>本报告由急进高原新兵心理应激多模态神经生理监测预警系统自动生成</p>
            <p style="margin-top: 10px; font-size: 12px;">
              报告内容仅供参考，具体诊断请咨询专业医疗机构
            </p>
          </div>
        </div>
      </body>
      </html>
    `;
  }
  
  // 生成PDF - 使用iframe隔离渲染，避免影响主页面
  static async generatePDF(htmlContent: string, filename: string): Promise<void> {
    // 创建隔离的iframe
    const iframe = document.createElement('iframe');
    iframe.style.position = 'absolute';
    iframe.style.left = '-9999px';
    iframe.style.top = '-9999px';
    iframe.style.width = '794px'; // A4宽度（210mm = 794px at 96dpi）
    iframe.style.height = '1123px'; // A4高度（297mm = 1123px at 96dpi）
    iframe.style.border = 'none';
    document.body.appendChild(iframe);
    
    try {
      // 等待iframe加载完成
      await new Promise<void>((resolve) => {
        iframe.onload = () => resolve();
        // 写入HTML内容到iframe
        const iframeDoc = iframe.contentDocument || iframe.contentWindow?.document;
        if (!iframeDoc) {
          throw new Error('无法访问iframe文档');
        }
        iframeDoc.open();
        iframeDoc.write(htmlContent);
        iframeDoc.close();
      });
      
      const iframeDoc = iframe.contentDocument || iframe.contentWindow?.document;
      if (!iframeDoc) {
        throw new Error('无法访问iframe文档');
      }
      
      const pdf = new jsPDF({
        orientation: 'portrait',
        unit: 'mm',
        format: 'a4'
      });
      
      // 获取所有section（每个section是一页）
      const sections = iframeDoc.querySelectorAll('.section');
      
      if (sections.length === 0) {
        throw new Error('未找到任何页面内容');
      }
      
      // 逐页渲染
      for (let i = 0; i < sections.length; i++) {
        const section = sections[i] as HTMLElement;
        
        // 转换为Canvas（直接在iframe中渲染）
        const canvas = await html2canvas(section, {
          scale: 2,
          useCORS: true,
          allowTaint: true,
          width: 794,
          height: 1123,
          windowWidth: 794,
          windowHeight: 1123,
          backgroundColor: '#ffffff'
        });
        
        // 添加到PDF
        if (i > 0) {
          pdf.addPage();
        }
        
        const imgData = canvas.toDataURL('image/png');
        const imgWidth = 210; // A4宽度（mm）
        const imgHeight = 297; // A4高度（mm）
        
        pdf.addImage(imgData, 'PNG', 0, 0, imgWidth, imgHeight);
      }
      
      // 下载PDF
      pdf.save(filename);
      
    } catch (error) {
      console.error('PDF生成失败:', error);
      throw error;
    } finally {
      // 清理iframe
      document.body.removeChild(iframe);
    }
  }
  
  private static getRiskClass(score: number): string {
    if (score >= 50) return 'risk-high';
    if (score >= 30) return 'risk-medium';
    return 'risk-low';
  }
  
  private static getRiskLevel(score: number): string {
    if (score >= 50) return '高风险';
    if (score >= 30) return '中等风险';
    return '正常';
  }
  
  private static calculateOverallRiskLevel(result: ResultItem): string {
    const averageScore = (
      result.stress_score + 
      result.depression_score + 
      result.anxiety_score + 
      result.social_isolation_score
    ) / 4;
    
    if (averageScore >= 50) return '高风险';
    if (averageScore >= 30) return '中等风险';
    return '低风险';
  }
}