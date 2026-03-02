"""
评估指标工具函数
"""
import numpy as np
from typing import List, Tuple
from scipy import stats


def calculate_momentum_score(win_sequence: np.ndarray, 
                            window_size: int = 5) -> np.ndarray:
    """
    计算动量得分
    
    Parameters:
    -----------
    win_sequence : np.ndarray
        胜负序列（1表示获胜，0表示失败）
    window_size : int
        滚动窗口大小
        
    Returns:
    --------
    np.ndarray
        动量得分序列
    """
    momentum = np.convolve(win_sequence, 
                          np.ones(window_size) / window_size, 
                          mode='same')
    return momentum


def calculate_win_streak(win_sequence: np.ndarray) -> np.ndarray:
    """
    计算连胜次数
    
    Parameters:
    -----------
    win_sequence : np.ndarray
        胜负序列
        
    Returns:
    --------
    np.ndarray
        每个点的连胜次数
    """
    streak = np.zeros_like(win_sequence, dtype=int)
    current_streak = 0
    
    for i in range(len(win_sequence)):
        if win_sequence[i] == 1:
            current_streak += 1
        else:
            current_streak = 0
        streak[i] = current_streak
    
    return streak


def permutation_test(observed_statistic: float, 
                     null_distribution: np.ndarray) -> Tuple[float, float]:
    """
    置换检验（Permutation Test）
    
    Parameters:
    -----------
    observed_statistic : float
        观察到的统计量
    null_distribution : np.ndarray
        零假设下的统计量分布
        
    Returns:
    --------
    tuple
        (p值, 置信区间)
    """
    p_value = np.mean(null_distribution >= observed_statistic)
    ci_lower = np.percentile(null_distribution, 2.5)
    ci_upper = np.percentile(null_distribution, 97.5)
    
    return p_value, (ci_lower, ci_upper)


def calculate_key_point_impact(df, point_type: str = 'break_pt') -> dict:
    """
    计算关键分的影响
    
    Parameters:
    -----------
    df : pd.DataFrame
        比赛数据
    point_type : str
        关键分类型：'break_pt', 'set_point', 'match_point'
        
    Returns:
    --------
    dict
        关键分统计信息
    """
    # 这里需要根据实际数据结构实现
    # 示例框架
    stats_dict = {
        'total_count': 0,
        'conversion_rate': 0.0,
        'momentum_shift_probability': 0.0
    }
    
    return stats_dict
