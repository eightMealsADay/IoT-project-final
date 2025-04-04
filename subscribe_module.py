# encoding=utf-8
# subscribe_module.py
import json
import time
from datetime import datetime
import global_var as gv
from MQTTClient import MQTTClient
from data_processor import DataFitter
from shared_data import message_queue

# MQTT客户端实例
mqtt_client = None
data_fitter = DataFitter(max_data_points=15)

def on_message(client, userdata, msg):
    """处理接收到的MQTT消息"""
    try:
        print(f"\nDebug - Received message:")
        print(f"Debug - Topic: {msg.topic}")
        payload = json.loads(msg.payload.decode())
        print(f"Debug - Raw payload: {payload}")
        transform_data(payload, msg.topic)
    except json.JSONDecodeError:
        print("Error decoding message payload")
    except Exception as e:
        print(f"Error processing message: {e}")
        import traceback
        print(traceback.format_exc())

def disconnect_mqtt():
    global mqtt_client
    try:
        if mqtt_client and mqtt_client.is_connected():
            mqtt_client.disconnect()
            gv.global_var.user_initiated_disconnect = True
            print("MQTT connection is disconnected.")
    except Exception as e:
        print('Error while trying to disconnect:', e)

def connect_mqtt(broker_host, broker_port, client_id, username, password):
    global mqtt_client
    try:
        print(f"Debug: Attempting to connect with parameters:")
        print(f"Debug: Host: {broker_host}")
        print(f"Debug: Port: {broker_port}")
        print(f"Debug: Client ID: {client_id}")
        print(f"Debug: Username: {username}")
        
        mqtt_client = MQTTClient(broker_host, broker_port, client_id, username, password)
        
        # 设置连接回调
        def on_connect(client, userdata, flags, rc):
            print(f"Debug: MQTT Connection result code: {rc}")
            connection_codes = {
                0: "Connection successful",
                1: "Connection refused - incorrect protocol version",
                2: "Connection refused - invalid client identifier",
                3: "Connection refused - server unavailable",
                4: "Connection refused - bad username or password",
                5: "Connection refused - not authorised"
            }
            print(f"Debug: Connection status: {connection_codes.get(rc, 'Unknown error')}")
            if rc == 0:
                mqtt_client.connected = True
            else:
                raise Exception(connection_codes.get(rc, f"Connection failed with code {rc}"))

        mqtt_client.set_on_connect(on_connect)
        mqtt_client.set_on_message(on_message)
        
        # 连接到服务器
        print("Debug: Attempting to connect to MQTT broker...")
        if mqtt_client.connect():
            print("Debug: Connection successful")
            return True
        else:
            raise Exception("Failed to connect to MQTT broker")
            
    except Exception as e:
        print(f'Debug: Connection failed with error: {str(e)}')
        raise e

def transform_data(payload, topic):
    try:
        print("\nDebug - Transform data called")
        print(f"Debug - Payload: {payload}")
        print(f"Debug - Topic: {topic}")
        
        # 将ISO格式时间转换为时间戳
        time_str = payload['params']['DetectTime']
        dt = datetime.strptime(time_str, "%Y-%m-%dT%H:%M:%S")
        timestamp = int(dt.timestamp() * 1000)
        
        # 从主题中提取类型
        topic_type = None
        if 'temperature' in topic.lower():
            topic_type = 'temperature'
        elif 'humidity' in topic.lower():
            topic_type = 'humidity'
        elif 'pressure' in topic.lower():
            topic_type = 'pressure'
            
        print(f"Debug - Detected topic type: {topic_type}")
        
        # 创建或更新 DataFitter
        global data_fitter
        if data_fitter is None or data_fitter.topic_type != topic_type:
            data_fitter = DataFitter(max_data_points=15, topic_type=topic_type)
            print(f"Debug - Created new DataFitter for {topic_type}")
            
        # 检查是否有 'Value' 字段
        if 'Value' in payload['params']:
            value = float(payload['params']['Value'])
            # 创建消息对象
            message = {
                'timestamp': time_str,
                'raw_timestamp': timestamp,
                'value': f"{value:.2f}",  # 格式化显示值
                'raw_value': value,
                'formatted_time': dt.strftime("%Y-%m-%d %H:%M:%S")  # 添加格式化时间
            }
            # 添加到消息队列
            message_queue.append(message)
            print(f"Debug - Added message to queue: {message}")
            
            # 添加数据到拟合器
            data_fitter.add_data(time_str, str(value))
            
        print(f"Debug - Current queue size: {len(message_queue)}")
        
    except Exception as e:
        print(f"Error transforming data: {str(e)}")
        import traceback
        print(traceback.format_exc())

def timestamp_to_time(timestamp):
    if isinstance(timestamp, float):
        dt_obj = datetime.fromtimestamp(timestamp / 1000.0)
    else:
        dt_obj = datetime.fromtimestamp(int(timestamp) / 1000)
    return dt_obj.strftime('%Y-%m-%dT%H:%M:%S')

def format_topicData(prop_data):
    formatted_ans = "time:" + timestamp_to_time(prop_data["time"]) + " "
    formatted_ans += " ".join([f"{k}:{v}" for k, v in prop_data.items() if k != "printed" and k != "time"]) + "\n"
    return formatted_ans

def get_fitted_data():
    return data_fitter.get_fitted_data()

def clear_data():
    """清除所有数据"""
    message_queue.clear()  # 清除消息队列
    data_fitter.clear_data()  # 清除拟合数据
    # 不要影响 MQTT 连接状态


