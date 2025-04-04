# MQTT 温湿度压力监控系统

一个基于 MQTT 协议的实时数据监控系统，支持温度、湿度和压力数据的发布和订阅，并提供数据可视化和预测功能。

## 功能特点

- 实时数据发布与订阅
- 数据可视化展示
- 历史数据拟合
- 趋势预测
- 支持多种数据类型（温度、湿度、压力）
- 实时日志显示

## 系统要求

- Python 3.8+
- MQTT Broker (如 Mosquitto)
- 现代浏览器（支持 HTML5）

## 安装步骤

1. 创建并激活虚拟环境：
```bash
conda env create -f environment.yml
conda activate THPSys
```

2. 配置 MQTT Broker：
- 安装 Mosquitto
- 配置用户名和密码
- 确保 Broker 在指定端口运行
- 学习链接：https://www.bilibili.com/video/BV13a4y1W7Kw/?spm_id_from=333.1387.favlist.content.click&vd_source=5e8b0c370ec2cd4cb1cd3c5199b54517

## 使用说明

### 启动系统

1. 启动发布端：
```bash
python publish_app.py
```

2. 启动订阅端：
```bash
python subscribe_app.py
```


### 发布数据

1. 在发布端界面：
   - 连接到MQTT服务器
   - 选择要发布的数据类型（温度/湿度/压力）
   - 输入JSON格式的数据
   - 点击发布按钮

数据格式示例：
```json
{
  "2014-02-13T00:00:00": "4",
  "2014-02-13T00:20:00": "4.0",
  "2014-02-13T00:50:00": "4.0",
  "2014-02-13T01:00:00": "4"
}
```

### 订阅数据

1. 在订阅端界面：
   - 连接到MQTT服务器
   - 选择要订阅的数据类型
   - 点击订阅按钮
   - 查看实时数据和图表

## 项目结构

```
THPSys/
├── publish_app.py      # 发布端应用 (运行时只需要运行这两个app)
├── subscribe_app.py    # 订阅端应用 (运行时只需要运行这两个app)
├── subscribe_module.py    # 订阅端函数
├── sortData.py    # 预处理数据脚本，把原文件无序的时间排好序（数据已经排好序，这个无需运行）
├── MQTTClient.py      # MQTT客户端封装
├── data_processor.py  # 数据处理模块
├── global_var.py      # 全局变量
├── shared_data.py     # 共享数据
├── templates/         # 前端模板
│   ├── publish.html   # 发布端界面
│   └── subscribe.html # 订阅端界面
└── environment.yml    # 环境配置文件
```

## 主要功能模块

- **发布模块**：负责数据发布，支持批量数据上传
- **订阅模块**：接收实时数据，支持数据可视化
- **数据处理**：实现数据拟合和预测
- **可视化**：使用 Plotly.js 实现数据图表展示

## 注意事项

1. 确保 MQTT Broker 正确配置并运行
2. 检查网络连接和端口设置
3. 数据格式必须符合规范
4. 建议使用现代浏览器访问Web界面

## 常见问题

1. 连接失败
   - 检查 Broker 地址和端口
   - 验证用户名和密码

2. 数据不显示
   - 确认已订阅正确的主题
   - 检查数据格式是否正确

3. 图表不更新
   - 检查网络连接
   - 确认数据流正常

## 维护者




