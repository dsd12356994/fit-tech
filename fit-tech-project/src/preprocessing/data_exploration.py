"""
数据探索模块：全面分析数据集的基本信息、质量评估和预处理建议
基于2024年温网比赛数据集
"""
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from pathlib import Path
import sys

sys.path.append(str(Path(__file__).parent.parent.parent))

from config import RAW_DATA_PATH, VISUALIZATION_DIR, VISUALIZATION_CONFIG


class DataExplorer:
    """数据探索分析类"""
    
    def __init__(self, config: dict = None):
        """
        初始化数据探索器
        
        Parameters:
        -----------
        config : dict, optional
            配置字典
        """
        self.config = config or {}
        self._setup_style()
    
    def _setup_style(self):
        """设置绘图样式"""
        plt.rcParams['font.sans-serif'] = ['WenQuanYi Zen Hei', 'Arial Unicode MS', 'SimHei']
        plt.rcParams['axes.unicode_minus'] = False
    
    def load_data(self, file_path: Path = None) -> pd.DataFrame:
        """加载原始数据"""
        file_path = file_path or RAW_DATA_PATH
        
        if not file_path.exists():
            raise FileNotFoundError(f"数据文件不存在: {file_path}")
        
        print(f"正在加载数据: {file_path}")
        df = pd.read_csv(file_path)
        print(f"数据加载完成: {df.shape[0]} 行, {df.shape[1]} 列")
        
        return df
    
    def basic_info(self, df: pd.DataFrame) -> None:
        """
        输出数据集基本信息
        
        Parameters:
        -----------
        df : pd.DataFrame
            数据集
        """
        print("="*60)
        print("1. 数据集基本信息")
        print("="*60)
        print(f"数据集形状: {df.shape} (行数, 列数)")
        print(f"数据集大小: {df.size} 个数据点")
        print(f"数据类型: {df.dtypes.unique()}")
        print()
    
    def column_info(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        输出列名和数据类型信息
        
        Parameters:
        -----------
        df : pd.DataFrame
            数据集
            
        Returns:
        --------
        pd.DataFrame
            列信息汇总表
        """
        print("="*60)
        print("2. 列名及对应数据类型")
        print("="*60)
        
        column_info = pd.DataFrame({
            '列名': df.columns,
            '数据类型': df.dtypes.values,
            '非空值数量': df.count().values,
            '缺失值数量': df.isnull().sum().values,
            '缺失值比例(%)': (df.isnull().sum() / len(df) * 100).round(2).values
        })
        
        print(column_info.to_string(index=False))
        print()
        
        return column_info
    
    def numeric_statistics(self, df: pd.DataFrame) -> None:
        """
        输出数值型数据统计描述
        
        Parameters:
        -----------
        df : pd.DataFrame
            数据集
        """
        print("="*60)
        print("3. 数值型数据统计描述")
        print("="*60)
        
        numeric_cols = df.select_dtypes(include=[np.number]).columns
        if len(numeric_cols) > 0:
            print(df[numeric_cols].describe().round(2))
        else:
            print("数据集中没有数值型列")
        print()
    
    def missing_values_analysis(self, df: pd.DataFrame, save_plot: bool = True) -> None:
        """
        缺失值情况分析和可视化
        
        Parameters:
        -----------
        df : pd.DataFrame
            数据集
        save_plot : bool
            是否保存图表
        """
        print("="*60)
        print("4. 缺失值情况可视化")
        print("="*60)
        
        missing_data = df.isnull().sum()
        missing_data = missing_data[missing_data > 0].sort_values(ascending=False)
        
        if len(missing_data) > 0:
            fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(15, 6))
            
            # 柱状图显示缺失值数量
            missing_data.plot(kind='bar', ax=ax1, color='salmon')
            ax1.set_title('各列缺失值数量', fontsize=14)
            ax1.set_xlabel('列名', fontsize=12)
            ax1.set_ylabel('缺失值数量', fontsize=12)
            ax1.tick_params(axis='x', rotation=45)
            
            # 饼图显示缺失值占比
            missing_percentage = (missing_data / len(df) * 100).round(2)
            ax2.pie(missing_percentage.values, labels=missing_percentage.index, 
                   autopct='%1.1f%%', startangle=90, 
                   colors=plt.cm.Set3(np.linspace(0, 1, len(missing_percentage))))
            ax2.set_title('各列缺失值占比', fontsize=14)
            
            plt.tight_layout()
            
            if save_plot:
                save_path = VISUALIZATION_DIR / "missing_values_analysis.png"
                save_path.parent.mkdir(parents=True, exist_ok=True)
                plt.savefig(save_path, dpi=300, bbox_inches='tight')
                print(f"缺失值分析图已保存至: {save_path}")
            
            plt.close()
        else:
            print("数据集中没有缺失值")
        print()
    
    def duplicate_check(self, df: pd.DataFrame) -> None:
        """
        重复值检查
        
        Parameters:
        -----------
        df : pd.DataFrame
            数据集
        """
        print("="*60)
        print("5. 重复值检查")
        print("="*60)
        
        duplicate_count = df.duplicated().sum()
        print(f"完全重复的行数: {duplicate_count}")
        print(f"重复值占比: {duplicate_count/len(df)*100:.2f}%")
        
        # 检查关键列的重复情况
        if 'match_id' in df.columns:
            duplicate_matches = df['match_id'].duplicated().sum()
            print(f"重复的比赛ID数量: {duplicate_matches}")
        print()
    
    def categorical_analysis(self, df: pd.DataFrame, max_cols: int = 5) -> None:
        """
        分类变量分析
        
        Parameters:
        -----------
        df : pd.DataFrame
            数据集
        max_cols : int
            最多分析的列数
        """
        print("="*60)
        print(f"6. 分类变量分析（前{max_cols}个分类列）")
        print("="*60)
        
        categorical_cols = df.select_dtypes(include=['object', 'category']).columns
        if len(categorical_cols) > 0:
            for col in categorical_cols[:max_cols]:
                print(f"\n{col}:")
                print(f"  唯一值数量: {df[col].nunique()}")
                print(f"  前5个唯一值: {list(df[col].unique()[:5])}")
                print(f"  值计数（前5个）:")
                print(df[col].value_counts().head().to_string())
        else:
            print("数据集中没有分类变量")
        print()
    
    def outlier_analysis(self, df: pd.DataFrame) -> None:
        """
        异常值分析
        
        Parameters:
        -----------
        df : pd.DataFrame
            数据集
        """
        print("="*60)
        print("7. 数值型列数据范围检查")
        print("="*60)
        
        numeric_cols = df.select_dtypes(include=[np.number]).columns
        if len(numeric_cols) > 0:
            outlier_summary = []
            
            for col in numeric_cols:
                min_val = df[col].min()
                max_val = df[col].max()
                mean_val = df[col].mean()
                std_val = df[col].std()
                
                # 检查是否有异常值（±3σ标准）
                lower_bound = mean_val - 3 * std_val
                upper_bound = mean_val + 3 * std_val
                outliers = ((df[col] < lower_bound) | (df[col] > upper_bound)).sum()
                outlier_pct = outliers / len(df) * 100
                
                outlier_summary.append({
                    '列名': col,
                    '最小值': f"{min_val:.2f}",
                    '最大值': f"{max_val:.2f}",
                    '均值': f"{mean_val:.2f}",
                    '标准差': f"{std_val:.2f}",
                    '异常值数量': outliers,
                    '异常值比例(%)': f"{outlier_pct:.2f}"
                })
                
                if outliers > 0:
                    print(f"{col}:")
                    print(f"  范围: [{min_val:.2f}, {max_val:.2f}]")
                    print(f"  均值: {mean_val:.2f}, 标准差: {std_val:.2f}")
                    print(f"  异常值数量（±3σ）: {outliers} ({outlier_pct:.2f}%)")
            
            # 保存异常值摘要
            outlier_df = pd.DataFrame(outlier_summary)
            outlier_df = outlier_df[outlier_df['异常值数量'].astype(int) > 0]
            if len(outlier_df) > 0:
                print(f"\n异常值摘要（共{len(outlier_df)}列有异常值）:")
                print(outlier_df.to_string(index=False))
        else:
            print("数据集中没有数值型列")
        print()
    
    def preprocessing_recommendations(self, df: pd.DataFrame) -> None:
        """
        数据预处理建议总结
        
        Parameters:
        -----------
        df : pd.DataFrame
            数据集
        """
        print("="*60)
        print("8. 数据预处理建议总结")
        print("="*60)
        
        recommendations = []
        
        # 检查缺失值
        missing_cols = df.columns[df.isnull().any()].tolist()
        if missing_cols:
            recommendations.append(f"✓ 发现 {len(missing_cols)} 列存在缺失值，建议使用前向填充或均值填充")
        else:
            recommendations.append("✓ 数据完整性良好，无缺失值")
        
        # 检查数据类型
        object_cols = df.select_dtypes(include=['object']).columns.tolist()
        score_cols = [col for col in object_cols if 'score' in col.lower()]
        if score_cols:
            recommendations.append(f"✓ 发现比分列 {score_cols} 为字符串类型，需要转换为数值型")
        
        if 'elapsed_time' in object_cols:
            recommendations.append("✓ elapsed_time 为字符串类型，需要转换为秒数")
        
        # 检查异常值
        numeric_cols = df.select_dtypes(include=[np.number]).columns
        outlier_cols = []
        for col in numeric_cols:
            mean_val = df[col].mean()
            std_val = df[col].std()
            if std_val > 0:
                outliers = ((df[col] < mean_val - 3*std_val) | 
                           (df[col] > mean_val + 3*std_val)).sum()
                if outliers > len(df) * 0.05:  # 超过5%的异常值
                    outlier_cols.append(col)
        
        if outlier_cols:
            recommendations.append(f"✓ 发现 {len(outlier_cols)} 列存在较多异常值，建议验证是否为真实数据")
        
        # 特征工程建议
        recommendations.append("✓ 建议创建以下特征：")
        recommendations.append("  - 滚动胜率（过去N点）")
        recommendations.append("  - 连胜次数")
        recommendations.append("  - 动量得分")
        recommendations.append("  - 关键分标识（破发点、决胜分）")
        recommendations.append("  - 发球优势指标")
        
        for rec in recommendations:
            print(rec)
        print()
    
    def explore(self, df: pd.DataFrame = None, save_plots: bool = True) -> dict:
        """
        执行完整的数据探索流程
        
        Parameters:
        -----------
        df : pd.DataFrame, optional
            数据集，如果不提供则从文件加载
        save_plots : bool
            是否保存图表
            
        Returns:
        --------
        dict
            探索结果摘要
        """
        if df is None:
            df = self.load_data()
        
        print("\n" + "="*80)
        print("2024年温网比赛数据集 - 完整数据探索分析")
        print("="*80 + "\n")
        
        # 执行各项分析
        self.basic_info(df)
        column_info = self.column_info(df)
        self.numeric_statistics(df)
        self.missing_values_analysis(df, save_plot=save_plots)
        self.duplicate_check(df)
        self.categorical_analysis(df)
        self.outlier_analysis(df)
        self.preprocessing_recommendations(df)
        
        # 返回摘要
        summary = {
            'shape': df.shape,
            'total_missing': df.isnull().sum().sum(),
            'duplicate_rows': df.duplicated().sum(),
            'numeric_cols': len(df.select_dtypes(include=[np.number]).columns),
            'categorical_cols': len(df.select_dtypes(include=['object', 'category']).columns)
        }
        
        print("="*80)
        print("数据探索完成！")
        print("="*80)
        
        return summary


def main():
    """主函数：执行数据探索"""
    explorer = DataExplorer()
    summary = explorer.explore(save_plots=True)
    
    print("\n探索结果摘要:")
    for key, value in summary.items():
        print(f"  {key}: {value}")


if __name__ == "__main__":
    main()
