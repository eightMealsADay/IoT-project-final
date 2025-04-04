# sortData.py
from datetime import datetime
import json
import os


def sort_daily_data(input_file, output_file):
    """
    读取并排序数据，按天分组后对每天内的数据进行时间排序
    """
    try:
        # 读取数据
        daily_data = {}  # 用于存储按天分组的数据

        with open(input_file, 'r', encoding='utf-8') as f:
            for line in f:
                data_dict = json.loads(line.strip())
                for time_str, value in data_dict.items():
                    # 解析时间
                    dt = datetime.strptime(time_str, '%Y-%m-%dT%H:%M:%S')
                    day_key = dt.strftime('%Y-%m-%d')

                    # 按天分组
                    if day_key not in daily_data:
                        daily_data[day_key] = []

                    daily_data[day_key].append({
                        'timestamp': time_str,
                        'value': value,
                        'datetime': dt
                    })

        # 对每天的数据进行排序
        for day in daily_data:
            daily_data[day].sort(key=lambda x: x['datetime'])

        # 写入排序后的数据
        with open(output_file, 'w', encoding='utf-8') as f:
            for day in sorted(daily_data.keys()):
                day_dict = {}
                for entry in daily_data[day]:
                    day_dict[entry['timestamp']] = entry['value']
                f.write(json.dumps(day_dict) + '\n')

        print(f"Successfully sorted data from {input_file} to {output_file}")

    except Exception as e:
        print(f"Error processing file {input_file}: {str(e)}")


def process_data_folder(input_folder, output_folder):
    """
    处理文件夹中的所有txt文件
    """
    # 创建输出文件夹（如果不存在）
    if not os.path.exists(output_folder):
        os.makedirs(output_folder)

    # 处理每个txt文件
    for filename in os.listdir(input_folder):
        if filename.endswith('.txt'):
            input_path = os.path.join(input_folder, filename)
            output_path = os.path.join(output_folder, f'sorted_{filename}')
            print(f"Processing {filename}...")
            sort_daily_data(input_path, output_path)


# 使用示例
if __name__ == "__main__":
    input_folder = "originalData"  # 输入文件夹路径
    output_folder = "preProcessData"  # 输出文件夹路径
    process_data_folder(input_folder, output_folder)