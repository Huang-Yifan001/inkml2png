import numpy as np
import matplotlib.pyplot as plt
import xml.etree.ElementTree as ET
import os

# -----------------------------------------------------------------------------
# 从 InkML 渲染 PNG 图片的函数
# -----------------------------------------------------------------------------

def get_traces_data(inkml_file_abs_path, xmlns='{http://www.w3.org/2003/InkML}'):
    """
    一个健壮的 inkml 解析器，可处理不同格式的坐标数据并避免不必要的缩放。
    """
    traces_data = []
    tree = ET.parse(inkml_file_abs_path)
    root = tree.getroot()
    doc_namespace = xmlns

    # 1. 查找所有 <trace> 标签并安全地解析它们的坐标
    all_trace_tags = root.findall(doc_namespace + 'trace')
    traces_all = []
    
    for i, trace_tag in enumerate(all_trace_tags):
        # 使用索引作为备用ID，以防 'id' 属性缺失
        trace_id = trace_tag.get('id', str(i))
        coords_text = trace_tag.text or ''
        point_strings = coords_text.strip().replace('\n', '').split(',')
        
        current_trace_coords = []
        for point_str in point_strings:
            # 使用 .split() 可以优雅地处理一个或多个空格
            values = point_str.strip().split()
            
            # 确保至少有两个坐标值 (X 和 Y)
            if len(values) >= 2:
                try:
                    # 将坐标直接转换为浮点数，不进行缩放
                    x = float(values[0])
                    y = float(values[1])
                    current_trace_coords.append([x, y])
                except ValueError:
                    # 如果坐标不是有效数字，则跳过这个点
                    pass
        
        if current_trace_coords:
             traces_all.append({'id': trace_id, 'coords': current_trace_coords})

    # 按ID排序，以确保在 traceGroup 中能正确引用
    # 注意：这里假设ID是数字字符串
    try:
        traces_all.sort(key=lambda trace_dict: int(trace_dict['id']))
    except (ValueError, KeyError):
        # 如果ID不是数字，则不排序，按文件顺序处理
        pass

    # 2. 如果存在 <traceGroup> (分割信息)，则按组聚合笔画
    traceGroupWrapper = root.find(doc_namespace + 'traceGroup')
    if traceGroupWrapper is not None:
        for traceGroup in traceGroupWrapper.findall(doc_namespace + 'traceGroup'):
            label = traceGroup.find(doc_namespace + 'annotation').text
            traces_curr = []
            for traceView in traceGroup.findall(doc_namespace + 'traceView'):
                traceDataRef = int(traceView.get('traceDataRef'))
                # 通过索引安全地获取笔画数据
                if traceDataRef < len(traces_all):
                    single_trace = traces_all[traceDataRef]['coords']
                    traces_curr.append(single_trace)
            if traces_curr:
                traces_data.append({'label': label, 'trace_group': traces_curr})
    else:
        # 如果没有 <traceGroup>，则每个笔画自成一组
        for trace in traces_all:
            if trace['coords']:
                traces_data.append({'trace_group': [trace['coords']]})

    return traces_data


def inkml2img(input_path, output_path, color='#284054'):
    """
    将单个 InkML 文件转换为 PNG 图片。
    """
    try:
        traces = get_traces_data(input_path)
        plt.figure()
        plt.gca().invert_yaxis()
        plt.gca().set_aspect('equal', adjustable='box')
        plt.gca().get_xaxis().set_visible(False)
        plt.gca().get_yaxis().set_visible(False)
        plt.gca().spines[['top', 'right', 'bottom', 'left']].set_visible(False)

        for elem in traces:
            for sub_ls in elem['trace_group']:
                if not sub_ls: continue
                data = np.array(sub_ls)
                # 确保 data 是二维的
                if data.ndim == 2 and data.shape[1] >= 2:
                    plt.plot(data[:, 0], data[:, 1], c=color, linewidth=2)
        
        plt.savefig(output_path, bbox_inches='tight', dpi=100, pad_inches=0.1)
    
    finally:
        # 确保关闭图形，以释放内存
        plt.close('all')


# -----------------------------------------------------------------------------
# 从 InkML 提取 LaTeX 标签的函数
# -----------------------------------------------------------------------------

def extract_label_from_inkml(inkml_file_path):
    """
    从 InkML 文件中提取规范化的 LaTeX 标签。
    优先查找 'normalizedLabel'，其次是 'label'。
    """
    try:
        tree = ET.parse(inkml_file_path)
        root = tree.getroot()
        namespace = {'ns': 'http://www.w3.org/2003/InkML'}
        
        # 1. 优先查找 normalizedLabel
        norm_label_element = root.find(".//ns:annotation[@type='normalizedLabel']", namespace)
        if norm_label_element is not None and norm_label_element.text:
            return norm_label_element.text.strip()
            
        # 2. 其次查找 label
        label_element = root.find(".//ns:annotation[@type='label']", namespace)
        if label_element is not None and label_element.text:
            return label_element.text.strip()
            
        return None

    except (FileNotFoundError, ET.ParseError):
        return None
