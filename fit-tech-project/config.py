"""
配置文件：设置数据路径、模型参数等
"""
import os
from pathlib import Path

# 项目根目录
PROJECT_ROOT = Path(__file__).parent

# 数据路径配置
DATA_DIR = PROJECT_ROOT / "data"
RAW_DATA_DIR = DATA_DIR / "raw"
PROCESSED_DATA_DIR = DATA_DIR / "processed"
RESULTS_DIR = DATA_DIR / "results"

# 原始数据文件路径（用户需要修改）
RAW_DATA_PATH = RAW_DATA_DIR / "2024_Wimbledon_featured_matches.csv"

# 处理后数据保存路径
PROCESSED_DATA_PATH = PROCESSED_DATA_DIR / "processed_wimbledon.csv"
FEATURES_DATA_PATH = PROCESSED_DATA_DIR / "features_wimbledon.csv"

# 结果保存路径
MOMENTUM_RESULTS_PATH = RESULTS_DIR / "momentum_states.csv"
CHANGEPOINT_RESULTS_PATH = RESULTS_DIR / "changepoints.csv"
PREDICTION_RESULTS_PATH = RESULTS_DIR / "predictions.csv"

# 可视化输出路径
VISUALIZATION_DIR = PROJECT_ROOT / "figures"

# 创建必要的目录
for dir_path in [RAW_DATA_DIR, PROCESSED_DATA_DIR, RESULTS_DIR, VISUALIZATION_DIR]:
    dir_path.mkdir(parents=True, exist_ok=True)

# 数据预处理参数
PREPROCESSING_CONFIG = {
    "score_mapping": {
        "0": 0,
        "15": 1,
        "30": 2,
        "40": 3,
        "AD": 4
    },
    "rolling_window": 10,  # 滚动窗口大小（点数）
    "outlier_method": "iqr",  # 异常值检测方法：'iqr' 或 'zscore'
    "outlier_threshold": 3.0,  # Z-score阈值
    "missing_value_strategy": "forward_fill"  # 缺失值填充策略
}

# HMM模型参数
HMM_CONFIG = {
    "n_states": 3,  # 状态数量：优势、劣势、平衡
    "n_iter": 100,  # 迭代次数
    "random_state": 42
}

# 转折点检测参数
CHANGEPOINT_CONFIG = {
    "model": "rbf",  # 模型类型：'l2', 'rbf', 'linear'
    "pen": 10,  # 惩罚参数
    "min_size": 5  # 最小段长度
}

# LSTM预测模型参数
LSTM_CONFIG = {
    "sequence_length": 20,  # 输入序列长度
    "hidden_units": 64,  # 隐藏层单元数
    "epochs": 50,
    "batch_size": 32,
    "validation_split": 0.2,
    "random_state": 42
}

# 可视化参数
VISUALIZATION_CONFIG = {
    "figure_size": (12, 6),
    "dpi": 300,
    "style": "seaborn-v0_8",
    "font_size": 12,
    "chinese_font": "WenQuanYi Zen Hei"  # 中文字体
}

# 随机种子
RANDOM_SEED = 42
