"""
主运行脚本：执行完整的数据处理和建模流程
"""
import sys
from pathlib import Path
import pandas as pd

# 添加项目根目录到路径
PROJECT_ROOT = Path(__file__).parent
sys.path.append(str(PROJECT_ROOT))

from config import RAW_DATA_PATH
from src.preprocessing.data_cleaning import DataCleaner
from src.preprocessing.feature_engineering import FeatureEngineer
from src.models.momentum_hmm import MomentumHMM
from src.models.changepoint_detection import ChangepointDetector
from src.visualization.match_flow import MatchFlowVisualizer
from src.visualization.heatmap_analysis import HeatmapAnalyzer


def main():
    """主函数：执行完整流程"""
    print("="*80)
    print("2024 MCM Problem C: 网球动量分析 - 完整流程")
    print("="*80)
    
    # 检查数据文件
    if not RAW_DATA_PATH.exists():
        print(f"\n错误: 数据文件不存在: {RAW_DATA_PATH}")
        print("请将数据文件放置在 data/raw/ 目录下")
        return
    
    try:
        # =================================================================
        # 步骤1: 数据清洗
        # =================================================================
        print("\n" + "="*80)
        print("步骤 1/6: 数据清洗")
        print("="*80)
        cleaner = DataCleaner()
        cleaned_df = cleaner.clean()
        cleaner.save_cleaned_data(cleaned_df)
        
        # =================================================================
        # 步骤2: 特征工程
        # =================================================================
        print("\n" + "="*80)
        print("步骤 2/6: 特征工程")
        print("="*80)
        engineer = FeatureEngineer()
        featured_df = engineer.engineer_features(cleaned_df)
        engineer.save_features(featured_df)
        
        # =================================================================
        # 步骤3: HMM动量分析
        # =================================================================
        print("\n" + "="*80)
        print("步骤 3/6: HMM动量状态识别")
        print("="*80)
        try:
            hmm_model = MomentumHMM()
            if 'match_id' in featured_df.columns:
                match_ids = featured_df['match_id'].unique()
                all_results = []
                
                for match_id in match_ids:
                    print(f"\n处理比赛: {match_id}")
                    match_df = featured_df[featured_df['match_id'] == match_id].copy().sort_values('point_no')
                    hmm_model.fit(match_df)
                    states = hmm_model.predict(match_df)
                    result_df = hmm_model.analyze_momentum_shifts(match_df, states)
                    all_results.append(result_df)
                
                momentum_results = pd.concat(all_results, ignore_index=True)
            else:
                hmm_model.fit(featured_df)
                states = hmm_model.predict(featured_df)
                momentum_results = hmm_model.analyze_momentum_shifts(featured_df, states)
            
            from config import MOMENTUM_RESULTS_PATH
            MOMENTUM_RESULTS_PATH.parent.mkdir(parents=True, exist_ok=True)
            momentum_results.to_csv(MOMENTUM_RESULTS_PATH, index=False)
            print(f"\n动量分析结果已保存至: {MOMENTUM_RESULTS_PATH}")
        except Exception as e:
            print(f"HMM分析出错: {e}")
            momentum_results = None
        
        # =================================================================
        # 步骤4: 转折点检测
        # =================================================================
        print("\n" + "="*80)
        print("步骤 4/6: 转折点检测")
        print("="*80)
        try:
            detector = ChangepointDetector()
            if 'match_id' in featured_df.columns:
                match_ids = featured_df['match_id'].unique()
                all_results = []
                
                for match_id in match_ids:
                    print(f"\n处理比赛: {match_id}")
                    match_df = featured_df[featured_df['match_id'] == match_id].copy().sort_values('point_no')
                    results = detector.detect(match_df)
                    results['match_id'] = match_id
                    all_results.append(results)
                
                changepoint_results = pd.concat(all_results, ignore_index=True)
            else:
                changepoint_results = detector.detect(featured_df)
            
            from config import CHANGEPOINT_RESULTS_PATH
            CHANGEPOINT_RESULTS_PATH.parent.mkdir(parents=True, exist_ok=True)
            changepoint_results.to_csv(CHANGEPOINT_RESULTS_PATH, index=False)
            print(f"\n转折点检测结果已保存至: {CHANGEPOINT_RESULTS_PATH}")
        except Exception as e:
            print(f"转折点检测出错: {e}")
            changepoint_results = None
        
        # =================================================================
        # 步骤5: 可视化
        # =================================================================
        print("\n" + "="*80)
        print("步骤 5/6: 生成可视化")
        print("="*80)
        try:
            visualizer = MatchFlowVisualizer()
            analyzer = HeatmapAnalyzer()
            
            if 'match_id' in featured_df.columns:
                match_ids = featured_df['match_id'].unique()[:3]  # 处理前3场
                
                for match_id in match_ids:
                    from config import VISUALIZATION_DIR
                    # 动量走势图
                    save_path = VISUALIZATION_DIR / f"momentum_flow_{match_id}.png"
                    visualizer.plot_momentum_flow(featured_df, match_id=match_id, save_path=save_path)
                    
                    # 关键分热力图
                    save_path = VISUALIZATION_DIR / f"key_points_heatmap_{match_id}.png"
                    analyzer.plot_key_points_heatmap(featured_df, match_id=match_id, save_path=save_path)
                    
                    # 动量状态图
                    if momentum_results is not None:
                        save_path = VISUALIZATION_DIR / f"momentum_states_{match_id}.png"
                        visualizer.plot_momentum_states(featured_df, momentum_results,
                                                       match_id=match_id, save_path=save_path)
                    
                    # 转折点分析
                    if changepoint_results is not None:
                        save_path = VISUALIZATION_DIR / f"changepoint_analysis_{match_id}.png"
                        analyzer.plot_changepoint_analysis(featured_df, changepoint_results,
                                                          match_id=match_id, save_path=save_path)
            else:
                from config import VISUALIZATION_DIR
                visualizer.plot_momentum_flow(featured_df, 
                                             save_path=VISUALIZATION_DIR / "momentum_flow.png")
                analyzer.plot_key_points_heatmap(featured_df,
                                                save_path=VISUALIZATION_DIR / "key_points_heatmap.png")
            
            print("\n可视化完成！")
        except Exception as e:
            print(f"可视化出错: {e}")
        
        # =================================================================
        # 步骤6: 预测模型（可选）
        # =================================================================
        print("\n" + "="*80)
        print("步骤 6/6: LSTM预测模型（可选）")
        print("="*80)
        print("提示: LSTM模型训练需要较长时间，如需训练请运行:")
        print("     python src/models/lstm_predictor.py")
        
        print("\n" + "="*80)
        print("流程完成！")
        print("="*80)
        print("\n输出文件:")
        print(f"  - 清洗后数据: data/processed/processed_wimbledon.csv")
        print(f"  - 特征数据: data/processed/features_wimbledon.csv")
        if momentum_results is not None:
            print(f"  - 动量结果: data/results/momentum_states.csv")
        if changepoint_results is not None:
            print(f"  - 转折点结果: data/results/changepoints.csv")
        print(f"  - 可视化图表: figures/")
        
    except Exception as e:
        print(f"\n错误: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()
