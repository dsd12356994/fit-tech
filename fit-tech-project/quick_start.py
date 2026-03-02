"""
快速开始脚本：演示如何使用项目进行网球动量分析
"""
import sys
from pathlib import Path

# 添加项目根目录到路径
PROJECT_ROOT = Path(__file__).parent
sys.path.append(str(PROJECT_ROOT))

from config import RAW_DATA_PATH
from src.preprocessing.data_exploration import DataExplorer
from src.preprocessing.data_cleaning import DataCleaner
from src.preprocessing.feature_engineering import FeatureEngineer
from src.preprocessing.data_reduction import DataReducer
from src.models.momentum_hmm import MomentumHMM
from src.models.changepoint_detection import ChangepointDetector
from src.visualization.match_flow import MatchFlowVisualizer
from src.visualization.heatmap_analysis import HeatmapAnalyzer
from src.utils.statistical_tests import comprehensive_momentum_test
import pandas as pd


def main():
    """快速开始主函数"""
    print("="*80)
    print("2024 MCM Problem C: 网球动量分析 - 快速开始")
    print("="*80)
    
    # 检查数据文件
    if not RAW_DATA_PATH.exists():
        print(f"\n❌ 错误: 数据文件不存在: {RAW_DATA_PATH}")
        print("请将数据文件放置在 data/raw/ 目录下")
        print("或修改 config.py 中的 RAW_DATA_PATH")
        return
    
    try:
        # =================================================================
        # 步骤1: 数据探索
        # =================================================================
        print("\n" + "="*80)
        print("步骤 1/7: 数据探索")
        print("="*80)
        explorer = DataExplorer()
        summary = explorer.explore(save_plots=True)
        print(f"\n✓ 数据探索完成")
        print(f"  - 数据形状: {summary['shape']}")
        print(f"  - 缺失值: {summary['total_missing']}")
        print(f"  - 数值列: {summary['numeric_cols']}")
        
        # =================================================================
        # 步骤2: 数据清洗
        # =================================================================
        print("\n" + "="*80)
        print("步骤 2/7: 数据清洗")
        print("="*80)
        cleaner = DataCleaner()
        cleaned_df = cleaner.clean()
        cleaner.save_cleaned_data(cleaned_df)
        print(f"\n✓ 数据清洗完成")
        print(f"  - 清洗后形状: {cleaned_df.shape}")
        
        # =================================================================
        # 步骤3: 特征工程
        # =================================================================
        print("\n" + "="*80)
        print("步骤 3/7: 特征工程")
        print("="*80)
        engineer = FeatureEngineer()
        featured_df = engineer.engineer_features(cleaned_df)
        engineer.save_features(featured_df)
        print(f"\n✓ 特征工程完成")
        print(f"  - 特征数量: {featured_df.shape[1]}")
        print(f"  - 新增特征示例: {[col for col in featured_df.columns if 'rolling' in col or 'momentum' in col][:5]}")
        
        # =================================================================
        # 步骤4: 数据精简（可选）
        # =================================================================
        print("\n" + "="*80)
        print("步骤 4/7: 数据精简（可选）")
        print("="*80)
        reducer = DataReducer()
        reduced_df = reducer.reduce(featured_df, mode='deep', aggregate=False, sample=False)
        reducer.save_reduced_data(reduced_df, filename='reduced_deep_wimbledon.csv')
        print(f"\n✓ 数据精简完成")
        print(f"  - 精简后形状: {reduced_df.shape}")
        
        # =================================================================
        # 步骤5: HMM动量分析
        # =================================================================
        print("\n" + "="*80)
        print("步骤 5/7: HMM动量状态识别")
        print("="*80)
        
        if 'match_id' in featured_df.columns:
            match_ids = featured_df['match_id'].unique()[:3]  # 处理前3场比赛
            all_results = []
            
            for match_id in match_ids:
                print(f"\n处理比赛: {match_id}")
                match_df = featured_df[featured_df['match_id'] == match_id].copy().sort_values('point_no')
                
                hmm_model = MomentumHMM()
                hmm_model.fit(match_df)
                states = hmm_model.predict(match_df)
                result_df = hmm_model.analyze_momentum_shifts(match_df, states)
                result_df['match_id'] = match_id
                all_results.append(result_df)
            
            momentum_results = pd.concat(all_results, ignore_index=True)
        else:
            hmm_model = MomentumHMM()
            hmm_model.fit(featured_df)
            states = hmm_model.predict(featured_df)
            momentum_results = hmm_model.analyze_momentum_shifts(featured_df, states)
        
        from config import MOMENTUM_RESULTS_PATH
        MOMENTUM_RESULTS_PATH.parent.mkdir(parents=True, exist_ok=True)
        momentum_results.to_csv(MOMENTUM_RESULTS_PATH, index=False)
        print(f"\n✓ HMM分析完成")
        print(f"  - 结果已保存至: {MOMENTUM_RESULTS_PATH}")
        print(f"  - 状态分布:\n{momentum_results['momentum_state_label'].value_counts()}")
        
        # =================================================================
        # 步骤6: 转折点检测
        # =================================================================
        print("\n" + "="*80)
        print("步骤 6/7: 转折点检测")
        print("="*80)
        
        if 'match_id' in featured_df.columns:
            match_ids = featured_df['match_id'].unique()[:3]
            all_results = []
            
            for match_id in match_ids:
                print(f"\n处理比赛: {match_id}")
                match_df = featured_df[featured_df['match_id'] == match_id].copy().sort_values('point_no')
                
                detector = ChangepointDetector()
                results = detector.detect(match_df)
                results['match_id'] = match_id
                all_results.append(results)
            
            changepoint_results = pd.concat(all_results, ignore_index=True)
        else:
            detector = ChangepointDetector()
            changepoint_results = detector.detect(featured_df)
        
        from config import CHANGEPOINT_RESULTS_PATH
        CHANGEPOINT_RESULTS_PATH.parent.mkdir(parents=True, exist_ok=True)
        changepoint_results.to_csv(CHANGEPOINT_RESULTS_PATH, index=False)
        print(f"\n✓ 转折点检测完成")
        print(f"  - 结果已保存至: {CHANGEPOINT_RESULTS_PATH}")
        print(f"  - 检测到 {len(changepoint_results)} 个转折点")
        
        # =================================================================
        # 步骤7: 可视化
        # =================================================================
        print("\n" + "="*80)
        print("步骤 7/7: 生成可视化")
        print("="*80)
        
        visualizer = MatchFlowVisualizer()
        analyzer = HeatmapAnalyzer()
        
        if 'match_id' in featured_df.columns:
            match_ids = featured_df['match_id'].unique()[:2]  # 处理前2场比赛
            
            for match_id in match_ids:
                from config import VISUALIZATION_DIR
                
                # 动量走势图
                save_path = VISUALIZATION_DIR / f"momentum_flow_{match_id}.png"
                visualizer.plot_momentum_flow(featured_df, match_id=match_id, save_path=save_path)
                
                # 关键分热力图
                save_path = VISUALIZATION_DIR / f"key_points_heatmap_{match_id}.png"
                analyzer.plot_key_points_heatmap(featured_df, match_id=match_id, save_path=save_path)
                
                # 动量状态图
                match_momentum = momentum_results[momentum_results['match_id'] == match_id]
                save_path = VISUALIZATION_DIR / f"momentum_states_{match_id}.png"
                visualizer.plot_momentum_states(featured_df, match_momentum,
                                               match_id=match_id, save_path=save_path)
                
                # 转折点分析
                match_changepoints = changepoint_results[changepoint_results['match_id'] == match_id]
                save_path = VISUALIZATION_DIR / f"changepoint_analysis_{match_id}.png"
                analyzer.plot_changepoint_analysis(featured_df, match_changepoints,
                                                  match_id=match_id, save_path=save_path)
        else:
            from config import VISUALIZATION_DIR
            visualizer.plot_momentum_flow(featured_df, save_path=VISUALIZATION_DIR / "momentum_flow.png")
            analyzer.plot_key_points_heatmap(featured_df, save_path=VISUALIZATION_DIR / "key_points_heatmap.png")
        
        print(f"\n✓ 可视化完成")
        print(f"  - 图表已保存至: figures/ 目录")
        
        # =================================================================
        # 步骤8: 统计检验（可选）
        # =================================================================
        print("\n" + "="*80)
        print("步骤 8/8: 统计检验（可选）")
        print("="*80)
        
        try:
            # 选择第一场比赛进行统计检验
            if 'match_id' in featured_df.columns:
                first_match_id = featured_df['match_id'].unique()[0]
                test_df = featured_df[featured_df['match_id'] == first_match_id].copy()
                test_states = momentum_results[momentum_results['match_id'] == first_match_id]['momentum_state'].values
            else:
                test_df = featured_df.copy()
                test_states = momentum_results['momentum_state'].values
            
            print(f"\n执行统计检验...")
            test_results = comprehensive_momentum_test(test_df, test_states)
            
            print(f"\n✓ 统计检验完成")
            print(f"  - Player 1 动量显著性: {'显著' if test_results['player1']['is_significant'] else '不显著'}")
            print(f"  - Player 2 动量显著性: {'显著' if test_results['player2']['is_significant'] else '不显著'}")
        except Exception as e:
            print(f"统计检验出错: {e}")
            print("（这不会影响其他结果）")
        
        # =================================================================
        # 完成总结
        # =================================================================
        print("\n" + "="*80)
        print("✅ 快速开始流程完成！")
        print("="*80)
        print("\n输出文件:")
        print(f"  📊 清洗后数据: data/processed/processed_wimbledon.csv")
        print(f"  📊 特征数据: data/processed/features_wimbledon.csv")
        print(f"  📊 精简数据: data/processed/reduced_deep_wimbledon.csv")
        print(f"  📈 动量结果: data/results/momentum_states.csv")
        print(f"  📈 转折点结果: data/results/changepoints.csv")
        print(f"  🎨 可视化图表: figures/")
        print("\n下一步:")
        print("  - 查看可视化图表了解比赛走势")
        print("  - 分析动量状态转换规律")
        print("  - 研究转折点的特征")
        print("  - 运行LSTM预测模型（可选）")
        print("\n详细使用说明请参考: USAGE.md")
        
    except Exception as e:
        print(f"\n❌ 错误: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()
