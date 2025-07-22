import os
import pandas as pd
import logging
import traceback

class ResultProcessor:
    """
    评估结果后处理类
    处理三种不同类型的评估结果：普通应激、抑郁、焦虑
    """
    
    @staticmethod
    def process_result(result_type, probability_score, data_path):
        """
        处理评估结果
        
        Args:
            result_type (int): 结果类型 (0: 普通应激, 1: 抑郁, 2: 焦虑)
            probability_score (float): 模型输出的概率分数 (0-95)
            data_path (str): 数据路径，用于读取量表和血清学数据
            
        Returns:
            float: 最终评估分数 (0-95)
        """
        try:
            # 初始化分数
            score_lb_1 = 0  # 量表1分数
            score_lb_2 = 0  # 量表2分数
            score_xq = 0    # 血清学分数
            
            # 处理量表数据
            lb_path = os.path.join(data_path, 'lb.csv')
            if os.path.exists(lb_path):
                try:
                    df = pd.read_csv(lb_path)
                    if len(df) >= 1:
                        # 计算前20列总和
                        first_20_sum = df.iloc[0, :20].sum()
                        score_lb_1 = (first_20_sum - 48) / 80 * 3
                        
                        # 计算后20列总和
                        last_20_sum = df.iloc[0, 20:40].sum()
                        score_lb_2 = (last_20_sum - 53) / 80 * 3
                        
                        logging.info(f"量表数据处理完成: score_lb_1={score_lb_1}, score_lb_2={score_lb_2}")
                except Exception as e:
                    logging.error(f"处理量表数据时发生错误: {str(e)}")
                    logging.error(traceback.format_exc())
            
            # 处理血清学数据
            xq_path = os.path.join(data_path, 'xq.csv')
            if os.path.exists(xq_path):
                try:
                    df = pd.read_csv(xq_path)
                    if len(df) >= 1:
                        def clean_value(val):
                            if isinstance(val, str):
                                val = val.replace('<', '').replace('>', '').replace('≤', '').replace('≥', '')
                            try:
                                return float(val)
                            except:
                                return 0
                        
                        # 应用清理函数并求和
                        xq_sum = sum(clean_value(val) for val in df.iloc[0])
                        score_xq = xq_sum / 5000
                        logging.info(f"血清学数据处理完成: score_xq={score_xq}")
                except Exception as e:
                    logging.error(f"处理血清学数据时发生错误: {str(e)}")
                    logging.error(traceback.format_exc())
            
            # 根据不同类型计算最终分数
            final_score = probability_score
            if result_type == 0:  # 普通应激
                final_score = probability_score + score_xq
            elif result_type == 1:  # 抑郁
                final_score = probability_score + score_lb_1
            elif result_type == 2:  # 焦虑
                final_score = probability_score + score_lb_2
            
            # 确保最终分数在0-95之间
            final_score = float(min(95, max(0, final_score)))
            
            return final_score
            
        except Exception as e:
            logging.error(f"结果处理过程中发生错误: {str(e)}")
            logging.error(traceback.format_exc())
            return probability_score  # 如果处理出错，返回原始分数 