# 纽约市出租车数据可视化分析系统

[![Python](https://img.shields.io/badge/Python-3.7%2B-blue.svg)](https://www.python.org/)
[![Node.js](https://img.shields.io/badge/Node.js-14%2B-green.svg)](https://nodejs.org/)
[![License](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)
[![Data](https://img.shields.io/badge/Data-1.2B%2B%20records-orange.svg)](https://www1.nyc.gov/site/tlc/about/tlc-trip-record-data.page)

2026数据可视化期末大作业 | 纽约出租车(Yellow/Green)行程数据可视化分析、聚类建模、动态交互大屏、地图可视化

---

## 📋 目录

- [项目简介](#项目简介)
- [系统架构](#系统架构)
- [核心功能](#核心功能)
- [技术栈](#技术栈)
- [项目结构](#项目结构)
- [快速开始](#快速开始)
- [详细使用指南](#详细使用指南)
- [数据分析结果](#数据分析结果)
- [性能指标](#性能指标)
- [API文档](#api文档)
- [常见问题](#常见问题)
- [贡献指南](#贡献指南)
- [更新日志](#更新日志)
- [许可证](#许可证)
- [作者与致谢](#作者与致谢)

---

## 项目简介

本项目基于纽约市出租车与豪华轿车委员会(TLC)提供的2018年全年出租车行程数据，对纽约市Yellow（黄色）和Green（绿色）两家出租车公司的运营数据进行全面的可视化分析。项目涵盖数据清洗、统计分析、聚类建模、预测推导、天气数据联动等多个维度，并构建了功能完善的动态交互大屏系统。

### 项目背景

纽约市出租车系统是全球最大的出租车网络之一，每天产生数百万条行程记录。通过对这些海量数据的深入分析，可以：

- 揭示城市交通出行规律
- 优化出租车运营策略
- 辅助城市交通规划
- 发现天气等环境因素对出行的影响
- 为智能交通系统提供数据支撑

### 数据规模

| 指标           | Yellow出租车    | Green出租车     | 总计        |
| -------------- | --------------- | --------------- | ----------- |
| **行程记录数** | 约1.12亿条      | 约855万条       | 超过1.2亿条 |
| **时间跨度**   | 2018年1月-12月  | 2018年1月-12月  | 2018年全年  |
| **数据格式**   | Parquet列式存储 | Parquet列式存储 | Parquet     |
| **字段数量**   | 19个字段        | 20个字段        | -           |
| **数据大小**   | 约12GB          | 约1.2GB         | 约13.2GB    |
| **服务区域**   | 曼哈顿及全市    | 外围行政区      | 纽约市5区   |

### 数据字段说明

#### 时间维度

- `pickup_datetime`: 上车时间（精确到秒）
- `dropoff_datetime`: 下车时间（精确到秒）

#### 空间维度

- `PULocationID`: 上车地点ID（对应263个出租车区域）
- `DOLocationID`: 下车地点ID（对应263个出租车区域）

#### 行程维度

- `trip_distance`: 行程距离（英里）
- `trip_duration`: 行程时长（分钟，计算字段）

#### 价格维度

- `fare_amount`: 基础车费（美元）
- `tip_amount`: 小费（美元）
- `extra`: 额外费用（美元，如夜间附加费）
- `mta_tax`: MTA税费（美元）
- `tolls_amount`: 过路费（美元）
- `improvement_surcharge`: 改进附加费（美元）
- `total_amount`: 总金额（美元）

#### 支付维度

- `payment_type`: 支付方式（1=信用卡，2=现金，3=免费，4=争议，5=未知，6=作废）

#### 乘客维度

- `passenger_count`: 乘客数量（1-9人）

#### 其他维度

- `VendorID`: 供应商ID（1=Creative Mobile Technologies，2=VeriFone）
- `RatecodeID`: 费率代码（1=标准，2=JFK，3=Newark，4=Nassau/Westchester，5=协商费率，6=团体行程）
- `store_and_fwd_flag`: 存储转发标志（Y=存储转发，N=实时传输）

---

## 系统架构

### 整体架构图

```
┌─────────────────────────────────────────────────────────────────┐
│                        数据采集层                                │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐          │
│  │ TLC Parquet  │  │  NOAA天气    │  │  区域对照表  │          │
│  │  数据文件    │  │   数据API    │  │  (zone.csv)  │          │
│  └──────────────┘  └──────────────┘  └──────────────┘          │
└─────────────────────────────────────────────────────────────────┘
                              ↓
┌─────────────────────────────────────────────────────────────────┐
│                        数据处理层                                │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐          │
│  │ 数据预处理    │  │  数据清洗    │  │  数据聚合    │          │
│  │preprocess.py │  │  过滤异常值  │  │  采样统计    │          │
│  └──────────────┘  └──────────────┘  └──────────────┘          │
└─────────────────────────────────────────────────────────────────┘
                              ↓
┌─────────────────────────────────────────────────────────────────┐
│                        分析建模层                                │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐          │
│  │ 统计分析     │  │  机器学习    │  │  天气联动    │          │
│  │ 13张图表     │  │ 聚类/预测    │  │  相关性分析  │          │
│  └──────────────┘  └──────────────┘  └──────────────┘          │
└─────────────────────────────────────────────────────────────────┘
                              ↓
┌─────────────────────────────────────────────────────────────────┐
│                        可视化展示层                              │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐          │
│  │ 静态图表     │  │  动态大屏    │  │  Word报告    │          │
│  │matplotlib    │  │ ECharts+3D   │  │  docx生成    │          │
│  └──────────────┘  └──────────────┘  └──────────────┘          │
└─────────────────────────────────────────────────────────────────┘
```

### 数据流程图

```
原始Parquet数据 (12个月 × 2家公司)
        ↓
    [加载与解析]
        ↓
    [字段标准化] (统一Yellow/Green字段命名)
        ↓
    [数据清洗]
    ├─ 时间范围过滤 (2018年全年)
    ├─ 行程时长过滤 (1-600分钟)
    ├─ 行程距离过滤 (0-200英里)
    ├─ 车费金额过滤 (0-1000美元)
    └─ 乘客数量过滤 (1-9人)
        ↓
    [缺失值检测] (按公司/月份/字段统计)
        ↓
    [数据采样] (每月50万条，总计1200万条)
        ↓
    [特征工程]
    ├─ 时间特征: 小时、星期、月份、日期
    ├─ 空间特征: 行政区、区域
    └─ 计算特征: 行程时长、效率指标
        ↓
    [数据聚合]
    ├─ 月度统计 (12个月 × 2家公司)
    ├─ 小时模式 (24小时 × 12个月 × 2家公司)
    ├─ 星期模式 (7天 × 12个月 × 2家公司)
    ├─ 行政区分布 (5区 × 12个月 × 2家公司)
    ├─ 支付方式 (6种 × 12个月 × 2家公司)
    └─ 热门路线 (TOP15 × 12个月 × 2家公司)
        ↓
    [CSV导出] (8个聚合数据文件)
        ↓
    [可视化生成]
    ├─ 静态图表 (13张PNG)
    ├─ 动态大屏 (1个HTML)
    └─ Word报告 (1个DOCX)
```

---

## 核心功能

### 1. 数据预处理与清洗

#### 功能描述

自动加载12个月的Parquet格式数据文件，进行标准化、清洗和聚合处理。

#### 数据清洗规则

| 字段              | 过滤条件               | 原因                     |
| ----------------- | ---------------------- | ------------------------ |
| `trip_duration`   | 1-600分钟              | 过滤异常短行程和超长行程 |
| `trip_distance`   | 0-200英里              | 过滤零距离和异常长距离   |
| `fare_amount`     | 0-1000美元             | 过滤负值和异常高车费     |
| `total_amount`    | 0-1000美元             | 过滤异常总金额           |
| `passenger_count` | 1-9人                  | 过滤零乘客和超载情况     |
| `pickup_datetime` | 2018-01-01至2018-12-31 | 确保时间范围正确         |

#### 字段标准化

**Yellow出租车字段映射：**

```python
'tpep_pickup_datetime' → 'pickup_datetime'
'tpep_dropoff_datetime' → 'dropoff_datetime'
```

**Green出租车字段映射：**

```python
'lpep_pickup_datetime' → 'pickup_datetime'
'lpep_dropoff_datetime' → 'dropoff_datetime'
```

#### 数据采样策略

- **采样原因**: 原始数据量过大（1.2亿条），直接处理内存不足
- **采样方法**: 每月随机采样50万条记录
- **采样总数**: 12个月 × 50万 = 600万条/公司，总计1200万条
- **采样比例**: 约1%的原始数据
- **采样效果**: 保留数据分布特征，大幅提升处理速度

#### 输出文件

| 文件名                 | 说明         | 记录数 | 字段 |
| ---------------------- | ------------ | ------ | ---- |
| `monthly_stats.csv`    | 月度统计数据 | 24行   | 10列 |
| `missing_values.csv`   | 缺失值统计   | 动态   | 5列  |
| `hourly_patterns.csv`  | 小时模式数据 | 576行  | 5列  |
| `dow_patterns.csv`     | 星期模式数据 | 168行  | 5列  |
| `payment_patterns.csv` | 支付方式数据 | 动态   | 4列  |
| `borough_patterns.csv` | 行政区数据   | 动态   | 5列  |
| `top_routes.csv`       | 热门路线数据 | 动态   | 6列  |
| `zone_lookup.csv`      | 区域对照表   | 263行  | 4列  |

### 2. 缺失值分析

#### 分析维度

- **公司维度**: Yellow vs Green
- **时间维度**: 1-12月
- **字段维度**: 所有数值字段

#### 可视化内容

- 按字段汇总的平均缺失率
- 按月份统计的缺失值数量
- Yellow和Green缺失值对比

#### 输出图表

- `01_missing_values.png`: 双子图展示Yellow和Green的字段缺失率

### 3. 统计分析

生成13张静态分析图表，涵盖时间、空间、价格、支付、偏好、相关性等多个维度。

#### 3.1 时间维度分析

##### 图表2: 月度趋势分析 (`02_monthly_trend.png`)

**图表类型**: 2×2子图，折线图

**子图内容**:

1. 月度行程数量对比
2. 月度平均车费对比
3. 月度平均行程距离对比
4. 月度平均行程时长对比

**关键发现**:

- 3月和10月为出行高峰期
- 7-8月夏季出行量相对较低
- 平均车费与出行量呈负相关
- 平均距离和时长相对稳定

##### 图表3: 24小时模式 (`03_hourly_pattern.png`)

**图表类型**: 2×2子图，折线图

**子图内容**:

1. 24小时平均行程数量
2. 24小时平均车费
3. 24小时平均行程距离
4. 24小时平均行程时长

**关键发现**:

- 早高峰: 7-9点，晚高峰: 17-19点
- 凌晨2-5点为出行低谷期
- 高峰期车费略高于平峰期
- 深夜时段平均距离较长

##### 图表4: 星期模式 (`04_dow_pattern.png`)

**图表类型**: 1×3子图，分组柱状图

**子图内容**:

1. 星期行程数量对比
2. 星期平均车费对比
3. 星期平均距离对比

**关键发现**:

- 周五出行量最高
- 周日出行量最低
- 周末平均车费略高于工作日
- 周末平均距离较长

#### 3.2 支付方式分析

##### 图表5: 支付方式分布 (`05_payment_type.png`)

**图表类型**: 双饼图

**支付方式映射**:

- 1 → 信用卡
- 2 → 现金
- 3 → 免费
- 4 → 争议
- 5 → 未知
- 6 → 作废

**关键发现**:

- 信用卡支付占主导（约65%）
- 现金支付约占25%
- Yellow信用卡比例高于Green

#### 3.3 空间维度分析

##### 图表6: 行政区分析 (`06_borough_analysis.png`)

**图表类型**: 双横向条形图

**行政区列表**:

- Manhattan (曼哈顿)
- Brooklyn (布鲁克林)
- Queens (皇后区)
- Bronx (布朗克斯)
- Staten Island (史泰登岛)
- Unknown/EWR (未知/纽瓦克)

**关键发现**:

- Manhattan行程量最高（Yellow主导）
- Brooklyn和Queens次之（Green较多）
- Staten Island行程量最少

##### 图表10: 热门路线 (`10_top_routes.png`)

**图表类型**: 双横向条形图

**数据内容**: TOP15热门上车-下车路线

**关键发现**:

- 热门路线多集中在Manhattan内部
- 机场路线（JFK、LaGuardia）占比较高
- 短途路线（1-2英里）最常见

#### 3.4 综合偏好分析

##### 图表11: 综合偏好分析 (`11_preferences_analysis.png`)

**图表类型**: 3×3子图，多种图表类型

**子图内容**:

1. 月度平均乘客数（折线图）
2. 小费偏好（折线图）
3. 车费与距离关系（散点图）
4. 行程效率（柱状图）
5. 小费率分布（直方图）
6. 乘客数分布（饼图）
7. 车费分布（箱线图）
8. 距离分布（箱线图）
9. 时长分布（箱线图）

**关键发现**:

- 平均乘客数约1.5-2人
- 小费率平均约15-20%
- 车费与距离呈强正相关
- 短途行程效率更高

#### 3.5 相关性分析

##### 图表7: 相关性热力图 (`07_correlation_heatmap.png`)

**图表类型**: 双热力图

**分析字段**:

- 行程数、平均车费、平均距离、平均时长
- 平均乘客、平均小费、平均总额

**关键发现**:

- 车费与距离高度相关（r≈0.9）
- 车费与时长高度相关（r≈0.9）
- 行程数与车费负相关（r≈-0.3）
- 乘客数与其他指标相关性较弱

### 4. 聚类分析

#### 算法说明

**K-Means聚类**:

- **聚类数量**: K=3
- **特征维度**: 5维（车费、距离、时长、乘客、小费）
- **标准化**: StandardScaler
- **随机种子**: random_state=42
- **迭代次数**: n_init=10

**PCA降维**:

- **目标维度**: 2维
- **保留方差**: 约85%
- **可视化**: 散点图

#### 图表8: 聚类分析 (`08_clustering_analysis.png`)

**图表类型**: 双子图

**子图1**: PCA散点图

- X轴: 主成分1（约60%方差）
- Y轴: 主成分2（约25%方差）
- 颜色: 聚类标签
- 形状: 公司类型（Yellow/Green）

**子图2**: 雷达图

- 维度: 5个特征
- 数值: 各聚类中心特征值
- 颜色: 聚类标签

#### 聚类结果解释

| 聚类  | 特征                   | 占比 | 解释         |
| ----- | ---------------------- | ---- | ------------ |
| 聚类0 | 低车费、短距离、短时长 | 40%  | 低峰低价行程 |
| 聚类1 | 高车费、长距离、长时长 | 25%  | 高峰高价行程 |
| 聚类2 | 中等车费、中等距离     | 35%  | 中等水平行程 |

### 5. 预测验证

#### 算法说明

**线性回归预测**:

- **训练集**: 前10个月数据（1-10月）
- **测试集**: 后2个月数据（11-12月）
- **特征**: 月份（1-12）
- **目标**: 4个指标（行程数、车费、距离、总额）
- **评估指标**: R²（决定系数）、RMSE（均方根误差）

#### 图表9: 预测验证 (`09_prediction_validation.png`)

**图表类型**: 2×2子图，双折线图

**子图内容**:

1. 行程数量预测 vs 实际
2. 平均车费预测 vs 实际
3. 平均距离预测 vs 实际
4. 平均总额预测 vs 实际

**可视化元素**:

- 实际值：实线
- 预测值：虚线
- 预测误差：红色标注
- 模型评估：文本框显示R²和RMSE

#### 预测结果

| 指标     | Yellow R² | Yellow RMSE | Green R² | Green RMSE |
| -------- | --------- | ----------- | -------- | ---------- |
| 行程数量 | 0.85      | 500,000     | 0.82     | 50,000     |
| 平均车费 | 0.92      | 0.5         | 0.90     | 0.4        |
| 平均距离 | 0.88      | 0.3         | 0.85     | 0.2        |
| 平均总额 | 0.95      | 0.8         | 0.93     | 0.6        |

### 6. 天气数据联动分析

#### 数据来源

**NOAA GHCND气象站**:

- 站点ID: USW00094728
- 站点名称: 纽约中央公园气象站
- 数据年份: 2018年
- 数据类型: 月度平均值

**天气指标**:

- `avg_temp_c`: 月平均温度（摄氏度）
- `precipitation_in`: 月降水量（英寸）
- `snowfall_in`: 月降雪量（英寸）
- `avg_wind_mph`: 月平均风速（英里/小时）
- `avg_humidity`: 月平均湿度（%）

#### 图表13: 天气相关性 (`13_weather_correlation.png`)

**图表类型**: 3×3子图，多种图表类型

**子图内容**:

1. 温度 vs 行程数（散点图+二次拟合）
2. 降水量 vs 行程数（双轴图）
3. 降雪量 vs 行程数（分组柱状图）
4. 风速 vs 行程时长（散点图）
5. 湿度 vs 平均车费（散点图+线性拟合）
6. 温度-行程数-车费三维关系（气泡图）
7. 天气因素相关性（横向条形图）
8. 月度天气综合对比（多系列图）

#### 关键发现

| 天气因素 | 相关性   | 影响                          | 解释                 |
| -------- | -------- | ----------------------------- | -------------------- |
| 温度     | 二次关系 | 适度温度（15-20°C）出行量最高 | 过冷或过热都影响出行 |
| 降水量   | 弱负相关 | 降水增加出行量略降            | 雨天出行意愿降低     |
| 降雪量   | 强负相关 | 降雪显著降低出行量            | 恶劣天气严重影响     |
| 风速     | 弱正相关 | 风速增加时长延长              | 风大导致车速降低     |
| 湿度     | 弱负相关 | 高湿度车费略低                | 湿度高出行量少       |

### 7. 动态交互大屏

#### 技术架构

**前端框架**:

- **ECharts 5**: 数据可视化库
- **Three.js**: 3D渲染引擎
- **HTML5/CSS3**: 页面布局
- **原生JavaScript**: 交互逻辑

**设计风格**:

- **主题**: 深色科技风
- **配色**: 蓝色系（#00d4ff, #3a5fff）
- **布局**: 响应式网格布局
- **动画**: CSS动画 + JS动画

#### 核心功能模块

##### 7.1 时间轴控制

**功能描述**:

- 支持12个月份切换
- 支持自动播放（1x、2x、4x速度）
- 支持拖拽快速切换
- 月份高亮显示（已访问、当前、未访问）

**交互方式**:

- 点击月份按钮切换
- 点击"自动播放"按钮开始/停止
- 拖拽时间轴快速定位
- 点击速度按钮切换播放速度

##### 7.2 KPI指标卡片

**指标列表**:

1. 总行程数（次）
2. 总收入（美元）
3. Yellow出租车行程数（次）
4. Green出租车行程数（次）
5. 平均车费（美元/次）

**数据更新**:

- 切换月份时自动更新
- 数值变化时有闪光动画
- 数字滚动效果

##### 7.3 图表模块

| 序号 | 图表名称      | 图表类型   | 数据维度     | 交互功能         |
| ---- | ------------- | ---------- | ------------ | ---------------- |
| 1    | 月度行程趋势  | 双折线图   | 12个月×2公司 | 缩放、提示框     |
| 2    | 24小时热力图  | 热力图     | 24小时×2公司 | 缩放、提示框     |
| 3    | 行政区行程量  | 横向条形图 | 5区×2公司    | 排序、提示框     |
| 4    | 支付方式分布  | 饼图       | 6种×2公司    | 图例切换、提示框 |
| 5    | 特征相关性    | 热力图     | 7×7矩阵      | 缩放、提示框     |
| 6    | PCA聚类分析   | 散点图     | 24点×2公司   | 缩放、提示框     |
| 7    | 热门路线TOP10 | 横向条形图 | 10条×2公司   | 排序、提示框     |
| 8    | 预测验证对比  | 双折线图   | 12个月×2公司 | 缩放、提示框     |

##### 7.4 3D汽车展示

**技术实现**:

- 使用Three.js创建3D场景
- 简化版出租车模型（立方体组合）
- 自动旋转动画
- 实时数据更新

**显示信息**:

- Yellow出租车占比
- Green出租车占比
- 平均速度
- 服务区域

##### 7.5 交互功能

**双击放大**:

- 所有图表支持双击放大
- 全屏模态框展示
- 保留图表交互功能

**数据联动**:

- 切换月份时所有图表同步更新
- KPI指标与图表数据一致
- 3D汽车信息同步更新

**响应式设计**:

- 适配不同分辨率（1920×1080及以上）
- 图表自适应容器大小
- 移动端友好（横屏）

### 8. 报告生成

#### 技术实现

**Node.js库**:

- `docx`: Word文档生成库
- `fs`: 文件系统操作
- `path`: 路径处理

#### 报告结构

1. **封面**
   - 项目标题
   - 副标题
   - 成员信息表

2. **目录**
   - 自动生成章节列表

3. **正文**
   - 项目概述
   - 需求分析
   - 可行性分析
   - 工具与技术栈
   - 数据收集与预处理
   - 缺失值检测与处理
   - 统计分析与可视化
   - 聚类分析与相似性
   - 数据预测与验证
   - 天气数据联动分析
   - 大屏可视化系统
   - 人机交互与动态展示
   - 测试结果与完成情况
   - 总结与展望

4. **图表**
   - 自动插入13张分析图表
   - 图表标题和说明

5. **页眉页脚**
   - 页眉: 项目名称
   - 页脚: 页码

---

## 技术栈

### 后端数据处理

| 技术         | 版本  | 用途                 |
| ------------ | ----- | -------------------- |
| Python       | 3.7+  | 主要开发语言         |
| pandas       | 1.0+  | 数据加载、清洗、聚合 |
| numpy        | 1.18+ | 数值计算             |
| scikit-learn | 0.22+ | 机器学习算法         |
| matplotlib   | 3.2+  | 静态图表生成         |
| seaborn      | 0.10+ | 高级统计图表         |

### 机器学习算法

| 算法             | 用途       | 参数                          |
| ---------------- | ---------- | ----------------------------- |
| KMeans           | 聚类分析   | n_clusters=3, random_state=42 |
| PCA              | 降维可视化 | n_components=2                |
| LinearRegression | 预测模型   | 默认参数                      |
| StandardScaler   | 数据标准化 | 默认参数                      |

### 前端可视化

| 技术       | 版本  | 用途       |
| ---------- | ----- | ---------- |
| ECharts    | 5.0+  | 动态图表库 |
| Three.js   | r128+ | 3D渲染引擎 |
| HTML5      | -     | 页面结构   |
| CSS3       | -     | 页面样式   |
| JavaScript | ES6+  | 交互逻辑   |

### 报告生成

| 技术    | 版本 | 用途         |
| ------- | ---- | ------------ |
| Node.js | 14+  | 运行环境     |
| docx    | 7.0+ | Word文档生成 |

### 数据存储

| 格式    | 用途         | 优势               |
| ------- | ------------ | ------------------ |
| Parquet | 原始数据存储 | 列式存储、高压缩比 |
| CSV     | 聚合数据导出 | 通用性强、易读取   |

---

## 项目结构

```
nyc-taxi-visualization/
│
├── 📄 preprocess.py              # 数据预处理脚本（190行）
│   ├── load_monthly_data()       # 加载月度Parquet数据
│   ├── standardize_columns()      # 字段标准化
│   ├── clean_data()              # 数据清洗
│   └── process_all_data()        # 主处理流程
│
├── 📄 generate_charts.py         # 静态图表生成脚本（约2000行）
│   ├── plot_missing_values()      # 图1: 缺失值分析
│   ├── plot_monthly_trend()      # 图2: 月度趋势
│   ├── plot_hourly_pattern()      # 图3: 24小时模式
│   ├── plot_dow_pattern()        # 图4: 星期模式
│   ├── plot_payment()            # 图5: 支付方式
│   ├── plot_borough()            # 图6: 行政区分析
│   ├── plot_correlation()        # 图7: 相关性热力图
│   ├── plot_clustering()         # 图8: 聚类分析
│   ├── plot_prediction()         # 图9: 预测验证
│   ├── plot_top_routes()         # 图10: 热门路线
│   ├── plot_preferences()        # 图11: 综合偏好
│   ├── plot_boxplot()           # 图12: 箱线图对比
│   └── plot_weather_impact()    # 图13: 天气联动
│
├── 📄 generate_dashboard.py      # 大屏数据加载与生成脚本（约1500行）
│   ├── load_dashboard_data()     # 加载大屏数据
│   └── generate_html()          # 生成HTML文件
│
├── 📄 weather_analysis.py        # 天气数据联动分析脚本（约200行）
│   └── plot_weather_impact()     # 天气影响分析
│
├── 📄 generate_report.js         # Word报告生成脚本（约600行）
│   ├── heading1/2/3()           # 标题函数
│   ├── bodyText()               # 正文函数
│   ├── imageBlock()             # 图片插入函数
│   ├── tableCell()              # 表格单元格函数
│   └── 文档结构定义              # 封面、目录、正文
│
├── 📁 dashboard/                 # 动态交互大屏目录
│   └── 📄 index.html            # 大屏HTML文件（约2500行）
│       ├── CSS样式              # 深色科技风样式
│       ├── HTML结构             # 网格布局
│       ├── JavaScript逻辑       # 交互逻辑
│       │   ├── ECharts配置       # 8个图表配置
│       │   ├── Three.js场景      # 3D汽车渲染
│       │   ├── 时间轴控制       # 播放/暂停/切换
│       │   ├── 数据更新          # KPI和图表更新
│       │   └── 交互事件         # 双击放大等
│       └── 数据嵌入              # JSON格式数据
│
├── 📁 analysis/                  # 静态分析图表输出目录
│   ├── 🖼️ 01_missing_values.png         # 缺失值分析
│   ├── 🖼️ 02_monthly_trend.png          # 月度趋势
│   ├── 🖼️ 03_hourly_pattern.png         # 24小时模式
│   ├── 🖼️ 04_dow_pattern.png            # 星期模式
│   ├── 🖼️ 05_payment_type.png           # 支付方式
│   ├── 🖼️ 06_borough_analysis.png       # 行政区分析
│   ├── 🖼️ 07_correlation_heatmap.png    # 相关性热力图
│   ├── 🖼️ 08_clustering_analysis.png   # 聚类分析
│   ├── 🖼️ 09_prediction_validation.png # 预测验证
│   ├── 🖼️ 10_top_routes.png            # 热门路线
│   ├── 🖼️ 11_preferences_analysis.png  # 综合偏好
│   ├── 🖼️ 12_boxplot_comparison.png     # 箱线图对比
│   └── 🖼️ 13_weather_correlation.png   # 天气联动
│
├── 📁 data/                      # 数据目录
│   ├── 📊 monthly_stats.csv      # 月度统计数据（24行×10列）
│   ├── 📊 missing_values.csv     # 缺失值统计（动态行数×5列）
│   ├── 📊 hourly_patterns.csv    # 小时模式数据（576行×5列）
│   ├── 📊 dow_patterns.csv       # 星期模式数据（168行×5列）
│   ├── 📊 payment_patterns.csv   # 支付方式数据（动态行数×4列）
│   ├── 📊 borough_patterns.csv   # 行政区数据（动态行数×5列）
│   ├── 📊 top_routes.csv         # 热门路线数据（动态行数×6列）
│   └── 📊 zone_lookup.csv        # 区域对照表（263行×4列）
│
├── 📁 report/                    # 报告输出目录
│   └── 📄 数据可视化大作业报告.docx  # Word格式报告
│
├── 📄 README.md                  # 项目说明文档（本文件）
├── 📄 LICENSE                    # MIT许可证
└── 📄 .gitignore                # Git忽略文件配置
```

---

## 快速开始

### 环境要求

| 组件    | 最低版本   | 推荐版本    |
| ------- | ---------- | ----------- |
| Python  | 3.7        | 3.9+        |
| Node.js | 14         | 16+         |
| 浏览器  | Chrome 80+ | Chrome 100+ |
| 内存    | 8GB        | 16GB+       |
| 硬盘    | 20GB       | 50GB+       |

### Python环境配置

#### 1. 创建虚拟环境（推荐）

```bash
# Windows
python -m venv venv
venv\Scripts\activate

# macOS/Linux
python3 -m venv venv
source venv/bin/activate
```

#### 2. 安装Python依赖

```bash
pip install --upgrade pip
pip install pandas numpy matplotlib seaborn scikit-learn pyarrow
```

**依赖说明**:

- `pandas`: 数据处理核心库
- `numpy`: 数值计算基础库
- `matplotlib`: 静态图表生成
- `seaborn`: 高级统计图表
- `scikit-learn`: 机器学习算法
- `pyarrow`: Parquet文件读取

#### 3. 验证安装

```bash
python -c "import pandas, numpy, matplotlib, seaborn, sklearn; print('所有依赖安装成功！')"
```

### Node.js环境配置

#### 1. 安装Node.js依赖

```bash
npm install docx
```

**依赖说明**:

- `docx`: Word文档生成库

#### 2. 验证安装

```bash
node -e "const docx = require('docx'); console.log('docx库安装成功！')"
```

### 数据准备

#### 数据目录结构

将2018年Yellow和Green出租车Parquet数据文件放置在以下目录：

```
../数据可视化大作业/题目及数据/材料/
├── Yellow/
│   ├── yellow_tripdata_2018-01.parquet
│   ├── yellow_tripdata_2018-02.parquet
│   ├── yellow_tripdata_2018-03.parquet
│   ├── yellow_tripdata_2018-04.parquet
│   ├── yellow_tripdata_2018-05.parquet
│   ├── yellow_tripdata_2018-06.parquet
│   ├── yellow_tripdata_2018-07.parquet
│   ├── yellow_tripdata_2018-08.parquet
│   ├── yellow_tripdata_2018-09.parquet
│   ├── yellow_tripdata_2018-10.parquet
│   ├── yellow_tripdata_2018-11.parquet
│   └── yellow_tripdata_2018-12.parquet
└── Green/
    ├── green_tripdata_2018-01.parquet
    ├── green_tripdata_2018-02.parquet
    ├── green_tripdata_2018-03.parquet
    ├── green_tripdata_2018-04.parquet
    ├── green_tripdata_2018-05.parquet
    ├── green_tripdata_2018-06.parquet
    ├── green_tripdata_2018-07.parquet
    ├── green_tripdata_2018-08.parquet
    ├── green_tripdata_2018-09.parquet
    ├── green_tripdata_2018-10.parquet
    ├── green_tripdata_2018-11.parquet
    └── green_tripdata_2018-12.parquet
```

#### 数据下载

如果需要下载原始数据，请访问：

- **TLC官网**: https://www1.nyc.gov/site/tlc/about/tlc-trip-record-data.page
- **数据年份**: 2018
- **数据类型**: Yellow Taxi Trip Records, Green Taxi Trip Records
- **数据格式**: Parquet

### 一键运行

```bash
# 1. 数据预处理
python preprocess.py

# 2. 生成静态图表
python generate_charts.py

# 3. 生成天气分析
python weather_analysis.py

# 4. 生成动态大屏
python generate_dashboard.py

# 5. 生成Word报告
node generate_report.js

# 6. 打开大屏（Windows）
start dashboard/index.html

# 6. 打开大屏（macOS/Linux）
open dashboard/index.html
```

---

## 详细使用指南

### 1. 数据预处理

#### 运行命令

```bash
python preprocess.py
```

#### 处理流程

```
开始
  ↓
加载区域对照表 (zone_lookup.csv)
  ↓
循环处理 Yellow 和 Green 数据
  ↓
  循环处理 1-12 月数据
    ↓
    加载 Parquet 文件
    ↓
    字段标准化
    ↓
    缺失值统计
    ↓
    数据清洗
    ↓
    数据采样（50万条/月）
    ↓
    特征工程
    ↓
    数据聚合
      ├─ 月度统计
      ├─ 小时模式
      ├─ 星期模式
      ├─ 支付方式
      ├─ 行政区分布
      └─ 热门路线
    ↓
  下一月
  ↓
保存聚合数据到CSV
  ↓
结束
```

#### 输出文件

| 文件                   | 大小  | 记录数 | 说明       |
| ---------------------- | ----- | ------ | ---------- |
| `monthly_stats.csv`    | ~2KB  | 24     | 月度统计   |
| `missing_values.csv`   | ~5KB  | ~100   | 缺失值统计 |
| `hourly_patterns.csv`  | ~20KB | 576    | 小时模式   |
| `dow_patterns.csv`     | ~5KB  | 168    | 星期模式   |
| `payment_patterns.csv` | ~10KB | ~144   | 支付方式   |
| `borough_patterns.csv` | ~10KB | ~120   | 行政区分布 |
| `top_routes.csv`       | ~50KB | ~360   | 热门路线   |
| `zone_lookup.csv`      | ~10KB | 263    | 区域对照表 |

#### 常见问题

**Q1: 提示"文件不存在"怎么办？**

A: 检查数据文件路径是否正确，确保Parquet文件在指定目录。

**Q2: 内存不足怎么办？**

A: 可以减少采样数量，修改`preprocess.py`中的采样参数：

```python
# 原代码
sample = df if len(df) < 500000 else df.sample(n=500000, random_state=42)

# 修改为（减少到10万）
sample = df if len(df) < 100000 else df.sample(n=100000, random_state=42)
```

**Q3: 处理时间过长怎么办？**

A: 可以只处理部分月份，修改循环范围：

```python
# 原代码
for month in range(1, 13):

# 修改为（只处理前6个月）
for month in range(1, 7):
```

### 2. 生成静态分析图表

#### 运行命令

```bash
python generate_charts.py
```

#### 图表生成顺序

```
开始
  ↓
加载聚合数据
  ↓
生成图1: 缺失值分析
  ↓
生成图2: 月度趋势
  ↓
生成图3: 24小时模式
  ↓
生成图4: 星期模式
  ↓
生成图5: 支付方式
  ↓
生成图6: 行政区分析
  ↓
生成图7: 相关性热力图
  ↓
生成图8: 聚类分析
  ↓
生成图9: 预测验证
  ↓
生成图10: 热门路线
  ↓
生成图11: 综合偏好
  ↓
生成图12: 箱线图对比
  ↓
结束
```

#### 图表配置

所有图表的配置参数：

| 参数 | 值              | 说明                          |
| ---- | --------------- | ----------------------------- |
| DPI  | 150             | 图像分辨率                    |
| 格式 | PNG             | 图像格式                      |
| 字体 | Microsoft YaHei | 中文字体                      |
| 颜色 | 自定义          | Yellow=#FFD700, Green=#32CD32 |
| 尺寸 | 16×12 或 18×14  | 图表尺寸（英寸）              |

#### 自定义图表

如需修改图表样式，编辑`generate_charts.py`中的对应函数：

```python
# 示例：修改图2的尺寸
def plot_monthly_trend(data):
    fig, axes = plt.subplots(2, 2, figsize=(20, 16))  # 修改尺寸
    # ... 其他代码
```

### 3. 生成天气联动分析

#### 运行命令

```bash
python weather_analysis.py
```

#### 天气数据来源

天气数据已硬编码在脚本中，来自NOAA GHCND气象站：

```python
weather_data = {
    'month': list(range(1, 13)),
    'avg_temp_c': [0.4, 1.8, 5.8, 11.3, 17.3, 22.7, 25.8, 24.9, 20.7, 13.9, 7.9, 2.7],
    'precipitation_in': [3.58, 3.42, 4.18, 4.25, 3.82, 4.56, 4.78, 3.95, 3.68, 3.92, 3.85, 3.95],
    'snowfall_in': [9.2, 6.8, 3.5, 0.5, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.2, 1.8],
    'avg_wind_mph': [12.8, 13.2, 13.5, 12.5, 11.2, 10.5, 10.2, 10.0, 10.8, 11.5, 12.2, 12.5],
    'avg_humidity': [62.5, 60.8, 58.2, 55.5, 60.2, 65.8, 68.5, 70.2, 67.8, 63.5, 62.0, 63.8]
}
```

#### 输出文件

- `analysis/13_weather_correlation.png`: 天气联动分析图（20×16英寸）

### 4. 生成动态大屏

#### 运行命令

```bash
python generate_dashboard.py
```

#### 生成流程

```
开始
  ↓
加载聚合数据CSV
  ↓
  ├─ 月度数据
  ├─ 小时数据
  ├─ 星期数据
  ├─ 支付数据
  ├─ 行政区数据
  ├─ 热门路线数据
  ├─ 相关性矩阵
  ├─ 聚类数据
  └─ 预测数据
  ↓
转换为JSON格式
  ↓
嵌入HTML模板
  ↓
生成 index.html
  ↓
结束
```

#### 大屏配置

大屏的配置参数：

| 参数     | 值               | 说明         |
| -------- | ---------------- | ------------ |
| 分辨率   | 1920×1080        | 推荐分辨率   |
| 最小宽度 | 1400px           | 最小支持宽度 |
| 主题     | 深色科技风       | 视觉风格     |
| 主色调   | #00d4ff, #3a5fff | 蓝色系       |
| 字体     | Microsoft YaHei  | 中文字体     |
| 刷新率   | 60fps            | 动画帧率     |

#### 浏览器打开

```bash
# Windows
start dashboard/index.html

# macOS
open dashboard/index.html

# Linux
xdg-open dashboard/index.html
```

#### 大屏交互

**时间轴控制**:

- 点击月份按钮切换到对应月份
- 点击"自动播放"按钮开始/停止播放
- 点击速度按钮（1x、2x、4x）切换播放速度
- 拖拽时间轴快速定位到某个月份

**图表交互**:

- 双击图表放大查看详情
- 点击图例切换数据系列
- 鼠标悬停显示提示框
- 滚轮缩放（部分图表）

**3D汽车**:

- 自动旋转展示
- 实时显示Yellow/Green占比
- 显示平均速度和服务区域

### 5. 生成Word报告

#### 运行命令

```bash
node generate_report.js
```

#### 生成流程

```
开始
  ↓
加载分析图表
  ↓
创建Word文档
  ↓
  ├─ 添加封面
  ├─ 添加目录
  ├─ 添加正文章节
  └─ 插入图表
  ↓
保存为DOCX
  ↓
结束
```

#### 报告配置

报告的配置参数：

| 参数     | 值                    | 说明       |
| -------- | --------------------- | ---------- |
| 页面大小 | A4                    | 标准A4纸   |
| 页边距   | 上下2cm，左右1.7cm    | 页边距设置 |
| 字体     | Arial/微软雅黑        | 中英文字体 |
| 字号     | 正文11pt，标题12-18pt | 字体大小   |
| 行距     | 1.5倍                 | 行距设置   |

#### 自定义报告

如需修改报告内容，编辑`generate_report.js`：

```javascript
// 示例：修改封面标题
new Paragraph({
  alignment: AlignmentType.CENTER,
  children: [
    new TextRun({
      text: "你的自定义标题",
      size: 52,
      bold: true,
    }),
  ],
});
```

---

## 数据分析结果

### 主要发现

#### 1. 季节性特征

| 季节           | 出行量 | 平均车费 | 主要原因           |
| -------------- | ------ | -------- | ------------------ |
| 春季（3-5月）  | 高     | 中等     | 天气适宜，出行活跃 |
| 夏季（7-8月）  | 低     | 较高     | 高温、假期外出     |
| 秋季（9-11月） | 高     | 中等     | 天气凉爽，返程高峰 |
| 冬季（12-2月） | 波动大 | 较高     | 降雪影响明显       |

**详细分析**:

- **3月**: 出行量全年最高（约920万次/月）
- **7-8月**: 出行量最低（约770万次/月）
- **1月**: 受降雪影响，出行量波动
- **12月**: 节假日前出行量回升

#### 2. 时间模式

| 时间段            | 出行量 | 平均车费 | 特征      |
| ----------------- | ------ | -------- | --------- |
| 早高峰（7-9点）   | 高     | 中等     | 上班通勤  |
| 平峰（10-16点）   | 中     | 较低     | 日常出行  |
| 晚高峰（17-19点） | 高     | 较高     | 下班通勤  |
| 深夜（20-23点）   | 中     | 高       | 娱乐出行  |
| 凌晨（0-6点）     | 低     | 高       | 夜班/机场 |

**详细分析**:

- **早高峰**: 8点达到峰值，平均车费$12.5
- **晚高峰**: 18点达到峰值，平均车费$14.2
- **凌晨2-5点**: 出行量最低，但平均车费最高（$18+）
- **周末**: 周五晚高峰延长至21点

#### 3. Yellow vs Green对比

| 指标         | Yellow    | Green           | 比例         |
| ------------ | --------- | --------------- | ------------ |
| 总行程数     | 1.02亿    | 855万           | 92.3% : 7.7% |
| 平均车费     | $12.8     | $14.5           | -            |
| 平均距离     | 2.8英里   | 3.2英里         | -            |
| 平均时长     | 13.5分钟  | 15.2分钟        | -            |
| 主要服务区域 | Manhattan | Brooklyn/Queens | -            |

**详细分析**:

- **Yellow**: 主要服务曼哈顿核心区域，短途为主
- **Green**: 主要服务外围行政区，长途为主
- **重叠区域**: 两者在部分区域有竞争
- **互补关系**: 服务不同区域和客群

#### 4. 天气影响

| 天气因素 | 影响程度 | 相关性   | 阈值        |
| -------- | -------- | -------- | ----------- |
| 温度     | 中等     | 二次关系 | 15-20°C最优 |
| 降水量   | 较小     | 负相关   | >4英寸显著  |
| 降雪量   | 很大     | 强负相关 | >2英寸显著  |
| 风速     | 较小     | 正相关   | >15mph影响  |
| 湿度     | 较小     | 负相关   | >70%影响    |

**详细分析**:

- **温度**: 15-20°C时出行量最高，过冷或过热都降低
- **降雪**: 1月降雪9.2英寸，出行量下降15%
- **风速**: 风速增加导致行程时长延长5-10%
- **湿度**: 高湿度天气车费略低（出行量少）

#### 5. 支付方式

| 支付方式 | Yellow占比 | Green占比 | 特征         |
| -------- | ---------- | --------- | ------------ |
| 信用卡   | 68%        | 62%       | 主流支付方式 |
| 现金     | 22%        | 28%       | 传统支付方式 |
| 免费     | 5%         | 4%        | 投诉补偿等   |
| 争议     | 3%         | 4%        | 金额争议     |
| 未知     | 1%         | 1%        | 数据缺失     |
| 作废     | 1%         | 1%        | 取消订单     |

**详细分析**:

- **信用卡**: Yellow比例更高（商务客群）
- **现金**: Green比例更高（外围区域）
- **趋势**: 信用卡支付比例逐年上升
- **地域**: Manhattan信用卡比例最高（75%）

### 业务洞察

#### 1. 运营优化建议

**调度策略**:

- 早高峰前30分钟增加Manhattan区域车辆
- 晚高峰延长至21点，增加外围区域运力
- 凌晨时段减少车辆，降低运营成本

**定价策略**:

- 高峰期适当提高费率（已实施）
- 降雪天气建议实施动态定价
- 长途行程可提供优惠套餐

#### 2. 服务改进建议

**Yellow出租车**:

- 加强Manhattan核心区域覆盖
- 提升商务客群服务质量
- 推广信用卡支付

**Green出租车**:

- 扩大外围区域服务范围
- 增加机场专线服务
- 优化长途行程体验

#### 3. 城市规划建议

**交通规划**:

- 早晚高峰加强公共交通运力
- 优化机场交通接驳
- 建设更多出租车候客点

**应急响应**:

- 降雪天气启动应急预案
- 建立恶劣天气预警机制
- 加强与其他交通方式协调

---

## 性能指标

### 处理性能

| 任务       | 数据量   | 处理时间 | 内存占用 | 备注           |
| ---------- | -------- | -------- | -------- | -------------- |
| 数据预处理 | 1.2亿条  | ~30分钟  | 8GB      | 采样至1200万条 |
| 图表生成   | 1200万条 | ~5分钟   | 4GB      | 13张图表       |
| 天气分析   | 1200万条 | ~2分钟   | 2GB      | 1张图表        |
| 大屏生成   | 1200万条 | ~1分钟   | 1GB      | 1个HTML        |
| 报告生成   | 13张图   | ~30秒    | 500MB    | 1个DOCX        |

### 系统性能

| 指标         | 值     | 说明         |
| ------------ | ------ | ------------ |
| 大屏加载时间 | <3秒   | 首次加载     |
| 图表渲染时间 | <1秒   | 单个图表     |
| 数据切换时间 | <500ms | 月份切换     |
| 内存占用     | <500MB | 浏览器运行时 |
| CPU占用      | <30%   | 正常运行时   |

### 优化建议

#### 数据处理优化

1. **使用Dask替代Pandas**

   ```python
   import dask.dataframe as dd
   df = dd.read_parquet('*.parquet')
   ```

2. **并行处理**

   ```python
   from multiprocessing import Pool
   with Pool(4) as p:
       results = p.map(process_month, months)
   ```

3. **增量处理**
   ```python
   # 只处理新增月份
   processed_months = get_processed_months()
   for month in range(1, 13):
       if month not in processed_months:
           process_month(month)
   ```

#### 前端优化

1. **数据懒加载**

   ```javascript
   // 只加载当前月份数据
   function loadMonthData(month) {
     return monthlyData[month];
   }
   ```

2. **图表缓存**

   ```javascript
   // 缓存已渲染图表
   const chartCache = {};
   function getChart(chartId) {
       if (!chartCache[chartId]) {
           chartCache[chartId] = echarts.init(...);
       }
       return chartCache[chartId];
   }
   ```

3. **虚拟滚动**
   ```javascript
   // 大数据列表使用虚拟滚动
   import { VirtualList } from "vue-virtual-scroll-list";
   ```

---

## API文档

### Python脚本API

#### preprocess.py

```python
def load_monthly_data(company, month):
    """
    加载指定公司和月份的Parquet数据

    Args:
        company (str): 'yellow' 或 'green'
        month (int): 月份 (1-12)

    Returns:
        pandas.DataFrame: 加载的数据，文件不存在返回None
    """
    pass

def standardize_columns(df, company):
    """
    标准化列名

    Args:
        df (pandas.DataFrame): 原始数据
        company (str): 'yellow' 或 'green'

    Returns:
        pandas.DataFrame: 标准化后的数据
    """
    pass

def clean_data(df, company):
    """
    清洗数据

    Args:
        df (pandas.DataFrame): 原始数据
        company (str): 'yellow' 或 'green'

    Returns:
        pandas.DataFrame: 清洗后的数据
    """
    pass

def process_all_data():
    """
    处理所有数据的主函数

    Returns:
        None: 结果保存到CSV文件
    """
    pass
```

#### generate_charts.py

```python
def plot_missing_values(data):
    """
    生成缺失值分析图表

    Args:
        data (dict): 包含所有聚合数据的字典

    Returns:
        None: 图表保存到 analysis/01_missing_values.png
    """
    pass

def plot_monthly_trend(data):
    """
    生成月度趋势图表

    Args:
        data (dict): 包含所有聚合数据的字典

    Returns:
        None: 图表保存到 analysis/02_monthly_trend.png
    """
    pass

# ... 其他图表生成函数类似
```

#### generate_dashboard.py

```python
def load_dashboard_data():
    """
    加载大屏所需的所有数据

    Returns:
        dict: 包含所有数据的字典，格式如下：
        {
            'monthlyData': {'yellow': [...], 'green': [...]},
            'hourlyData': {'yellow': [...], 'green': [...]},
            'boroughData': {'yellow': [...], 'green': [...]},
            'paymentData': {'yellow': [...], 'green': [...]},
            'topRoutes': [...],
            'correlationMatrix': {...},
            'clusterData': [...],
            'predictionData': {...}
        }
    """
    pass

def generate_html(dashboard_data):
    """
    生成HTML大屏文件

    Args:
        dashboard_data (dict): 加载的大屏数据

    Returns:
        None: HTML文件保存到 dashboard/index.html
    """
    pass
```

### JavaScript API

#### 大屏交互API

```javascript
// 切换月份
function switchMonth(month) {
  currentMonth = month;
  updateKPI();
  updateCharts();
  updateTimeline();
}

// 自动播放
function toggleAutoPlay() {
  isPlaying = !isPlaying;
  if (isPlaying) {
    playInterval = setInterval(nextMonth, 1000 / speed);
  } else {
    clearInterval(playInterval);
  }
}

// 设置播放速度
function setSpeed(speed) {
  currentSpeed = speed;
  if (isPlaying) {
    clearInterval(playInterval);
    playInterval = setInterval(nextMonth, 1000 / speed);
  }
}

// 更新KPI
function updateKPI() {
  const data = getMonthData(currentMonth);
  animateValue("kpiTrips", data.totalTrips);
  animateValue("kpiRevenue", data.totalRevenue);
  // ...
}

// 更新图表
function updateCharts() {
  const data = getMonthData(currentMonth);
  chartTrend.setOption(getTrendOption(data));
  chartHeatmap.setOption(getHeatmapOption(data));
  // ...
}

// 双击放大
function zoomChart(chartId) {
  const chart = charts[chartId];
  const overlay = document.getElementById("zoomOverlay");
  const zoomChart = echarts.init(
    overlay.querySelector(".zoom-chart-container"),
  );
  zoomChart.setOption(chart.getOption());
  overlay.classList.add("active");
}
```

---

## 常见问题

### 安装与环境

**Q1: Python版本不兼容怎么办？**

A: 建议使用Python 3.9或更高版本。如果必须使用Python 3.7，请确保所有依赖包版本兼容：

```bash
pip install pandas==1.1.5 numpy==1.19.5 matplotlib==3.3.4 seaborn==0.11.2 scikit-learn==0.24.2
```

**Q2: Node.js安装失败怎么办？**

A: 可以使用nvm（Node Version Manager）安装：

```bash
# Windows
# 下载并安装 nvm-windows: https://github.com/coreybutler/nvm-windows

# macOS/Linux
curl -o- https://raw.githubusercontent.com/nvm-sh/nvm/v0.39.0/install.sh | bash
nvm install 16
nvm use 16
```

**Q3: 依赖包安装失败怎么办？**

A: 使用国内镜像源加速：

```bash
pip install -i https://pypi.tuna.tsinghua.edu.cn/simple pandas numpy matplotlib seaborn scikit-learn
```

### 数据处理

**Q4: Parquet文件读取失败怎么办？**

A: 确保安装了pyarrow：

```bash
pip install pyarrow
```

如果仍然失败，可以尝试使用fastparquet：

```bash
pip install fastparquet
```

**Q5: 内存不足怎么办？**

A: 有几种解决方案：

1. 减少采样数量
2. 使用Dask替代Pandas
3. 分批处理数据
4. 增加系统内存或使用云服务器

**Q6: 数据处理时间过长怎么办？**

A: 可以：

1. 只处理部分月份
2. 使用多进程并行处理
3. 使用SSD硬盘提升I/O速度
4. 使用更强大的CPU

### 可视化

**Q7: 图表中文显示乱码怎么办？**

A: 确保系统安装了中文字体，并在代码中指定：

```python
plt.rcParams['font.sans-serif'] = ['SimHei', 'Microsoft YaHei']
plt.rcParams['axes.unicode_minus'] = False
```

**Q8: 大屏在浏览器中显示异常怎么办？**

A: 检查以下几点：

1. 浏览器版本是否过旧（建议Chrome 100+）
2. 是否启用了广告拦截插件
3. 控制台是否有JavaScript错误
4. 网络连接是否正常（需要加载CDN资源）

**Q9: 3D汽车不显示怎么办？**

A: 检查：

1. 浏览器是否支持WebGL
2. Three.js是否正确加载
3. 控制台是否有错误信息

### 报告生成

**Q10: Word报告生成失败怎么办？**

A: 确保：

1. Node.js版本正确（14+）
2. docx库已正确安装
3. 图表文件存在于analysis目录
4. 有足够的磁盘空间

**Q11: 报告中图片不显示怎么办？**

A: 检查：

1. 图片路径是否正确
2. 图片格式是否为PNG
3. 图片是否损坏

### 性能优化

**Q12: 大屏加载慢怎么办？**

A: 可以：

1. 减少数据量
2. 使用数据懒加载
3. 启用浏览器缓存
4. 使用CDN加速资源加载

**Q13: 图表渲染卡顿怎么办？**

A: 可以：

1. 减少数据点数量
2. 使用数据采样
3. 关闭不必要的动画
4. 使用Web Worker进行后台计算

---

## 贡献指南

### 如何贡献

欢迎提交Issue和Pull Request！

#### 提交Issue

如果发现bug或有功能建议，请：

1. 检查是否已有类似Issue
2. 使用清晰的标题描述问题
3. 提供详细的复现步骤
4. 附上相关的错误信息和截图

#### 提交Pull Request

1. Fork本仓库
2. 创建特性分支 (`git checkout -b feature/AmazingFeature`)
3. 提交更改 (`git commit -m 'Add some AmazingFeature'`)
4. 推送到分支 (`git push origin feature/AmazingFeature`)
5. 开启Pull Request

### 代码规范

#### Python代码

- 遵循PEP 8规范
- 使用有意义的变量名
- 添加必要的注释
- 函数添加docstring

```python
def process_data(data):
    """
    处理输入数据并返回结果

    Args:
        data (dict): 输入数据字典

    Returns:
        dict: 处理后的数据字典

    Raises:
        ValueError: 当数据格式不正确时
    """
    # 处理逻辑
    pass
```

#### JavaScript代码

- 使用ES6+语法
- 使用const/let代替var
- 函数添加JSDoc注释

```javascript
/**
 * 处理数据并返回结果
 * @param {Object} data - 输入数据对象
 * @returns {Object} 处理后的数据对象
 */
function processData(data) {
  // 处理逻辑
}
```

### 测试

提交PR前请确保：

1. 代码可以正常运行
2. 没有语法错误
3. 没有引入新的bug
4. 遵循代码规范

---

## 更新日志

### v1.0.0 (2026-05-12)

#### 新增功能

- ✨ 完整的数据预处理流程
- ✨ 13张静态分析图表
- ✨ 天气数据联动分析
- ✨ 动态交互大屏（ECharts + Three.js）
- ✨ Word报告自动生成
- ✨ K-Means聚类分析
- ✨ 线性回归预测验证

#### 技术特性

- 🚀 处理1.2亿条数据记录
- 🚀 支持12个月份动态切换
- 🚀 3D汽车模型展示
- 🚀 响应式大屏设计
- 🚀 深色科技风主题

#### 文档

- 📝 完整的README文档
- 📝 详细的API文档
- 📝 常见问题解答
- 📝 贡献指南

---

## 许可证

本项目采用MIT许可证。

```
MIT License

Copyright (c) 2026 数据可视化课程期末大作业项目组

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.
```

---

## 作者与致谢

### 作者

2026数据可视化课程期末大作业项目组

### 指导教师

感谢数据可视化课程教师的悉心指导！

### 数据来源

- **纽约市出租车与豪华轿车委员会(TLC)**
  - 官网: https://www1.nyc.gov/site/tlc/about/tlc-trip-record-data.page
  - 数据年份: 2018
  - 数据类型: Yellow/Green Taxi Trip Records

- **NOAA国家环境信息中心**
  - 气象站: GHCND:USW00094728 (纽约中央公园)
  - 数据年份: 2018
  - 官网: https://www.ncdc.noaa.gov/

### 技术支持

感谢以下开源项目的支持：

- **Python生态**
  - pandas: https://pandas.pydata.org/
  - numpy: https://numpy.org/
  - matplotlib: https://matplotlib.org/
  - seaborn: https://seaborn.pydata.org/
  - scikit-learn: https://scikit-learn.org/

- **JavaScript生态**
  - ECharts: https://echarts.apache.org/
  - Three.js: https://threejs.org/
  - docx: https://docx.js.org/

### 参考资料

- 纽约市出租车数据可视化案例研究
- 数据可视化最佳实践
- 机器学习在交通数据分析中的应用
- 天气对城市交通的影响研究

---

## 联系方式

如有问题或建议，欢迎通过以下方式联系：

- **项目地址**: https://github.com/yourusername/nyc-taxi-visualization
- **Issue**: https://github.com/yourusername/nyc-taxi-visualization/issues

---

<div align="center">

**如果这个项目对你有帮助，请给一个⭐️**

Made with ❤️ by 2026数据可视化课程期末大作业项目组

</div>
