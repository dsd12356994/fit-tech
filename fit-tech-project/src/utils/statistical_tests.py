"""
统计检验模块：验证动量存在性和显著性
包括置换检验、状态转换概率分析等
"""
import numpy as np
import pandas as pd
from typing import Tuple, Dict
from scipy import stats
from tqdm import tqdm


def permutation_test_momentum(observed_statistic: float,
                             win_sequence: np.ndarray,
                             n_permutations: int = 10000,
                             random_seed: int = 42) -> Tuple[float, np.ndarray, Tuple[float, float]]:
    """
    置换检验：验证动量是否显著（非随机）
    
    Parameters:
    -----------
    observed_statistic : float
        观察到的统计量（如最长连胜次数、平均连胜长度等）
    win_sequence : np.ndarray
        胜负序列（1表示获胜，0表示失败）
    n_permutations : int
        置换次数
    random_seed : int
        随机种子
        
    Returns:
    --------
    tuple
        (p值, 零假设分布, 置信区间)
    """
    np.random.seed(random_seed)
    
    null_distribution = np.zeros(n_permutations)
    
    print(f"执行置换检验（{n_permutations}次置换）...")
    for i in tqdm(range(n_permutations)):
        # 随机打乱序列
        shuffled = np.random.permutation(win_sequence)
        # 计算统计量（这里使用最长连胜次数作为示例）
        null_stat = calculate_max_streak(shuffled)
        null_distribution[i] = null_stat
    
    # 计算p值
    p_value = np.mean(null_distribution >= observed_statistic)
    
    # 计算95%置信区间
    ci_lower = np.percentile(null_distribution, 2.5)
    ci_upper = np.percentile(null_distribution, 97.5)
    
    return p_value, null_distribution, (ci_lower, ci_upper)


def calculate_max_streak(win_sequence: np.ndarray) -> int:
    """
    计算最长连胜次数
    
    Parameters:
    -----------
    win_sequence : np.ndarray
        胜负序列
        
    Returns:
    --------
    int
        最长连胜次数
    """
    max_streak = 0
    current_streak = 0
    
    for result in win_sequence:
        if result == 1:
            current_streak += 1
            max_streak = max(max_streak, current_streak)
        else:
            current_streak = 0
    
    return max_streak


def calculate_avg_streak_length(win_sequence: np.ndarray) -> float:
    """
    计算平均连胜长度
    
    Parameters:
    -----------
    win_sequence : np.ndarray
        胜负序列
        
    Returns:
    --------
    float
        平均连胜长度
    """
    streaks = []
    current_streak = 0
    
    for result in win_sequence:
        if result == 1:
            current_streak += 1
        else:
            if current_streak > 0:
                streaks.append(current_streak)
            current_streak = 0
    
    # 处理序列末尾的连胜
    if current_streak > 0:
        streaks.append(current_streak)
    
    return np.mean(streaks) if streaks else 0.0


def test_momentum_significance(df: pd.DataFrame,
                              player: int = 1,
                              n_permutations: int = 10000) -> Dict:
    """
    测试动量显著性
    
    Parameters:
    -----------
    df : pd.DataFrame
        比赛数据
    player : int
        球员编号（1或2）
    n_permutations : int
        置换次数
        
    Returns:
    --------
    dict
        检验结果
    """
    # 提取胜负序列
    win_col = f'p{player}_point_win' if f'p{player}_point_win' in df.columns else None
    
    if win_col is None:
        # 从point_victor推导
        if 'point_victor' in df.columns:
            win_sequence = (df['point_victor'] == player).astype(int).values
        else:
            raise ValueError("无法找到胜负序列")
    else:
        win_sequence = df[win_col].values
    
    # 计算观察到的统计量
    max_streak = calculate_max_streak(win_sequence)
    avg_streak = calculate_avg_streak_length(win_sequence)
    win_rate = win_sequence.mean()
    
    print(f"\nPlayer {player} 统计量:")
    print(f"  最长连胜: {max_streak}")
    print(f"  平均连胜长度: {avg_streak:.2f}")
    print(f"  总胜率: {win_rate:.2%}")
    
    # 执行置换检验
    p_value_max, null_dist_max, ci_max = permutation_test_momentum(
        max_streak, win_sequence, n_permutations
    )
    
    p_value_avg, null_dist_avg, ci_avg = permutation_test_momentum(
        avg_streak, win_sequence, n_permutations
    )
    
    results = {
        'player': player,
        'observed_max_streak': max_streak,
        'observed_avg_streak': avg_streak,
        'win_rate': win_rate,
        'p_value_max_streak': p_value_max,
        'p_value_avg_streak': p_value_avg,
        'ci_max_streak': ci_max,
        'ci_avg_streak': ci_avg,
        'null_distribution_max': null_dist_max,
        'null_distribution_avg': null_dist_avg,
        'is_significant': p_value_max < 0.05 or p_value_avg < 0.05
    }
    
    print(f"\n置换检验结果:")
    print(f"  最长连胜 p值: {p_value_max:.4f} {'***' if p_value_max < 0.001 else '**' if p_value_max < 0.01 else '*' if p_value_max < 0.05 else '(不显著)'}")
    print(f"  平均连胜 p值: {p_value_avg:.4f} {'***' if p_value_avg < 0.001 else '**' if p_value_avg < 0.01 else '*' if p_value_avg < 0.05 else '(不显著)'}")
    
    return results


def analyze_state_transition_probability(momentum_states: np.ndarray) -> Dict:
    """
    分析状态转换概率
    
    Parameters:
    -----------
    momentum_states : np.ndarray
        动量状态序列
        
    Returns:
    --------
    dict
        状态转换分析结果
    """
    n_states = len(np.unique(momentum_states))
    
    # 创建转换矩阵
    transition_matrix = np.zeros((n_states, n_states))
    
    for i in range(len(momentum_states) - 1):
        current_state = int(momentum_states[i])
        next_state = int(momentum_states[i + 1])
        transition_matrix[current_state, next_state] += 1
    
    # 转换为概率
    row_sums = transition_matrix.sum(axis=1, keepdims=True)
    row_sums[row_sums == 0] = 1  # 避免除零
    transition_prob = transition_matrix / row_sums
    
    # 计算状态持续时间
    state_durations = {}
    for state in range(n_states):
        durations = []
        current_duration = 0
        
        for s in momentum_states:
            if s == state:
                current_duration += 1
            else:
                if current_duration > 0:
                    durations.append(current_duration)
                current_duration = 0
        
        if current_duration > 0:
            durations.append(current_duration)
        
        state_durations[state] = {
            'mean': np.mean(durations) if durations else 0,
            'std': np.std(durations) if durations else 0,
            'max': np.max(durations) if durations else 0
        }
    
    results = {
        'transition_matrix': transition_matrix,
        'transition_probability': transition_prob,
        'state_durations': state_durations,
        'n_states': n_states
    }
    
    return results


def chi_square_test_independence(transition_matrix: np.ndarray) -> Tuple[float, float]:
    """
    卡方检验：测试状态转换是否独立
    
    Parameters:
    -----------
    transition_matrix : np.ndarray
        状态转换矩阵
        
    Returns:
    --------
    tuple
        (卡方统计量, p值)
    """
    # 计算期望频数（假设独立）
    row_totals = transition_matrix.sum(axis=1, keepdims=True)
    col_totals = transition_matrix.sum(axis=0, keepdims=True)
    grand_total = transition_matrix.sum()
    
    expected = (row_totals @ col_totals) / grand_total
    
    # 计算卡方统计量
    chi2 = ((transition_matrix - expected) ** 2 / expected).sum()
    
    # 自由度
    df = (transition_matrix.shape[0] - 1) * (transition_matrix.shape[1] - 1)
    
    # p值
    p_value = 1 - stats.chi2.cdf(chi2, df)
    
    return chi2, p_value


def comprehensive_momentum_test(df: pd.DataFrame,
                               momentum_states: np.ndarray = None) -> Dict:
    """
    综合动量检验
    
    Parameters:
    -----------
    df : pd.DataFrame
        比赛数据
    momentum_states : np.ndarray, optional
        动量状态序列
        
    Returns:
    --------
    dict
        综合检验结果
    """
    results = {}
    
    # 1. 测试两个球员的动量显著性
    print("="*60)
    print("测试Player 1的动量显著性")
    print("="*60)
    results['player1'] = test_momentum_significance(df, player=1)
    
    print("\n" + "="*60)
    print("测试Player 2的动量显著性")
    print("="*60)
    results['player2'] = test_momentum_significance(df, player=2)
    
    # 2. 如果有动量状态，分析状态转换
    if momentum_states is not None:
        print("\n" + "="*60)
        print("分析状态转换概率")
        print("="*60)
        
        transition_results = analyze_state_transition_probability(momentum_states)
        results['state_transition'] = transition_results
        
        # 卡方检验
        chi2, p_value = chi_square_test_independence(transition_results['transition_matrix'])
        results['chi_square_test'] = {
            'chi2': chi2,
            'p_value': p_value,
            'is_independent': p_value > 0.05
        }
        
        print(f"\n状态转换独立性检验:")
        print(f"  卡方统计量: {chi2:.4f}")
        print(f"  p值: {p_value:.4f}")
        print(f"  是否独立: {'是' if p_value > 0.05 else '否'}")
    
    return results


if __name__ == "__main__":
    # 示例用法
    print("统计检验模块示例")
    print("="*60)
