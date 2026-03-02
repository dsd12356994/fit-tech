"""
LSTM预测模型：预测下一局/下一盘的胜者
"""
import pandas as pd
import numpy as np
from pathlib import Path
import sys
from sklearn.preprocessing import StandardScaler
from sklearn.model_selection import train_test_split
import tensorflow as tf
from tensorflow import keras
from tensorflow.keras import layers
import joblib

sys.path.append(str(Path(__file__).parent.parent.parent))

from config import FEATURES_DATA_PATH, PREDICTION_RESULTS_PATH, LSTM_CONFIG, RANDOM_SEED


class LSTMPredictor:
    """LSTM预测模型"""
    
    def __init__(self, config: dict = None):
        """
        初始化LSTM预测器
        
        Parameters:
        -----------
        config : dict, optional
            配置字典
        """
        self.config = config or LSTM_CONFIG
        self.model = None
        self.scaler = StandardScaler()
        self.sequence_length = self.config.get('sequence_length', 20)
        tf.random.set_seed(self.config.get('random_state', RANDOM_SEED))
    
    def prepare_sequences(self, df: pd.DataFrame, 
                         target_column: str = 'p1_game_win') -> tuple:
        """
        准备LSTM输入序列和目标
        
        Parameters:
        -----------
        df : pd.DataFrame
            特征数据
        target_column : str
            目标列名
            
        Returns:
        --------
        tuple
            (X, y) 序列数据和目标
        """
        # 选择特征列
        feature_cols = [
            'p1_rolling_win_rate',
            'p1_momentum_score',
            'p1_win_streak',
            'set_diff',
            'game_diff',
            'score_diff',
            'serve_win_rate',
            'p1_rolling_distance',
            'rally_count'
        ]
        
        available_cols = [col for col in feature_cols if col in df.columns]
        
        if not available_cols:
            raise ValueError("没有找到可用的特征列")
        
        # 准备目标
        if target_column not in df.columns:
            # 如果没有游戏胜负，使用点胜负
            if 'p1_point_win' in df.columns:
                target_column = 'p1_point_win'
            else:
                raise ValueError(f"找不到目标列: {target_column}")
        
        # 按比赛分组处理
        if 'match_id' in df.columns:
            match_ids = df['match_id'].unique()
            all_X, all_y = [], []
            
            for match_id in match_ids:
                match_df = df[df['match_id'] == match_id].copy().sort_values('point_no')
                
                X_match, y_match = self._create_sequences_for_match(
                    match_df, available_cols, target_column
                )
                
                if len(X_match) > 0:
                    all_X.append(X_match)
                    all_y.append(y_match)
            
            X = np.concatenate(all_X, axis=0)
            y = np.concatenate(all_y, axis=0)
        else:
            X, y = self._create_sequences_for_match(df, available_cols, target_column)
        
        return X, y
    
    def _create_sequences_for_match(self, match_df: pd.DataFrame,
                                    feature_cols: list,
                                    target_column: str) -> tuple:
        """为单场比赛创建序列"""
        # 提取特征和目标
        features = match_df[feature_cols].values
        targets = match_df[target_column].values
        
        # 处理缺失值
        features = np.nan_to_num(features, nan=0.0)
        
        # 标准化特征
        features = self.scaler.fit_transform(features)
        
        # 创建序列
        X, y = [], []
        
        for i in range(self.sequence_length, len(features)):
            X.append(features[i-self.sequence_length:i])
            y.append(targets[i])
        
        if len(X) == 0:
            return np.array([]), np.array([])
        
        return np.array(X), np.array(y)
    
    def build_model(self, input_shape: tuple) -> keras.Model:
        """
        构建LSTM模型
        
        Parameters:
        -----------
        input_shape : tuple
            输入形状 (sequence_length, n_features)
            
        Returns:
        --------
        keras.Model
            LSTM模型
        """
        model = keras.Sequential([
            layers.LSTM(
                self.config.get('hidden_units', 64),
                return_sequences=True,
                input_shape=input_shape
            ),
            layers.Dropout(0.2),
            layers.LSTM(
                self.config.get('hidden_units', 64),
                return_sequences=False
            ),
            layers.Dropout(0.2),
            layers.Dense(32, activation='relu'),
            layers.Dense(1, activation='sigmoid')  # 二分类
        ])
        
        model.compile(
            optimizer='adam',
            loss='binary_crossentropy',
            metrics=['accuracy']
        )
        
        return model
    
    def fit(self, df: pd.DataFrame, 
            target_column: str = 'p1_game_win') -> None:
        """
        训练模型
        
        Parameters:
        -----------
        df : pd.DataFrame
            训练数据
        target_column : str
            目标列名
        """
        print("="*60)
        print("训练LSTM预测模型")
        print("="*60)
        
        # 准备数据
        X, y = self.prepare_sequences(df, target_column)
        
        if len(X) == 0:
            raise ValueError("无法创建有效的训练序列")
        
        print(f"序列数量: {len(X)}")
        print(f"序列长度: {self.sequence_length}")
        print(f"特征维度: {X.shape[2]}")
        
        # 划分训练集和验证集
        X_train, X_val, y_train, y_val = train_test_split(
            X, y,
            test_size=self.config.get('validation_split', 0.2),
            random_state=self.config.get('random_state', RANDOM_SEED),
            stratify=y if len(np.unique(y)) > 1 else None
        )
        
        print(f"训练集大小: {len(X_train)}")
        print(f"验证集大小: {len(X_val)}")
        
        # 构建模型
        self.model = self.build_model((X.shape[1], X.shape[2]))
        print("\n模型结构:")
        self.model.summary()
        
        # 训练模型
        history = self.model.fit(
            X_train, y_train,
            validation_data=(X_val, y_val),
            epochs=self.config.get('epochs', 50),
            batch_size=self.config.get('batch_size', 32),
            verbose=1
        )
        
        print("\n模型训练完成")
        return history
    
    def predict(self, df: pd.DataFrame) -> np.ndarray:
        """
        预测
        
        Parameters:
        -----------
        df : pd.DataFrame
            数据
            
        Returns:
        --------
        np.ndarray
            预测概率
        """
        if self.model is None:
            raise ValueError("模型尚未训练，请先调用fit()方法")
        
        X, _ = self.prepare_sequences(df)
        
        if len(X) == 0:
            return np.array([])
        
        predictions = self.model.predict(X)
        return predictions.flatten()
    
    def evaluate(self, df: pd.DataFrame, 
                 target_column: str = 'p1_game_win') -> dict:
        """
        评估模型
        
        Parameters:
        -----------
        df : pd.DataFrame
            测试数据
        target_column : str
            目标列名
            
        Returns:
        --------
        dict
            评估指标
        """
        if self.model is None:
            raise ValueError("模型尚未训练")
        
        X, y = self.prepare_sequences(df, target_column)
        
        if len(X) == 0:
            return {}
        
        loss, accuracy = self.model.evaluate(X, y, verbose=0)
        
        predictions = self.predict(df)
        predictions_binary = (predictions > 0.5).astype(int)
        
        from sklearn.metrics import precision_score, recall_score, f1_score
        
        metrics = {
            'loss': loss,
            'accuracy': accuracy,
            'precision': precision_score(y, predictions_binary, zero_division=0),
            'recall': recall_score(y, predictions_binary, zero_division=0),
            'f1_score': f1_score(y, predictions_binary, zero_division=0)
        }
        
        return metrics


def main():
    """主函数：执行LSTM预测"""
    # 加载特征数据
    print("加载特征数据...")
    df = pd.read_csv(FEATURES_DATA_PATH)
    
    # 创建预测器
    predictor = LSTMPredictor()
    
    # 训练模型
    history = predictor.fit(df, target_column='p1_game_win')
    
    # 评估模型
    metrics = predictor.evaluate(df, target_column='p1_game_win')
    print("\n模型评估结果:")
    for key, value in metrics.items():
        print(f"{key}: {value:.4f}")
    
    # 保存模型
    model_path = PREDICTION_RESULTS_PATH.parent / "lstm_model.h5"
    predictor.model.save(model_path)
    print(f"\n模型已保存至: {model_path}")
    
    # 保存scaler
    scaler_path = PREDICTION_RESULTS_PATH.parent / "scaler.pkl"
    joblib.dump(predictor.scaler, scaler_path)
    print(f"Scaler已保存至: {scaler_path}")


if __name__ == "__main__":
    main()
