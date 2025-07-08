# MathWriting-2024 数据集处理器

本项目提供了一套工具，用于处理谷歌发布的 **MathWriting-2024** 手写数学公式数据集。其核心功能是将原始的 `.inkml` 格式文件，批量转换为 `.png` 图片，并为每个数据集分区（train/test/valid）生成一个包含图片文件名与对应 LaTeX 标签的 `labels.json` 文件，方便下游任务（如手写识别模型的训练）直接使用。

## 📝 关于数据集

1.  **数据来源**: 本项目处理的数据源自 Google Research 发布的 `MathWriting-2024` 数据集。您可以从以下链接获取：
    * **完整数据集 (2.9 GB):** [mathwriting2024.tgz](https://storage.googleapis.com/mathwriting_data/mathwriting-2024.tgz)
    * **部分示例数据 (1.5 MB):** [mathwriting2024-excerpt.tgz](https://storage.googleapis.com/mathwriting_data/mathwriting-2024-excerpt.tgz)

2.  **数据说明**:
    * 本项目仓库中包含的 `mathwriting-2024-excerpt` 文件夹是一小部分示例数据，用于快速演示和测试代码功能。
    * 在原始数据集中，`synthetic` 文件夹下的合成数据已被合并到 `train` 文件夹下，统一用于训练。

## ✨ 功能特性

- **InkML 转 PNG**: 将复杂的 InkML 笔迹数据高效渲染成高质量、背景透明的 PNG 图片。
- **标签提取**: 自动从 InkML 文件中提取 `normalizedLabel` 字段作为公式的真值（Ground Truth）。
- **数据集构建**: 自动为 `train`, `test`, `valid` 三个分区创建统一格式的输出目录结构。
- **易于使用**: 只需一个命令即可完成整个数据集的处理流程。
- **进度可视化**: 使用 `tqdm` 库提供清晰的进度条，方便跟踪大数据集的处理进度。

## 📁 最终输出结构

运行主脚本后，将会生成如下结构的 `mathwriting-2024-png` 文件夹：

```
/mathwriting-2024-png/
├── train/
│   ├── images/
│   │   ├── 000aa4c444cba3f2.png
│   │   └── ... (更多图片)
│   └── labels.json
│
├── test/
│   ├── images/
│   │   └── ...
│   └── labels.json
│
└── valid/
    ├── images/
    │   └── ...
    └── labels.json
```


其中，labels.json内容如下：
```json
[
    {
        "file_name": "000aa4c444cba3f2.png",
        "label": "\\vartheta=-\\frac{log\\frac{\\phi_{\\varsigma_{1}}}{\\phi_{\\varsigma_{2}}}}{log\\frac{\\varsigma_{1}}{\\varsigma_{2}}}"
    },
    {
        "file_name": "...",
        "label": "..."
    }
]
```

## 🏃‍♂️ 如何运行
确保已完成安装和数据准备。然后，在项目根目录下运行主脚本：

```python
python process_dataset.py
``````

脚本将自动查找输入文件夹中的所有` .inkml` 文件，处理它们，并在 `mathwriting-2024-png `文件夹中生成最终结果。