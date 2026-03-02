"""
热力图分析：展示关键分分布和动量转换
"""
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from pathlib import Path
import sys

sys.path.append(str(Path(__file__).parent.parent.parent))

from config import FEATURES_DATA_PATH, CHANGEPOINT_RESULTS_PATH, VISUALIZATION_DIR, VISUALIZATION_CONFIG


class HeatmapAnalyzer:
    """热力图分析器"""
    
    def __init__(self, config: dict = None):
        """初始化分析器"""
        self.config = config or VISUALIZATION_CONFIG
        self._setup_style()
    
    def _setup_style(self):
        """设置绘图样式"""
        plt.style.use(self.config.get('style', 'seaborn-v0_8'))
        plt.rcParams['figure.figsize'] = self.config.get('figure_size', (12, 8))
        plt.rcParams['font.size'] = self.config.get('font_size', 12)
        
        try:
            plt.rcParams['font.sans-serif'] = [self.config.get('chinese_font', 'Arial')]
            plt.rcParams['axes.unicode_minus'] = False
        except:
            pass
    
    def plot_key_points_heatmap(self, df: pd.DataFrame,
                               match_id: str = None,
                               save_path: Path = None) -> None:
        """
        绘制关键分热力图
        
        Parameters:
        -----------
        df : pd.DataFrame
            数据
        match_id : str, optional
            比赛ID
        save_path : Path, optional
            保存路径
        """
        if match_id and 'match_id' in df.columns:
            df = df[df['match_id'] == match_id].copy()
        
        # 创建关键分矩阵
        if 'set_no' in df.columns and 'game_no' in df.columns:
            # 创建集合-局矩阵
            max_set = df['set_no'].max()
            max_game = df['game_no'].max()
            
            heatmap_data = np.zeros((max_set, max_game))
            
            # 标记关键分
            key_point_types = {
                'break_point': 'is_break_point',
                'set_point': 'is_set_point'
            }
            
            for point_type, col_name in key_point_types.items():
                if col_name in df.columns:
                    for _, row in df[df[col_name] == 1].iterrows():
                        set_idx = int(row['set_no']) - 1
                        game_idx = int(row['game_no']) - 1
                        if 0 <= set_idx < max_set and 0 <= game_idx < max_game:
                            heatmap_data[set_idx, game_idx] += 1
            
            # 绘制热力图
            fig, ax = plt.subplots(figsize=(12, 6))
            
            sns.heatmap(heatmap_data, annot=True, fmt='.0f', cmap='YlOrRd',
                       xticklabels=range(1, max_game + 1),
                       yticklabels=range(1, max_set + 1),
                       cbar_kws={'label': 'Key Points Count'},
                       ax=ax)
            
            ax.set_xlabel('Game Number', fontsize=12)
            ax.set_ylabel('Set Number', fontsize=12)
            ax.set_title('Key Points Distribution Heatmap', fontsize=14, fontweight='bold')
            
            plt.tight_layout()
            
            if save_path:
                save_path.parent.mkdir(parents=True, exist_ok=True)
                plt.savefig(save_path, dpi=self.config.get('dpi', 300), bbox_inches='tight')
                print(f"图表已保存至: {save_path}")
            else:
                plt.show()
            
            plt.close()
    
    def plot_momentum_transition_heatmap(self, momentum_df: pd.DataFrame,
                                        match_id: str = None,
                                        save_path: Path = None) -> None:
        """
        绘制动量转换热力图
        
        Parameters:
        -----------
        momentum_df : pd.DataFrame
            动量状态数据
        match_id : str, optional
            比赛ID
        save_path : Path, optional
            保存路径
        """
        if match_id and 'match_id' in momentum_df.columns:
            momentum_df = momentum_df[momentum_df['match_id'] == match_id].copy()
        
        if 'momentum_state' not in momentum_df.columns:
            print("动量状态数据不存在")
            return
        
        # 创建状态转换矩阵
        states = momentum_df['momentum_state'].values
        n_states = len(np.unique(states))
        
        transition_matrix = np.zeros((n_states, n_states))
        
        for i in range(len(states) - 1):
            current_state = int(states[i])
            next_state = int(states[i + 1])
            transition_matrix[current_state, next_state] += 1
        
        # 转换为概率
        row_sums = transition_matrix.sum(axis=1, keepdims=True)
        row_sums[row_sums == 0] = 1  # 避免除零
        transition_prob = transition_matrix / row_sums
        
        # 绘制热力图
        fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(14, 6))
        
        # 转换次数
        sns.heatmap(transition_matrix, annot=True, fmt='.0f', cmap='Blues',
                   xticklabels=['Disadvantage', 'Balance', 'Advantage'][:n_states],
                   yticklabels=['Disadvantage', 'Balance', 'Advantage'][:n_states],
                   cbar_kws={'label': 'Transition Count'},
                   ax=ax1)
        ax1.set_title('Momentum State Transition Count', fontsize=12, fontweight='bold')
        ax1.set_xlabel('Next State', fontsize=10)
        ax1.set_ylabel('Current State', fontsize=10)
        
        # 转换概率
        sns.heatmap(transition_prob, annot=True, fmt='.2f', cmap='YlOrRd',
                   xticklabels=['Disadvantage', 'Balance', 'Advantage'][:n_states],
                   yticklabels=['Disadvantage', 'Balance', 'Advantage'][:n_states],
                   cbar_kws={'label': 'Transition Probability'},
                   vmin=0, vmax=1,
                   ax=ax2)
        ax2.set_title('Momentum State Transition Probability', fontsize=12, fontweight='bold')
        ax2.set_xlabel('Next State', fontsize=10)
        ax2.set_ylabel('Current State', fontsize=10)
        
        plt.tight_layout()
        
        if save_path:
            save_path.parent.mkdir(parents=True, exist_ok=True)
            plt.savefig(save_path, dpi=self.config.get('dpi', 300), bbox_inches='tight')
            print(f"图表已保存至: {save_path}")
        else:
            plt.show()
        
        plt.close()
    
    def plot_changepoint_analysis(self, df: pd.DataFrame,
                                 changepoint_df: pd.DataFrame,
                                 match_id: str = None,
                                 save_path: Path = None) -> None:
        """
        绘制转折点分析图
        
        Parameters:
        -----------
        df : pd.DataFrame
            特征数据
        changepoint_df : pd.DataFrame
            转折点数据
        match_id : str, optional
            比赛ID
        save_path : Path, optional
            保存路径
        """
        if match_id and 'match_id' in df.columns:
            df = df[df['match_id'] == match_id].copy().sort_values('point_no')
            changepoint_df = changepoint_df[changepoint_df['match_id'] == match_id].copy()
        
        fig, ax = plt.subplots(figsize=(14, 6))
        
        # 绘制动量得分
        if 'p1_momentum_score' in df.columns:
            ax.plot(df['point_no'], df['p1_momentum_score'],
                   linewidth=2, color='blue', alpha=0.7, label='Momentum Score')
        
        # 标记转折点
        if len(changepoint_df) > 0:
            changepoints = changepoint_df['point_no'].values
            
            for cp in changepoints:
                ax.axvline(x=cp, color='red', linestyle='--', linewidth=2, alpha=0.7)
                
                # 标注转折点信息
                cp_data = changepoint_df[changepoint_df['point_no'] == cp].iloc[0]
                if 'momentum_change' in cp_data:
                    ax.text(cp, ax.get_ylim()[1] * 0.9,
                           f'Δ={cp_data["momentum_change"]:.2f}',
                           rotation=90, fontsize=8, ha='right')
        
        ax.axhline(y=0, color='black', linestyle='-', alpha=0.3)
        ax.set_xlabel('Point Number', fontsize=12)
        ax.set_ylabel('Momentum Score', fontsize=12)
        ax.set_title('Momentum Changepoints Analysis', fontsize=14, fontweight='bold')
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
    """主函数：生成热力图分析"""
    print("加载数据...")
    df = pd.read_csv(FEATURES_DATA_PATH)
    
    # 检查转折点数据
    changepoint_path = CHANGEPOINT_RESULTS_PATH
    changepoint_df = None
    if changepoint_path.exists():
        changepoint_df = pd.read_csv(changepoint_path)
        print("转折点数据已加载")
    
    analyzer = HeatmapAnalyzer()
    
    # 获取比赛ID
    if 'match_id' in df.columns:
        match_ids = df['match_id'].unique()[:2]  # 处理前2场比赛
        
        for match_id in match_ids:
            print(f"\n生成比赛 {match_id} 的热力图分析...")
            
            # 关键分热力图
            save_path = VISUALIZATION_DIR / f"key_points_heatmap_{match_id}.png"
            analyzer.plot_key_points_heatmap(df, match_id=match_id, save_path=save_path)
            
            # 转折点分析
            if changepoint_df is not None:
                save_path = VISUALIZATION_DIR / f"changepoint_analysis_{match_id}.png"
                analyzer.plot_changepoint_analysis(df, changepoint_df,
                                                   match_id=match_id, save_path=save_path)
    else:
        # 单场比赛
        save_path = VISUALIZATION_DIR / "key_points_heatmap.png"
        analyzer.plot_key_points_heatmap(df, save_path=save_path)
        
        if changepoint_df is not None:
            save_path = VISUALIZATION_DIR / "changepoint_analysis.png"
            analyzer.plot_changepoint_analysis(df, changepoint_df, save_path=save_path)
    
    print("\n热力图分析完成！")


if __name__ == "__main__":
    main()
