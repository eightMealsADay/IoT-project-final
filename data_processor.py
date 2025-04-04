import numpy as np
from sklearn.preprocessing import PolynomialFeatures, StandardScaler
from sklearn.pipeline import Pipeline
from sklearn.svm import SVR
from sklearn.linear_model import Ridge
from datetime import datetime, timedelta
import pandas as pd


class DataFitter:
    def __init__(self, max_data_points=15, topic_type=None):
        """
        初始化拟合器
        :param max_data_points: 开始拟合所需的最小数据点数量
        :param topic_type: 当前订阅的主题类型 ('temperature', 'humidity', 'pressure')
        """
        print("Debug - DataFitter initialized with max_points:", max_data_points)
        self.max_data_points = max_data_points
        self.topic_type = topic_type
        self.is_fitted = False
        self.fitted_times = []
        self.fitted_values = []
        self.start_time = None
        self.dataset = []
        
        # 创建模型管道
        self.model = Pipeline([
            ('scaler', StandardScaler()),
            ('poly', PolynomialFeatures(degree=5)),
            ('svr', SVR(kernel='rbf', C=100, gamma='auto'))
        ])

    def add_data(self, time_str, value_str):
        """添加新的数据点并在达到条件时触发拟合"""
        try:
            print("\nDebug - Adding new data point:")
            print(f"Debug - Time: {time_str}")
            print(f"Debug - Value: {value_str}")
            
            # 解析时间
            time_str = time_str.replace(" T ", "T")
            dt = datetime.strptime(time_str, "%Y-%m-%dT%H:%M:%S")
            value = float(value_str)
            
            if not self.start_time:
                self.start_time = dt
            
            # 添加到数据集
            self.dataset.append((dt, value))
            print(f"Debug - Successfully added to dataset")
            print(f"Debug - Current dataset size: {len(self.dataset)}")

            # 当收集到足够的数据点时，进行拟合
            if len(self.dataset) >= self.max_data_points:
                print(f"Debug - Prepared {len(self.dataset)} points for fitting")
                self.fit_model()
            else:
                print(f"Debug - Waiting for more points ({len(self.dataset)}/{self.max_data_points})")
            
        except Exception as e:
            print(f"Adding data error: {str(e)}")
            import traceback
            print(traceback.format_exc())

    def fit_model(self):
        """使用机器学习模型拟合数据并从历史数据生成预测"""
        try:
            print("\nDebug - Starting model fitting")
            
            # 准备数据
            sorted_data = sorted(self.dataset, key=lambda x: x[0])
            times = [dt for dt, _ in sorted_data]
            values = [float(val) for _, val in sorted_data]
            
            # 计算总时长和预测时长
            total_minutes = (times[-1] - times[0]).total_seconds() / 60
            predict_minutes = total_minutes / 6  # 预测1/24的时长
            
            # 将时间转换为相对分钟数（特征）
            minutes = np.array([(dt - self.start_time).total_seconds() / 60 for dt in times])
            X = minutes.reshape(-1, 1)
            y = np.array(values)
            
            # 拟合当前数据
            self.model.fit(X, y)
            fitted_values = self.model.predict(X)
            
            # 生成预测时间点
            last_time = times[-1]
            future_times = []
            future_values = []
            
            # 计算预测点数量
            num_predict_points = int(predict_minutes / 60) + 1  # 改为60分钟间隔
            
            # 根据主题类型选择对应的数据列
            value_column = {
                'temperature': 'Temperature',
                'humidity': 'Humidity',
                'pressure': 'Pressure'
            }.get(self.topic_type)
            
            if not value_column:
                raise ValueError(f"Unsupported topic type: {self.topic_type}")
                
            print(f"Debug - Using data from column: {value_column}")
            
            try:
                # 读取历史数据文件
                data = pd.read_csv('preProcessData/historical_data.csv')
                print("\nDebug - Historical data loaded:")
                print(f"Debug - Columns: {data.columns.tolist()}")
                
                # 不需要处理列名分割了，因为CSV格式已经正确
                
                # 转换数据类型
                for col in ['Month', 'Day', 'Hour', 'Minute']:
                    data[col] = pd.to_numeric(data[col], errors='coerce')
                
                # 确保数值列是浮点数类型
                value_columns = ['Humidity', 'Pressure', 'Temperature']
                for col in value_columns:
                    if col in data.columns:
                        data[col] = pd.to_numeric(data[col], errors='coerce')
                
                print("\nDebug - Data types:")
                print(data.dtypes)
                print("\nDebug - First few rows:")
                print(data.head())
                
                # 确保列名正确
                required_columns = ['Month', 'Day', 'Hour', 'Minute']
                if not all(col in data.columns for col in required_columns):
                    print("Debug - Required columns not found in historical data")
                    print(f"Debug - Expected: {required_columns}")
                    print(f"Debug - Found: {data.columns.tolist()}")
                    raise Exception("Missing required columns in historical data")
                
                # 第一个预测点使用拟合的最后一个值
                future_times.append(last_time)  # 从最后一个实际时间点开始
                future_values.append(fitted_values[-1])  # 使用拟合的最后一个值，而不是实际值
                
                # 预测后续点
                for i in range(1, num_predict_points):  # 从1开始，因为第0个点已经设置
                    future_dt = last_time + timedelta(minutes=i*60)
                    future_times.append(future_dt)
                    
                    # 从future_dt提取月、日、小时
                    month = future_dt.month
                    day = future_dt.day
                    hour = future_dt.hour
                    
                    print(f"\nDebug - Predicting for time point {i+1}/{num_predict_points}:")
                    print(f"Debug - Future datetime: {future_dt}")
                    print(f"Debug - Looking for M:{month} D:{day} H:{hour}")
                    print(f"Debug - Last actual value: {values[-1]}")
                    
                    try:
                        # 在历史数据中找到最接近的时间点的数据
                        mask = (data['Month'] == month) & (data['Day'] == day) & (data['Hour'] == hour)
                        matching_rows = data[mask]
                        print(f"Debug - Found {len(matching_rows)} matching records")
                        
                        if len(matching_rows) > 0:
                            if value_column in data.columns:
                                base_value = float(matching_rows[value_column].iloc[0])
                                print(f"Debug - Found historical {value_column.lower()}: {base_value}")
                            else:
                                print(f"Debug - Column {value_column} not found in data")
                                base_value = values[-1]
                        else:
                            base_value = values[-1]
                            print(f"Debug - No matching record found, using last actual value: {base_value}")
                        
                        try:
                            # 根据主题类型设置波动范围
                            if self.topic_type == 'pressure':
                                variation = 0.001  # 压力波动范围 ±0.1%
                            else:  # 温度和湿度
                                variation = 0.02   # 温度和湿度波动范围 ±2%
                            
                            # 添加随机波动
                            random_factor = 1 + np.random.uniform(-variation, variation)
                            predicted_value = float(base_value) * random_factor
                            print(f"Debug - Topic type: {self.topic_type}")
                            print(f"Debug - Variation range: ±{variation*100}%")
                            print(f"Debug - Base value: {base_value} (type: {type(base_value)})")
                            print(f"Debug - Random factor: {random_factor:.4f}")
                            print(f"Debug - Final predicted value: {predicted_value:.2f}")
                            
                            future_values.append(predicted_value)
                        except Exception as e:
                            print(f"Debug - Error in value calculation: {str(e)}")
                            print(f"Debug - Base value: {base_value} (type: {type(base_value)})")
                            # 使用最后一个实际值作为后备，使用相同的波动逻辑
                            variation = 0.001 if self.topic_type == 'pressure' else 0.02
                            predicted_value = values[-1] * (1 + np.random.uniform(-variation, variation))
                            future_values.append(predicted_value)
                        
                    except Exception as e:
                        print(f"Debug - Error processing prediction point: {str(e)}")
                        base_value = values[-1]
                        random_factor = 1 + np.random.uniform(-0.04, 0.04)
                        predicted_value = base_value * random_factor
                        future_values.append(predicted_value)
            
            except Exception as e:
                print(f"Error reading historical data: {str(e)}")
                print("Debug - Falling back to simple trend prediction")
                # 如果无法读取历史数据，使用简单的趋势预测
                for i in range(num_predict_points):
                    future_dt = last_time + timedelta(minutes=(i)*60)
                    future_times.append(future_dt)
                    base_value = values[-1]
                    random_factor = 1 + np.random.uniform(-0.04, 0.04)
                    future_values.append(base_value * random_factor)
            
            # 合并历史拟合值和预测值
            all_times = times + future_times
            all_values = np.concatenate([fitted_values, future_values])
            
            # 存储结果
            self.fitted_times = [t.strftime("%Y-%m-%dT%H:%M:%S") for t in all_times]
            self.fitted_values = all_values.tolist()
            self.is_fitted = True
            
            print("Debug - Generated values:", len(self.fitted_times))
            print("Debug - Historical points:", len(times))
            print("Debug - Prediction points:", len(future_times))
            print("Debug - Time range:", self.fitted_times[0], "to", self.fitted_times[-1])
            print("Debug - First few original values:", values[:5])
            print("Debug - First few fitted values:", fitted_values[:5])
            print("Debug - First few predictions:", future_values[:5])
            
            # 计算拟合误差
            mse = np.mean((y - fitted_values) ** 2)
            rmse = np.sqrt(mse)
            print(f"Debug - Fitting RMSE: {rmse:.2f}")
            
        except Exception as e:
            print(f"Fitting model error: {str(e)}")
            import traceback
            print(traceback.format_exc())

    def get_fitted_data(self):
        """获取拟合结果"""
        print("\nDebug - Getting fitted data")
        print(f"Debug - Is fitted: {self.is_fitted}")
        print(f"Debug - Dataset size: {len(self.dataset)}")
        if self.is_fitted:
            # 分界点是原始数据的长度
            split_index = len(self.dataset)
            return {
                'times': self.fitted_times,
                'values': self.fitted_values,
                'original_data': [(dt.strftime("%Y-%m-%dT%H:%M:%S"), val) for dt, val in self.dataset],
                'prediction_start': split_index
            }
            
        print("Debug - No fitted data available")
        return None

    def clear_data(self):
        """清除所有数据并重置拟合器状态"""
        print("\nDebug - Clearing all data")
        self.dataset = []
        self.is_fitted = False
        self.fitted_times = []
        self.fitted_values = []
        self.start_time = None
        # 重新初始化模型
        self.model = Pipeline([
            ('scaler', StandardScaler()),
            ('poly', PolynomialFeatures(degree=3)),
            ('svr', SVR(kernel='rbf', C=100, gamma='auto'))
        ])
        print("Debug - All data cleared")
