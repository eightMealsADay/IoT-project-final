class global_var:
    receive_data = [] #列表类型，用于存储接收到的MQTT消息数据 
    topic_list = [] #列表类型，用于存储当前订阅的主题

    user_initiated_disconnect = False # 用于跟踪断开连接是否是用户主动操作的
    current_topic = None  # 当前订阅的主题

    def init():
        global receive_data
        global user_initiated_disconnect
        global topic_list
        global current_topic  # 添加这行
        
        receive_data = []
        user_initiated_disconnect = False
        topic_list = []
        current_topic = None  # 添加这行

# 在文件开头调用初始化
global_var.init()
