% =========================================================================
% 数据清洗模块 (MATLAB版本)
% =========================================================================
% 
% 功能：处理缺失值、异常值、比分转换、时间对齐
% 
% 使用方法：
%   1. 修改 data_path 变量为你的数据文件路径
%   2. 运行脚本：data_cleaning
%
% =========================================================================

clear; clc; close all;

% ========== 本地数据上传路径（学生需修改） ==========
% Windows: data_path = 'C:\MCM\2024_C\2024_Wimbledon_featured_matches.csv';
% Mac/Linux: data_path = '/Users/xxx/MCM/2024_C/2024_Wimbledon_featured_matches.csv';
data_path = '请替换为你的本地数据文件路径';

% 检查文件是否存在
if ~exist(data_path, 'file')
    error('数据文件不存在，请检查路径: %s', data_path);
end

fprintf('正在加载数据: %s\n', data_path);
data = readtable(data_path);
fprintf('数据加载完成: %d 行, %d 列\n', height(data), width(data));

% =========================================================================
% 1. 处理缺失值
% =========================================================================
fprintf('\n处理缺失值...\n');

% 统计缺失值
missing_count = sum(ismissing(data), 1);
missing_cols = missing_count > 0;
if any(missing_cols)
    fprintf('缺失值统计:\n');
    disp(table(data.Properties.VariableNames(missing_cols)', ...
               missing_count(missing_cols)', ...
               'VariableNames', {'Column', 'MissingCount'}));
    
    % 前向填充数值列
    numeric_vars = varfun(@isnumeric, data, 'OutputFormat', 'uniform');
    for i = 1:width(data)
        if numeric_vars(i) && missing_count(i) > 0
            data{:, i} = fillmissing(data{:, i}, 'previous');
            data{:, i} = fillmissing(data{:, i}, 'next');  % 处理开头缺失值
        end
    end
    
    % 前向填充字符串列
    for i = 1:width(data)
        if ~numeric_vars(i) && missing_count(i) > 0
            data{:, i} = fillmissing(data{:, i}, 'previous');
            data{:, i} = fillmissing(data{:, i}, 'next');
        end
    end
else
    fprintf('数据集中没有缺失值\n');
end

% =========================================================================
% 2. 比分转换
% =========================================================================
fprintf('\n转换比分格式...\n');

% 创建比分映射
score_map = containers.Map({'0','15','30','40','AD','Love'}, {0,1,2,3,4,0});

% 转换 p1_score
if ismember('p1_score', data.Properties.VariableNames)
    p1_score_num = zeros(height(data), 1);
    for i = 1:height(data)
        score_str = char(data.p1_score(i));
        if isKey(score_map, score_str)
            p1_score_num(i) = score_map(score_str);
        else
            p1_score_num(i) = NaN;
        end
    end
    data.p1_score_num = p1_score_num;
    fprintf('p1_score 转换完成\n');
end

% 转换 p2_score
if ismember('p2_score', data.Properties.VariableNames)
    p2_score_num = zeros(height(data), 1);
    for i = 1:height(data)
        score_str = char(data.p2_score(i));
        if isKey(score_map, score_str)
            p2_score_num(i) = score_map(score_str);
        else
            p2_score_num(i) = NaN;
        end
    end
    data.p2_score_num = p2_score_num;
    fprintf('p2_score 转换完成\n');
end

% =========================================================================
% 3. 时间转换
% =========================================================================
fprintf('\n转换时间格式...\n');

if ismember('elapsed_time', data.Properties.VariableNames)
    elapsed_time_seconds = zeros(height(data), 1);
    for i = 1:height(data)
        time_str = char(data.elapsed_time(i));
        parts = strsplit(time_str, ':');
        if length(parts) == 3
            hours = str2double(parts{1});
            minutes = str2double(parts{2});
            seconds = str2double(parts{3});
            elapsed_time_seconds(i) = hours * 3600 + minutes * 60 + seconds;
        elseif length(parts) == 2
            minutes = str2double(parts{1});
            seconds = str2double(parts{2});
            elapsed_time_seconds(i) = minutes * 60 + seconds;
        else
            elapsed_time_seconds(i) = NaN;
        end
    end
    data.elapsed_time_seconds = elapsed_time_seconds;
    fprintf('elapsed_time 转换完成\n');
end

% =========================================================================
% 4. 异常值检测（IQR方法）
% =========================================================================
fprintf('\n检测异常值 (IQR方法)...\n');

numeric_vars = varfun(@isnumeric, data, 'OutputFormat', 'uniform');
numeric_cols = find(numeric_vars);

for i = 1:length(numeric_cols)
    col_idx = numeric_cols(i);
    col_name = data.Properties.VariableNames{col_idx};
    col_data = data{:, col_idx};
    
    % 计算IQR
    Q1 = prctile(col_data, 25);
    Q3 = prctile(col_data, 75);
    IQR = Q3 - Q1;
    lower_bound = Q1 - 1.5 * IQR;
    upper_bound = Q3 + 1.5 * IQR;
    
    % 标记异常值
    outlier_col_name = [col_name '_is_outlier'];
    data.(outlier_col_name) = (col_data < lower_bound) | (col_data > upper_bound);
    
    outlier_count = sum(data.(outlier_col_name));
    if outlier_count > 0
        fprintf('%s: %d 个异常值 (%.2f%%)\n', col_name, outlier_count, ...
                outlier_count/height(data)*100);
    end
end

% =========================================================================
% 5. 保存处理后的数据
% =========================================================================
output_path = 'data/processed/processed_wimbledon.csv';
if ~exist('data/processed', 'dir')
    mkdir('data/processed');
end

writetable(data, output_path);
fprintf('\n数据清洗完成\n');
fprintf('最终数据形状: %d 行, %d 列\n', height(data), width(data));
fprintf('清洗后的数据已保存至: %s\n', output_path);

% 显示数据摘要
fprintf('\n数据摘要:\n');
head(data, 5)
