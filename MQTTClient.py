import paho.mqtt.client as mqtt
import json
import random
import time


class MQTTClient:
    def __init__(self, broker_host, broker_port, client_id, username=None, password=None):
        print(f"Debug: 初始化MQTT客户端")
        print(f"Debug: broker_host={broker_host}, broker_port={broker_port}")
        print(f"Debug: client_id={client_id}, username={username}")
        
        # 创建 MQTT 客户端
        self.client = mqtt.Client(client_id)

        # 如果需要用户名和密码进行认证，可以设置
        if username and password:
            print("Debug: 设置用户名和密码")
            self.client.username_pw_set(username, password)

        # 设置连接信息
        self.broker_host = broker_host
        self.broker_port = broker_port
        self.client_id = client_id

        self.connected = False
        
        # 设置回调函数
        self.client.on_connect = self.on_connect
        self.client.on_disconnect = self.on_disconnect
        self.client.on_publish = self.on_publish
        self.client.on_message = self.on_message

    def on_connect(self, client, userdata, flags, rc):
        print(f"Debug: MQTT连接回调 - rc={rc}, flags={flags}")
        if rc == 0:
            print("Debug: MQTT连接成功")
            self.connected = True
        else:
            error_messages = {
                1: "协议版本错误",
                2: "无效的客户端标识符",
                3: "服务器不可用",
                4: "用户名或密码错误",
                5: "未授权"
            }
            error_msg = error_messages.get(rc, "未知错误")
            print(f"Debug: MQTT连接失败 - {error_msg} (rc={rc})")
            self.connected = False

    def set_on_connect(self, callback):
        self._user_on_connect = callback
        def wrapped_callback(client, userdata, flags, rc):
            self.on_connect(client, userdata, flags, rc)  # 先调用内部回调
            callback(client, userdata, flags, rc)  # 再调用用户回调
        self.client.on_connect = wrapped_callback

    def set_on_message(self, callback):
        self.client.on_message = callback

    def on_disconnect(self, client, userdata, rc):
        self.connected = False
        print(f"Debug: MQTT断开连接 (rc={rc})")

    def on_publish(self, client, userdata, mid):
        print(f"Debug: 消息已发布 (mid={mid})")

    def on_message(self, client, userdata, msg):
        print(f"Debug: 收到消息 (topic={msg.topic}, payload={msg.payload})")

    def connect(self):
        try:
            print(f"Debug: 正在连接到 {self.broker_host}:{self.broker_port}")
            # 异步连接
            self.client.connect(self.broker_host, self.broker_port, 60)
            # 启动客户端循环，处理消息
            self.client.loop_start()
            
            # 等待连接完成，最多等待5秒
            timeout = 5
            while timeout > 0 and not self.connected:
                time.sleep(1)
                timeout -= 1
                print(f"Debug: 等待连接... 剩余 {timeout} 秒")
            
            if not self.connected:
                print("Debug: 连接超时")
                self.client.loop_stop()
                return False
                
            print("Debug: 连接成功")
            return True
            
        except Exception as e:
            print(f"Debug: 连接错误: {str(e)}")
            self.client.loop_stop()
            return False

    def disconnect(self):
        print("Debug: 正在断开MQTT连接...")
        self.client.disconnect()
        self.client.loop_stop()  # 停止客户端循环

    def publish(self, topic, message):
        if not self.connected:
            print("Debug: 无法发布 - 未连接")
            return mqtt.MQTT_ERR_NO_CONN, None
        # 发布消息
        print(f"Debug: 正在发布消息到主题 {topic}")
        print(f"Debug: 消息内容: {message}")
        result, mid = self.client.publish(topic, message)
        print(f"Debug: 发布结果 - result={result}, mid={mid}")
        return result, mid

    def subscribe(self, topic):
        # 订阅主题
        self.client.subscribe(topic)
        print(f"Debug: 已订阅主题: {topic}")

    def unsubscribe(self, topic):
        # 取消订阅主题
        self.client.unsubscribe(topic)
        print(f"Debug: 已取消订阅主题: {topic}")

    def is_connected(self):
        return self.connected

    # 上报随机数据
    def post_random_data(self, topic):
        prop_data = {
            "CurrentTemperature": random.randint(-10, 40),
            "CurrentHumidity": random.randint(0, 100),
            "CurrentPressure": random.randint(900, 1100),
            "DetectTime": str(int(round(time.time() * 1000)))
        }
        payload = {
            "id": "123",
            "version": "1.0",
            "params": prop_data,
            "method": "thing.event.property.post"
        }
        result, mid = self.publish(topic, payload)
        if result == mqtt.MQTT_ERR_SUCCESS:
            print(f"Debug: 属性发布成功: {result}, message id: {mid}")
        else:
            print(f"Debug: 属性发布失败, result: {result}")


# 测试：如何使用该类
if __name__ == "__main__":
    # 使用你的用户名和密码创建 MQTT 客户端实例
    mqtt_client = MQTTClient(
        broker_host="172.20.10.4",
        broker_port=1883,
        client_id="client_01",
        username="admin",  # 替换为你的用户名
        password="1234"  # 替换为你的密码
    )

    if mqtt_client.connect():
        # 订阅某个主题
        mqtt_client.subscribe("test/topic")
        mqtt_client.post_random_data("test/topic")

        time.sleep(5)  # 等待消息处理
        mqtt_client.disconnect()
    else:
        print("MQTT connection failed.")
