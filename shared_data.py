from collections import deque

# 共享数据
message_queue = deque(maxlen=1000)  # 最多存储1000条消息 