"""
数据清洗模块：处理缺失值、异常值、数据类型转换等
"""
import pandas as pd
import numpy as np
from pathlib import Path
import sys

# 添加项目根目录到路径
sys.path.append(str(Path(__file__).parent.parent.parent))

from config import RAW_DATA_PATH, PROCESSED_DATA_PATH, PREPROCESSING_CONFIG
from src.utils.score_converter import ScoreConverter, convert_elapsed_time


class DataCleaner:
    """数据清洗类"""
    
    def __init__(self, config: dict = None):
        """
        初始化数据清洗器
        
        Parameters:
        -----------
        config : dict, optional
            配置字典，默认使用config.py中的配置
        """
        self.config = config or PREPROCESSING_CONFIG
        self.score_converter = ScoreConverter(self.config.get("score_mapping"))
    
    def load_data(self, file_path: Path = None) -> pd.DataFrame:
        """
        加载原始数据
        
        Parameters:
        -----------
        file_path : Path, optional
            数据文件路径，默认使用config中的路径
            
        Returns:
        --------
        pd.DataFrame
            原始数据
        """
        file_path = file_path or RAW_DATA_PATH
        
        if not file_path.exists():
            raise FileNotFoundError(f"数据文件不存在: {file_path}")
        
        print(f"正在加载数据: {file_path}")
        df = pd.read_csv(file_path)
        print(f"数据加载完成: {df.shape[0]} 行, {df.shape[1]} 列")
        
        return df
    
    def handle_missing_values(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        处理缺失值
        
        Parameters:
        -----------
        df : pd.DataFrame
            原始数据
            
        Returns:
        --------
        pd.DataFrame
            处理后的数据
        """
        df = df.copy()
        strategy = self.config.get("missing_value_strategy", "forward_fill")
        
        print("\n处理缺失值...")
        print(f"缺失值统计:\n{df.isnull().sum()[df.isnull().sum() > 0]}")
        
        if strategy == "forward_fill":
            df.fillna(method='ffill', inplace=True)
            df.fillna(method='bfill', inplace=True)  # 处理开头缺失值
        elif strategy == "mean":
            numeric_cols = df.select_dtypes(include=[np.number]).columns
            df[numeric_cols] = df[numeric_cols].fillna(df[numeric_cols].mean())
        elif strategy == "median":
            numeric_cols = df.select_dtypes(include=[np.number]).columns
            df[numeric_cols] = df[numeric_cols].fillna(df[numeric_cols].median())
        
        # 对于非数值列，用前一个值填充
        object_cols = df.select_dtypes(include=['object']).columns
        df[object_cols] = df[object_cols].fillna(method='ffill')
        df[object_cols] = df[object_cols].fillna(method='bfill')
        
        remaining_missing = df.isnull().sum().sum()
        print(f"处理后剩余缺失值: {remaining_missing}")
        
        return df
    
    def detect_outliers(self, df: pd.DataFrame, 
                       columns: list = None) -> pd.DataFrame:
        """
        检测异常值
        
        Parameters:
        -----------
        df : pd.DataFrame
            数据
        columns : list, optional
            要检测的列，默认检测所有数值列
            
        Returns:
        --------
        pd.DataFrame
            添加了异常值标记的数据
        """
        df = df.copy()
        method = self.config.get("outlier_method", "iqr")
        threshold = self.config.get("outlier_threshold", 3.0)
        
        if columns is None:
            columns = df.select_dtypes(include=[np.number]).columns
        
        print(f"\n检测异常值 (方法: {method})...")
        
        for col in columns:
            if col not in df.columns:
                continue
            
            if method == "zscore":
                z_scores = np.abs((df[col] - df[col].mean()) / df[col].std())
                df[f"{col}_is_outlier"] = (z_scores > threshold).astype(int)
            elif method == "iqr":
                Q1 = df[col].quantile(0.25)
                Q3 = df[col].quantile(0.75)
                IQR = Q3 - Q1
                lower_bound = Q1 - 1.5 * IQR
                upper_bound = Q3 + 1.5 * IQR
                df[f"{col}_is_outlier"] = (
                    (df[col] < lower_bound) | (df[col] > upper_bound)
                ).astype(int)
        
        # 统计异常值
        outlier_cols = [col for col in df.columns if col.endswith('_is_outlier')]
        if outlier_cols:
            outlier_counts = df[outlier_cols].sum()
            print(f"异常值统计:\n{outlier_counts[outlier_counts > 0]}")
        
        return df
    
    def convert_scores(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        转换比分格式
        
        Parameters:
        -----------
        df : pd.DataFrame
            数据
            
        Returns:
        --------
        pd.DataFrame
            转换后的数据
        """
        df = df.copy()
        
        print("\n转换比分格式...")
        
        # 转换p1_score和p2_score
        score_columns = ['p1_score', 'p2_score']
        for col in score_columns:
            if col in df.columns:
                df[f"{col}_num"] = self.score_converter.convert_series(df[col])
                print(f"{col} 转换完成")
        
        return df
    
    def convert_time(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        转换时间格式
        
        Parameters:
        -----------
        df : pd.DataFrame
            数据
            
        Returns:
        --------
        pd.DataFrame
            转换后的数据
        """
        df = df.copy()
        
        print("\n转换时间格式...")
        
        if 'elapsed_time' in df.columns:
            df['elapsed_time_seconds'] = df['elapsed_time'].apply(convert_elapsed_time)
            print("elapsed_time 转换完成")
        
        return df
    
    def clean(self, df: pd.DataFrame = None) -> pd.DataFrame:
        """
        执行完整的数据清洗流程
        
        Parameters:
        -----------
        df : pd.DataFrame, optional
            数据，如果不提供则从文件加载
            
        Returns:
        --------
        pd.DataFrame
            清洗后的数据
        """
        if df is None:
            df = self.load_data()
        
        print("="*60)
        print("开始数据清洗流程")
        print("="*60)
        
        # 1. 处理缺失值
        df = self.handle_missing_values(df)
        
        # 2. 转换比分
        df = self.convert_scores(df)
        
        # 3. 转换时间
        df = self.convert_time(df)
        
        # 4. 检测异常值（不删除，只标记）
        df = self.detect_outliers(df)
        
        print("\n" + "="*60)
        print("数据清洗完成")
        print("="*60)
        print(f"最终数据形状: {df.shape}")
        
        return df
    
    def save_cleaned_data(self, df: pd.DataFrame, 
                         output_path: Path = None) -> None:
        """
        保存清洗后的数据
        
        Parameters:
        -----------
        df : pd.DataFrame
            清洗后的数据
        output_path : Path, optional
            输出路径，默认使用config中的路径
        """
        output_path = output_path or PROCESSED_DATA_PATH
        output_path.parent.mkdir(parents=True, exist_ok=True)
        
        df.to_csv(output_path, index=False)
        print(f"\n清洗后的数据已保存至: {output_path}")


def main():
    """主函数：执行数据清洗"""
    cleaner = DataCleaner()
    cleaned_df = cleaner.clean()
    cleaner.save_cleaned_data(cleaned_df)
    
    # 显示数据摘要
    print("\n数据摘要:")
    print(cleaned_df.head())
    print(f"\n数据类型:\n{cleaned_df.dtypes}")


if __name__ == "__main__":
    main()
