"""
隐马尔可夫模型（HMM）用于动量状态识别
"""
import pandas as pd
import numpy as np
from pathlib import Path
import sys
from hmmlearn import hmm
import joblib

sys.path.append(str(Path(__file__).parent.parent.parent))

from config import FEATURES_DATA_PATH, MOMENTUM_RESULTS_PATH, HMM_CONFIG


class MomentumHMM:
    """基于HMM的动量状态识别模型"""
    
    def __init__(self, config: dict = None):
        """
        初始化HMM模型
        
        Parameters:
        -----------
        config : dict, optional
            配置字典
        """
        self.config = config or HMM_CONFIG
        self.model = None
        self.state_names = ['劣势', '平衡', '优势']  # 对应3个状态
    
    def prepare_features(self, df: pd.DataFrame) -> np.ndarray:
        """
        准备HMM输入特征
        
        Parameters:
        -----------
        df : pd.DataFrame
            特征数据
            
        Returns:
        --------
        np.ndarray
            特征矩阵，形状为 (n_samples, n_features)
        """
        feature_cols = [
            'p1_rolling_win_rate',
            'p1_momentum_score',
            'p1_win_streak',
            'set_diff',
            'game_diff',
            'score_diff'
        ]
        
        # 选择存在的列
        available_cols = [col for col in feature_cols if col in df.columns]
        
        if not available_cols:
            raise ValueError("没有找到可用的特征列")
        
        features = df[available_cols].values
        
        # 处理缺失值
        features = np.nan_to_num(features, nan=0.0, posinf=1.0, neginf=-1.0)
        
        return features
    
    def fit(self, df: pd.DataFrame) -> None:
        """
        训练HMM模型
        
        Parameters:
        -----------
        df : pd.DataFrame
            训练数据
        """
        print("="*60)
        print("训练HMM动量模型")
        print("="*60)
        
        # 准备特征
        X = self.prepare_features(df)
        
        print(f"特征维度: {X.shape}")
        print(f"状态数量: {self.config['n_states']}")
        
        # 创建并训练HMM模型
        self.model = hmm.GaussianHMM(
            n_components=self.config['n_states'],
            covariance_type="full",
            n_iter=self.config['n_iter'],
            random_state=self.config.get('random_state', 42)
        )
        
        self.model.fit(X)
        
        print("模型训练完成")
        print(f"收敛迭代次数: {self.model.monitor_.iter}")
    
    def predict(self, df: pd.DataFrame) -> np.ndarray:
        """
        预测动量状态
        
        Parameters:
        -----------
        df : pd.DataFrame
            数据
            
        Returns:
        --------
        np.ndarray
            预测的状态序列
        """
        if self.model is None:
            raise ValueError("模型尚未训练，请先调用fit()方法")
        
        X = self.prepare_features(df)
        states = self.model.predict(X)
        
        return states
    
    def predict_proba(self, df: pd.DataFrame) -> np.ndarray:
        """
        预测状态概率
        
        Parameters:
        -----------
        df : pd.DataFrame
            数据
            
        Returns:
        --------
        np.ndarray
            状态概率矩阵，形状为 (n_samples, n_states)
        """
        if self.model is None:
            raise ValueError("模型尚未训练，请先调用fit()方法")
        
        X = self.prepare_features(df)
        proba = self.model.predict_proba(X)
        
        return proba
    
    def interpret_states(self, states: np.ndarray) -> pd.Series:
        """
        将数值状态转换为可解释的标签
        
        Parameters:
        -----------
        states : np.ndarray
            状态序列
            
        Returns:
        --------
        pd.Series
            状态标签序列
        """
        # 根据状态值映射到标签
        # 假设状态0=劣势，1=平衡，2=优势
        state_labels = pd.Series(states).map({
            0: self.state_names[0],
            1: self.state_names[1],
            2: self.state_names[2]
        })
        
        return state_labels
    
    def analyze_momentum_shifts(self, df: pd.DataFrame, 
                               states: np.ndarray) -> pd.DataFrame:
        """
        分析动量转换
        
        Parameters:
        -----------
        df : pd.DataFrame
            数据
        states : np.ndarray
            状态序列
            
        Returns:
        --------
        pd.DataFrame
            动量转换分析结果
        """
        df_result = df[['match_id', 'point_no', 'set_no', 'game_no']].copy()
        df_result['momentum_state'] = states
        df_result['momentum_state_label'] = self.interpret_states(states)
        
        # 检测状态转换
        df_result['state_change'] = (df_result['momentum_state'].diff() != 0).astype(int)
        
        # 计算状态持续时间
        df_result['state_duration'] = 1
        for i in range(1, len(df_result)):
            if df_result.loc[i, 'momentum_state'] == df_result.loc[i-1, 'momentum_state']:
                df_result.loc[i, 'state_duration'] = df_result.loc[i-1, 'state_duration'] + 1
        
        return df_result


def main():
    """主函数：执行HMM动量分析"""
    # 加载特征数据
    print("加载特征数据...")
    df = pd.read_csv(FEATURES_DATA_PATH)
    
    # 按比赛分组训练和预测
    if 'match_id' in df.columns:
        match_ids = df['match_id'].unique()
        print(f"找到 {len(match_ids)} 场比赛")
        
        all_results = []
        
        for match_id in match_ids:
            print(f"\n处理比赛: {match_id}")
            match_df = df[df['match_id'] == match_id].copy().sort_values('point_no')
            
            # 训练模型（使用当前比赛数据）
            hmm_model = MomentumHMM()
            hmm_model.fit(match_df)
            
            # 预测状态
            states = hmm_model.predict(match_df)
            
            # 分析结果
            result_df = hmm_model.analyze_momentum_shifts(match_df, states)
            all_results.append(result_df)
        
        # 合并所有结果
        final_results = pd.concat(all_results, ignore_index=True)
    else:
        # 单场比赛
        print("处理单场比赛数据...")
        hmm_model = MomentumHMM()
        hmm_model.fit(df)
        states = hmm_model.predict(df)
        final_results = hmm_model.analyze_momentum_shifts(df, states)
    
    # 保存结果
    MOMENTUM_RESULTS_PATH.parent.mkdir(parents=True, exist_ok=True)
    final_results.to_csv(MOMENTUM_RESULTS_PATH, index=False)
    print(f"\n结果已保存至: {MOMENTUM_RESULTS_PATH}")
    
    # 显示统计信息
    print("\n动量状态统计:")
    print(final_results['momentum_state_label'].value_counts())
    print(f"\n状态转换次数: {final_results['state_change'].sum()}")


if __name__ == "__main__":
    main()
