"""
比分转换工具：将网球比分字符串转换为数值型
"""
import numpy as np
import pandas as pd
from typing import Union, Dict


class ScoreConverter:
    """网球比分转换器"""
    
    def __init__(self, score_mapping: Dict[str, int] = None):
        """
        初始化比分转换器
        
        Parameters:
        -----------
        score_mapping : dict, optional
            比分映射字典，默认使用标准网球比分
        """
        if score_mapping is None:
            self.score_mapping = {
                "0": 0,
                "15": 1,
                "30": 2,
                "40": 3,
                "AD": 4,
                "Love": 0
            }
        else:
            self.score_mapping = score_mapping
    
    def convert_score(self, score: Union[str, int, float]) -> Union[int, float]:
        """
        将单个比分字符串转换为数值
        
        Parameters:
        -----------
        score : str, int, float
            比分值
            
        Returns:
        --------
        int or float
            转换后的数值，如果无法转换返回np.nan
        """
        if pd.isna(score):
            return np.nan
        
        # 如果已经是数值型，直接返回
        if isinstance(score, (int, float)):
            return float(score)
        
        # 转换为字符串并去除空格
        score_str = str(score).strip()
        
        # 查找映射
        if score_str in self.score_mapping:
            return self.score_mapping[score_str]
        
        # 尝试直接转换为数值
        try:
            return float(score_str)
        except ValueError:
            return np.nan
    
    def convert_series(self, series: pd.Series) -> pd.Series:
        """
        将pandas Series中的比分转换为数值型
        
        Parameters:
        -----------
        series : pd.Series
            包含比分的Series
            
        Returns:
        --------
        pd.Series
            转换后的数值型Series
        """
        return series.apply(self.convert_score)
    
    def convert_dataframe_scores(self, df: pd.DataFrame, 
                                  score_columns: list = None) -> pd.DataFrame:
        """
        转换DataFrame中的比分列
        
        Parameters:
        -----------
        df : pd.DataFrame
            包含比分列的DataFrame
        score_columns : list, optional
            需要转换的列名列表，默认自动检测p1_score和p2_score
            
        Returns:
        --------
        pd.DataFrame
            转换后的DataFrame，新增*_num列
        """
        df = df.copy()
        
        if score_columns is None:
            score_columns = [col for col in df.columns if 'score' in col.lower()]
        
        for col in score_columns:
            if col in df.columns:
                new_col_name = f"{col}_num"
                df[new_col_name] = self.convert_series(df[col])
        
        return df


def convert_elapsed_time(time_str: str) -> float:
    """
    将elapsed_time字符串转换为秒数
    
    Parameters:
    -----------
    time_str : str
        时间字符串，格式如 "00:15:30" (HH:MM:SS)
        
    Returns:
    --------
    float
        总秒数
    """
    if pd.isna(time_str):
        return np.nan
    
    try:
        parts = str(time_str).strip().split(':')
        if len(parts) == 3:
            hours, minutes, seconds = map(int, parts)
            return hours * 3600 + minutes * 60 + seconds
        elif len(parts) == 2:
            minutes, seconds = map(int, parts)
            return minutes * 60 + seconds
        else:
            return float(time_str)
    except (ValueError, AttributeError):
        return np.nan
