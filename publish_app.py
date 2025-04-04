# publish_app.py
from flask import Flask, render_template, request, jsonify
import datetime
from MQTTClient import MQTTClient
import json
import time
import threading

# Mosquitto MQTT配置
broker_host = "172.20.10.4"  # Mosquitto服务器地址
broker_port = 1883  # Mosquitto服务器端口
client_id = "publisher_client"  # 发布者客户端ID
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

app = Flask(__name__)
mqtt_client = MQTTClient(broker_host, broker_port, client_id, username, password)

def on_connect(client, userdata, flags, rc):
    print(f"Debug: MQTT连接回调 - 返回码: {rc}")
    if rc == 0:
        print("Debug: MQTT连接成功")
    else:
        print(f"Debug: MQTT连接失败，错误码: {rc}")
        # rc 的含义：
        # 0: 连接成功
        # 1: 协议版本错误
        # 2: 无效的客户端标识符
        # 3: 服务器不可用
        # 4: 错误的用户名或密码
        # 5: 未授权

# 设置连接回调
mqtt_client.set_on_connect(on_connect)

# 全局变量，用于存储状态
publish_status = {
    'count': 0,
    'complete': False,
    'error': None
}

def publish_data_line(timestamp, value, topic_type):
    try:
        if topic_type not in TOPIC_MAP:
            return False, "无效的主题类型"
            
        # 构造上报数据结构
        prop_data = {
            "DetectTime": timestamp.strip('"'),  # 移除可能存在的引号
            "Value": value.strip('"')  # 移除可能存在的引号
        }
        payload = {
            "id": "123",
            "version": "1.0",
            "params": prop_data,
            "method": "thing.event.property.post"
        }
        # 上报属性
        print(f"Debug: 尝试发布到主题 {TOPIC_MAP[topic_type]}")
        print(f"Debug: 发布数据: {json.dumps(payload)}")
        rc, request_id = mqtt_client.publish(
            TOPIC_MAP[topic_type],
            json.dumps(payload)
        )
        print(f"Debug: 发布结果 - rc: {rc}, request_id: {request_id}")
        if rc != 0:
            return False, f"发布失败，错误码={rc}"
        return True, None
    except Exception as e:
        print(f"Debug: 发布异常: {str(e)}")
        return False, str(e)

# 接口
@app.route('/')
def index():
    try:
        return render_template('publish.html')
    except Exception as e:
        print(f"渲染模板错误: {e}")
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
        return jsonify({'timestamp': str(datetime.datetime.now()), 'status': 'success', 'message': '已成功断开连接。'})
    else:
        return jsonify({'timestamp': str(datetime.datetime.now()), 'status': 'already_disconnected', 'message': '已经断开连接。'})

@app.route('/publishCustom', methods=['POST'])
def publish_custom():
    if not mqtt_client.is_connected():
        return jsonify({
            'timestamp': str(datetime.datetime.now()),
            'status': 'error',
            'message': '未连接到MQTT服务器，请先建立连接。'
        })

    try:
        data = request.json.get('data', '')
        topic_type = request.json.get('topic', '')
        
        if not topic_type:
            return jsonify({
                'timestamp': str(datetime.datetime.now()),
                'status': 'error',
                'message': '请选择要发布的主题。'
            })
            
        try:
            # 解析JSON数据
            data_dict = json.loads(data)
            if not isinstance(data_dict, dict):
                return jsonify({
                    'timestamp': str(datetime.datetime.now()),
                    'status': 'error',
                    'message': '数据格式错误：输入必须是有效的JSON对象，请检查数据格式。'
                })
            
            # 按时间戳排序
            sorted_timestamps = sorted(data_dict.keys())
            success_count = 0
            
            for timestamp in sorted_timestamps:
                value = data_dict[timestamp]
                success, error = publish_data_line(timestamp, value, topic_type)
                if success:
                    success_count += 1
                else:
                    return jsonify({
                        'timestamp': str(datetime.datetime.now()),
                        'status': 'error',
                        'message': f'发布失败：正在处理第 {success_count + 1} 个数据点时出错。错误信息：{error}'
                    })
                
                time.sleep(0.5)
            
            return jsonify({
                'timestamp': str(datetime.datetime.now()),
                'status': 'complete',
                'message': f'发布完成：成功发布 {success_count} 条数据到 {TOPIC_MAP[topic_type]} 主题。'
            })
            
        except json.JSONDecodeError:
            return jsonify({
                'timestamp': str(datetime.datetime.now()),
                'status': 'error',
                'message': '数据格式错误：无效的JSON格式，请检查输入数据的格式是否正确。'
            })
        
    except Exception as e:
        return jsonify({
            'timestamp': str(datetime.datetime.now()),
            'status': 'error',
            'message': f'发生错误：{str(e)}。请检查数据格式和网络连接。'
        })

if __name__ == '__main__':
    app.run(debug=True, port=5001)
