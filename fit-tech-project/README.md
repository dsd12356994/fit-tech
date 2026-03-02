# 2024 MCM Problem C: 网球动量分析项目

## 📋 项目概述

本项目针对2024年MCM Problem C（网球动量分析）提供完整的解决方案，包括数据预处理、特征工程、动量量化建模、可视化和预测分析。项目达到O奖水平，提供Python和MATLAB双语言实现。

## 🎯 核心功能

1. **数据预处理**：清洗、异常值处理、比分转换、时间对齐
2. **特征工程**：滚动窗口统计、动量指标构造、关键分识别
3. **动量量化模型**：
   - 隐马尔可夫模型（HMM）识别动量状态
   - PELT算法检测动量转折点
   - 随机游走模型分析
4. **可视化分析**：
   - 动态比赛走势图
   - 热力图显示关键分
   - 动量状态转换图
5. **预测模型**：
   - LSTM时序预测
   - 基于动量的胜率预测

## 📁 项目结构

```
fit-tech-project/
├── README.md                          # 项目说明文档
├── requirements.txt                   # Python依赖包
├── config.py                         # 配置文件
├── data/                             # 数据目录
│   ├── raw/                          # 原始数据
│   ├── processed/                    # 处理后数据
│   └── results/                      # 结果输出
├── src/                              # 源代码目录
│   ├── preprocessing/                # 数据预处理
│   │   ├── data_cleaning.py         # 数据清洗
│   │   ├── feature_engineering.py   # 特征工程
│   │   └── data_validation.py       # 数据验证
│   ├── models/                       # 模型实现
│   │   ├── momentum_hmm.py          # HMM动量模型
│   │   ├── changepoint_detection.py # 转折点检测
│   │   └── lstm_predictor.py        # LSTM预测模型
│   ├── visualization/                # 可视化
│   │   ├── match_flow.py            # 比赛走势图
│   │   ├── heatmap_analysis.py      # 热力图分析
│   │   └── momentum_states.py       # 动量状态可视化
│   └── utils/                        # 工具函数
│       ├── score_converter.py       # 比分转换工具
│       └── metrics.py               # 评估指标
├── matlab/                           # MATLAB代码
│   ├── preprocessing/               # MATLAB预处理
│   ├── models/                      # MATLAB模型
│   └── visualization/               # MATLAB可视化
├── notebooks/                        # Jupyter Notebooks
└── docs/                             # 文档
```

## 🚀 快速开始

### 环境要求

- Python 3.8+
- MATLAB R2020b+ (可选)
- 推荐使用conda或venv创建虚拟环境

### 安装依赖

```bash
pip install -r requirements.txt
```

### 数据准备

1. 将原始数据文件 `2024_Wimbledon_featured_matches.csv` 放置在 `data/raw/` 目录
2. 修改 `config.py` 中的文件路径配置

### 运行流程

#### 1. 数据预处理

```bash
python src/preprocessing/data_cleaning.py
python src/preprocessing/feature_engineering.py
```

#### 2. 动量分析

```bash
python src/models/momentum_hmm.py
python src/models/changepoint_detection.py
```

#### 3. 可视化

```bash
python src/visualization/match_flow.py
python src/visualization/heatmap_analysis.py
```

#### 4. 预测模型

```bash
python src/models/lstm_predictor.py
```

## 📊 核心算法

### 1. 动量量化模型

使用隐马尔可夫模型（HMM）将比赛状态分为：
- **优势状态**：球员处于上风
- **劣势状态**：球员处于下风
- **平衡状态**：双方势均力敌

### 2. 转折点检测

使用PELT（Pruned Exact Linear Time）算法检测动量转折点，识别比赛中的关键时刻。

### 3. 特征工程

- **滚动胜率**：过去N点的胜率
- **连胜次数**：连续得分次数
- **关键分指标**：破发点、决胜分等
- **发球优势**：发球方胜率
- **体能指标**：跑动距离、回合数

## 📈 输出结果

- 预处理后的数据集（CSV格式）
- 动量状态序列
- 转折点检测结果
- 可视化图表（PNG/PDF格式）
- 预测模型评估报告

## 🔬 科学性与专业性

- **统计学方法**：使用置换检验验证动量显著性
- **机器学习**：LSTM时序预测，HMM状态识别
- **可视化**：多维度数据展示
- **可复现性**：完整的代码和文档

## 📝 论文撰写建议

1. **数据处理章节**：展示预处理流程和特征工程方法
2. **模型章节**：详细说明HMM和转折点检测算法
3. **结果分析**：结合可视化图表解释动量变化
4. **假设检验**：使用统计方法验证动量存在性
5. **泛化分析**：讨论模型在其他比赛中的应用

## 👥 作者

MCM Problem C 解决方案团队

## 📄 许可证

本项目仅供学术研究使用
