import pandas as pd
import numpy as np
from statsmodels.tsa.statespace.sarimax import SARIMAX
import matplotlib.pyplot as plt
from datetime import datetime, timedelta

# 原始数据：2014年2月13日和14日的温度变化数据
data1 = {
    "2014-02-13T00:00:00": 66, "2014-02-13T00:20:00": 75, "2014-02-13T00:50:00": 75,
    "2014-02-13T01:00:00": 65, "2014-02-13T01:20:00": 75, "2014-02-13T01:50:00": 75,
    "2014-02-13T02:00:00": 73, "2014-02-13T02:20:00": 87, "2014-02-13T02:50:00": 87,
    "2014-02-13T03:00:00": 84, "2014-02-13T03:20:00": 87, "2014-02-13T03:50:00": 93,
    "2014-02-13T04:00:00": 87, "2014-02-13T04:20:00": 93, "2014-02-13T04:50:00": 93,
    "2014-02-13T05:00:00": 89, "2014-02-13T05:20:00": 93, "2014-02-13T05:50:00": 93,
    "2014-02-13T06:00:00": 91, "2014-02-13T06:20:00": 93, "2014-02-13T06:50:00": 93,
    "2014-02-13T07:00:00": 86, "2014-02-13T07:20:00": 93, "2014-02-13T07:50:00": 93,
    "2014-02-13T08:00:00": 88, "2014-02-13T08:20:00": 87, "2014-02-13T08:50:00": 87,
    "2014-02-13T09:00:00": 85, "2014-02-13T09:20:00": 87, "2014-02-13T09:50:00": 87,
    "2014-02-13T10:00:00": 82, "2014-02-13T10:20:00": 81, "2014-02-13T10:50:00": 81,
    "2014-02-13T11:00:00": 69, "2014-02-13T11:20:00": 76, "2014-02-13T11:50:00": 76,
    "2014-02-13T12:00:00": 66, "2014-02-13T12:20:00": 76, "2014-02-13T12:50:00": 76,
    "2014-02-13T13:00:00": 62, "2014-02-13T13:20:00": 70, "2014-02-13T13:50:00": 66,
    "2014-02-13T14:20:00": 66, "2014-02-13T14:50:00": 66, "2014-02-13T15:00:00": 56,
    "2014-02-13T15:20:00": 70, "2014-02-13T15:50:00": 66, "2014-02-13T16:00:00": 55,
    "2014-02-13T16:20:00": 66, "2014-02-13T16:50:00": 70, "2014-02-13T17:00:00": 60,
    "2014-02-13T17:20:00": 70, "2014-02-13T17:50:00": 70, "2014-02-13T18:00:00": 62,
    "2014-02-13T18:20:00": 70, "2014-02-13T18:50:00": 75, "2014-02-13T19:00:00": 67,
    "2014-02-13T19:20:00": 75, "2014-02-13T19:50:00": 75, "2014-02-13T20:20:00": 75,
    "2014-02-13T20:50:00": 81, "2014-02-13T21:00:00": 73, "2014-02-13T21:20:00": 81,
    "2014-02-13T21:50:00": 75, "2014-02-13T22:00:00": 72, "2014-02-13T22:20:00": 81,
    "2014-02-13T22:50:00": 81, "2014-02-13T23:00:00": 71, "2014-02-13T23:20:00": 81,
    "2014-02-13T23:50:00": 87
}

data2 = {"2014-02-14T00:00:00": "76", "2014-02-14T00:20:00": "81", "2014-02-14T00:50:00": "87", "2014-02-14T01:00:00": "82", "2014-02-14T01:20:00": "93", "2014-02-14T01:50:00": "93", "2014-02-14T02:00:00": "86", "2014-02-14T02:20:00": "93", "2014-02-14T02:50:00": "93", "2014-02-14T03:00:00": "84", "2014-02-14T03:20:00": "87", "2014-02-14T03:50:00": "93", "2014-02-14T04:00:00": "86", "2014-02-14T04:20:00": "93", "2014-02-14T04:50:00": "87", "2014-02-14T05:00:00": "86", "2014-02-14T05:20:00": "93", "2014-02-14T05:50:00": "93", "2014-02-14T06:00:00": "89", "2014-02-14T06:20:00": "93", "2014-02-14T06:50:00": "93", "2014-02-14T07:00:00": "91", "2014-02-14T07:20:00": "93", "2014-02-14T07:50:00": "93", "2014-02-14T08:00:00": "87", "2014-02-14T08:20:00": "93", "2014-02-14T08:50:00": "93", "2014-02-14T09:00:00": "89", "2014-02-14T09:20:00": "93", "2014-02-14T09:50:00": "87", "2014-02-14T10:00:00": "82", "2014-02-14T10:50:00": "81", "2014-02-14T11:20:00": "81", "2014-02-14T11:50:00": "87", "2014-02-14T12:00:00": "75", "2014-02-14T12:20:00": "81", "2014-02-14T12:50:00": "76", "2014-02-14T13:00:00": "72", "2014-02-14T13:20:00": "87", "2014-02-14T13:50:00": "81", "2014-02-14T14:00:00": "72", "2014-02-14T14:20:00": "81", "2014-02-14T14:50:00": "76", "2014-02-14T15:00:00": "67", "2014-02-14T15:20:00": "76", "2014-02-14T15:50:00": "76", "2014-02-14T16:00:00": "70", "2014-02-14T16:20:00": "76", "2014-02-14T16:50:00": "81", "2014-02-14T17:00:00": "67", "2014-02-14T17:20:00": "76", "2014-02-14T17:50:00": "76", "2014-02-14T18:00:00": "74", "2014-02-14T18:20:00": "81", "2014-02-14T18:50:00": "81", "2014-02-14T19:00:00": "76", "2014-02-14T19:20:00": "87", "2014-02-14T19:50:00": "81", "2014-02-14T20:00:00": "79", "2014-02-14T20:20:00": "81", "2014-02-14T20:50:00": "87", "2014-02-14T21:20:00": "87", "2014-02-14T21:50:00": "81", "2014-02-14T22:00:00": "77", "2014-02-14T22:20:00": "81", "2014-02-14T22:50:00": "87", "2014-02-14T23:00:00": "76", "2014-02-14T23:20:00": "87", "2014-02-14T23:50:00": "87"}

def fit_and_forecast_sarima(data, forecast_hours=2):
    """
    使用SARIMA模型拟合数据并预测
    :param data: 原始数据字典
    :param forecast_hours: 预测未来的小时数
    """
    # 合并数据并创建时间序列
    df = pd.Series(data)
    df.index = pd.to_datetime(df.index)
    
    # 确保时间序列均匀（按20分钟重新采样）
    df = df.resample('20T').mean().interpolate(method='linear')
    
    # 计算季节性参数
    samples_per_hour = 3  # 每小时3个样本点
    samples_per_day = 24 * samples_per_hour  # 每天72个样本点
    
    # 尝试不同的SARIMA参数组合
    models = [
        {
            'order': (2, 1, 2),
            'seasonal_order': (1, 1, 1, samples_per_day),
            'name': 'Daily Seasonal'
        },
        {
            'order': (2, 1, 2),
            'seasonal_order': (1, 1, 1, samples_per_day // 2),
            'name': 'Half-Day Seasonal'
        },
        {
            'order': (3, 1, 2),
            'seasonal_order': (1, 1, 1, samples_per_hour * 6),
            'name': '6-Hour Seasonal'
        }
    ]
    
    best_aic = float('inf')
    best_model = None
    best_results = None
    
    print("\nFitting SARIMA models:")
    for model_config in models:
        try:
            print(f"\nTrying {model_config['name']}...")
            model = SARIMAX(
                df,
                order=model_config['order'],
                seasonal_order=model_config['seasonal_order'],
                enforce_stationarity=False,
                enforce_invertibility=False
            )
            results = model.fit(disp=False)
            
            print(f"AIC: {results.aic}")
            if results.aic < best_aic:
                best_aic = results.aic
                best_model = model_config
                best_results = results
                
        except Exception as e:
            print(f"Error fitting {model_config['name']}: {str(e)}")
    
    if best_model is None:
        raise Exception("No model could be fitted successfully")
    
    print(f"\nBest model: {best_model['name']} (AIC: {best_aic:.2f})")
    
    # 预测未来时间点
    forecast_steps = forecast_hours * samples_per_hour
    forecast = best_results.get_forecast(steps=forecast_steps)
    forecast_mean = forecast.predicted_mean
    conf_int = forecast.conf_int()
    
    # 创建预测时间索引
    last_time = df.index[-1]
    forecast_index = pd.date_range(
        start=last_time + timedelta(minutes=20),
        periods=forecast_steps,
        freq='20T'
    )
    
    # 绘制结果
    plt.figure(figsize=(15, 8))
    
    # 绘制最后24小时的历史数据
    last_24h = min(len(df), samples_per_day)
    plt.plot(df.index[-last_24h:], df.values[-last_24h:], 
             label='Historical Data', color='blue')
    
    # 绘制预测值
    plt.plot(forecast_index, forecast_mean, 
             label='Forecast', color='red', linestyle='--')
    
    # 绘制置信区间
    plt.fill_between(
        forecast_index,
        conf_int.iloc[:, 0],
        conf_int.iloc[:, 1],
        color='red', alpha=0.1,
        label='95% Confidence Interval'
    )
    
    plt.title(f'SARIMA Forecast (Best Model: {best_model["name"]})')
    plt.xlabel('Time')
    plt.ylabel('Value')
    plt.legend()
    plt.grid(True)
    plt.xticks(rotation=45)
    plt.tight_layout()
    
    # 保存图片
    plt.savefig('sarima_forecast.png')
    plt.close()
    
    return {
        'forecast': forecast_mean,
        'conf_int': conf_int,
        'model': best_model,
        'results': best_results
    }

def main():
    # 合并数据
    data = {**data1, **data2}
    
    try:
        # 拟合模型并预测
        results = fit_and_forecast_sarima(data, forecast_hours=2)
        
        # 打印预测结果
        print("\nForecast for next 2 hours:")
        for time, value in zip(results['forecast'].index, results['forecast'].values):
            print(f"{time}: {value:.2f}")
        
        # 打印模型评估指标
        model_results = results['results']
        print("\nModel Diagnostics:")
        print(f"AIC: {model_results.aic:.2f}")
        print(f"BIC: {model_results.bic:.2f}")
        
    except Exception as e:
        print(f"Error: {str(e)}")

if __name__ == "__main__":
    main()
