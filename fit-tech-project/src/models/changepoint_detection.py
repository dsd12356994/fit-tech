"""
转折点检测：使用PELT算法检测动量转折点
"""
import pandas as pd
import numpy as np
from pathlib import Path
import sys
import ruptures as rpt

sys.path.append(str(Path(__file__).parent.parent.parent))

from config import FEATURES_DATA_PATH, CHANGEPOINT_RESULTS_PATH, CHANGEPOINT_CONFIG


class ChangepointDetector:
    """转折点检测器"""
    
    def __init__(self, config: dict = None):
        """
        初始化转折点检测器
        
        Parameters:
        -----------
        config : dict, optional
            配置字典
        """
        self.config = config or CHANGEPOINT_CONFIG
        self.detector = None
    
    def prepare_signal(self, df: pd.DataFrame, 
                      signal_column: str = 'p1_momentum_score') -> np.ndarray:
        """
        准备检测信号
        
        Parameters:
        -----------
        df : pd.DataFrame
            数据
        signal_column : str
            用于检测的信号列名
            
        Returns:
        --------
        np.ndarray
            信号序列
        """
        if signal_column not in df.columns:
            # 如果没有指定列，使用滚动胜率
            if 'p1_rolling_win_rate' in df.columns:
                signal_column = 'p1_rolling_win_rate'
            else:
                raise ValueError(f"找不到信号列: {signal_column}")
        
        signal = df[signal_column].values
        
        # 处理缺失值
        signal = np.nan_to_num(signal, nan=0.0)
        
        return signal
    
    def detect_changepoints(self, signal: np.ndarray, 
                           max_changepoints: int = None) -> np.ndarray:
        """
        检测转折点
        
        Parameters:
        -----------
        signal : np.ndarray
            信号序列
        max_changepoints : int, optional
            最大转折点数量
            
        Returns:
        --------
        np.ndarray
            转折点位置数组
        """
        # 创建检测器
        model = self.config.get('model', 'rbf')
        min_size = self.config.get('min_size', 5)
        pen = self.config.get('pen', 10)
        
        algo = rpt.Pelt(model=model, min_size=min_size).fit(signal.reshape(-1, 1))
        
        if max_changepoints is None:
            # 自动检测转折点数量
            changepoints = algo.predict(pen=pen)
        else:
            # 指定转折点数量
            changepoints = algo.predict(n_bkps=max_changepoints)
        
        # 移除最后一个点（序列结束点）
        if len(changepoints) > 0 and changepoints[-1] == len(signal):
            changepoints = changepoints[:-1]
        
        return np.array(changepoints)
    
    def analyze_changepoints(self, df: pd.DataFrame, 
                            changepoints: np.ndarray) -> pd.DataFrame:
        """
        分析转折点特征
        
        Parameters:
        -----------
        df : pd.DataFrame
            数据
        changepoints : np.ndarray
            转折点位置
            
        Returns:
        --------
        pd.DataFrame
            转折点分析结果
        """
        results = []
        
        for cp_idx in changepoints:
            if cp_idx >= len(df):
                continue
            
            cp_data = df.iloc[cp_idx]
            
            result = {
                'point_no': cp_data.get('point_no', cp_idx),
                'set_no': cp_data.get('set_no', np.nan),
                'game_no': cp_data.get('game_no', np.nan),
                'changepoint_index': cp_idx,
                'p1_score': cp_data.get('p1_score', ''),
                'p2_score': cp_data.get('p2_score', ''),
                'p1_sets': cp_data.get('p1_sets', np.nan),
                'p2_sets': cp_data.get('p2_sets', np.nan),
                'p1_games': cp_data.get('p1_games', np.nan),
                'p2_games': cp_data.get('p2_games', np.nan),
            }
            
            # 添加动量相关特征
            if 'p1_momentum_score' in cp_data:
                result['momentum_before'] = df.iloc[max(0, cp_idx-5):cp_idx]['p1_momentum_score'].mean()
                result['momentum_after'] = df.iloc[cp_idx:min(len(df), cp_idx+5)]['p1_momentum_score'].mean()
                result['momentum_change'] = result['momentum_after'] - result['momentum_before']
            
            # 检查是否为关键分
            if 'is_break_point' in cp_data:
                result['is_break_point'] = cp_data['is_break_point']
            if 'is_set_point' in cp_data:
                result['is_set_point'] = cp_data['is_set_point']
            
            results.append(result)
        
        return pd.DataFrame(results)
    
    def detect(self, df: pd.DataFrame, 
               signal_column: str = 'p1_momentum_score') -> pd.DataFrame:
        """
        执行完整的转折点检测流程
        
        Parameters:
        -----------
        df : pd.DataFrame
            数据
        signal_column : str
            信号列名
            
        Returns:
        --------
        pd.DataFrame
            转折点检测结果
        """
        print("="*60)
        print("开始转折点检测")
        print("="*60)
        
        # 准备信号
        signal = self.prepare_signal(df, signal_column)
        print(f"信号长度: {len(signal)}")
        
        # 检测转折点
        changepoints = self.detect_changepoints(signal)
        print(f"检测到 {len(changepoints)} 个转折点")
        print(f"转折点位置: {changepoints}")
        
        # 分析转折点
        results = self.analyze_changepoints(df, changepoints)
        
        return results


def main():
    """主函数：执行转折点检测"""
    # 加载特征数据
    print("加载特征数据...")
    df = pd.read_csv(FEATURES_DATA_PATH)
    
    # 按比赛分组检测
    if 'match_id' in df.columns:
        match_ids = df['match_id'].unique()
        print(f"找到 {len(match_ids)} 场比赛")
        
        all_results = []
        
        for match_id in match_ids:
            print(f"\n处理比赛: {match_id}")
            match_df = df[df['match_id'] == match_id].copy().sort_values('point_no')
            
            detector = ChangepointDetector()
            results = detector.detect(match_df)
            results['match_id'] = match_id
            
            all_results.append(results)
        
        # 合并所有结果
        final_results = pd.concat(all_results, ignore_index=True)
    else:
        # 单场比赛
        print("处理单场比赛数据...")
        detector = ChangepointDetector()
        final_results = detector.detect(df)
    
    # 保存结果
    CHANGEPOINT_RESULTS_PATH.parent.mkdir(parents=True, exist_ok=True)
    final_results.to_csv(CHANGEPOINT_RESULTS_PATH, index=False)
    print(f"\n结果已保存至: {CHANGEPOINT_RESULTS_PATH}")
    
    # 显示统计信息
    print("\n转折点统计:")
    print(f"总转折点数: {len(final_results)}")
    if 'momentum_change' in final_results.columns:
        print(f"平均动量变化: {final_results['momentum_change'].mean():.4f}")


if __name__ == "__main__":
    main()
