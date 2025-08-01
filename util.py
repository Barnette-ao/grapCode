import sys
import os

import re
import json
from math import ceil
from collections import defaultdict
from typing import List, Optional, Tuple
from functools import lru_cache

dict_of_changed_content = { 
    '笔画练习': '控笔练习',
    '综合分类': '综合资料'
}

# 为匹配小程序的文件目录名以及先锋网站的类别名
def match_file_name(paths):
    [firstcategory, secondcategory] = paths
    if firstcategory == "幼小衔接" and secondcategory in dict_of_changed_content:
        secondcategory = dict_of_changed_content[secondcategory]
    return [firstcategory, secondcategory]

# 在之后构建form-data时需要categoryId,和parentId,但是类别接口返回的数据和现在的目录结构不匹配
# 先锋学霸资料\二年级上册\语文\预习资料\二年级（上）语文《识字表》生字音节音序部首组词.pdf
# 先锋学霸资料去掉，二年级上册改为二年级上，预习资料\二年级（上）语文《识字表》生字音节音序部首组词.pdf去掉，二年级上\语文
def process_path(path):
    # 1. 移除开头的"先锋学霸资料\"
    path = re.sub(r'^先锋学霸资料\\', '', path)
    
    # 2. 替换"上册"->"上"，"下册"->"下"
    path = path.replace('上册', '上').replace('下册', '下')

    parts = path.split('\\')
    if len(parts) >= 2:
        [firstcategory, secondcategory] = match_file_name([parts[0], parts[1]])
        return f"{firstcategory}\\{secondcategory}"
    else:
        print("路径格式不正确")
        return None

def convert_category_data_to_tuple(category_data: List[dict]) -> tuple:
    """
    将原始分类数据列表转换为可哈希的元组
    :param category_data: 原始数据格式 [{"id":1, "pid":None, "name":"语文"}, ...]
    :return: 元组格式 ((id, pid, name), ...)
    """
    return tuple(
        (item["id"], item["pid"], item["name"])
        for item in category_data
    )


def get_category_id_pid(category_data, category_name, parent_category_name):
    """
    根据类别名称在类别数据中查找对应的ID和对应的父类别ID
    """
    candidates = [item for item in category_data if item['name'] == category_name]
    # print("candidates",candidates)

    # 情况1：无匹配项
    if not candidates:
        print(f"未找到类别名称为 {category_name} 的项")
        return None
    
    # 情况2：唯一匹配项
    if len(candidates) == 1:
        return [candidates[0]['id'], candidates[0]['pid']]
    
    # 情况3：多个同名项且有父类别名
    parent_category_id = next(
        (item['id'] for item in category_data 
         if item['name'] == parent_category_name),
        None
    )

    if not parent_category_id:
        print(f"未找到父类别名称为 {parent_category_name} 的项")
        return None

    result = next(
        (item for item in category_data 
         if item['pid'] == parent_category_id and item['name'] == category_name),
        None
    )

    return [result['id'],result['pid'] ] if result else None           

@lru_cache(maxsize=128)
def get_category_id_pid_cached(
    category_data_tuple: tuple,  # 必须转换为可哈希类型
    category_name: str,
    parent_category_name: str
) -> Optional[List]:
    """
    带缓存的分类ID查询
    :param category_data_tuple: ((id, pid, name), ...)
    :return: [category_id, parent_id] 或 None
    """
    # 临时转换回列表格式（保持原逻辑）
    category_data = [
        {"id": item[0], "pid": item[1], "name": item[2]}
        for item in category_data_tuple
    ]
    return get_category_id_pid(category_data, category_name, parent_category_name)


def get_categoryId_with_parentId(
    file_path:str, 
    category_data_tuple:tuple
) -> Optional[List]:
    """
    根据文件路径获取对应的categoryId和parentId
    :param file_path: 文件路径
    :param category_data_tuple: 类别数据(元组)
    :return: [categoryId, parentId, categoryName] 或 None
    """

    # 路径格式正确，如parent_category//category,否则返回None    
    processed_path = process_path(file_path)
    if not processed_path or '\\' not in processed_path:
        return None

    parent_category, category = processed_path.split('\\', maxsplit=1)

    # 调用带缓存的版本
    result = get_category_id_pid_cached(category_data_tuple, category, parent_category)
    
    if not result:
        return None
          
    return [result[0], result[1], category]

def build_tree(data):
    """
    根据pid构建树形结构
    :param data: 原始数据列表
    :return: 树形结构的根节点列表
    """
    # 创建节点字典 {id: node}
    nodes = {item['id']: {'id': item['id'], 'name': item['name'], 'children': []} for item in data}
    
    # 构建树
    tree = []
    for item in data:
        node = nodes[item['id']]
        pid = item['pid']
        if pid is None:
            tree.append(node)  # 根节点
        else:
            parent = nodes.get(pid)
            if parent:
                parent['children'].append(node)
    
    return tree

def print_tree(nodes, level=0):
    """
    递归打印树形结构
    :param nodes: 当前层节点列表
    :param level: 当前层级（用于缩进）
    """
    for node in nodes:
        print('  ' * level + '├─', node['name'], f"(id:{node['id']})")
        if node['children']:
            print_tree(node['children'], level + 1)


def get_subfolder_paths(root_folder):
    """
    获取指定文件夹下所有子文件夹的完整路径
    :param root_folder: 根文件夹路径（如"先锋学霸资料"）
    :return: 子文件夹完整路径列表
    """
    # 构建完整根路径
    root_path = os.path.abspath(root_folder)
    
    # 检查文件夹是否存在
    if not os.path.exists(root_path):
        raise FileNotFoundError(f"文件夹不存在: {root_path}")
    if not os.path.isdir(root_path):
        raise NotADirectoryError(f"路径不是文件夹: {root_path}")

    # 遍历获取子文件夹
    subfolder_paths = []
    for entry in os.scandir(root_path):
        if entry.is_dir():
            full_path = os.path.join(root_folder, entry.name)
            subfolder_paths.append(full_path)
    
    return subfolder_paths


def smart_split_files(file_paths, max_files=50, max_total_size=500 * 1024 * 1024, max_single_file=200 * 1024 * 1024):
    """
    智能分块文件路径
    :param file_paths: 文件路径列表
    :param max_files: 每块最多文件数（默认50）
    :param max_total_size: 每块最大总大小（字节，默认500MB）
    :param max_single_file: 单文件最大大小（字节，默认200MB）
    :return: 分块后的列表 [[path1,path2,...], [...]]
    """
    # 1. 过滤超大文件并预计算大小
    categorized = defaultdict(list)
    for path in file_paths:
        try:    
            size = os.path.getsize(path)
            if size > max_single_file:
                continue
               
            # 获取分类（如"二年级上\语文"）
            category = process_path(path)
            if not category:
                print(f"路径格式错误: {path}")
                continue
        
            categorized[category].append((path, size))    

        except OSError:
            print(f"文件无法访问: {path}")
            continue

    chunks = []

    for category, files  in categorized.items() :
        current_chunk = []
        current_size = 0

        for path, size in files:
            # 检查是否需要新建分块
            if (len(current_chunk) >= max_files) or (current_size + size > max_total_size):
                chunks.append(current_chunk)
                current_chunk = []
                current_size = 0

            current_chunk.append(path)
            current_size += size

            if current_chunk:
                chunks.append(current_chunk)


    return chunks 