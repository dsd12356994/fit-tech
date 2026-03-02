"""
比赛走势可视化：动态展示比赛进程和动量变化
"""
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from pathlib import Path
import sys

sys.path.append(str(Path(__file__).parent.parent.parent))

from config import FEATURES_DATA_PATH, MOMENTUM_RESULTS_PATH, VISUALIZATION_DIR, VISUALIZATION_CONFIG


class MatchFlowVisualizer:
    """比赛走势可视化器"""
    
    def __init__(self, config: dict = None):
        """
        初始化可视化器
        
        Parameters:
        -----------
        config : dict, optional
            配置字典
        """
        self.config = config or VISUALIZATION_CONFIG
        self._setup_style()
    
    def _setup_style(self):
        """设置绘图样式"""
        plt.style.use(self.config.get('style', 'seaborn-v0_8'))
        plt.rcParams['figure.figsize'] = self.config.get('figure_size', (12, 6))
        plt.rcParams['font.size'] = self.config.get('font_size', 12)
        
        # 设置中文字体
        try:
            plt.rcParams['font.sans-serif'] = [self.config.get('chinese_font', 'Arial')]
            plt.rcParams['axes.unicode_minus'] = False
        except:
            pass
    
    def plot_momentum_flow(self, df: pd.DataFrame, 
                          match_id: str = None,
                          save_path: Path = None) -> None:
        """
        绘制动量走势图
        
        Parameters:
        -----------
        df : pd.DataFrame
            特征数据
        match_id : str, optional
            比赛ID，如果提供则只绘制该比赛
        save_path : Path, optional
            保存路径
        """
        if match_id and 'match_id' in df.columns:
            df = df[df['match_id'] == match_id].copy().sort_values('point_no')
        
        fig, axes = plt.subplots(3, 1, figsize=(14, 10))
        
        # 1. 滚动胜率
        if 'p1_rolling_win_rate' in df.columns:
            axes[0].plot(df['point_no'], df['p1_rolling_win_rate'], 
                        label='Player 1 Win Rate', linewidth=2, color='blue')
            axes[0].plot(df['point_no'], 1 - df['p1_rolling_win_rate'], 
                        label='Player 2 Win Rate', linewidth=2, color='red')
            axes[0].axhline(y=0.5, color='gray', linestyle='--', alpha=0.5)
            axes[0].set_ylabel('Win Rate', fontsize=12)
            axes[0].set_title('Rolling Win Rate Over Points', fontsize=14, fontweight='bold')
            axes[0].legend()
            axes[0].grid(True, alpha=0.3)
        
        # 2. 动量得分
        if 'p1_momentum_score' in df.columns:
            axes[1].plot(df['point_no'], df['p1_momentum_score'], 
                        label='Player 1 Momentum', linewidth=2, color='blue')
            axes[1].plot(df['point_no'], -df['p1_momentum_score'], 
                        label='Player 2 Momentum', linewidth=2, color='red')
            axes[1].axhline(y=0, color='gray', linestyle='--', alpha=0.5)
            axes[1].fill_between(df['point_no'], 0, df['p1_momentum_score'], 
                                 where=(df['p1_momentum_score'] > 0), 
                                 alpha=0.3, color='blue')
            axes[1].fill_between(df['point_no'], 0, df['p1_momentum_score'], 
                                 where=(df['p1_momentum_score'] < 0), 
                                 alpha=0.3, color='red')
            axes[1].set_ylabel('Momentum Score', fontsize=12)
            axes[1].set_title('Momentum Score Over Points', fontsize=14, fontweight='bold')
            axes[1].legend()
            axes[1].grid(True, alpha=0.3)
        
        # 3. 比分变化
        if 'p1_sets' in df.columns and 'p2_sets' in df.columns:
            axes[2].plot(df['point_no'], df['p1_sets'], 
                        label='Player 1 Sets', marker='o', markersize=4, color='blue')
            axes[2].plot(df['point_no'], df['p2_sets'], 
                        label='Player 2 Sets', marker='s', markersize=4, color='red')
            axes[2].set_xlabel('Point Number', fontsize=12)
            axes[2].set_ylabel('Sets Won', fontsize=12)
            axes[2].set_title('Set Score Over Points', fontsize=14, fontweight='bold')
            axes[2].legend()
            axes[2].grid(True, alpha=0.3)
        
        plt.tight_layout()
        
        if save_path:
            save_path.parent.mkdir(parents=True, exist_ok=True)
            plt.savefig(save_path, dpi=self.config.get('dpi', 300), bbox_inches='tight')
            print(f"图表已保存至: {save_path}")
        else:
            plt.show()
        
        plt.close()
    
    def plot_momentum_states(self, df: pd.DataFrame, 
                            momentum_df: pd.DataFrame,
                            match_id: str = None,
                            save_path: Path = None) -> None:
        """
        绘制动量状态图
        
        Parameters:
        -----------
        df : pd.DataFrame
            特征数据
        momentum_df : pd.DataFrame
            动量状态数据
        match_id : str, optional
            比赛ID
        save_path : Path, optional
            保存路径
        """
        if match_id and 'match_id' in df.columns:
            df = df[df['match_id'] == match_id].copy().sort_values('point_no')
            momentum_df = momentum_df[momentum_df['match_id'] == match_id].copy().sort_values('point_no')
        
        fig, ax = plt.subplots(figsize=(14, 6))
        
        # 绘制动量得分
        if 'p1_momentum_score' in df.columns:
            ax.plot(df['point_no'], df['p1_momentum_score'], 
                   linewidth=2, color='gray', alpha=0.5, label='Momentum Score')
        
        # 根据状态着色
        if 'momentum_state' in momentum_df.columns:
            states = momentum_df['momentum_state'].values
            point_nos = momentum_df['point_no'].values
            
            # 定义状态颜色
            colors = {0: 'red', 1: 'yellow', 2: 'green'}
            labels = {0: 'Disadvantage', 1: 'Balance', 2: 'Advantage'}
            
            for state in [0, 1, 2]:
                mask = states == state
                if np.any(mask):
                    ax.scatter(point_nos[mask], 
                              df.loc[df['point_no'].isin(point_nos[mask]), 'p1_momentum_score'].values 
                              if 'p1_momentum_score' in df.columns else point_nos[mask],
                              c=colors[state], s=30, alpha=0.7, 
                              label=labels[state], edgecolors='black', linewidth=0.5)
        
        # 标记转折点
        if 'state_change' in momentum_df.columns:
            changepoints = momentum_df[momentum_df['state_change'] == 1]['point_no'].values
            for cp in changepoints:
                ax.axvline(x=cp, color='black', linestyle='--', alpha=0.5, linewidth=1)
        
        ax.axhline(y=0, color='black', linestyle='-', alpha=0.3)
        ax.set_xlabel('Point Number', fontsize=12)
        ax.set_ylabel('Momentum Score', fontsize=12)
        ax.set_title('Momentum States Over Match', fontsize=14, fontweight='bold')
        ax.legend()
        ax.grid(True, alpha=0.3)
        
        plt.tight_layout()
        
        if save_path:
            save_path.parent.mkdir(parents=True, exist_ok=True)
            plt.savefig(save_path, dpi=self.config.get('dpi', 300), bbox_inches='tight')
            print(f"图表已保存至: {save_path}")
        else:
            plt.show()
        
        plt.close()


def main():
    """主函数：生成可视化"""
    print("加载数据...")
    df = pd.read_csv(FEATURES_DATA_PATH)
    
    # 检查是否有动量结果
    momentum_path = MOMENTUM_RESULTS_PATH
    momentum_df = None
    if momentum_path.exists():
        momentum_df = pd.read_csv(momentum_path)
        print("动量状态数据已加载")
    
    visualizer = MatchFlowVisualizer()
    
    # 获取所有比赛ID
    if 'match_id' in df.columns:
        match_ids = df['match_id'].unique()[:3]  # 只处理前3场比赛作为示例
        
        for match_id in match_ids:
            print(f"\n生成比赛 {match_id} 的可视化...")
            
            # 动量走势图
            save_path = VISUALIZATION_DIR / f"momentum_flow_{match_id}.png"
            visualizer.plot_momentum_flow(df, match_id=match_id, save_path=save_path)
            
            # 动量状态图
            if momentum_df is not None:
                save_path = VISUALIZATION_DIR / f"momentum_states_{match_id}.png"
                visualizer.plot_momentum_states(df, momentum_df, 
                                               match_id=match_id, save_path=save_path)
    else:
        # 单场比赛
        save_path = VISUALIZATION_DIR / "momentum_flow.png"
        visualizer.plot_momentum_flow(df, save_path=save_path)
        
        if momentum_df is not None:
            save_path = VISUALIZATION_DIR / "momentum_states.png"
            visualizer.plot_momentum_states(df, momentum_df, save_path=save_path)
    
    print("\n可视化完成！")


if __name__ == "__main__":
    main()
