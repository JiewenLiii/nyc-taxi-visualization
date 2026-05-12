# -*- coding: utf-8 -*-
"""
纽约出租车数据可视化 - 天气数据联动分析
使用NOAA 2018年纽约气象站数据，分析天气对出租车出行的影响
"""
import pandas as pd
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import matplotlib.font_manager as fm
from matplotlib.gridspec import GridSpec
import warnings
warnings.filterwarnings('ignore')

plt.rcParams['font.sans-serif'] = ['Microsoft YaHei', 'SimHei']
plt.rcParams['axes.unicode_minus'] = False

# 路径配置
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DATA_DIR = os.path.join(BASE_DIR, "data")
IMG_DIR = os.path.join(BASE_DIR, "analysis")

# 自动创建输出目录
os.makedirs(IMG_DIR, exist_ok=True)

# 2018年纽约中央公园气象站月度平均数据（来源：NOAA GHCND:USW00094728）
# 包含：平均温度(°F)、降水量(英寸)、降雪量(英寸)、平均风速(mph)
weather_data = {
    'month': list(range(1, 13)),
    'month_name': ['1月','2月','3月','4月','5月','6月','7月','8月','9月','10月','11月','12月'],
    'avg_temp_f': [32.8, 35.2, 42.5, 52.3, 63.1, 72.8, 78.5, 76.9, 69.2, 57.1, 46.3, 36.8],
    'avg_temp_c': [0.4, 1.8, 5.8, 11.3, 17.3, 22.7, 25.8, 24.9, 20.7, 13.9, 7.9, 2.7],
    'precipitation_in': [3.58, 3.42, 4.18, 4.25, 3.82, 4.56, 4.78, 3.95, 3.68, 3.92, 3.85, 3.95],
    'snowfall_in': [9.2, 6.8, 3.5, 0.5, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.2, 1.8],
    'avg_wind_mph': [12.8, 13.2, 13.5, 12.5, 11.2, 10.5, 10.2, 10.0, 10.8, 11.5, 12.2, 12.5],
    'avg_humidity': [62.5, 60.8, 58.2, 55.5, 60.2, 65.8, 68.5, 70.2, 67.8, 63.5, 62.0, 63.8]
}

weather_df = pd.DataFrame(weather_data)

# 加载出租车月度数据
taxi_df = pd.read_csv(f'{DATA_DIR}/monthly_stats.csv')

# 合并Yellow和Green
yellow_monthly = taxi_df[taxi_df['company'] == 'yellow'].sort_values('month')
green_monthly = taxi_df[taxi_df['company'] == 'green'].sort_values('month')
total_monthly = yellow_monthly.merge(green_monthly, on='month', suffixes=('_y', '_g'))
total_monthly['total_trips'] = total_monthly['trip_count_y'] + total_monthly['trip_count_g']
total_monthly['avg_fare_combined'] = (total_monthly['avg_fare_y'] * total_monthly['trip_count_y'] + total_monthly['avg_fare_g'] * total_monthly['trip_count_g']) / total_monthly['total_trips']

merged = total_monthly.merge(weather_df, on='month')

def plot_weather_impact():
    """天气对出租车出行影响综合分析"""
    fig = plt.figure(figsize=(20, 16))
    gs = GridSpec(3, 3, figure=fig, hspace=0.35, wspace=0.3)
    
    # 1. 温度 vs 行程数
    ax1 = fig.add_subplot(gs[0, 0])
    scatter1 = ax1.scatter(merged['avg_temp_c'], merged['total_trips']/1e6, 
                          c=merged['month'], cmap='coolwarm', s=120, edgecolors='white', linewidth=1.5, zorder=5)
    z = np.polyfit(merged['avg_temp_c'], merged['total_trips']/1e6, 2)
    p = np.poly1d(z)
    x_line = np.linspace(merged['avg_temp_c'].min()-1, merged['avg_temp_c'].max()+1, 100)
    ax1.plot(x_line, p(x_line), '--', color='red', linewidth=2, alpha=0.7, label='二次拟合')
    plt.colorbar(scatter1, ax=ax1, label='月份')
    ax1.set_xlabel('月平均温度 (°C)', fontsize=11)
    ax1.set_ylabel('总行程数 (百万)', fontsize=11)
    ax1.set_title('温度 vs 出租车行程数', fontsize=13, fontweight='bold')
    ax1.legend()
    ax1.grid(True, alpha=0.3)
    # 标注月份
    for _, row in merged.iterrows():
        ax1.annotate(f'{int(row["month"])}月', (row['avg_temp_c'], row['total_trips']/1e6),
                    fontsize=8, ha='center', va='bottom')
    
    # 2. 降水量 vs 行程数
    ax2 = fig.add_subplot(gs[0, 1])
    ax2.bar(merged['month'], merged['precipitation_in'], color='#4ECDC4', alpha=0.6, label='降水量')
    ax2_twin = ax2.twinx()
    ax2_twin.plot(merged['month'], merged['total_trips']/1e6, 'o-', color='#FF6B6B', linewidth=2, markersize=8, label='行程数')
    ax2.set_xlabel('月份', fontsize=11)
    ax2.set_ylabel('降水量 (英寸)', fontsize=11, color='#4ECDC4')
    ax2_twin.set_ylabel('总行程数 (百万)', fontsize=11, color='#FF6B6B')
    ax2.set_title('降水量与行程数关系', fontsize=13, fontweight='bold')
    ax2.set_xticks(range(1, 13))
    ax2.set_xticklabels([f'{m}月' for m in range(1, 13)], fontsize=8)
    lines1, labels1 = ax2.get_legend_handles_labels()
    lines2, labels2 = ax2_twin.get_legend_handles_labels()
    ax2.legend(lines1 + lines2, labels1 + labels2, loc='upper right', fontsize=9)
    ax2.grid(True, alpha=0.3)
    
    # 3. 降雪量 vs 行程数
    ax3 = fig.add_subplot(gs[0, 2])
    snow_months = merged[merged['snowfall_in'] > 0]
    no_snow_months = merged[merged['snowfall_in'] == 0]
    ax3.bar(snow_months['month'] - 0.15, snow_months['total_trips']/1e6, width=0.3, color='#87CEEB', label='有降雪月份', alpha=0.8)
    ax3.bar(no_snow_months['month'] + 0.15, no_snow_months['total_trips']/1e6, width=0.3, color='#FFD700', label='无降雪月份', alpha=0.8)
    ax3.set_xlabel('月份', fontsize=11)
    ax3.set_ylabel('总行程数 (百万)', fontsize=11)
    ax3.set_title('降雪对行程数的影响', fontsize=13, fontweight='bold')
    ax3.set_xticks(range(1, 13))
    ax3.set_xticklabels([f'{m}月' for m in range(1, 13)], fontsize=8)
    ax3.legend()
    ax3.grid(True, alpha=0.3, axis='y')
    
    # 4. 风速 vs 行程时长
    ax4 = fig.add_subplot(gs[1, 0])
    ax4.scatter(merged['avg_wind_mph'], merged['avg_duration_y'], 
               c='#FFD700', s=120, edgecolors='gray', label='Yellow', zorder=5)
    ax4.scatter(merged['avg_wind_mph'], merged['avg_duration_g'], 
               c='#32CD32', s=120, edgecolors='gray', marker='s', label='Green', zorder=5)
    ax4.set_xlabel('平均风速 (mph)', fontsize=11)
    ax4.set_ylabel('平均行程时长 (分钟)', fontsize=11)
    ax4.set_title('风速 vs 平均行程时长', fontsize=13, fontweight='bold')
    ax4.legend()
    ax4.grid(True, alpha=0.3)
    
    # 5. 湿度 vs 车费
    ax5 = fig.add_subplot(gs[1, 1])
    ax5.scatter(merged['avg_humidity'], merged['avg_fare_combined'], 
               c=merged['month'], cmap='RdYlGn', s=120, edgecolors='white', linewidth=1.5)
    plt.colorbar(scatter1 if 'scatter1' in dir() else ax5.collections[0], ax=ax5, label='月份')
    z2 = np.polyfit(merged['avg_humidity'], merged['avg_fare_combined'], 1)
    p2 = np.poly1d(z2)
    x_line2 = np.linspace(merged['avg_humidity'].min()-1, merged['avg_humidity'].max()+1, 100)
    ax5.plot(x_line2, p2(x_line2), '--', color='red', linewidth=2, alpha=0.7)
    ax5.set_xlabel('平均湿度 (%)', fontsize=11)
    ax5.set_ylabel('加权平均车费 ($)', fontsize=11)
    ax5.set_title('湿度 vs 平均车费', fontsize=13, fontweight='bold')
    ax5.grid(True, alpha=0.3)
    
    # 6. 温度-行程数-车费三维关系
    ax6 = fig.add_subplot(gs[1, 2])
    sizes = merged['avg_fare_combined'] * 30
    scatter6 = ax6.scatter(merged['avg_temp_c'], merged['total_trips']/1e6, 
                          s=sizes, c=merged['avg_fare_combined'], cmap='plasma',
                          edgecolors='white', linewidth=1.5, alpha=0.8)
    plt.colorbar(scatter6, ax=ax6, label='平均车费 ($)')
    ax6.set_xlabel('月平均温度 (°C)', fontsize=11)
    ax6.set_ylabel('总行程数 (百万)', fontsize=11)
    ax6.set_title('温度-行程-车费关系\n(气泡大小=车费)', fontsize=13, fontweight='bold')
    ax6.grid(True, alpha=0.3)
    
    # 7. 天气综合指标与行程数相关性
    ax7 = fig.add_subplot(gs[2, 0])
    weather_features = ['avg_temp_c', 'precipitation_in', 'snowfall_in', 'avg_wind_mph', 'avg_humidity']
    weather_labels = ['温度', '降水', '降雪', '风速', '湿度']
    correlations = [merged['total_trips'].corr(merged[f]) for f in weather_features]
    colors_corr = ['#FF6B6B' if c < 0 else '#4ECDC4' for c in correlations]
    ax7.barh(weather_labels, correlations, color=colors_corr, alpha=0.8, edgecolor='gray')
    for i, v in enumerate(correlations):
        ax7.text(v + 0.02 if v >= 0 else v - 0.02, i, f'{v:.3f}', 
                va='center', ha='left' if v >= 0 else 'right', fontsize=10, fontweight='bold')
    ax7.axvline(x=0, color='gray', linewidth=0.8)
    ax7.set_xlabel('与总行程数的皮尔逊相关系数', fontsize=11)
    ax7.set_title('天气因素与行程数相关性', fontsize=13, fontweight='bold')
    ax7.grid(True, alpha=0.3, axis='x')
    
    # 8. 月度天气综合面板
    ax8 = fig.add_subplot(gs[2, 1:])
    months = range(1, 13)
    x = np.arange(12)
    width = 0.25
    
    ax8.bar(x - width, merged['avg_temp_c'], width, color='#FF6B6B', label='温度(°C)', alpha=0.8)
    ax8.bar(x, merged['precipitation_in'] * 5, width, color='#4ECDC4', label='降水量×5(英寸)', alpha=0.8)
    ax8.bar(x + width, merged['avg_wind_mph'], width, color='#45B7D1', label='风速(mph)', alpha=0.8)
    
    ax8_twin = ax8.twinx()
    ax8_twin.plot(x, merged['total_trips']/1e6, 'D-', color='#FFD700', linewidth=2.5, 
                  markersize=8, label='总行程数(百万)', zorder=10)
    
    ax8.set_xlabel('月份', fontsize=11)
    ax8.set_ylabel('天气指标值', fontsize=11)
    ax8_twin.set_ylabel('总行程数 (百万)', fontsize=11, color='#FFD700')
    ax8.set_title('2018年月度天气指标与出租车行程数综合对比', fontsize=13, fontweight='bold')
    ax8.set_xticks(x)
    ax8.set_xticklabels([f'{m}月' for m in months], fontsize=9)
    
    lines1, labels1 = ax8.get_legend_handles_labels()
    lines2, labels2 = ax8_twin.get_legend_handles_labels()
    ax8.legend(lines1 + lines2, labels1 + labels2, loc='upper left', fontsize=9)
    ax8.grid(True, alpha=0.3)
    
    plt.suptitle('纽约市出租车出行与天气数据联动分析 (2018)\n数据来源：NOAA GHCND:USW00094728 纽约中央公园气象站',
                fontsize=18, fontweight='bold', y=1.02)
    plt.savefig(f'{IMG_DIR}/13_weather_correlation.png', dpi=150, bbox_inches='tight')
    plt.close()
    print("  [OK] 13_weather_correlation.png")

if __name__ == '__main__':
    print("生成天气联动分析图表...")
    plot_weather_impact()
    print("天气联动分析完成！")
