"""
特征工程模块：构造动量相关特征
"""
import pandas as pd
import numpy as np
from pathlib import Path
import sys

sys.path.append(str(Path(__file__).parent.parent.parent))

from config import PROCESSED_DATA_PATH, FEATURES_DATA_PATH, PREPROCESSING_CONFIG
from src.utils.metrics import calculate_momentum_score, calculate_win_streak


class FeatureEngineer:
    """特征工程类"""
    
    def __init__(self, config: dict = None):
        """
        初始化特征工程器
        
        Parameters:
        -----------
        config : dict, optional
            配置字典
        """
        self.config = config or PREPROCESSING_CONFIG
        self.window_size = self.config.get("rolling_window", 10)
    
    def load_data(self, file_path: Path = None) -> pd.DataFrame:
        """加载清洗后的数据"""
        file_path = file_path or PROCESSED_DATA_PATH
        
        if not file_path.exists():
            raise FileNotFoundError(f"数据文件不存在: {file_path}")
        
        print(f"正在加载数据: {file_path}")
        df = pd.read_csv(file_path)
        return df
    
    def create_win_indicators(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        创建胜负指示变量
        
        Parameters:
        -----------
        df : pd.DataFrame
            数据
            
        Returns:
        --------
        pd.DataFrame
            添加了胜负指示变量的数据
        """
        df = df.copy()
        
        print("\n创建胜负指示变量...")
        
        # 点级别胜负
        if 'point_victor' in df.columns:
            df['p1_point_win'] = (df['point_victor'] == 1).astype(int)
            df['p2_point_win'] = (df['point_victor'] == 2).astype(int)
        
        # 局级别胜负
        if 'game_victor' in df.columns:
            df['p1_game_win'] = (df['game_victor'] == 1).astype(int)
            df['p2_game_win'] = (df['game_victor'] == 2).astype(int)
        
        # 盘级别胜负
        if 'set_victor' in df.columns:
            df['p1_set_win'] = (df['set_victor'] == 1).astype(int)
            df['p2_set_win'] = (df['set_victor'] == 2).astype(int)
        
        return df
    
    def create_rolling_features(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        创建滚动窗口特征
        
        Parameters:
        -----------
        df : pd.DataFrame
            数据
            
        Returns:
        --------
        pd.DataFrame
            添加了滚动特征的数据
        """
        df = df.copy()
        
        print(f"\n创建滚动窗口特征 (窗口大小: {self.window_size})...")
        
        # 按比赛分组计算滚动特征
        if 'match_id' in df.columns:
            grouped = df.groupby('match_id')
        else:
            # 如果没有match_id，假设整个数据集是一场比赛
            grouped = [(None, df)]
        
        result_dfs = []
        
        for match_id, match_df in grouped:
            match_df = match_df.copy().sort_values('point_no')
            
            # 滚动胜率
            if 'p1_point_win' in match_df.columns:
                match_df['p1_rolling_win_rate'] = (
                    match_df['p1_point_win']
                    .rolling(window=self.window_size, min_periods=1)
                    .mean()
                )
                match_df['p2_rolling_win_rate'] = (
                    match_df['p2_point_win']
                    .rolling(window=self.window_size, min_periods=1)
                    .mean()
                )
            
            # 滚动得分差
            if 'p1_points_won' in match_df.columns and 'p2_points_won' in match_df.columns:
                match_df['point_diff'] = match_df['p1_points_won'] - match_df['p2_points_won']
                match_df['rolling_point_diff'] = (
                    match_df['point_diff']
                    .rolling(window=self.window_size, min_periods=1)
                    .mean()
                )
            
            # 连胜次数
            if 'p1_point_win' in match_df.columns:
                match_df['p1_win_streak'] = calculate_win_streak(
                    match_df['p1_point_win'].values
                )
                match_df['p2_win_streak'] = calculate_win_streak(
                    match_df['p2_point_win'].values
                )
            
            # 动量得分
            if 'p1_point_win' in match_df.columns:
                match_df['p1_momentum_score'] = calculate_momentum_score(
                    match_df['p1_point_win'].values,
                    window_size=self.window_size
                )
                match_df['p2_momentum_score'] = calculate_momentum_score(
                    match_df['p2_point_win'].values,
                    window_size=self.window_size
                )
            
            result_dfs.append(match_df)
        
        df = pd.concat(result_dfs, ignore_index=True)
        
        return df
    
    def create_score_features(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        创建比分相关特征
        
        Parameters:
        -----------
        df : pd.DataFrame
            数据
            
        Returns:
        --------
        pd.DataFrame
            添加了比分特征的数据
        """
        df = df.copy()
        
        print("\n创建比分特征...")
        
        # 当前盘分差
        if 'p1_sets' in df.columns and 'p2_sets' in df.columns:
            df['set_diff'] = df['p1_sets'] - df['p2_sets']
        
        # 当前局分差
        if 'p1_games' in df.columns and 'p2_games' in df.columns:
            df['game_diff'] = df['p1_games'] - df['p2_games']
        
        # 当前分数差（数值型）
        if 'p1_score_num' in df.columns and 'p2_score_num' in df.columns:
            df['score_diff'] = df['p1_score_num'] - df['p2_score_num']
        
        # 是否处于关键分
        if 'p1_break_pt' in df.columns:
            df['is_break_point'] = (
                (df['p1_break_pt'] == 1) | (df['p2_break_pt'] == 1)
            ).astype(int)
        
        # 是否处于决胜分
        if 'p1_score_num' in df.columns and 'p2_score_num' in df.columns:
            df['is_set_point'] = (
                ((df['p1_score_num'] >= 3) & (df['p1_games'] >= 5)) |
                ((df['p2_score_num'] >= 3) & (df['p2_games'] >= 5))
            ).astype(int)
        
        return df
    
    def create_serve_features(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        创建发球相关特征
        
        Parameters:
        -----------
        df : pd.DataFrame
            数据
            
        Returns:
        --------
        pd.DataFrame
            添加了发球特征的数据
        """
        df = df.copy()
        
        print("\n创建发球特征...")
        
        # 发球优势（发球方胜率）
        if 'server' in df.columns and 'point_victor' in df.columns:
            df['server_wins'] = (df['server'] == df['point_victor']).astype(int)
            
            # 滚动发球胜率
            if 'match_id' in df.columns:
                grouped = df.groupby('match_id')
            else:
                grouped = [(None, df)]
            
            result_dfs = []
            for match_id, match_df in grouped:
                match_df = match_df.copy().sort_values('point_no')
                match_df['serve_win_rate'] = (
                    match_df['server_wins']
                    .rolling(window=self.window_size, min_periods=1)
                    .mean()
                )
                result_dfs.append(match_df)
            
            df = pd.concat(result_dfs, ignore_index=True)
        
        # 发球质量指标
        if 'p1_ace' in df.columns and 'p2_ace' in df.columns:
            df['ace_rate'] = (
                (df['p1_ace'] + df['p2_ace']) / 
                (df['serve_no'].clip(lower=1))
            )
        
        if 'p1_double_fault' in df.columns and 'p2_double_fault' in df.columns:
            df['double_fault_rate'] = (
                (df['p1_double_fault'] + df['p2_double_fault']) / 
                (df['serve_no'].clip(lower=1))
            )
        
        return df
    
    def create_physical_features(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        创建体能相关特征
        
        Parameters:
        -----------
        df : pd.DataFrame
            数据
            
        Returns:
        --------
        pd.DataFrame
            添加了体能特征的数据
        """
        df = df.copy()
        
        print("\n创建体能特征...")
        
        # 滚动平均跑动距离
        if 'p1_distance_run' in df.columns and 'p2_distance_run' in df.columns:
            if 'match_id' in df.columns:
                grouped = df.groupby('match_id')
            else:
                grouped = [(None, df)]
            
            result_dfs = []
            for match_id, match_df in grouped:
                match_df = match_df.copy().sort_values('point_no')
                match_df['p1_rolling_distance'] = (
                    match_df['p1_distance_run']
                    .rolling(window=self.window_size, min_periods=1)
                    .mean()
                )
                match_df['p2_rolling_distance'] = (
                    match_df['p2_distance_run']
                    .rolling(window=self.window_size, min_periods=1)
                    .mean()
                )
                result_dfs.append(match_df)
            
            df = pd.concat(result_dfs, ignore_index=True)
        
        # 回合数特征
        if 'rally_count' in df.columns:
            df['avg_rally_length'] = (
                df['rally_count']
                .rolling(window=self.window_size, min_periods=1)
                .mean()
            )
        
        return df
    
    def engineer_features(self, df: pd.DataFrame = None) -> pd.DataFrame:
        """
        执行完整的特征工程流程
        
        Parameters:
        -----------
        df : pd.DataFrame, optional
            数据，如果不提供则从文件加载
            
        Returns:
        --------
        pd.DataFrame
            添加了特征的数据
        """
        if df is None:
            df = self.load_data()
        
        print("="*60)
        print("开始特征工程流程")
        print("="*60)
        
        # 1. 创建胜负指示变量
        df = self.create_win_indicators(df)
        
        # 2. 创建滚动窗口特征
        df = self.create_rolling_features(df)
        
        # 3. 创建比分特征
        df = self.create_score_features(df)
        
        # 4. 创建发球特征
        df = self.create_serve_features(df)
        
        # 5. 创建体能特征
        df = self.create_physical_features(df)
        
        print("\n" + "="*60)
        print("特征工程完成")
        print("="*60)
        print(f"最终数据形状: {df.shape}")
        print(f"特征列数: {len(df.columns)}")
        
        return df
    
    def save_features(self, df: pd.DataFrame, 
                     output_path: Path = None) -> None:
        """保存特征数据"""
        output_path = output_path or FEATURES_DATA_PATH
        output_path.parent.mkdir(parents=True, exist_ok=True)
        
        df.to_csv(output_path, index=False)
        print(f"\n特征数据已保存至: {output_path}")


def main():
    """主函数：执行特征工程"""
    engineer = FeatureEngineer()
    featured_df = engineer.engineer_features()
    engineer.save_features(featured_df)
    
    # 显示特征摘要
    print("\n特征列:")
    print(list(featured_df.columns))
    print(f"\n前5行数据:\n{featured_df.head()}")


if __name__ == "__main__":
    main()
