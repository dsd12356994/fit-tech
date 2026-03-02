# 使用指南

## 📋 目录

1. [快速开始](#快速开始)
2. [数据准备](#数据准备)
3. [完整流程运行](#完整流程运行)
4. [分步执行](#分步执行)
5. [数据探索](#数据探索)
6. [数据精简](#数据精简)
7. [统计检验](#统计检验)
8. [结果解读](#结果解读)

---

## 🚀 快速开始

### 1. 环境准备

```bash
# 创建虚拟环境（推荐）
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

# 安装依赖
pip install -r requirements.txt
```

### 2. 数据准备

将原始数据文件 `2024_Wimbledon_featured_matches.csv` 放置在 `data/raw/` 目录下。

### 3. 运行完整流程

```bash
python run_pipeline.py
```

---

## 📁 数据准备

### 数据文件要求

- **文件名**: `2024_Wimbledon_featured_matches.csv`
- **位置**: `data/raw/2024_Wimbledon_featured_matches.csv`
- **格式**: CSV格式，包含以下必需列：
  - `match_id`: 比赛ID
  - `player1`, `player2`: 球员姓名
  - `set_no`, `game_no`, `point_no`: 比赛进程
  - `p1_score`, `p2_score`: 比分
  - `server`: 发球方
  - `point_victor`: 得分者

### 修改数据路径

如果数据文件在其他位置，修改 `config.py` 中的路径：

```python
RAW_DATA_PATH = Path("your/path/to/data.csv")
```

---

## 🔄 完整流程运行

运行 `run_pipeline.py` 将执行以下步骤：

1. **数据清洗** → `data/processed/processed_wimbledon.csv`
2. **特征工程** → `data/processed/features_wimbledon.csv`
3. **HMM动量分析** → `data/results/momentum_states.csv`
4. **转折点检测** → `data/results/changepoints.csv`
5. **可视化生成** → `figures/` 目录

---

## 📝 分步执行

### 1. 数据探索

```bash
python src/preprocessing/data_exploration.py
```

**输出**:
- 数据集基本信息
- 列信息汇总
- 缺失值分析图: `figures/missing_values_analysis.png`
- 异常值分析
- 预处理建议

### 2. 数据清洗

```bash
python src/preprocessing/data_cleaning.py
```

**输出**:
- `data/processed/processed_wimbledon.csv`

**功能**:
- 处理缺失值（前向填充）
- 转换比分格式（字符串→数值）
- 转换时间格式（HH:MM:SS→秒数）
- 检测异常值（标记，不删除）

### 3. 特征工程

```bash
python src/preprocessing/feature_engineering.py
```

**输出**:
- `data/processed/features_wimbledon.csv`

**创建的特征**:
- 滚动胜率（过去N点）
- 连胜次数
- 动量得分
- 比分差（盘分、局分、分数）
- 关键分标识（破发点、决胜分）
- 发球优势指标
- 体能指标（跑动距离、回合数）

### 4. 数据精简（可选）

```bash
python src/preprocessing/data_reduction.py
```

**输出**:
- `data/processed/reduced_deep_wimbledon.csv` (深度分析方案，18-20列)
- `data/processed/reduced_basic_wimbledon.csv` (基础分析方案，10列)
- `data/processed/reduced_deep_aggregated_wimbledon.csv` (按局聚合)

**用途**: 生成精简版数据集，便于AI模型使用

### 5. HMM动量分析

```bash
python src/models/momentum_hmm.py
```

**输出**:
- `data/results/momentum_states.csv`

**功能**:
- 识别动量状态（优势/劣势/平衡）
- 检测状态转换
- 计算状态持续时间

### 6. 转折点检测

```bash
python src/models/changepoint_detection.py
```

**输出**:
- `data/results/changepoints.csv`

**功能**:
- 使用PELT算法检测动量转折点
- 分析转折点特征
- 计算动量变化

### 7. 可视化

```bash
# 比赛走势图
python src/visualization/match_flow.py

# 热力图分析
python src/visualization/heatmap_analysis.py
```

**输出** (在 `figures/` 目录):
- `momentum_flow_*.png`: 动量走势图
- `momentum_states_*.png`: 动量状态图
- `key_points_heatmap_*.png`: 关键分热力图
- `changepoint_analysis_*.png`: 转折点分析图

### 8. LSTM预测模型（可选）

```bash
python src/models/lstm_predictor.py
```

**输出**:
- `data/results/lstm_model.h5`: 训练好的模型
- `data/results/scaler.pkl`: 特征标准化器

**注意**: 训练需要较长时间，建议使用GPU

### 9. 统计检验

```python
from src.utils.statistical_tests import comprehensive_momentum_test
import pandas as pd

# 加载数据
df = pd.read_csv('data/processed/features_wimbledon.csv')
momentum_states = pd.read_csv('data/results/momentum_states.csv')['momentum_state'].values

# 执行综合检验
results = comprehensive_momentum_test(df, momentum_states)
```

**输出**:
- 置换检验结果（验证动量显著性）
- 状态转换概率分析
- 卡方检验（状态转换独立性）

---

## 📊 数据探索

### 使用DataExplorer类

```python
from src.preprocessing.data_exploration import DataExplorer

explorer = DataExplorer()
summary = explorer.explore(save_plots=True)

# 查看摘要
print(summary)
```

### 自定义探索

```python
from src.preprocessing.data_exploration import DataExplorer
import pandas as pd

df = pd.read_csv('data/raw/2024_Wimbledon_featured_matches.csv')
explorer = DataExplorer()

# 执行各项分析
explorer.basic_info(df)
explorer.column_info(df)
explorer.missing_values_analysis(df)
explorer.outlier_analysis(df)
```

---

## 🎯 数据精简

### 创建精简数据集

```python
from src.preprocessing.data_reduction import DataReducer

reducer = DataReducer()

# 方案1: 深度分析方案（18-20列，完整数据）
deep_df = reducer.reduce(mode='deep', aggregate=False, sample=False)
reducer.save_reduced_data(deep_df, filename='reduced_deep.csv')

# 方案2: 基础分析方案（10列，完整数据）
basic_df = reducer.reduce(mode='basic', aggregate=False, sample=False)
reducer.save_reduced_data(basic_df, filename='reduced_basic.csv')

# 方案3: 按局聚合（减少行数）
aggregated_df = reducer.reduce(mode='deep', aggregate=True, 
                               aggregate_level='game', sample=False)
reducer.save_reduced_data(aggregated_df, filename='reduced_aggregated.csv')
```

### 参数说明

- `mode`: `'basic'` 或 `'deep'`
- `aggregate`: 是否聚合（`True`/`False`）
- `aggregate_level`: 聚合级别（`'game'` 或 `'set'`）
- `sample`: 是否抽样（`True`/`False`）
- `sample_ratio`: 抽样比例（0-1之间）

---

## 🔬 统计检验

### 置换检验

```python
from src.utils.statistical_tests import test_momentum_significance
import pandas as pd

df = pd.read_csv('data/processed/features_wimbledon.csv')

# 测试Player 1的动量显著性
results = test_momentum_significance(df, player=1, n_permutations=10000)

print(f"最长连胜: {results['observed_max_streak']}")
print(f"p值: {results['p_value_max_streak']:.4f}")
print(f"是否显著: {results['is_significant']}")
```

### 状态转换分析

```python
from src.utils.statistical_tests import analyze_state_transition_probability
import pandas as pd
import numpy as np

momentum_df = pd.read_csv('data/results/momentum_states.csv')
states = momentum_df['momentum_state'].values

# 分析状态转换
results = analyze_state_transition_probability(states)

print("状态转换概率矩阵:")
print(results['transition_probability'])
print("\n状态持续时间:")
print(results['state_durations'])
```

---

## 📈 结果解读

### 动量状态

- **0 (劣势)**: 球员处于下风
- **1 (平衡)**: 双方势均力敌
- **2 (优势)**: 球员处于上风

### 转折点

转折点表示动量发生显著变化的位置，通常对应：
- 破发点
- 决胜分
- 关键局

### 统计检验结果

- **p值 < 0.05**: 动量显著（非随机）
- **p值 >= 0.05**: 动量不显著（可能是随机的）

---

## ⚙️ 配置说明

### 修改预处理参数

编辑 `config.py`:

```python
PREPROCESSING_CONFIG = {
    "rolling_window": 10,  # 滚动窗口大小
    "outlier_method": "iqr",  # 异常值检测方法
    "missing_value_strategy": "forward_fill"  # 缺失值填充策略
}
```

### 修改模型参数

```python
HMM_CONFIG = {
    "n_states": 3,  # HMM状态数量
    "n_iter": 100,  # 迭代次数
}

LSTM_CONFIG = {
    "sequence_length": 20,  # 输入序列长度
    "hidden_units": 64,  # LSTM隐藏单元数
    "epochs": 50,  # 训练轮数
}
```

---

## 🐛 常见问题

### 1. 数据文件不存在

**错误**: `FileNotFoundError: 数据文件不存在`

**解决**: 确保数据文件在 `data/raw/` 目录下，或修改 `config.py` 中的路径

### 2. 内存不足

**解决**: 
- 使用数据精简功能减少数据量
- 按比赛分组处理
- 使用聚合功能（按局或按盘）

### 3. LSTM训练慢

**解决**:
- 使用GPU加速
- 减少训练轮数（epochs）
- 减少序列长度（sequence_length）

### 4. 可视化中文乱码

**解决**: 修改 `config.py` 中的字体设置：

```python
VISUALIZATION_CONFIG = {
    "chinese_font": "SimHei"  # Windows
    # 或 "WenQuanYi Zen Hei"  # Linux
    # 或 "Arial Unicode MS"  # Mac
}
```

---

## 📚 更多资源

- **README.md**: 项目概述
- **PROJECT_SUMMARY.md**: 项目总结
- **docs/methodology.md**: 方法论说明

---

## 💡 提示

1. **首次运行**: 建议先运行数据探索，了解数据质量
2. **大数据集**: 使用数据精简功能生成精简版数据集
3. **快速测试**: 使用抽样功能（`sample=True`）快速测试流程
4. **结果保存**: 所有结果都会自动保存，可以随时查看

---

**最后更新**: 2024年  
**版本**: 1.0.0
