import json
import pandas as pd
import os
from datetime import datetime

def process_json_file(file_path, data_type):
    """处理单个JSON文件并转换为DataFrame"""
    print(f"\nProcessing {file_path}...")
    
    records = []
    
    # 读取文件
    with open(file_path, 'r') as f:
        for line in f:
            try:
                # 解析JSON对象
                data = json.loads(line.strip())
                
                # 处理每个时间点的数据
                for timestamp, value in data.items():
                    try:
                        # 解析ISO格式的时间戳
                        dt = datetime.strptime(timestamp, "%Y-%m-%dT%H:%M:%S")
                        
                        # 创建记录
                        record = {
                            'Month': dt.month,
                            'Day': dt.day,
                            'Hour': dt.hour,
                            'Minute': dt.minute,
                            data_type: float(value)
                        }
                        records.append(record)
                        
                    except Exception as e:
                        print(f"Error processing record {timestamp}: {str(e)}")
                        
            except json.JSONDecodeError as e:
                print(f"Error parsing JSON in line: {str(e)}")
                continue
    
    if not records:
        raise ValueError(f"No valid records found in {file_path}")
    
    # 创建DataFrame
    df = pd.DataFrame(records)
    
    # 按时间排序
    df = df.sort_values(by=['Month', 'Day', 'Hour', 'Minute'])
    
    return df

def main():
    # 输入和输出目录
    input_dir = 'D:\AAA桌面\IoT-final\preProcessData'
    
    # 数据类型映射
    type_mapping = {
        'humidity': 'Humidity',
        'temperature': 'Temperature',
        'pressure': 'Pressure'
    }
    
    all_dfs = []  # 存储所有数据框
    
    # 处理每个txt文件
    for filename in os.listdir(input_dir):
        if filename.endswith('.txt'):
            # 确定数据类型
            data_type = None
            for key in type_mapping:
                if key in filename.lower():
                    data_type = type_mapping[key]
                    break
            
            if data_type:
                file_path = os.path.join(input_dir, filename)
                
                try:
                    # 处理文件
                    df = process_json_file(file_path, data_type)
                    all_dfs.append(df)
                    
                    print(f"Processed {filename}")
                    print(f"Shape: {df.shape}")
                    print(f"Columns: {df.columns.tolist()}")
                    print("\nFirst few rows:")
                    print(df.head())
                    
                except Exception as e:
                    print(f"Error processing {filename}: {str(e)}")
            else:
                print(f"Could not determine data type for {filename}")
    
    # 合并所有数据框
    if all_dfs:
        final_df = pd.merge(all_dfs[0], all_dfs[1], on=['Month', 'Day', 'Hour', 'Minute'], how='outer')
        if len(all_dfs) > 2:
            final_df = pd.merge(final_df, all_dfs[2], on=['Month', 'Day', 'Hour', 'Minute'], how='outer')
        
        # 按时间排序
        final_df = final_df.sort_values(by=['Month', 'Day', 'Hour', 'Minute'])
        
        # 保存最终的CSV文件
        output_file = os.path.join(input_dir, 'historical_data.csv')
        final_df.to_csv(output_file, index=False)
        print(f"\nSaved combined data to {output_file}")
        print(f"Final shape: {final_df.shape}")
        print(f"Final columns: {final_df.columns.tolist()}")
        print("\nFirst few rows of combined data:")
        print(final_df.head())

if __name__ == "__main__":
    main()