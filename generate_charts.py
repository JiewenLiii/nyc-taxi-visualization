# -*- coding: utf-8 -*-
"""
纽约出租车数据可视化 - 静态分析图表生成
包含：缺失值分析、月度趋势、小时模式、星期模式、
      支付方式、行政区分析、相关性热力图、聚类分析、预测验证
"""
import pandas as pd
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import matplotlib.font_manager as fm
from matplotlib.gridspec import GridSpec
import seaborn as sns
from sklearn.cluster import KMeans
from sklearn.preprocessing import StandardScaler
from sklearn.linear_model import LinearRegression
from sklearn.metrics import mean_squared_error, r2_score
import warnings
warnings.filterwarnings('ignore')

# 中文字体配置
plt.rcParams['font.sans-serif'] = ['Microsoft YaHei', 'SimHei']
plt.rcParams['axes.unicode_minus'] = False

# 路径配置
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DATA_DIR = os.path.join(BASE_DIR, "data")
IMG_DIR = os.path.join(BASE_DIR, "analysis")

# 自动创建输出目录
os.makedirs(IMG_DIR, exist_ok=True)

def load_data():
    files = {
        'monthly': 'monthly_stats.csv',
        'missing': 'missing_values.csv',
        'hourly': 'hourly_patterns.csv',
        'dow': 'dow_patterns.csv',
        'payment': 'payment_patterns.csv',
        'borough': 'borough_patterns.csv',
        'routes': 'top_routes.csv',
        'zone': 'zone_lookup.csv'
    }
    data = {}
    for key, fname in files.items():
        fpath = f'{DATA_DIR}/{fname}'
        if os.path.exists(fpath):
            data[key] = pd.read_csv(fpath)
    return data

import os

# ============ 图1: 缺失值分析 ============
def plot_missing_values(data):
    if 'missing' not in data or data['missing'].empty:
        return
    df = data['missing']
    fig, axes = plt.subplots(1, 2, figsize=(16, 6))
    
    # 按字段汇总缺失率
    summary = df.groupby(['company', 'column']).agg(
        avg_null_pct=('null_pct', 'mean'),
        total_null=('null_count', 'sum')
    ).reset_index()
    
    colors = {'yellow': '#FFD700', 'green': '#32CD32'}
    for idx, company in enumerate(['yellow', 'green']):
        cdata = summary[summary['company'] == company].sort_values('avg_null_pct', ascending=True)
        if cdata.empty:
            continue
        axes[idx].barh(cdata['column'], cdata['avg_null_pct'], color=colors[company], alpha=0.8, edgecolor='gray')
        axes[idx].set_xlabel('平均缺失率 (%)')
        axes[idx].set_title(f'{company.upper()} 出租车字段缺失率', fontsize=14, fontweight='bold')
        for i, (v, col) in enumerate(zip(cdata['avg_null_pct'], cdata['column'])):
            axes[idx].text(v + 0.5, i, f'{v:.1f}%', va='center', fontsize=9)
    
    plt.tight_layout()
    plt.savefig(f'{IMG_DIR}/01_missing_values.png', dpi=150, bbox_inches='tight')
    plt.close()
    print("  [OK] 01_missing_values.png")

# ============ 图2: 月度行程趋势对比 ============
def plot_monthly_trend(data):
    df = data['monthly']
    fig, axes = plt.subplots(2, 2, figsize=(16, 12))
    months = range(1, 13)
    month_labels = [f'{m}月' for m in months]
    
    colors = {'yellow': '#FFD700', 'green': '#32CD32'}
    
    for company in ['yellow', 'green']:
        cdata = df[df['company'] == company]
        label = 'Yellow' if company == 'yellow' else 'Green'
        
        axes[0, 0].plot(months, cdata['trip_count'], 'o-', color=colors[company], label=label, linewidth=2, markersize=6)
        axes[0, 1].plot(months, cdata['avg_fare'], 's-', color=colors[company], label=label, linewidth=2, markersize=6)
        axes[1, 0].plot(months, cdata['avg_distance'], '^-', color=colors[company], label=label, linewidth=2, markersize=6)
        axes[1, 1].plot(months, cdata['avg_duration'], 'D-', color=colors[company], label=label, linewidth=2, markersize=6)
    
    axes[0, 0].set_title('月度行程数量', fontsize=13, fontweight='bold')
    axes[0, 0].set_ylabel('行程数')
    axes[0, 0].legend()
    axes[0, 0].set_xticks(months)
    axes[0, 0].set_xticklabels(month_labels)
    axes[0, 0].grid(True, alpha=0.3)
    
    axes[0, 1].set_title('月度平均车费', fontsize=13, fontweight='bold')
    axes[0, 1].set_ylabel('车费 ($)')
    axes[0, 1].legend()
    axes[0, 1].set_xticks(months)
    axes[0, 1].set_xticklabels(month_labels)
    axes[0, 1].grid(True, alpha=0.3)
    
    axes[1, 0].set_title('月度平均行程距离', fontsize=13, fontweight='bold')
    axes[1, 0].set_ylabel('距离 (英里)')
    axes[1, 0].legend()
    axes[1, 0].set_xticks(months)
    axes[1, 0].set_xticklabels(month_labels)
    axes[1, 0].grid(True, alpha=0.3)
    
    axes[1, 1].set_title('月度平均行程时长', fontsize=13, fontweight='bold')
    axes[1, 1].set_ylabel('时长 (分钟)')
    axes[1, 1].legend()
    axes[1, 1].set_xticks(months)
    axes[1, 1].set_xticklabels(month_labels)
    axes[1, 1].grid(True, alpha=0.3)
    
    plt.suptitle('Yellow vs Green 出租车 2018年月度趋势对比', fontsize=16, fontweight='bold', y=1.02)
    plt.tight_layout()
    plt.savefig(f'{IMG_DIR}/02_monthly_trend.png', dpi=150, bbox_inches='tight')
    plt.close()
    print("  [OK] 02_monthly_trend.png")

# ============ 图3: 24小时行程模式 ============
def plot_hourly_pattern(data):
    df = data['hourly']
    # 汇总全年小时模式
    hourly_agg = df.groupby(['company', 'pickup_hour']).agg(
        avg_trip_count=('trip_count', 'mean'),
        avg_fare=('avg_fare', 'mean'),
        avg_distance=('avg_distance', 'mean'),
        avg_duration=('avg_duration', 'mean')
    ).reset_index()
    
    fig, axes = plt.subplots(2, 2, figsize=(16, 12))
    hours = list(range(24))
    
    for company in ['yellow', 'green']:
        cdata = hourly_agg[hourly_agg['company'] == company].sort_values('pickup_hour')
        color = '#FFD700' if company == 'yellow' else '#32CD32'
        label = 'Yellow' if company == 'yellow' else 'Green'
        lw = 2.5 if company == 'yellow' else 2
        
        axes[0, 0].plot(cdata['pickup_hour'], cdata['avg_trip_count'], 'o-', color=color, label=label, linewidth=lw)
        axes[0, 1].plot(cdata['pickup_hour'], cdata['avg_fare'], 's-', color=color, label=label, linewidth=lw)
        axes[1, 0].plot(cdata['pickup_hour'], cdata['avg_distance'], '^-', color=color, label=label, linewidth=lw)
        axes[1, 1].plot(cdata['pickup_hour'], cdata['avg_duration'], 'D-', color=color, label=label, linewidth=lw)
    
    titles = ['24小时平均行程数量', '24小时平均车费', '24小时平均行程距离', '24小时平均行程时长']
    ylabels = ['行程数', '车费 ($)', '距离 (英里)', '时长 (分钟)']
    
    for i, ax in enumerate(axes.flat):
        ax.set_title(titles[i], fontsize=13, fontweight='bold')
        ax.set_xlabel('小时')
        ax.set_ylabel(ylabels[i])
        ax.legend()
        ax.set_xticks(hours)
        ax.grid(True, alpha=0.3)
    
    plt.suptitle('Yellow vs Green 出租车 24小时运营模式对比', fontsize=16, fontweight='bold', y=1.02)
    plt.tight_layout()
    plt.savefig(f'{IMG_DIR}/03_hourly_pattern.png', dpi=150, bbox_inches='tight')
    plt.close()
    print("  [OK] 03_hourly_pattern.png")

# ============ 图4: 星期模式 ============
def plot_dow_pattern(data):
    df = data['dow']
    dow_agg = df.groupby(['company', 'pickup_dayofweek']).agg(
        avg_trip_count=('trip_count', 'mean'),
        avg_fare=('avg_fare', 'mean'),
        avg_distance=('avg_distance', 'mean')
    ).reset_index()
    
    fig, axes = plt.subplots(1, 3, figsize=(18, 6))
    dow_labels = ['周一', '周二', '周三', '周四', '周五', '周六', '周日']
    
    x = np.arange(7)
    width = 0.35
    
    for company in ['yellow', 'green']:
        cdata = dow_agg[dow_agg['company'] == company].sort_values('pickup_dayofweek')
        color = '#FFD700' if company == 'yellow' else '#32CD32'
        label = 'Yellow' if company == 'yellow' else 'Green'
        offset = 0 if company == 'yellow' else width
        
        axes[0].bar(x + offset, cdata['avg_trip_count'], width, color=color, label=label, alpha=0.8)
        axes[1].bar(x + offset, cdata['avg_fare'], width, color=color, label=label, alpha=0.8)
        axes[2].bar(x + offset, cdata['avg_distance'], width, color=color, label=label, alpha=0.8)
    
    titles = ['星期行程数量', '星期平均车费', '星期平均距离']
    ylabels = ['行程数', '车费 ($)', '距离 (英里)']
    
    for i, ax in enumerate(axes):
        ax.set_title(titles[i], fontsize=13, fontweight='bold')
        ax.set_ylabel(ylabels[i])
        ax.set_xticks(x + width/2)
        ax.set_xticklabels(dow_labels)
        ax.legend()
        ax.grid(True, alpha=0.3, axis='y')
    
    plt.suptitle('Yellow vs Green 出租车 星期运营模式对比', fontsize=16, fontweight='bold', y=1.02)
    plt.tight_layout()
    plt.savefig(f'{IMG_DIR}/04_dow_pattern.png', dpi=150, bbox_inches='tight')
    plt.close()
    print("  [OK] 04_dow_pattern.png")

# ============ 图5: 支付方式饼图 ============
def plot_payment(data):
    if 'payment' not in data:
        return
    df = data['payment']
    # 汇总全年
    pay_agg = df.groupby(['company', 'payment_type'])['count'].sum().reset_index()
    
    fig, axes = plt.subplots(1, 2, figsize=(14, 6))
    colors_pie = ['#FF6B6B', '#4ECDC4', '#45B7D1', '#96CEB4', '#FFEAA7', '#DDA0DD']
    
    for idx, company in enumerate(['yellow', 'green']):
        cdata = pay_agg[pay_agg['company'] == company].sort_values('count', ascending=False)
        total = cdata['count'].sum()
        labels = [f'{row["payment_type"]}\n({row["count"]/total*100:.1f}%)' for _, row in cdata.iterrows()]
        axes[idx].pie(cdata['count'], labels=labels, colors=colors_pie[:len(cdata)],
                      autopct='', startangle=90, textprops={'fontsize': 10})
        title = 'Yellow' if company == 'yellow' else 'Green'
        axes[idx].set_title(f'{title} 出租车支付方式分布', fontsize=14, fontweight='bold')
    
    plt.tight_layout()
    plt.savefig(f'{IMG_DIR}/05_payment_type.png', dpi=150, bbox_inches='tight')
    plt.close()
    print("  [OK] 05_payment_type.png")

# ============ 图6: 行政区分析 ============
def plot_borough(data):
    if 'borough' not in data:
        return
    df = data['borough']
    borough_agg = df.groupby(['company', 'Borough']).agg(
        total_trips=('trip_count', 'sum'),
        avg_fare=('avg_fare', 'mean')
    ).reset_index()
    
    fig, axes = plt.subplots(1, 2, figsize=(16, 7))
    
    for idx, company in enumerate(['yellow', 'green']):
        cdata = borough_agg[borough_agg['company'] == company].sort_values('total_trips', ascending=True)
        color = '#FFD700' if company == 'yellow' else '#32CD32'
        title = 'Yellow' if company == 'yellow' else 'Green'
        
        axes[idx].barh(cdata['Borough'], cdata['total_trips'], color=color, alpha=0.8, edgecolor='gray')
        axes[idx].set_xlabel('总行程数')
        axes[idx].set_title(f'{title} 出租车各行政区行程量', fontsize=14, fontweight='bold')
        for i, v in enumerate(cdata['total_trips']):
            axes[idx].text(v + cdata['total_trips'].max()*0.01, i, f'{v:,.0f}', va='center', fontsize=9)
    
    plt.tight_layout()
    plt.savefig(f'{IMG_DIR}/06_borough_analysis.png', dpi=150, bbox_inches='tight')
    plt.close()
    print("  [OK] 06_borough_analysis.png")

# ============ 图7: 相关性热力图 ============
def plot_correlation(data):
    # 使用月度统计数据做相关性分析
    df = data['monthly']
    
    fig, axes = plt.subplots(1, 2, figsize=(18, 7))
    
    for idx, company in enumerate(['yellow', 'green']):
        cdata = df[df['company'] == company]
        numeric_cols = ['trip_count', 'avg_fare', 'avg_distance', 'avg_duration', 'avg_passengers', 'avg_tip', 'avg_total']
        corr = cdata[numeric_cols].corr()
        
        title = 'Yellow' if company == 'yellow' else 'Green'
        sns.heatmap(corr, annot=True, fmt='.2f', cmap='RdYlBu_r', center=0,
                    ax=axes[idx], square=True, linewidths=0.5,
                    xticklabels=['行程数', '平均车费', '平均距离', '平均时长', '平均乘客', '平均小费', '平均总额'],
                    yticklabels=['行程数', '平均车费', '平均距离', '平均时长', '平均乘客', '平均小费', '平均总额'])
        axes[idx].set_title(f'{title} 出租车字段相关性', fontsize=14, fontweight='bold')
    
    plt.tight_layout()
    plt.savefig(f'{IMG_DIR}/07_correlation_heatmap.png', dpi=150, bbox_inches='tight')
    plt.close()
    print("  [OK] 07_correlation_heatmap.png")

# ============ 图8: K-Means聚类分析 ============
def plot_clustering(data):
    # 使用月度数据进行聚类
    df = data['monthly']
    features = ['avg_fare', 'avg_distance', 'avg_duration', 'avg_passengers', 'avg_tip']
    
    scaler = StandardScaler()
    X = scaler.fit_transform(df[features])
    
    # K-Means聚类
    kmeans = KMeans(n_clusters=3, random_state=42, n_init=10)
    df['cluster'] = kmeans.fit_predict(X)
    
    fig, axes = plt.subplots(1, 2, figsize=(16, 7))
    cluster_colors = ['#FF6B6B', '#4ECDC4', '#45B7D1']
    cluster_labels = ['聚类1 (低峰低价)', '聚类2 (高峰高价)', '聚类3 (中等水平)']
    
    # 用前两个主成分可视化
    from sklearn.decomposition import PCA
    pca = PCA(n_components=2)
    X_pca = pca.fit_transform(X)
    
    for i in range(3):
        mask = df['cluster'] == i
        axes[0].scatter(X_pca[mask, 0], X_pca[mask, 1], c=cluster_colors[i],
                       label=cluster_labels[i], s=100, alpha=0.8, edgecolors='white')
    
    axes[0].set_xlabel(f'主成分1 ({pca.explained_variance_ratio_[0]:.1%})')
    axes[0].set_ylabel(f'主成分2 ({pca.explained_variance_ratio_[1]:.1%})')
    axes[0].set_title('K-Means聚类结果 (PCA降维)', fontsize=14, fontweight='bold')
    axes[0].legend()
    axes[0].grid(True, alpha=0.3)
    
    # 聚类特征雷达图
    cluster_means = df.groupby('cluster')[features].mean()
    categories = ['平均车费', '平均距离', '平均时长', '平均乘客', '平均小费']
    
    angles = np.linspace(0, 2*np.pi, len(categories), endpoint=False).tolist()
    angles += angles[:1]
    
    ax2 = fig.add_subplot(122, polar=True)
    axes[1].set_visible(False)
    
    for i in range(3):
        values = cluster_means.iloc[i].tolist()
        values += values[:1]
        ax2.plot(angles, values, 'o-', color=cluster_colors[i], linewidth=2, label=cluster_labels[i])
        ax2.fill(angles, values, alpha=0.15, color=cluster_colors[i])
    
    ax2.set_xticks(angles[:-1])
    ax2.set_xticklabels(categories, fontsize=10)
    ax2.set_title('各聚类特征对比 (雷达图)', fontsize=14, fontweight='bold', pad=20)
    ax2.legend(loc='upper right', bbox_to_anchor=(1.3, 1.1))
    
    plt.tight_layout()
    plt.savefig(f'{IMG_DIR}/08_clustering_analysis.png', dpi=150, bbox_inches='tight')
    plt.close()
    print("  [OK] 08_clustering_analysis.png")

# ============ 图9: 预测验证 - 用前10个月预测后2个月 ============
def plot_prediction(data):
    df = data['monthly']
    
    fig, axes = plt.subplots(2, 2, figsize=(16, 12))
    
    metrics_to_predict = [
        ('trip_count', '行程数量'),
        ('avg_fare', '平均车费'),
        ('avg_distance', '平均距离'),
        ('avg_total', '平均总额')
    ]
    
    for idx, (col, label) in enumerate(metrics_to_predict):
        ax = axes[idx // 2][idx % 2]
        
        for company in ['yellow', 'green']:
            cdata = df[df['company'] == company].sort_values('month')
            color = '#FFD700' if company == 'yellow' else '#32CD32'
            label_c = 'Yellow' if company == 'yellow' else 'Green'
            
            # 前10个月训练
            train_x = cdata['month'].values[:10].reshape(-1, 1)
            train_y = cdata[col].values[:10]
            # 后2个月测试
            test_x = cdata['month'].values[10:].reshape(-1, 1)
            test_y = cdata[col].values[10:]
            
            model = LinearRegression()
            model.fit(train_x, train_y)
            pred_y = model.predict(test_x)
            
            # 全部预测
            all_x = cdata['month'].values.reshape(-1, 1)
            all_pred = model.predict(all_x)
            
            # 绘制
            ax.plot(cdata['month'], cdata[col], 'o-', color=color, label=f'{label_c} 实际', linewidth=2, markersize=6)
            ax.plot(cdata['month'], all_pred, '--', color=color, label=f'{label_c} 预测', linewidth=1.5, alpha=0.7)
            
            # 标注预测误差
            for i, (actual, pred) in enumerate(zip(test_y, pred_y)):
                month = cdata['month'].values[10 + i]
                error_pct = abs(actual - pred) / actual * 100
                ax.annotate(f'误差: {error_pct:.1f}%', xy=(month, pred),
                          fontsize=8, color='red', ha='center',
                          bbox=dict(boxstyle='round,pad=0.3', facecolor='yellow', alpha=0.7))
            
            r2 = r2_score(test_y, pred_y)
            rmse = np.sqrt(mean_squared_error(test_y, pred_y))
            ax.text(0.02, 0.98, f'{label_c}\nR²={r2:.3f}\nRMSE={rmse:.2f}',
                   transform=ax.transAxes, fontsize=9, verticalalignment='top',
                   bbox=dict(boxstyle='round', facecolor='wheat', alpha=0.5))
        
        ax.set_title(f'{label} - 线性回归预测验证', fontsize=13, fontweight='bold')
        ax.set_xlabel('月份')
        ax.set_ylabel(label)
        ax.legend(fontsize=8)
        ax.set_xticks(range(1, 13))
        ax.grid(True, alpha=0.3)
    
    plt.suptitle('数据预测推导与验证 (前10个月训练 → 后2个月验证)', fontsize=16, fontweight='bold', y=1.02)
    plt.tight_layout()
    plt.savefig(f'{IMG_DIR}/09_prediction_validation.png', dpi=150, bbox_inches='tight')
    plt.close()
    print("  [OK] 09_prediction_validation.png")

# ============ 图10: 热门路线桑基图/条形图 ============
def plot_top_routes(data):
    if 'routes' not in data:
        return
    df = data['routes']
    # 汇总全年
    route_agg = df.groupby(['PU_Zone', 'DO_Zone', 'company'])['count'].sum().reset_index()
    
    fig, axes = plt.subplots(1, 2, figsize=(18, 8))
    
    for idx, company in enumerate(['yellow', 'green']):
        cdata = route_agg[route_agg['company'] == company].nlargest(15, 'count')
        cdata['route'] = cdata['PU_Zone'].astype(str) + ' → ' + cdata['DO_Zone'].astype(str)
        cdata = cdata.sort_values('count', ascending=True)
        
        color = '#FFD700' if company == 'yellow' else '#32CD32'
        title = 'Yellow' if company == 'yellow' else 'Green'
        
        axes[idx].barh(range(len(cdata)), cdata['count'], color=color, alpha=0.8, edgecolor='gray')
        axes[idx].set_yticks(range(len(cdata)))
        axes[idx].set_yticklabels(cdata['route'], fontsize=8)
        axes[idx].set_xlabel('行程次数')
        axes[idx].set_title(f'{title} 出租车 TOP15 热门路线', fontsize=14, fontweight='bold')
    
    plt.tight_layout()
    plt.savefig(f'{IMG_DIR}/10_top_routes.png', dpi=150, bbox_inches='tight')
    plt.close()
    print("  [OK] 10_top_routes.png")

# ============ 图11: 综合偏好分析 ============
def plot_preferences(data):
    df = data['monthly']
    
    fig = plt.figure(figsize=(18, 14))
    gs = GridSpec(3, 3, figure=fig, hspace=0.4, wspace=0.3)
    
    # 1. 乘客数量分布
    ax1 = fig.add_subplot(gs[0, 0])
    for company in ['yellow', 'green']:
        cdata = df[df['company'] == company]
        color = '#FFD700' if company == 'yellow' else '#32CD32'
        label = 'Yellow' if company == 'yellow' else 'Green'
        ax1.plot(cdata['month'], cdata['avg_passengers'], 'o-', color=color, label=label, linewidth=2)
    ax1.set_title('月度平均乘客数', fontweight='bold')
    ax1.legend()
    ax1.grid(True, alpha=0.3)
    ax1.set_xticks(range(1, 13))
    
    # 2. 小费偏好
    ax2 = fig.add_subplot(gs[0, 1])
    for company in ['yellow', 'green']:
        cdata = df[df['company'] == company]
        color = '#FFD700' if company == 'yellow' else '#32CD32'
        label = 'Yellow' if company == 'yellow' else 'Green'
        ax2.plot(cdata['month'], cdata['avg_tip'], 'o-', color=color, label=label, linewidth=2)
    ax2.set_title('月度平均小费', fontweight='bold')
    ax2.legend()
    ax2.grid(True, alpha=0.3)
    ax2.set_xticks(range(1, 13))
    
    # 3. 收入趋势
    ax3 = fig.add_subplot(gs[0, 2])
    for company in ['yellow', 'green']:
        cdata = df[df['company'] == company]
        color = '#FFD700' if company == 'yellow' else '#32CD32'
        label = 'Yellow' if company == 'yellow' else 'Green'
        ax3.bar(cdata['month'] + (0.2 if company == 'yellow' else -0.2), cdata['total_revenue'],
                width=0.4, color=color, label=label, alpha=0.8)
    ax3.set_title('月度总收入', fontweight='bold')
    ax3.legend()
    ax3.grid(True, alpha=0.3, axis='y')
    ax3.set_xticks(range(1, 13))
    
    # 4. 车费vs距离散点图
    ax4 = fig.add_subplot(gs[1, 0])
    for company in ['yellow', 'green']:
        cdata = df[df['company'] == company]
        color = '#FFD700' if company == 'yellow' else '#32CD32'
        label = 'Yellow' if company == 'yellow' else 'Green'
        ax4.scatter(cdata['avg_distance'], cdata['avg_fare'], c=color, s=80, label=label, edgecolors='gray', alpha=0.8)
        for _, row in cdata.iterrows():
            ax4.annotate(f'{int(row["month"])}月', (row['avg_distance'], row['avg_fare']), fontsize=7, ha='center')
    ax4.set_xlabel('平均距离 (英里)')
    ax4.set_ylabel('平均车费 ($)')
    ax4.set_title('车费 vs 距离 散点图', fontweight='bold')
    ax4.legend()
    ax4.grid(True, alpha=0.3)
    
    # 5. 时长vs车费
    ax5 = fig.add_subplot(gs[1, 1])
    for company in ['yellow', 'green']:
        cdata = df[df['company'] == company]
        color = '#FFD700' if company == 'yellow' else '#32CD32'
        label = 'Yellow' if company == 'yellow' else 'Green'
        ax5.scatter(cdata['avg_duration'], cdata['avg_fare'], c=color, s=80, label=label, edgecolors='gray', alpha=0.8)
    ax5.set_xlabel('平均时长 (分钟)')
    ax5.set_ylabel('平均车费 ($)')
    ax5.set_title('车费 vs 时长 散点图', fontweight='bold')
    ax5.legend()
    ax5.grid(True, alpha=0.3)
    
    # 6. Yellow/Green比例
    ax6 = fig.add_subplot(gs[1, 2])
    yellow_total = df[df['company'] == 'yellow']['trip_count'].sum()
    green_total = df[df['company'] == 'green']['trip_count'].sum()
    ax6.pie([yellow_total, green_total], labels=['Yellow', 'Green'],
            colors=['#FFD700', '#32CD32'], autopct='%1.1f%%', startangle=90,
            textprops={'fontsize': 12})
    ax6.set_title('Yellow vs Green 行程占比', fontweight='bold')
    
    # 7-9. 小时模式热力图
    hourly_df = data['hourly']
    for idx, company in enumerate(['yellow', 'green']):
        ax = fig.add_subplot(gs[2, idx])
        cdata = hourly_df[hourly_df['company'] == company]
        pivot = cdata.pivot_table(values='trip_count', index='pickup_hour', columns='month', aggfunc='mean')
        title = 'Yellow' if company == 'yellow' else 'Green'
        sns.heatmap(pivot, ax=ax, cmap='YlOrRd', annot=False, fmt='.0f',
                    xticklabels=[f'{m}月' for m in range(1, 13)])
        ax.set_title(f'{title} 小时-月份行程热力图', fontweight='bold')
        ax.set_ylabel('小时')
    
    plt.suptitle('纽约出租车综合偏好分析', fontsize=18, fontweight='bold', y=1.01)
    plt.savefig(f'{IMG_DIR}/11_preferences_analysis.png', dpi=150, bbox_inches='tight')
    plt.close()
    print("  [OK] 11_preferences_analysis.png")

# ============ 图12: 箱线图对比 ============
def plot_boxplots(data):
    df = data['monthly']
    
    fig, axes = plt.subplots(2, 3, figsize=(18, 10))
    
    metrics = [
        ('trip_count', '行程数量'),
        ('avg_fare', '平均车费 ($)'),
        ('avg_distance', '平均距离 (英里)'),
        ('avg_duration', '平均时长 (分钟)'),
        ('avg_tip', '平均小费 ($)'),
        ('avg_passengers', '平均乘客数')
    ]
    
    for idx, (col, label) in enumerate(metrics):
        ax = axes[idx // 3][idx % 3]
        yellow_data = df[df['company'] == 'yellow'][col]
        green_data = df[df['company'] == 'green'][col]
        
        bp = ax.boxplot([yellow_data, green_data], labels=['Yellow', 'Green'],
                       patch_artist=True, widths=0.5)
        bp['boxes'][0].set_facecolor('#FFD700')
        bp['boxes'][1].set_facecolor('#32CD32')
        
        ax.set_title(label, fontsize=13, fontweight='bold')
        ax.grid(True, alpha=0.3)
    
    plt.suptitle('Yellow vs Green 出租车各指标箱线图对比', fontsize=16, fontweight='bold', y=1.02)
    plt.tight_layout()
    plt.savefig(f'{IMG_DIR}/12_boxplot_comparison.png', dpi=150, bbox_inches='tight')
    plt.close()
    print("  [OK] 12_boxplot_comparison.png")

if __name__ == '__main__':
    print("加载聚合数据...")
    data = load_data()
    print(f"已加载 {len(data)} 个数据文件")
    
    print("\n生成分析图表...")
    plot_missing_values(data)
    plot_monthly_trend(data)
    plot_hourly_pattern(data)
    plot_dow_pattern(data)
    plot_payment(data)
    plot_borough(data)
    plot_correlation(data)
    plot_clustering(data)
    plot_prediction(data)
    plot_top_routes(data)
    plot_preferences(data)
    plot_boxplots(data)
    
    print("\n所有图表生成完成！")
