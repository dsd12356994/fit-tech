# 数据目录说明

## 原始数据

请将温网比赛数据文件 `2024_Wimbledon_featured_matches.csv` 放置在此目录下。

## 数据格式要求

数据文件应包含以下列（根据实际数据调整）：

### 必需列
- `match_id`: 比赛ID
- `player1`, `player2`: 选手姓名
- `set_no`, `game_no`, `point_no`: 比赛进程标识
- `p1_sets`, `p2_sets`: 盘分
- `p1_games`, `p2_games`: 局分
- `p1_score`, `p2_score`: 分数（字符串格式：0, 15, 30, 40, AD）
- `point_victor`: 得分者（1或2）
- `server`: 发球方（1或2）

### 可选列（用于更深入的分析）
- `elapsed_time`: 比赛时间
- `p1_ace`, `p2_ace`: ACE球数
- `p1_double_fault`, `p2_double_fault`: 双误数
- `p1_winner`, `p2_winner`: 制胜分数
- `p1_distance_run`, `p2_distance_run`: 跑动距离
- `rally_count`: 回合数
- `speed_mph`: 发球速度
- `p1_break_pt`, `p2_break_pt`: 破发点标识
- 其他技术统计列

## 数据示例

```csv
match_id,player1,player2,set_no,game_no,point_no,p1_sets,p2_sets,p1_games,p2_games,p1_score,p2_score,point_victor,server
2023-W-001,Player A,Player B,1,1,1,0,0,0,0,0,0,1,1
2023-W-001,Player A,Player B,1,1,2,0,0,0,0,15,0,1,1
...
```

## 注意事项

1. 确保数据文件为CSV格式
2. 编码建议使用UTF-8
3. 如果数据中包含缺失值，代码会自动处理
4. 确保 `match_id` 列存在，用于区分不同比赛
