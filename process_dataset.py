import os
import json
import glob
from tqdm import tqdm
from src.inkml_utils import inkml2img, extract_label_from_inkml

# --- 配置路径 ---
# 获取当前脚本所在目录的绝对路径
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
# 输入数据文件夹
INPUT_DIR = os.path.join(BASE_DIR, 'mathwriting-2024-excerpt')
# 输出数据文件夹
OUTPUT_DIR = os.path.join(BASE_DIR, 'mathwriting-2024-png')


def process_split(split_name):
    """
    处理单个数据集分区 (train, test, 或 valid)。
    
    Args:
        split_name (str): 分区的名称 ('train', 'test', 'valid')。
    """
    print(f"\n--- 开始处理 {split_name} 数据集 ---")
    
    # 定义输入和输出路径
    input_split_dir = os.path.join(INPUT_DIR, split_name)
    output_split_dir = os.path.join(OUTPUT_DIR, split_name)
    output_images_dir = os.path.join(output_split_dir, 'images')
    
    # 检查输入目录是否存在
    if not os.path.isdir(input_split_dir):
        print(f"警告: 输入目录 '{input_split_dir}' 不存在，跳过该分区。")
        return

    # 创建输出目录
    os.makedirs(output_images_dir, exist_ok=True)
    
    # 查找所有 .inkml 文件
    inkml_files = glob.glob(os.path.join(input_split_dir, '*.inkml'))
    
    if not inkml_files:
        print(f"在 '{input_split_dir}' 中没有找到 .inkml 文件。")
        return

    labels_data = []
    
    # 使用 tqdm 创建进度条
    for inkml_path in tqdm(inkml_files, desc=f"处理 {split_name} 文件", unit="file"):
        # 获取不带扩展名的文件名
        base_filename = os.path.splitext(os.path.basename(inkml_path))[0]
        png_filename = f"{base_filename}.png"
        output_png_path = os.path.join(output_images_dir, png_filename)
        
        # 1. 将 InkML 转换为 PNG
        inkml2img(inkml_path, output_png_path)
        
        # 2. 从 InkML 提取标签
        label = extract_label_from_inkml(inkml_path)
        
        if label is not None:
            labels_data.append({
                "file_name": png_filename,
                "label": label
            })
        else:
            print(f"警告: 未能从文件 '{os.path.basename(inkml_path)}' 中提取到标签。")

    # 3. 将标签数据保存为 JSON 文件
    output_json_path = os.path.join(output_split_dir, 'labels.json')
    with open(output_json_path, 'w', encoding='utf-8') as f:
        json.dump(labels_data, f, ensure_ascii=False, indent=4)
        
    print(f"处理完成！ {len(labels_data)} 个图文对已保存至 '{output_json_path}'")

def main():
    """主函数，按顺序处理所有数据集分区。"""
    if not os.path.isdir(INPUT_DIR):
        print(f"错误：输入数据目录 '{INPUT_DIR}' 未找到。")
        print("请确保 'mathwriting-2024-excerpt' 文件夹位于项目根目录。")
        return
        
    for split in ['train', 'test', 'valid']:
        process_split(split)
        
    print("\n所有数据集处理完毕！")

if __name__ == '__main__':
    main()
