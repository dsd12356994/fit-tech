"""
数据精简模块：生成核心特征精简版数据集，便于AI模型使用
"""
import pandas as pd
import numpy as np
from pathlib import Path
import sys

sys.path.append(str(Path(__file__).parent.parent.parent))

from config import RAW_DATA_PATH, PROCESSED_DATA_DIR


class DataReducer:
    """数据精简器：创建核心特征精简版数据集"""
    
    def __init__(self):
        """初始化数据精简器"""
        # 基础分析方案的核心列（10列）
        self.basic_columns = [
            'match_id', 'player1', 'player2',
            'set_no', 'game_no', 'point_no',
            'p1_score', 'p2_score',
            'server', 'point_victor'
        ]
        
        # 深度分析方案的核心列（18-20列）
        self.deep_columns = [
            # 基础列
            'match_id', 'player1', 'player2',
            'set_no', 'game_no', 'point_no',
            'p1_sets', 'p2_sets', 'p1_games', 'p2_games',
            'p1_score', 'p2_score',
            'server', 'point_victor',
            # 技术统计
            'p1_ace', 'p2_ace',
            'p1_double_fault', 'p2_double_fault',
            'p1_winner', 'p2_winner',
            'p1_net_pt', 'p2_net_pt',
            'p1_break_pt', 'p2_break_pt',
            'rally_count', 'speed_mph',
            'p1_distance_run', 'p2_distance_run'
        ]
    
    def load_data(self, file_path: Path = None) -> pd.DataFrame:
        """加载原始数据"""
        file_path = file_path or RAW_DATA_PATH
        
        if not file_path.exists():
            raise FileNotFoundError(f"数据文件不存在: {file_path}")
        
        print(f"正在加载数据: {file_path}")
        df = pd.read_csv(file_path)
        print(f"数据加载完成: {df.shape[0]} 行, {df.shape[1]} 列")
        
        return df
    
    def create_basic_dataset(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        创建基础分析方案数据集（10列）
        
        Parameters:
        -----------
        df : pd.DataFrame
            原始数据
            
        Returns:
        --------
        pd.DataFrame
            精简后的数据集
        """
        print("\n创建基础分析方案数据集...")
        
        # 选择存在的列
        available_cols = [col for col in self.basic_columns if col in df.columns]
        missing_cols = [col for col in self.basic_columns if col not in df.columns]
        
        if missing_cols:
            print(f"警告: 以下列不存在，将被跳过: {missing_cols}")
        
        reduced_df = df[available_cols].copy()
        
        print(f"基础数据集: {reduced_df.shape[0]} 行, {reduced_df.shape[1]} 列")
        
        return reduced_df
    
    def create_deep_dataset(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        创建深度分析方案数据集（18-20列）
        
        Parameters:
        -----------
        df : pd.DataFrame
            原始数据
            
        Returns:
        --------
        pd.DataFrame
            精简后的数据集
        """
        print("\n创建深度分析方案数据集...")
        
        # 选择存在的列
        available_cols = [col for col in self.deep_columns if col in df.columns]
        missing_cols = [col for col in self.deep_columns if col not in df.columns]
        
        if missing_cols:
            print(f"警告: 以下列不存在，将被跳过: {missing_cols}")
        
        reduced_df = df[available_cols].copy()
        
        print(f"深度数据集: {reduced_df.shape[0]} 行, {reduced_df.shape[1]} 列")
        
        return reduced_df
    
    def aggregate_by_game(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        按局级别聚合数据（减少行数）
        
        Parameters:
        -----------
        df : pd.DataFrame
            点级别数据
            
        Returns:
        --------
        pd.DataFrame
            局级别聚合数据
        """
        print("\n按局级别聚合数据...")
        
        if 'match_id' not in df.columns:
            print("警告: 没有match_id列，无法按比赛分组")
            return df
        
        # 分组键
        group_keys = ['match_id', 'set_no', 'game_no']
        available_keys = [key for key in group_keys if key in df.columns]
        
        if not available_keys:
            print("警告: 没有可用的分组键")
            return df
        
        # 数值列聚合方式
        numeric_cols = df.select_dtypes(include=[np.number]).columns
        numeric_cols = [col for col in numeric_cols if col not in available_keys]
        
        agg_dict = {}
        for col in numeric_cols:
            if 'win' in col.lower() or 'victor' in col.lower():
                agg_dict[col] = 'sum'  # 胜负相关列求和
            elif 'score' in col.lower() or 'sets' in col.lower() or 'games' in col.lower():
                agg_dict[col] = 'last'  # 比分列取最后值
            else:
                agg_dict[col] = 'mean'  # 其他数值列取均值
        
        # 字符串列取第一个值
        object_cols = df.select_dtypes(include=['object']).columns
        object_cols = [col for col in object_cols if col not in available_keys]
        for col in object_cols:
            agg_dict[col] = 'first'
        
        # 执行聚合
        aggregated_df = df.groupby(available_keys).agg(agg_dict).reset_index()
        
        print(f"聚合前: {df.shape[0]} 行")
        print(f"聚合后: {aggregated_df.shape[0]} 行")
        print(f"压缩比例: {aggregated_df.shape[0] / df.shape[0] * 100:.1f}%")
        
        return aggregated_df
    
    def aggregate_by_set(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        按盘级别聚合数据（进一步减少行数）
        
        Parameters:
        -----------
        df : pd.DataFrame
            点级别数据
            
        Returns:
        --------
        pd.DataFrame
            盘级别聚合数据
        """
        print("\n按盘级别聚合数据...")
        
        if 'match_id' not in df.columns:
            print("警告: 没有match_id列，无法按比赛分组")
            return df
        
        # 分组键
        group_keys = ['match_id', 'set_no']
        available_keys = [key for key in group_keys if key in df.columns]
        
        if not available_keys:
            print("警告: 没有可用的分组键")
            return df
        
        # 数值列聚合方式
        numeric_cols = df.select_dtypes(include=[np.number]).columns
        numeric_cols = [col for col in numeric_cols if col not in available_keys]
        
        agg_dict = {}
        for col in numeric_cols:
            if 'win' in col.lower() or 'victor' in col.lower():
                agg_dict[col] = 'sum'
            elif 'score' in col.lower() or 'sets' in col.lower() or 'games' in col.lower():
                agg_dict[col] = 'last'
            else:
                agg_dict[col] = 'mean'
        
        # 字符串列取第一个值
        object_cols = df.select_dtypes(include=['object']).columns
        object_cols = [col for col in object_cols if col not in available_keys]
        for col in object_cols:
            agg_dict[col] = 'first'
        
        # 执行聚合
        aggregated_df = df.groupby(available_keys).agg(agg_dict).reset_index()
        
        print(f"聚合前: {df.shape[0]} 行")
        print(f"聚合后: {aggregated_df.shape[0]} 行")
        print(f"压缩比例: {aggregated_df.shape[0] / df.shape[0] * 100:.1f}%")
        
        return aggregated_df
    
    def sample_by_match(self, df: pd.DataFrame, sample_ratio: float = 0.3) -> pd.DataFrame:
        """
        按比赛抽样（减少行数）
        
        Parameters:
        -----------
        df : pd.DataFrame
            原始数据
        sample_ratio : float
            抽样比例（0-1之间）
            
        Returns:
        --------
        pd.DataFrame
            抽样后的数据
        """
        print(f"\n按比赛抽样（抽样比例: {sample_ratio*100:.1f}%）...")
        
        if 'match_id' not in df.columns:
            print("警告: 没有match_id列，无法按比赛抽样")
            return df
        
        match_ids = df['match_id'].unique()
        n_samples = max(1, int(len(match_ids) * sample_ratio))
        sampled_match_ids = np.random.choice(match_ids, size=n_samples, replace=False)
        
        sampled_df = df[df['match_id'].isin(sampled_match_ids)].copy()
        
        print(f"原始比赛数: {len(match_ids)}")
        print(f"抽样比赛数: {len(sampled_match_ids)}")
        print(f"原始行数: {df.shape[0]}")
        print(f"抽样后行数: {sampled_df.shape[0]}")
        
        return sampled_df
    
    def reduce(self, df: pd.DataFrame = None, 
               mode: str = 'deep',
               aggregate: bool = False,
               aggregate_level: str = 'game',
               sample: bool = False,
               sample_ratio: float = 0.3) -> pd.DataFrame:
        """
        执行数据精简
        
        Parameters:
        -----------
        df : pd.DataFrame, optional
            原始数据
        mode : str
            精简模式：'basic' 或 'deep'
        aggregate : bool
            是否聚合
        aggregate_level : str
            聚合级别：'game' 或 'set'
        sample : bool
            是否抽样
        sample_ratio : float
            抽样比例
            
        Returns:
        --------
        pd.DataFrame
            精简后的数据
        """
        if df is None:
            df = self.load_data()
        
        print("="*60)
        print("开始数据精简流程")
        print("="*60)
        
        # 1. 选择列
        if mode == 'basic':
            reduced_df = self.create_basic_dataset(df)
        else:
            reduced_df = self.create_deep_dataset(df)
        
        # 2. 抽样（如果需要）
        if sample:
            reduced_df = self.sample_by_match(reduced_df, sample_ratio)
        
        # 3. 聚合（如果需要）
        if aggregate:
            if aggregate_level == 'set':
                reduced_df = self.aggregate_by_set(reduced_df)
            else:
                reduced_df = self.aggregate_by_game(reduced_df)
        
        print("\n" + "="*60)
        print("数据精简完成")
        print("="*60)
        print(f"最终数据形状: {reduced_df.shape}")
        
        return reduced_df
    
    def save_reduced_data(self, df: pd.DataFrame, 
                         output_path: Path = None,
                         filename: str = 'reduced_wimbledon.csv') -> None:
        """
        保存精简后的数据
        
        Parameters:
        -----------
        df : pd.DataFrame
            精简后的数据
        output_path : Path, optional
            输出路径
        filename : str
            文件名
        """
        if output_path is None:
            output_path = PROCESSED_DATA_DIR / filename
        
        output_path.parent.mkdir(parents=True, exist_ok=True)
        df.to_csv(output_path, index=False)
        print(f"\n精简数据已保存至: {output_path}")
        print(f"文件大小: {output_path.stat().st_size / 1024 / 1024:.2f} MB")


def main():
    """主函数：执行数据精简"""
    reducer = DataReducer()
    
    # 创建深度分析方案的精简数据集（不聚合，不抽样）
    print("\n" + "="*80)
    print("方案1: 深度分析方案（18-20列，完整数据）")
    print("="*80)
    deep_df = reducer.reduce(mode='deep', aggregate=False, sample=False)
    reducer.save_reduced_data(deep_df, filename='reduced_deep_wimbledon.csv')
    
    # 创建基础分析方案的精简数据集
    print("\n" + "="*80)
    print("方案2: 基础分析方案（10列，完整数据）")
    print("="*80)
    basic_df = reducer.reduce(mode='basic', aggregate=False, sample=False)
    reducer.save_reduced_data(basic_df, filename='reduced_basic_wimbledon.csv')
    
    # 创建聚合版本（按局聚合）
    print("\n" + "="*80)
    print("方案3: 深度分析方案（按局聚合）")
    print("="*80)
    aggregated_df = reducer.reduce(mode='deep', aggregate=True, 
                                  aggregate_level='game', sample=False)
    reducer.save_reduced_data(aggregated_df, filename='reduced_deep_aggregated_wimbledon.csv')
    
    print("\n" + "="*80)
    print("所有精简数据集已生成完成！")
    print("="*80)


if __name__ == "__main__":
    main()
