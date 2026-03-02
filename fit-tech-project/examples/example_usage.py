"""
示例脚本：展示如何使用项目的各个模块
"""
import sys
from pathlib import Path

# 添加项目根目录到路径
PROJECT_ROOT = Path(__file__).parent.parent
sys.path.append(str(PROJECT_ROOT))

import pandas as pd
import numpy as np
from config import RAW_DATA_PATH, FEATURES_DATA_PATH, MOMENTUM_RESULTS_PATH

# ============================================================================
# 示例1: 数据探索
# ============================================================================
def example_data_exploration():
    """数据探索示例"""
    print("="*60)
    print("示例1: 数据探索")
    print("="*60)
    
    from src.preprocessing.data_exploration import DataExplorer
    
    explorer = DataExplorer()
    
    # 加载数据
    df = explorer.load_data()
    
    # 执行各项分析
    explorer.basic_info(df)
    explorer.column_info(df)
    explorer.missing_values_analysis(df, save_plot=True)
    explorer.outlier_analysis(df)


# ============================================================================
# 示例2: 数据清洗和特征工程
# ============================================================================
def example_preprocessing():
    """数据预处理示例"""
    print("="*60)
    print("示例2: 数据清洗和特征工程")
    print("="*60)
    
    from src.preprocessing.data_cleaning import DataCleaner
    from src.preprocessing.feature_engineering import FeatureEngineer
    
    # 数据清洗
    cleaner = DataCleaner()
    cleaned_df = cleaner.clean()
    
    # 特征工程
    engineer = FeatureEngineer()
    featured_df = engineer.engineer_features(cleaned_df)
    
    # 查看创建的特征
    print("\n创建的特征列:")
    new_features = [col for col in featured_df.columns 
                   if col not in cleaned_df.columns]
    print(new_features[:10])  # 显示前10个新特征


# ============================================================================
# 示例3: 动量分析
# ============================================================================
def example_momentum_analysis():
    """动量分析示例"""
    print("="*60)
    print("示例3: HMM动量分析")
    print("="*60)
    
    from src.models.momentum_hmm import MomentumHMM
    
    # 加载特征数据
    df = pd.read_csv(FEATURES_DATA_PATH)
    
    # 选择第一场比赛
    if 'match_id' in df.columns:
        first_match_id = df['match_id'].unique()[0]
        match_df = df[df['match_id'] == first_match_id].copy().sort_values('point_no')
    else:
        match_df = df.copy()
    
    # 训练HMM模型
    hmm_model = MomentumHMM()
    hmm_model.fit(match_df)
    
    # 预测状态
    states = hmm_model.predict(match_df)
    
    # 分析结果
    results = hmm_model.analyze_momentum_shifts(match_df, states)
    
    print("\n动量状态分布:")
    print(results['momentum_state_label'].value_counts())
    print(f"\n状态转换次数: {results['state_change'].sum()}")


# ============================================================================
# 示例4: 转折点检测
# ============================================================================
def example_changepoint_detection():
    """转折点检测示例"""
    print("="*60)
    print("示例4: 转折点检测")
    print("="*60)
    
    from src.models.changepoint_detection import ChangepointDetector
    
    # 加载特征数据
    df = pd.read_csv(FEATURES_DATA_PATH)
    
    # 选择第一场比赛
    if 'match_id' in df.columns:
        first_match_id = df['match_id'].unique()[0]
        match_df = df[df['match_id'] == first_match_id].copy().sort_values('point_no')
    else:
        match_df = df.copy()
    
    # 检测转折点
    detector = ChangepointDetector()
    changepoints = detector.detect(match_df)
    
    print(f"\n检测到 {len(changepoints)} 个转折点")
    print("\n转折点详情:")
    print(changepoints[['point_no', 'set_no', 'game_no', 'momentum_change']].head())


# ============================================================================
# 示例5: 可视化
# ============================================================================
def example_visualization():
    """可视化示例"""
    print("="*60)
    print("示例5: 可视化")
    print("="*60)
    
    from src.visualization.match_flow import MatchFlowVisualizer
    from src.visualization.heatmap_analysis import HeatmapAnalyzer
    from config import VISUALIZATION_DIR
    
    # 加载数据
    df = pd.read_csv(FEATURES_DATA_PATH)
    
    # 选择第一场比赛
    if 'match_id' in df.columns:
        first_match_id = df['match_id'].unique()[0]
        match_df = df[df['match_id'] == first_match_id].copy()
    else:
        match_df = df.copy()
        first_match_id = None
    
    # 创建可视化器
    visualizer = MatchFlowVisualizer()
    analyzer = HeatmapAnalyzer()
    
    # 生成动量走势图
    save_path = VISUALIZATION_DIR / f"example_momentum_flow_{first_match_id or 'all'}.png"
    visualizer.plot_momentum_flow(match_df, match_id=first_match_id, save_path=save_path)
    print(f"✓ 动量走势图已保存: {save_path}")
    
    # 生成关键分热力图
    save_path = VISUALIZATION_DIR / f"example_heatmap_{first_match_id or 'all'}.png"
    analyzer.plot_key_points_heatmap(match_df, match_id=first_match_id, save_path=save_path)
    print(f"✓ 热力图已保存: {save_path}")


# ============================================================================
# 示例6: 统计检验
# ============================================================================
def example_statistical_tests():
    """统计检验示例"""
    print("="*60)
    print("示例6: 统计检验")
    print("="*60)
    
    from src.utils.statistical_tests import test_momentum_significance
    
    # 加载数据
    df = pd.read_csv(FEATURES_DATA_PATH)
    
    # 选择第一场比赛
    if 'match_id' in df.columns:
        first_match_id = df['match_id'].unique()[0]
        match_df = df[df['match_id'] == first_match_id].copy()
    else:
        match_df = df.copy()
    
    # 测试Player 1的动量显著性
    print("\n测试Player 1的动量显著性:")
    results = test_momentum_significance(match_df, player=1, n_permutations=1000)
    
    print(f"\n结果:")
    print(f"  最长连胜: {results['observed_max_streak']}")
    print(f"  p值: {results['p_value_max_streak']:.4f}")
    print(f"  是否显著: {'是' if results['is_significant'] else '否'}")


# ============================================================================
# 示例7: 数据精简
# ============================================================================
def example_data_reduction():
    """数据精简示例"""
    print("="*60)
    print("示例7: 数据精简")
    print("="*60)
    
    from src.preprocessing.data_reduction import DataReducer
    
    # 加载原始数据
    reducer = DataReducer()
    df = reducer.load_data()
    
    # 创建精简数据集
    reduced_df = reducer.reduce(df, mode='deep', aggregate=False, sample=False)
    
    print(f"\n原始数据: {df.shape}")
    print(f"精简数据: {reduced_df.shape}")
    print(f"压缩比例: {reduced_df.shape[1] / df.shape[1] * 100:.1f}% (列数)")


# ============================================================================
# 主函数
# ============================================================================
def main():
    """运行所有示例"""
    print("="*80)
    print("项目使用示例")
    print("="*80)
    print("\n本脚本展示了项目的各个功能模块的使用方法")
    print("可以单独运行每个示例函数，或运行所有示例\n")
    
    examples = [
        ("数据探索", example_data_exploration),
        ("数据预处理", example_preprocessing),
        ("动量分析", example_momentum_analysis),
        ("转折点检测", example_changepoint_detection),
        ("可视化", example_visualization),
        ("统计检验", example_statistical_tests),
        ("数据精简", example_data_reduction),
    ]
    
    print("可用示例:")
    for i, (name, _) in enumerate(examples, 1):
        print(f"  {i}. {name}")
    
    print("\n运行所有示例...\n")
    
    for name, func in examples:
        try:
            func()
            print(f"\n✓ {name}示例完成\n")
        except Exception as e:
            print(f"\n❌ {name}示例出错: {e}\n")
            import traceback
            traceback.print_exc()
    
    print("="*80)
    print("所有示例运行完成！")
    print("="*80)


if __name__ == "__main__":
    main()
