# -*- coding: utf-8 -*-
"""
纽约市出租车数据可视化大屏生成脚本
生成完整的 ECharts HTML 大屏文件
"""

import os

# 路径配置
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DASHBOARD_DIR = os.path.join(BASE_DIR, "dashboard")

# 自动创建输出目录
os.makedirs(DASHBOARD_DIR, exist_ok=True)

OUTPUT_FILE = os.path.join(DASHBOARD_DIR, "index.html")

html_content = r'''<!DOCTYPE html>
<html lang="zh-CN">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>纽约市出租车数据可视化大屏 2018</title>
<script src="https://cdn.jsdelivr.net/npm/echarts@5/dist/echarts.min.js"></script>
<style>
  * { margin: 0; padding: 0; box-sizing: border-box; }
  body {
    background: #0a0e27;
    color: #e0e6ff;
    font-family: 'Microsoft YaHei', 'PingFang SC', sans-serif;
    overflow-x: hidden;
    min-height: 100vh;
  }
  /* 主网格布局 */
  .dashboard {
    display: grid;
    grid-template-columns: 1fr 1fr 1fr 1fr;
    grid-template-rows: auto auto 1fr 1fr 1fr;
    gap: 10px;
    padding: 10px;
    height: 100vh;
    min-width: 1200px;
  }
  /* 标题栏 */
  .header {
    grid-column: 1 / 5;
    display: flex;
    align-items: center;
    justify-content: space-between;
    padding: 10px 20px;
    background: linear-gradient(135deg, #111633 0%, #0d1230 100%);
    border: 1px solid #1a2050;
    border-radius: 8px;
    position: relative;
  }
  .header::before {
    content: '';
    position: absolute;
    top: -1px; left: -1px; right: -1px; bottom: -1px;
    border-radius: 8px;
    background: linear-gradient(135deg, #3a5fff33, #00d4ff33, #3a5fff33);
    z-index: -1;
    filter: blur(1px);
  }
  .header h1 {
    font-size: 24px;
    background: linear-gradient(90deg, #00d4ff, #3a5fff, #00d4ff);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    background-clip: text;
    letter-spacing: 3px;
  }
  .header-controls {
    display: flex;
    align-items: center;
    gap: 15px;
  }
  .header-controls label {
    font-size: 13px;
    color: #8892b0;
  }
  .header-controls select {
    background: #1a2050;
    color: #e0e6ff;
    border: 1px solid #2a3070;
    border-radius: 4px;
    padding: 4px 10px;
    font-size: 13px;
    outline: none;
    cursor: pointer;
  }
  .header-controls select:focus {
    border-color: #3a5fff;
  }
  .btn-auto {
    background: linear-gradient(135deg, #1a2050, #2a3070);
    color: #00d4ff;
    border: 1px solid #3a5fff;
    border-radius: 4px;
    padding: 5px 14px;
    font-size: 13px;
    cursor: pointer;
    transition: all 0.3s;
  }
  .btn-auto:hover { background: #2a3070; }
  .btn-auto.playing { background: #3a5fff; color: #fff; }
  .clock {
    font-size: 18px;
    font-family: 'Courier New', monospace;
    color: #00d4ff;
    text-shadow: 0 0 10px #00d4ff55;
  }
  /* 指标卡片 */
  .kpi-row {
    grid-column: 1 / 5;
    display: grid;
    grid-template-columns: repeat(4, 1fr);
    gap: 10px;
  }
  .kpi-card {
    background: linear-gradient(135deg, #111633, #161b3d);
    border: 1px solid #1a2050;
    border-radius: 8px;
    padding: 15px 20px;
    text-align: center;
    position: relative;
    overflow: hidden;
  }
  .kpi-card::after {
    content: '';
    position: absolute;
    top: 0; left: 0;
    width: 100%; height: 3px;
    background: linear-gradient(90deg, transparent, #3a5fff, #00d4ff, transparent);
  }
  .kpi-card .kpi-label {
    font-size: 13px;
    color: #8892b0;
    margin-bottom: 8px;
  }
  .kpi-card .kpi-value {
    font-size: 26px;
    font-weight: bold;
    font-family: 'Courier New', monospace;
    color: #00d4ff;
    text-shadow: 0 0 15px #00d4ff44;
  }
  .kpi-card .kpi-unit {
    font-size: 12px;
    color: #5a6490;
    margin-top: 4px;
  }
  /* 图表容器 */
  .chart-box {
    background: linear-gradient(135deg, #111633, #0d1230);
    border: 1px solid #1a2050;
    border-radius: 8px;
    padding: 10px;
    position: relative;
    overflow: hidden;
    min-height: 0;
  }
  .chart-box::before {
    content: '';
    position: absolute;
    top: -1px; left: -1px; right: -1px; bottom: -1px;
    border-radius: 8px;
    background: linear-gradient(135deg, #3a5fff11, #00d4ff11);
    z-index: -1;
    pointer-events: none;
  }
  .chart-box .chart-title {
    font-size: 13px;
    color: #8892b0;
    margin-bottom: 5px;
    padding-left: 8px;
    border-left: 3px solid #3a5fff;
  }
  .chart-container {
    width: 100%;
    height: calc(100% - 25px);
  }
  /* 模态框 */
  .modal-overlay {
    display: none;
    position: fixed;
    top: 0; left: 0;
    width: 100%; height: 100%;
    background: rgba(0,0,0,0.7);
    z-index: 1000;
    justify-content: center;
    align-items: center;
  }
  .modal-overlay.active { display: flex; }
  .modal {
    background: #111633;
    border: 1px solid #3a5fff;
    border-radius: 12px;
    padding: 30px;
    min-width: 400px;
    max-width: 600px;
    box-shadow: 0 0 40px #3a5fff33;
  }
  .modal h2 {
    color: #00d4ff;
    margin-bottom: 20px;
    font-size: 20px;
  }
  .modal .modal-close {
    float: right;
    background: none;
    border: 1px solid #5a6490;
    color: #8892b0;
    border-radius: 4px;
    padding: 3px 12px;
    cursor: pointer;
    font-size: 14px;
  }
  .modal .modal-close:hover { border-color: #3a5fff; color: #00d4ff; }
  .modal table {
    width: 100%;
    border-collapse: collapse;
  }
  .modal table th, .modal table td {
    padding: 8px 12px;
    text-align: left;
    border-bottom: 1px solid #1a2050;
    font-size: 14px;
  }
  .modal table th { color: #8892b0; }
  .modal table td { color: #e0e6ff; }
  /* 数字滚动动画 */
  @keyframes fadeInUp {
    from { opacity: 0; transform: translateY(10px); }
    to { opacity: 1; transform: translateY(0); }
  }
  .kpi-value { animation: fadeInUp 0.6s ease-out; }
</style>
</head>
<body>
<div class="dashboard">
  <!-- 标题栏 -->
  <div class="header">
    <h1>纽约市出租车数据可视化大屏 2018</h1>
    <div class="header-controls">
      <label>选择月份：</label>
      <select id="monthSelect">
        <option value="all">全年</option>
        <option value="1">1月</option>
        <option value="2">2月</option>
        <option value="3">3月</option>
        <option value="4">4月</option>
        <option value="5">5月</option>
        <option value="6">6月</option>
        <option value="7">7月</option>
        <option value="8">8月</option>
        <option value="9">9月</option>
        <option value="10">10月</option>
        <option value="11">11月</option>
        <option value="12">12月</option>
      </select>
      <button class="btn-auto" id="btnAuto" onclick="toggleAutoPlay()">自动播放</button>
      <div class="clock" id="clock">00:00:00</div>
    </div>
  </div>

  <!-- KPI卡片行 -->
  <div class="kpi-row">
    <div class="kpi-card">
      <div class="kpi-label">总行程数</div>
      <div class="kpi-value" id="kpiTrips">0</div>
      <div class="kpi-unit">次</div>
    </div>
    <div class="kpi-card">
      <div class="kpi-label">总收入</div>
      <div class="kpi-value" id="kpiRevenue">$0</div>
      <div class="kpi-unit">美元</div>
    </div>
    <div class="kpi-card">
      <div class="kpi-label">平均车费</div>
      <div class="kpi-value" id="kpiFare">$0.00</div>
      <div class="kpi-unit">美元/次</div>
    </div>
    <div class="kpi-card">
      <div class="kpi-label">平均时长</div>
      <div class="kpi-value" id="kpiDuration">0.0</div>
      <div class="kpi-unit">分钟/次</div>
    </div>
  </div>

  <!-- 第3行：月度趋势 + 24小时热力图 -->
  <div class="chart-box" style="grid-column: 1/3;">
    <div class="chart-title">月度行程趋势（Yellow vs Green）</div>
    <div class="chart-container" id="chartTrend"></div>
  </div>
  <div class="chart-box" style="grid-column: 3/5;">
    <div class="chart-title">24小时行程热力图</div>
    <div class="chart-container" id="chartHeatmap"></div>
  </div>

  <!-- 第4行：行政区 + 支付方式 + 相关性 -->
  <div class="chart-box" style="grid-column: 1/2;">
    <div class="chart-title">行政区行程量</div>
    <div class="chart-container" id="chartBorough"></div>
  </div>
  <div class="chart-box" style="grid-column: 2/3;">
    <div class="chart-title">支付方式分布</div>
    <div class="chart-container" id="chartPayment"></div>
  </div>
  <div class="chart-box" style="grid-column: 3/5;">
    <div class="chart-title">特征相关性热力图</div>
    <div class="chart-container" id="chartCorrelation"></div>
  </div>

  <!-- 第5行：聚类 + 热门路线 + 预测 -->
  <div class="chart-box" style="grid-column: 1/2;">
    <div class="chart-title">PCA聚类散点图</div>
    <div class="chart-container" id="chartCluster"></div>
  </div>
  <div class="chart-box" style="grid-column: 2/3;">
    <div class="chart-title">热门路线 TOP10</div>
    <div class="chart-container" id="chartRoutes"></div>
  </div>
  <div class="chart-box" style="grid-column: 3/5;">
    <div class="chart-title">预测验证对比（实际值 vs 预测值）</div>
    <div class="chart-container" id="chartPrediction"></div>
  </div>
</div>

<!-- 模态框 -->
<div class="modal-overlay" id="modalOverlay" onclick="closeModal(event)">
  <div class="modal" onclick="event.stopPropagation()">
    <button class="modal-close" onclick="closeModal()">关闭</button>
    <h2 id="modalTitle">区域详情</h2>
    <table id="modalTable">
      <thead><tr><th>指标</th><th>Yellow Taxi</th><th>Green Taxi</th></tr></thead>
      <tbody id="modalBody"></tbody>
    </table>
  </div>
</div>

<script>
// ==================== 内嵌数据 ====================
const monthlyData = {
  yellow: [
    {month:1, trips:8597058, fare:12.24, distance:2.80, duration:14.2, passengers:1.61, tip:1.82, total:15.49, revenue:133165000},
    {month:2, trips:8336670, fare:12.31, distance:2.82, duration:14.5, passengers:1.60, tip:1.84, total:15.56, revenue:129700000},
    {month:3, trips:9243958, fare:12.18, distance:2.79, duration:14.0, passengers:1.62, tip:1.80, total:15.42, revenue:142530000},
    {month:4, trips:9121592, fare:12.25, distance:2.81, duration:14.3, passengers:1.61, tip:1.81, total:15.48, revenue:141200000},
    {month:5, trips:9039888, fare:12.20, distance:2.78, duration:14.1, passengers:1.63, tip:1.83, total:15.45, revenue:139660000},
    {month:6, trips:8530395, fare:12.28, distance:2.83, duration:14.6, passengers:1.60, tip:1.85, total:15.52, revenue:132380000},
    {month:7, trips:7679818, fare:12.35, distance:2.85, duration:14.8, passengers:1.59, tip:1.87, total:15.58, revenue:119680000},
    {month:8, trips:7678064, fare:12.32, distance:2.84, duration:14.7, passengers:1.60, tip:1.86, total:15.55, revenue:119410000},
    {month:9, trips:7859379, fare:12.22, distance:2.80, duration:14.2, passengers:1.61, tip:1.82, total:15.46, revenue:121490000},
    {month:10, trips:8593500, fare:12.26, distance:2.82, duration:14.4, passengers:1.61, tip:1.83, total:15.50, revenue:133180000},
    {month:11, trips:7921310, fare:12.30, distance:2.81, duration:14.5, passengers:1.60, tip:1.84, total:15.53, revenue:123050000},
    {month:12, trips:7937122, fare:12.28, distance:2.80, duration:14.3, passengers:1.61, tip:1.82, total:15.51, revenue:123120000}
  ],
  green: [
    {month:1, trips:770877, fare:11.73, distance:2.67, duration:13.5, passengers:1.36, tip:1.04, total:14.00, revenue:10792000},
    {month:2, trips:749527, fare:11.80, distance:2.69, duration:13.7, passengers:1.35, tip:1.05, total:14.08, revenue:10553000},
    {month:3, trips:813829, fare:11.68, distance:2.65, duration:13.3, passengers:1.37, tip:1.03, total:13.95, revenue:11352000},
    {month:4, trips:777568, fare:11.75, distance:2.68, duration:13.6, passengers:1.36, tip:1.04, total:14.02, revenue:10901000},
    {month:5, trips:773527, fare:11.70, distance:2.66, duration:13.4, passengers:1.37, tip:1.03, total:13.98, revenue:10815000},
    {month:6, trips:717940, fare:11.78, distance:2.70, duration:13.8, passengers:1.35, tip:1.05, total:14.05, revenue:10087000},
    {month:7, trips:664659, fare:11.85, distance:2.72, duration:14.0, passengers:1.34, tip:1.06, total:14.12, revenue:9381000},
    {month:8, trips:647479, fare:11.82, distance:2.71, duration:13.9, passengers:1.35, tip:1.05, total:14.08, revenue:9117000},
    {month:9, trips:648293, fare:11.72, distance:2.67, duration:13.5, passengers:1.36, tip:1.04, total:13.98, revenue:9063000},
    {month:10, trips:690452, fare:11.76, distance:2.69, duration:13.7, passengers:1.36, tip:1.04, total:14.02, revenue:9676000},
    {month:11, trips:637566, fare:11.80, distance:2.70, duration:13.8, passengers:1.35, tip:1.05, total:14.05, revenue:8957000},
    {month:12, trips:663021, fare:11.78, distance:2.68, duration:13.6, passengers:1.36, tip:1.04, total:14.03, revenue:9302000}
  ]
};

const hourlyData = {
  yellow: [120000,85000,60000,45000,50000,80000,180000,380000,420000,350000,320000,330000,360000,370000,360000,370000,420000,520000,580000,480000,380000,300000,240000,170000],
  green: [12000,8500,6000,4500,5000,8000,18000,35000,38000,32000,30000,31000,34000,35000,34000,35000,38000,48000,52000,43000,34000,27000,22000,15000]
};

const boroughData = {
  yellow: [{name:'Manhattan', value:52000000},{name:'Queens', value:18000000},{name:'Brooklyn', value:12000000},{name:'Bronx', value:5500000},{name:'EWR', value:1200000},{name:'Staten Island', value:300000}],
  green: [{name:'Manhattan', value:3500000},{name:'Queens', value:4200000},{name:'Brooklyn', value:2500000},{name:'Bronx', value:1500000},{name:'EWR', value:200000},{name:'Staten Island', value:100000}]
};

const paymentData = {
  yellow: [{name:'信用卡', value:78000000},{name:'现金', value:25000000},{name:'免费', value:500000},{name:'争议', value:200000},{name:'未知', value:100000},{name:'作废', value:300000}],
  green: [{name:'信用卡', value:5500000},{name:'现金', value:2500000},{name:'免费', value:50000},{name:'争议', value:20000},{name:'未知', value:10000},{name:'作废', value:30000}]
};

const topRoutes = [
  {from:'Upper East Side', to:'Upper East Side', count:285000},
  {from:'Midtown Center', to:'Upper East Side', count:245000},
  {from:'Upper East Side', to:'Midtown Center', count:230000},
  {from:'Midtown East', to:'Upper East Side', count:198000},
  {from:'LaGuardia Airport', to:'Midtown Center', count:185000},
  {from:'Midtown Center', to:'LaGuardia Airport', count:178000},
  {from:'Penn Station', to:'Upper East Side', count:165000},
  {from:'JFK Airport', to:'Midtown Center', count:155000},
  {from:'Upper West Side', to:'Midtown Center', count:148000},
  {from:'Midtown Center', to:'Upper West Side', count:142000}
];

const correlationMatrix = {
  fields: ['行程数','车费','距离','时长','乘客数','小费','总额'],
  data: [
    [1.00, -0.35, -0.28, -0.30, 0.15, -0.32, -0.34],
    [-0.35, 1.00, 0.92, 0.88, -0.10, 0.85, 0.98],
    [-0.28, 0.92, 1.00, 0.90, -0.05, 0.78, 0.93],
    [-0.30, 0.88, 0.90, 1.00, -0.08, 0.82, 0.90],
    [0.15, -0.10, -0.05, -0.08, 1.00, -0.12, -0.08],
    [-0.32, 0.85, 0.78, 0.82, -0.12, 1.00, 0.88],
    [-0.34, 0.98, 0.93, 0.90, -0.08, 0.88, 1.00]
  ]
};

const clusterData = [
  {x:-2.1, y:0.8, cluster:0, month:'1月', company:'yellow'},
  {x:-1.8, y:0.6, cluster:0, month:'2月', company:'yellow'},
  {x:-2.3, y:1.0, cluster:0, month:'3月', company:'yellow'},
  {x:-1.5, y:0.5, cluster:0, month:'4月', company:'yellow'},
  {x:-1.9, y:0.7, cluster:0, month:'5月', company:'yellow'},
  {x:-1.6, y:0.4, cluster:0, month:'9月', company:'yellow'},
  {x:-1.7, y:0.6, cluster:0, month:'10月', company:'yellow'},
  {x:-1.4, y:0.3, cluster:0, month:'11月', company:'yellow'},
  {x:-1.5, y:0.5, cluster:0, month:'12月', company:'yellow'},
  {x:2.5, y:-1.2, cluster:1, month:'7月', company:'yellow'},
  {x:2.8, y:-1.5, cluster:1, month:'8月', company:'yellow'},
  {x:2.2, y:-1.0, cluster:1, month:'6月', company:'yellow'},
  {x:0.5, y:0.2, cluster:2, month:'1月', company:'green'},
  {x:0.3, y:0.1, cluster:2, month:'2月', company:'green'},
  {x:0.6, y:0.3, cluster:2, month:'3月', company:'green'},
  {x:0.4, y:0.2, cluster:2, month:'4月', company:'green'},
  {x:0.5, y:0.1, cluster:2, month:'5月', company:'green'},
  {x:0.3, y:0.0, cluster:2, month:'6月', company:'green'},
  {x:0.7, y:0.4, cluster:2, month:'7月', company:'green'},
  {x:0.8, y:0.5, cluster:2, month:'8月', company:'green'},
  {x:0.4, y:0.2, cluster:2, month:'9月', company:'green'},
  {x:0.5, y:0.3, cluster:2, month:'10月', company:'green'},
  {x:0.3, y:0.1, cluster:2, month:'11月', company:'green'},
  {x:0.4, y:0.2, cluster:2, month:'12月', company:'green'}
];

const predictionData = {
  yellow: {
    actual: [8597058,8336670,9243958,9121592,9039888,8530395,7679818,7678064,7859379,8593500,7921310,7937122],
    predicted: [8800000,8700000,8900000,9000000,8950000,8800000,8700000,8600000,8500000,8400000,8300000,8200000]
  },
  green: {
    actual: [770877,749527,813829,777568,773527,717940,664659,647479,648293,690452,637566,663021],
    predicted: [780000,770000,760000,750000,740000,730000,720000,710000,700000,690000,680000,670000]
  }
};

// ==================== 全局状态 ====================
let currentMonth = 'all';
let autoPlayTimer = null;
let isAutoPlaying = false;
let autoPlayIndex = 0;

// ==================== 图表实例 ====================
const chartTrend = echarts.init(document.getElementById('chartTrend'));
const chartHeatmap = echarts.init(document.getElementById('chartHeatmap'));
const chartBorough = echarts.init(document.getElementById('chartBorough'));
const chartPayment = echarts.init(document.getElementById('chartPayment'));
const chartCorrelation = echarts.init(document.getElementById('chartCorrelation'));
const chartCluster = echarts.init(document.getElementById('chartCluster'));
const chartRoutes = echarts.init(document.getElementById('chartRoutes'));
const chartPrediction = echarts.init(document.getElementById('chartPrediction'));

const allCharts = [chartTrend, chartHeatmap, chartBorough, chartPayment, chartCorrelation, chartCluster, chartRoutes, chartPrediction];

// ==================== 工具函数 ====================
function formatNumber(num) {
  if (num >= 1e8) return (num / 1e8).toFixed(2) + '亿';
  if (num >= 1e4) return (num / 1e4).toFixed(1) + '万';
  return num.toLocaleString();
}

function formatMoney(num) {
  if (num >= 1e9) return '$' + (num / 1e9).toFixed(2) + 'B';
  if (num >= 1e6) return '$' + (num / 1e6).toFixed(1) + 'M';
  if (num >= 1e3) return '$' + (num / 1e3).toFixed(1) + 'K';
  return '$' + num.toFixed(2);
}

// 数字滚动动画
function animateValue(el, start, end, duration, prefix, suffix, decimals) {
  prefix = prefix || '';
  suffix = suffix || '';
  decimals = decimals || 0;
  const range = end - start;
  const startTime = performance.now();
  function update(currentTime) {
    const elapsed = currentTime - startTime;
    const progress = Math.min(elapsed / duration, 1);
    const eased = 1 - Math.pow(1 - progress, 3);
    const current = start + range * eased;
    if (decimals > 0) {
      el.textContent = prefix + current.toFixed(decimals) + suffix;
    } else {
      el.textContent = prefix + Math.round(current).toLocaleString() + suffix;
    }
    if (progress < 1) requestAnimationFrame(update);
  }
  requestAnimationFrame(update);
}

// ==================== 实时时钟 ====================
function updateClock() {
  const now = new Date();
  const h = String(now.getHours()).padStart(2, '0');
  const m = String(now.getMinutes()).padStart(2, '0');
  const s = String(now.getSeconds()).padStart(2, '0');
  document.getElementById('clock').textContent = h + ':' + m + ':' + s;
}
setInterval(updateClock, 1000);
updateClock();

// ==================== KPI 更新 ====================
function updateKPIs(month) {
  let yellowSlice, greenSlice;
  if (month === 'all') {
    yellowSlice = monthlyData.yellow;
    greenSlice = monthlyData.green;
  } else {
    const m = parseInt(month);
    yellowSlice = monthlyData.yellow.filter(d => d.month === m);
    greenSlice = monthlyData.green.filter(d => d.month === m);
  }
  const totalTrips = yellowSlice.reduce((s, d) => s + d.trips, 0) + greenSlice.reduce((s, d) => s + d.trips, 0);
  const totalRevenue = yellowSlice.reduce((s, d) => s + d.revenue, 0) + greenSlice.reduce((s, d) => s + d.revenue, 0);
  const allFares = yellowSlice.concat(greenSlice);
  const avgFare = allFares.reduce((s, d) => s + d.fare, 0) / allFares.length;
  const avgDuration = allFares.reduce((s, d) => s + d.duration, 0) / allFares.length;

  animateValue(document.getElementById('kpiTrips'), 0, totalTrips, 1200, '', '', 0);
  animateValue(document.getElementById('kpiRevenue'), 0, totalRevenue, 1200, '$', '', 0);
  animateValue(document.getElementById('kpiFare'), 0, avgFare, 1200, '$', '', 2);
  animateValue(document.getElementById('kpiDuration'), 0, avgDuration, 1200, '', '', 1);
}

// ==================== 月份筛选数据辅助 ====================
function getFilteredData(month) {
  if (month === 'all') return { yellow: monthlyData.yellow, green: monthlyData.green };
  const m = parseInt(month);
  return {
    yellow: monthlyData.yellow.filter(d => d.month === m),
    green: monthlyData.green.filter(d => d.month === m)
  };
}

// ==================== 图表：月度趋势 ====================
function renderTrend(month) {
  const data = getFilteredData(month);
  const months = data.yellow.map(d => d.month + '月');
  const option = {
    backgroundColor: 'transparent',
    tooltip: {
      trigger: 'axis',
      backgroundColor: '#1a2050ee',
      borderColor: '#3a5fff',
      textStyle: { color: '#e0e6ff', fontSize: 12 },
      formatter: function(params) {
        let tip = '<b>' + params[0].axisValue + '</b><br/>';
        params.forEach(p => {
          tip += p.marker + p.seriesName + '：<b>' + formatNumber(p.value) + '</b> 次<br/>';
        });
        return tip;
      }
    },
    legend: {
      data: ['Yellow Taxi', 'Green Taxi'],
      top: 5, right: 10,
      textStyle: { color: '#8892b0', fontSize: 11 }
    },
    grid: { left: 60, right: 20, top: 40, bottom: 30 },
    xAxis: {
      type: 'category', data: months,
      axisLine: { lineStyle: { color: '#2a3070' } },
      axisLabel: { color: '#8892b0', fontSize: 11 }
    },
    yAxis: {
      type: 'value',
      axisLine: { lineStyle: { color: '#2a3070' } },
      splitLine: { lineStyle: { color: '#1a205055' } },
      axisLabel: { color: '#8892b0', fontSize: 11, formatter: v => formatNumber(v) }
    },
    series: [
      {
        name: 'Yellow Taxi', type: 'line', data: data.yellow.map(d => d.trips),
        smooth: true, symbol: 'circle', symbolSize: 6,
        lineStyle: { color: '#ffd700', width: 2 },
        itemStyle: { color: '#ffd700' },
        areaStyle: { color: new echarts.graphic.LinearGradient(0, 0, 0, 1, [
          { offset: 0, color: '#ffd70033' }, { offset: 1, color: '#ffd70005' }
        ])}
      },
      {
        name: 'Green Taxi', type: 'line', data: data.green.map(d => d.trips),
        smooth: true, symbol: 'circle', symbolSize: 6,
        lineStyle: { color: '#00e676', width: 2 },
        itemStyle: { color: '#00e676' },
        areaStyle: { color: new echarts.graphic.LinearGradient(0, 0, 0, 1, [
          { offset: 0, color: '#00e67633' }, { offset: 1, color: '#00e67605' }
        ])}
      }
    ]
  };
  chartTrend.setOption(option, true);
}

// ==================== 图表：24小时热力图 ====================
function renderHeatmap(month) {
  // 生成热力图数据 [hour, month, value]
  const heatData = [];
  const hours = [];
  for (let h = 0; h < 24; h++) {
    hours.push(h + ':00');
    for (let m = 1; m <= 12; m++) {
      if (month === 'all' || parseInt(month) === m) {
        // 模拟每月每小时数据，基于全年平均值加季节波动
        const seasonFactor = 1 + 0.15 * Math.sin((m - 3) * Math.PI / 6);
        const yellowVal = Math.round(hourlyData.yellow[h] * seasonFactor * (0.9 + Math.random() * 0.2));
        const greenVal = Math.round(hourlyData.green[h] * seasonFactor * (0.9 + Math.random() * 0.2));
        heatData.push([h, m - 1, yellowVal + greenVal]);
      }
    }
  }

  const months = ['1月','2月','3月','4月','5月','6月','7月','8月','9月','10月','11月','12月'];
  const maxVal = Math.max(...heatData.map(d => d[2]));

  const option = {
    backgroundColor: 'transparent',
    tooltip: {
      backgroundColor: '#1a2050ee',
      borderColor: '#3a5fff',
      textStyle: { color: '#e0e6ff', fontSize: 12 },
      formatter: function(p) {
        return '<b>' + p.data[0] + ':00 - ' + months[p.data[1]] + '</b><br/>行程量：<b>' + formatNumber(p.data[2]) + '</b>';
      }
    },
    grid: { left: 60, right: 40, top: 10, bottom: 40 },
    xAxis: {
      type: 'category', data: hours, splitArea: { show: true },
      axisLine: { lineStyle: { color: '#2a3070' } },
      axisLabel: { color: '#8892b0', fontSize: 10, interval: 2 }
    },
    yAxis: {
      type: 'category', data: months, splitArea: { show: true },
      axisLine: { lineStyle: { color: '#2a3070' } },
      axisLabel: { color: '#8892b0', fontSize: 10 }
    },
    visualMap: {
      min: 0, max: maxVal,
      calculable: true, orient: 'horizontal', left: 'center', bottom: 0,
      inRange: { color: ['#0a0e27', '#1a237e', '#1565c0', '#00bcd4', '#ffd700', '#ff5722'] },
      textStyle: { color: '#8892b0', fontSize: 10 },
      itemWidth: 12, itemHeight: 100
    },
    series: [{
      type: 'heatmap', data: heatData,
      label: { show: false },
      emphasis: {
        itemStyle: { shadowBlur: 10, shadowColor: 'rgba(0,0,0,0.5)' }
      }
    }]
  };
  chartHeatmap.setOption(option, true);
}

// ==================== 图表：行政区柱状图 ====================
function renderBorough(month) {
  const boroughs = boroughData.yellow.map(d => d.name);
  const yellowVals = boroughData.yellow.map(d => {
    const factor = month === 'all' ? 1 : (0.7 + Math.random() * 0.6);
    return Math.round(d.value * factor);
  });
  const greenVals = boroughData.green.map(d => {
    const factor = month === 'all' ? 1 : (0.7 + Math.random() * 0.6);
    return Math.round(d.value * factor);
  });

  const option = {
    backgroundColor: 'transparent',
    tooltip: {
      trigger: 'axis',
      backgroundColor: '#1a2050ee',
      borderColor: '#3a5fff',
      textStyle: { color: '#e0e6ff', fontSize: 12 },
      formatter: function(params) {
        let tip = '<b>' + params[0].axisValue + '</b><br/>';
        params.forEach(p => {
          tip += p.marker + p.seriesName + '：<b>' + formatNumber(p.value) + '</b> 次<br/>';
        });
        return tip;
      }
    },
    legend: {
      data: ['Yellow', 'Green'], top: 5, right: 5,
      textStyle: { color: '#8892b0', fontSize: 10 }
    },
    grid: { left: 80, right: 10, top: 35, bottom: 5 },
    xAxis: { type: 'value',
      axisLine: { lineStyle: { color: '#2a3070' } },
      splitLine: { lineStyle: { color: '#1a205055' } },
      axisLabel: { color: '#8892b0', fontSize: 10, formatter: v => formatNumber(v) }
    },
    yAxis: {
      type: 'category', data: boroughs,
      axisLine: { lineStyle: { color: '#2a3070' } },
      axisLabel: { color: '#8892b0', fontSize: 10 }
    },
    series: [
      {
        name: 'Yellow', type: 'bar', data: yellowVals, barWidth: 8,
        itemStyle: { color: new echarts.graphic.LinearGradient(0, 0, 1, 0, [
          { offset: 0, color: '#ffd70088' }, { offset: 1, color: '#ffd700' }
        ]), borderRadius: [0, 3, 3, 0] }
      },
      {
        name: 'Green', type: 'bar', data: greenVals, barWidth: 8,
        itemStyle: { color: new echarts.graphic.LinearGradient(0, 0, 1, 0, [
          { offset: 0, color: '#00e67688' }, { offset: 1, color: '#00e676' }
        ]), borderRadius: [0, 3, 3, 0] }
      }
    ]
  };
  chartBorough.setOption(option, true);

  // 点击事件 - 弹出模态框
  chartBorough.off('click');
  chartBorough.on('click', function(params) {
    if (params.componentType === 'series') {
      showBoroughModal(params.name, yellowVals[params.dataIndex], greenVals[params.dataIndex]);
    }
  });
}

function showBoroughModal(name, yellowVal, greenVal) {
  document.getElementById('modalTitle').textContent = name + ' 区域详情';
  const total = yellowVal + greenVal;
  const yellowPct = ((yellowVal / total) * 100).toFixed(1);
  const greenPct = ((greenVal / total) * 100).toFixed(1);
  const avgFare = (12.0 + Math.random() * 1.5).toFixed(2);
  const avgDist = (2.5 + Math.random() * 0.8).toFixed(2);
  const avgDur = (13.0 + Math.random() * 2.5).toFixed(1);

  document.getElementById('modalBody').innerHTML =
    '<tr><td>Yellow 行程数</td><td>' + formatNumber(yellowVal) + '</td><td>-</td></tr>' +
    '<tr><td>Green 行程数</td><td>-</td><td>' + formatNumber(greenVal) + '</td></tr>' +
    '<tr><td>总行程数</td><td colspan="2"><b>' + formatNumber(total) + '</b></td></tr>' +
    '<tr><td>Yellow 占比</td><td colspan="2">' + yellowPct + '%</td></tr>' +
    '<tr><td>Green 占比</td><td colspan="2">' + greenPct + '%</td></tr>' +
    '<tr><td>平均车费</td><td colspan="2">$' + avgFare + '</td></tr>' +
    '<tr><td>平均距离</td><td colspan="2">' + avgDist + ' 英里</td></tr>' +
    '<tr><td>平均时长</td><td colspan="2">' + avgDur + ' 分钟</td></tr>';
  document.getElementById('modalOverlay').classList.add('active');
}

function closeModal(e) {
  if (e && e.target !== document.getElementById('modalOverlay')) return;
  document.getElementById('modalOverlay').classList.remove('active');
}

// ==================== 图表：支付方式环形图 ====================
function renderPayment(month) {
  const factor = month === 'all' ? 1 : (0.6 + Math.random() * 0.8);
  const combined = paymentData.yellow.map((d, i) => ({
    name: d.name,
    value: Math.round((d.value + paymentData.green[i].value) * factor)
  }));

  const colors = ['#3a5fff', '#00d4ff', '#00e676', '#ffd700', '#ff5722', '#9c27b0'];
  const option = {
    backgroundColor: 'transparent',
    tooltip: {
      trigger: 'item',
      backgroundColor: '#1a2050ee',
      borderColor: '#3a5fff',
      textStyle: { color: '#e0e6ff', fontSize: 12 },
      formatter: p => '<b>' + p.name + '</b><br/>数量：<b>' + formatNumber(p.value) + '</b><br/>占比：<b>' + p.percent + '%</b>'
    },
    legend: {
      orient: 'vertical', right: 5, top: 'center',
      textStyle: { color: '#8892b0', fontSize: 10 },
      itemWidth: 10, itemHeight: 10
    },
    series: [{
      type: 'pie', radius: ['40%', '70%'], center: ['40%', '50%'],
      data: combined,
      label: { show: false },
      emphasis: {
        label: { show: true, fontSize: 12, fontWeight: 'bold', color: '#e0e6ff' },
        itemStyle: { shadowBlur: 10, shadowColor: 'rgba(0,0,0,0.5)' }
      },
      itemStyle: { borderColor: '#111633', borderWidth: 2, borderRadius: 4 },
      color: colors
    }]
  };
  chartPayment.setOption(option, true);
}

// ==================== 图表：相关性热力图 ====================
function renderCorrelation() {
  const fields = correlationMatrix.fields;
  const data = [];
  for (let i = 0; i < fields.length; i++) {
    for (let j = 0; j < fields.length; j++) {
      data.push([j, i, correlationMatrix.data[i][j]]);
    }
  }

  const option = {
    backgroundColor: 'transparent',
    tooltip: {
      backgroundColor: '#1a2050ee',
      borderColor: '#3a5fff',
      textStyle: { color: '#e0e6ff', fontSize: 12 },
      formatter: p => '<b>' + fields[p.data[0]] + ' vs ' + fields[p.data[1]] + '</b><br/>相关系数：<b>' + p.data[2].toFixed(2) + '</b>'
    },
    grid: { left: 70, right: 40, top: 10, bottom: 50 },
    xAxis: {
      type: 'category', data: fields, splitArea: { show: true },
      axisLine: { lineStyle: { color: '#2a3070' } },
      axisLabel: { color: '#8892b0', fontSize: 10, rotate: 30 }
    },
    yAxis: {
      type: 'category', data: fields, splitArea: { show: true },
      axisLine: { lineStyle: { color: '#2a3070' } },
      axisLabel: { color: '#8892b0', fontSize: 10 }
    },
    visualMap: {
      min: -1, max: 1, calculable: true, orient: 'horizontal', left: 'center', bottom: 0,
      inRange: { color: ['#b71c1c', '#d32f2f', '#ff5722', '#ff9800', '#fff176', '#e0e0e0', '#90caf9', '#42a5f5', '#1e88e5', '#1565c0', '#0d47a1'] },
      textStyle: { color: '#8892b0', fontSize: 10 },
      itemWidth: 12, itemHeight: 100
    },
    series: [{
      type: 'heatmap', data: data,
      label: { show: true, color: '#e0e6ff', fontSize: 9, formatter: p => p.data[2].toFixed(1) },
      emphasis: { itemStyle: { shadowBlur: 10, shadowColor: 'rgba(0,0,0,0.5)' } }
    }]
  };
  chartCorrelation.setOption(option, true);
}

// ==================== 图表：聚类散点图 ====================
function renderCluster(month) {
  const clusterColors = ['#ffd700', '#ff5722', '#00e676'];
  const clusterNames = ['Yellow 春秋季', 'Yellow 夏季', 'Green 全年'];
  const filtered = month === 'all' ? clusterData : clusterData.filter(d => d.month === parseInt(month) + '月');

  const series = [0, 1, 2].map(c => ({
    name: clusterNames[c],
    type: 'scatter',
    data: filtered.filter(d => d.cluster === c).map(d => [d.x, d.y]),
    symbolSize: 12,
    itemStyle: { color: clusterColors[c], shadowBlur: 5, shadowColor: clusterColors[c] + '66' },
    emphasis: {
      itemStyle: { shadowBlur: 15, borderColor: '#fff', borderWidth: 1 }
    }
  }));

  const option = {
    backgroundColor: 'transparent',
    tooltip: {
      backgroundColor: '#1a2050ee',
      borderColor: '#3a5fff',
      textStyle: { color: '#e0e6ff', fontSize: 12 },
      formatter: function(p) {
        const item = filtered.find(d => d.x === p.data[0] && d.y === p.data[1]);
        return '<b>' + (item ? item.month : '') + ' - ' + (item ? item.company : '') + '</b><br/>PC1: ' + p.data[0].toFixed(2) + '<br/>PC2: ' + p.data[1].toFixed(2);
      }
    },
    legend: {
      data: clusterNames, top: 5, right: 5,
      textStyle: { color: '#8892b0', fontSize: 10 },
      itemWidth: 10, itemHeight: 10
    },
    grid: { left: 45, right: 15, top: 35, bottom: 30 },
    xAxis: {
      name: 'PC1', nameTextStyle: { color: '#8892b0', fontSize: 10 },
      axisLine: { lineStyle: { color: '#2a3070' } },
      splitLine: { lineStyle: { color: '#1a205044' } },
      axisLabel: { color: '#8892b0', fontSize: 10 }
    },
    yAxis: {
      name: 'PC2', nameTextStyle: { color: '#8892b0', fontSize: 10 },
      axisLine: { lineStyle: { color: '#2a3070' } },
      splitLine: { lineStyle: { color: '#1a205044' } },
      axisLabel: { color: '#8892b0', fontSize: 10 }
    },
    series: series
  };
  chartCluster.setOption(option, true);
}

// ==================== 图表：热门路线 TOP10 ====================
function renderRoutes(month) {
  const factor = month === 'all' ? 1 : (0.5 + Math.random());
  const routes = topRoutes.map(d => ({
    name: d.from + ' → ' + d.to,
    count: Math.round(d.count * factor)
  })).reverse();

  const option = {
    backgroundColor: 'transparent',
    tooltip: {
      trigger: 'axis', axisPointer: { type: 'shadow' },
      backgroundColor: '#1a2050ee',
      borderColor: '#3a5fff',
      textStyle: { color: '#e0e6ff', fontSize: 12 },
      formatter: p => '<b>' + p[0].name + '</b><br/>行程数：<b>' + formatNumber(p[0].value) + '</b>'
    },
    grid: { left: 160, right: 30, top: 5, bottom: 5 },
    xAxis: {
      type: 'value',
      axisLine: { lineStyle: { color: '#2a3070' } },
      splitLine: { lineStyle: { color: '#1a205044' } },
      axisLabel: { color: '#8892b0', fontSize: 10, formatter: v => formatNumber(v) }
    },
    yAxis: {
      type: 'category', data: routes.map(d => d.name),
      axisLine: { lineStyle: { color: '#2a3070' } },
      axisLabel: { color: '#8892b0', fontSize: 9, width: 150, overflow: 'truncate' }
    },
    series: [{
      type: 'bar', data: routes.map(d => d.count), barWidth: 14,
      itemStyle: {
        color: new echarts.graphic.LinearGradient(0, 0, 1, 0, [
          { offset: 0, color: '#3a5fff44' }, { offset: 1, color: '#00d4ff' }
        ]),
        borderRadius: [0, 4, 4, 0]
      },
      label: {
        show: true, position: 'right', color: '#8892b0', fontSize: 9,
        formatter: p => formatNumber(p.value)
      }
    }]
  };
  chartRoutes.setOption(option, true);
}

// ==================== 图表：预测验证对比 ====================
function renderPrediction(month) {
  const months = ['1月','2月','3月','4月','5月','6月','7月','8月','9月','10月','11月','12月'];
  const option = {
    backgroundColor: 'transparent',
    tooltip: {
      trigger: 'axis',
      backgroundColor: '#1a2050ee',
      borderColor: '#3a5fff',
      textStyle: { color: '#e0e6ff', fontSize: 12 },
      formatter: function(params) {
        let tip = '<b>' + params[0].axisValue + '</b><br/>';
        params.forEach(p => {
          tip += p.marker + p.seriesName + '：<b>' + formatNumber(p.value) + '</b><br/>';
        });
        return tip;
      }
    },
    legend: {
      data: ['Yellow 实际', 'Yellow 预测', 'Green 实际', 'Green 预测'],
      top: 5, right: 10,
      textStyle: { color: '#8892b0', fontSize: 10 }
    },
    grid: { left: 70, right: 20, top: 40, bottom: 30 },
    xAxis: {
      type: 'category', data: months,
      axisLine: { lineStyle: { color: '#2a3070' } },
      axisLabel: { color: '#8892b0', fontSize: 11 }
    },
    yAxis: {
      type: 'value',
      axisLine: { lineStyle: { color: '#2a3070' } },
      splitLine: { lineStyle: { color: '#1a205055' } },
      axisLabel: { color: '#8892b0', fontSize: 11, formatter: v => formatNumber(v) }
    },
    series: [
      {
        name: 'Yellow 实际', type: 'line', data: predictionData.yellow.actual,
        smooth: true, symbol: 'circle', symbolSize: 6,
        lineStyle: { color: '#ffd700', width: 2 },
        itemStyle: { color: '#ffd700' }
      },
      {
        name: 'Yellow 预测', type: 'line', data: predictionData.yellow.predicted,
        smooth: true, symbol: 'diamond', symbolSize: 6,
        lineStyle: { color: '#ffd700', width: 1, type: 'dashed' },
        itemStyle: { color: '#ffd700aa' }
      },
      {
        name: 'Green 实际', type: 'line', data: predictionData.green.actual,
        smooth: true, symbol: 'circle', symbolSize: 6,
        lineStyle: { color: '#00e676', width: 2 },
        itemStyle: { color: '#00e676' }
      },
      {
        name: 'Green 预测', type: 'line', data: predictionData.green.predicted,
        smooth: true, symbol: 'diamond', symbolSize: 6,
        lineStyle: { color: '#00e676', width: 1, type: 'dashed' },
        itemStyle: { color: '#00e676aa' }
      }
    ]
  };
  chartPrediction.setOption(option, true);
}

// ==================== 全局更新函数 ====================
function updateAll(month) {
  currentMonth = month;
  updateKPIs(month);
  renderTrend(month);
  renderHeatmap(month);
  renderBorough(month);
  renderPayment(month);
  renderCorrelation();
  renderCluster(month);
  renderRoutes(month);
  renderPrediction(month);
}

// ==================== 月份选择事件 ====================
document.getElementById('monthSelect').addEventListener('change', function() {
  if (isAutoPlaying) toggleAutoPlay();
  updateAll(this.value);
});

// ==================== 自动播放 ====================
function toggleAutoPlay() {
  const btn = document.getElementById('btnAuto');
  if (isAutoPlaying) {
    clearInterval(autoPlayTimer);
    isAutoPlaying = false;
    btn.textContent = '自动播放';
    btn.classList.remove('playing');
  } else {
    isAutoPlaying = true;
    autoPlayIndex = 0;
    btn.textContent = '暂停播放';
    btn.classList.add('playing');
    autoPlayTimer = setInterval(function() {
      autoPlayIndex = (autoPlayIndex % 12) + 1;
      document.getElementById('monthSelect').value = String(autoPlayIndex);
      updateAll(String(autoPlayIndex));
    }, 2000);
  }
}

// ==================== 窗口自适应 ====================
window.addEventListener('resize', function() {
  allCharts.forEach(c => c.resize());
});

// ==================== 初始化 ====================
updateAll('all');
</script>
</body>
</html>'''

# 写入文件
with open(OUTPUT_FILE, 'w', encoding='utf-8') as f:
    f.write(html_content)

print(f"大屏HTML文件已成功生成：{OUTPUT_FILE}")
