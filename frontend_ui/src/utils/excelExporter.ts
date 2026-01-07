// utils/excelExporter.ts
import * as XLSX from 'xlsx';
import { Result } from '@/types';

export class ExcelExporter {
  /**
   * 导出评估结果到Excel
   * @param results 要导出的结果数组
   * @param filename 导出的文件名（不包含扩展名）
   */
  static exportResults(results: Result[], filename: string = '评估结果导出'): void {
    // 准备导出数据
    const exportData = results.map(result => {
      // 计算最大分数以确定状态
      const maxScore = Math.max(
        result.stress_score,
        result.depression_score,
        result.anxiety_score,
        result.social_isolation_score
      );
      
      // 确定状态
      let status = '正常';
      if (maxScore >= 50) {
        status = '高风险';
      } else if (maxScore >= 30) {
        status = '中等风险';
      }
      
      return {
        '结果ID': result.id,
        '人员ID': result.personnel_id || 'unknown',
        '人员姓名': result.personnel_name || '心理健康评估数据',
        '应激': result.stress_score.toFixed(1),
        '抑郁': result.depression_score.toFixed(1),
        '焦虑': result.anxiety_score.toFixed(1),
        '社交': result.social_isolation_score.toFixed(1),
        '状态': status,
        '评估时间': new Date(result.result_time).toLocaleString('zh-CN', {
          year: 'numeric',
          month: '2-digit',
          day: '2-digit',
          hour: '2-digit',
          minute: '2-digit',
          second: '2-digit'
        }).replace(/\//g, '/')
      };
    });
    
    // 创建工作簿
    const worksheet = XLSX.utils.json_to_sheet(exportData);
    
    // 设置列宽
    const columnWidths = [
      { wch: 10 }, // 结果ID
      { wch: 15 }, // 人员ID
      { wch: 20 }, // 人员姓名
      { wch: 10 }, // 应激
      { wch: 10 }, // 抑郁
      { wch: 10 }, // 焦虑
      { wch: 10 }, // 社交
      { wch: 12 }, // 状态
      { wch: 20 }  // 评估时间
    ];
    worksheet['!cols'] = columnWidths;
    
    const workbook = XLSX.utils.book_new();
    XLSX.utils.book_append_sheet(workbook, worksheet, '评估结果');
    
    // 生成文件名（带时间戳）
    const timestamp = new Date().toLocaleString('zh-CN', {
      year: 'numeric',
      month: '2-digit',
      day: '2-digit',
      hour: '2-digit',
      minute: '2-digit',
      second: '2-digit'
    }).replace(/[/:]/g, '-').replace(/\s/g, '_');
    
    const fullFilename = `${filename}_${timestamp}.xlsx`;
    
    // 导出文件
    XLSX.writeFile(workbook, fullFilename);
  }
}

