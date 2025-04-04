# subscribe_app.py
from flask import Flask, render_template, request, jsonify
import datetime
from MQTTClient import MQTTClient
import json
import time
import threading
import global_var
from shared_data import message_queue  # 从新模块导入
import subscribe_module

# Mosquitto MQTT配置
broker_host = "172.20.10.4"  # Mosquitto服务器地址
broker_port = 1883  # Mosquitto服务器端口
client_id = "subscriber_client"  # 订阅者客户端ID
username = "admin"  # Mosquitto用户名
password = "1234"  # Mosquitto密码

print(f"Debug: MQTT配置信息:")
print(f"Debug: 服务器地址: {broker_host}")
print(f"Debug: 端口: {broker_port}")
print(f"Debug: 客户端ID: {client_id}")
print(f"Debug: 用户名: {username}")

# MQTT主题映射
TOPIC_MAP = {
    'temperature': 'THP/temperature',  # 温度主题
    'humidity': 'THP/humidity',        # 湿度主题
    'pressure': 'THP/pressure'         # 压力主题
}

# 主题单位映射
UNIT_MAP = {
    'temperature': '°C',  # 温度单位
    'humidity': '%',      # 湿度单位
    'pressure': 'hPa'     # 压力单位
}

app = Flask(__name__)
mqtt_client = MQTTClient(broker_host, broker_port, client_id, username, password)

def clean_value(value_str):
    """清理数值字符串，移除引号和多余的字符"""
    try:
        # 如果是字符串类型，移除引号
        if isinstance(value_str, str):
            value_str = value_str.strip().strip('"')
        # 转换为浮点数
        return float(value_str)
    except Exception as e:
        print(f"Debug: 数值清理错误: {str(e)}")
        return None

def format_datetime(timestamp_str):
    """将ISO格式的时间字符串转换为更易读的格式"""
    try:
        # 清理时间戳字符串，移除引号和多余的字符
        timestamp_str = timestamp_str.strip().strip('"')
        # 确保时间戳格式完整
        if not timestamp_str.endswith('Z'):  # 如果不是UTC格式
            timestamp_str = timestamp_str.rstrip('Z')  # 移除可能存在的Z后缀
        # 解析ISO格式的时间字符串
        dt = datetime.datetime.strptime(timestamp_str, "%Y-%m-%dT%H:%M:%S")
        # 转换为易读格式
        return dt.strftime("%Y-%m-%d %H:%M:%S")
    except Exception as e:
        print(f"Debug: 时间格式化错误: {str(e)}")
        return timestamp_str

def on_connect(client, userdata, flags, rc):
    print(f"Debug: MQTT连接回调 - 返回���: {rc}")
    if rc == 0:
        print("Debug: MQTT连接成功")
    else:
        print(f"Debug: MQTT连接失败，错误码: {rc}")

# 设置回调
mqtt_client.set_on_connect(on_connect)
mqtt_client.set_on_message(subscribe_module.on_message)

@app.route('/')
def index():
    try:
        return render_template('subscribe.html')
    except Exception as e:
        print(f"Debug: 渲染模板错误: {e}")
        return str(e)

@app.route('/connect', methods=['POST'])
def connect():
    print("Debug: 收到连接请求")
    if not mqtt_client.is_connected():
        print("Debug: 尝试连接到MQTT服务器")
        success = mqtt_client.connect()
        if success:
            print("Debug: MQTT连接成功")
            return jsonify({
                'timestamp': str(datetime.datetime.now()),
                'status': 'success',
                'message': '成功连接到MQTT服务器。'
            })
        else:
            print("Debug: MQTT连接失败")
            return jsonify({
                'timestamp': str(datetime.datetime.now()),
                'status': 'error',
                'message': 'MQTT服务器连接失败，请检查服务器配置和网络连接。'
            })
    else:
        print("Debug: 已经连接到MQTT服务器")
        return jsonify({
            'timestamp': str(datetime.datetime.now()),
            'status': 'already_connected',
            'message': '已经连接到服务器。'
        })

@app.route('/disconnect', methods=['POST'])
def disconnect():
    if mqtt_client.is_connected():
        mqtt_client.disconnect()
        return jsonify({
            'timestamp': str(datetime.datetime.now()),
            'status': 'success',
            'message': '已成功断开连接。'
        })
    else:
        return jsonify({
            'timestamp': str(datetime.datetime.now()),
            'status': 'already_disconnected',
            'message': '已经断开连接。'
        })

@app.route('/subscribe', methods=['POST'])
def subscribe():
    if not mqtt_client.is_connected():
        return jsonify({
            'timestamp': str(datetime.datetime.now()),
            'status': 'error',
            'message': '未连接到MQTT服务器，请先连接。'
        })

    try:
        topic_type = request.json.get('topic', '')
        print(f"\nDebug - Subscribe request:")
        print(f"Debug - Topic type: {topic_type}")
        
        if not topic_type or topic_type not in TOPIC_MAP:
            return jsonify({
                'timestamp': str(datetime.datetime.now()),
                'status': 'error',
                'message': '无效的��题。'
            })

        # 如果之前订阅了其他主题，先取消订阅
        if global_var.global_var.current_topic:
            print(f"Debug - Unsubscribing from previous topic: {global_var.global_var.current_topic}")
            mqtt_client.unsubscribe(TOPIC_MAP[global_var.global_var.current_topic])
            message_queue.clear()
            subscribe_module.clear_data()

        # 订阅新主题
        mqtt_client.subscribe(TOPIC_MAP[topic_type])
        
        # 更新全局变量
        global_var.global_var.current_topic = topic_type
        global_var.global_var.topic_list = [topic_type]
        
        print(f"Debug - Updated global variables:")
        print(f"Debug - Current topic: {global_var.global_var.current_topic}")
        print(f"Debug - Topic list: {global_var.global_var.topic_list}")

        return jsonify({
            'timestamp': str(datetime.datetime.now()),
            'status': 'success',
            'message': f'成功订阅主题: {TOPIC_MAP[topic_type]}'
        })

    except Exception as e:
        print(f"订阅错误: {str(e)}")
        import traceback
        print(traceback.format_exc())
        return jsonify({
            'timestamp': str(datetime.datetime.now()),
            'status': 'error',
            'message': f'订阅失败: {str(e)}'
        })

@app.route('/messages', methods=['GET'])
def get_messages():
    """获取新消息"""
    messages = list(message_queue)
    print(f"Debug - Sending messages: {len(messages)} messages")  # 添加调试输出
    
    # 按时间戳排序
    messages.sort(key=lambda x: x['raw_timestamp'])
    
    # 不要清除消息队列，让数据积累
    # message_queue.clear()  # 注释掉这行
    
    return jsonify({
        'messages': messages
    })

# 添加新的路由用于清除消息
@app.route('/clear_messages', methods=['POST'])
def clear_messages():
    """清除消息队列"""
    message_queue.clear()
    subscribe_module.clear_data()
    return jsonify({
        'status': 'success',
        'message': 'Messages cleared'
    })

@app.route('/get_fitted_data')
def get_fitted_data():
    """获取拟合数据"""
    fitted_data = subscribe_module.get_fitted_data()
    print("Debug - Fitted Data:", fitted_data)  # 添加调试日志
    return jsonify(fitted_data if fitted_data else {'times': [], 'values': []})

if __name__ == '__main__':
    app.run(debug=True, port=5002)  # 使用不同的端口，避免与发布端冲突
