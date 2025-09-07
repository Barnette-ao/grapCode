import sys
import os

import re
import json
from math import ceil
from collections import defaultdict
from typing import List, Optional, Tuple
from functools import lru_cache
from getRequest import simple_get_request_with_cookie

dict_of_changed_content = { 
    '综合分类': '综合资料',
    '专项练习': '综合资料',
}

# 为匹配小程序的文件目录名以及先锋网站的类别名
def match_file_name(paths):
    [firstcategory, secondcategory] = paths
    if firstcategory == "幼小衔接" and secondcategory in dict_of_changed_content:
        secondcategory = dict_of_changed_content[secondcategory]
    return [firstcategory, secondcategory]

# 在之后构建form-data时需要categoryId,和parentId,但是类别接口返回的数据和现在的目录结构不匹配
# 输入先锋学霸资料\二年级\二年级上册\语文\预习资料\二年级（上）语文《识字表》生字音节音序部首组词.pdf
# 先锋学霸资料\幼小衔接\口算计算\撒记得哦爱家哦上帝.pdf
# 返回二年级上\语文\预习资料和幼小衔接\口算计算
def process_path(path):
    # 1. 替换"上册"->"上"，"下册"->"下"
    path = path.replace('上册', '上').replace('下册', '下')
    # 2. 切分
    parts = path.split('\\')
    # 3. 截取其中有用的部分
    path_list = match_file_name([parts[1], parts[2]]) if parts[1] == "幼小衔接" else [parts[2], parts[3], parts[4]] 

    # 4. 以\连接
    return "\\".join(path_list)
        

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
    # print("category_data, category_name, parent_category_name",category_data, category_name, parent_category_name)
    candidates = [item for item in category_data if item['name'] == category_name]

    # 情况1：无匹配项
    if not candidates:
        print(f"未找到类别名称为 {category_name} 的项")
        return None
    
    # 情况2：唯一匹配项
    if len(candidates) == 1:
        return [candidates[0]['id'], candidates[0]['pid']]
    
    # 情况3：多个同名项且有父类别名
    for target_item in candidates:
        targetId, targetPid= target_item['id'], target_item['pid']
         
        for item in category_data:
            if item['id'] == targetPid and item['name'] == parent_category_name:
                return [targetId, targetPid]

    return None        
                   

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


def get_detail_category(cookie_value, categoryId, thirdcategory, isVersion=False):
    """
    根据categoryId和thirdcategory获取filterDetailCode2
    """

    # 如果thirdcategory是空字符串，则直接返回空字符串
    if not thirdcategory:
        return ""

    # 版本号的唯一标识和类型的唯一标识接口结构类似
    # 查类型的数据比查版本的数据多得多，所以是否是版本默认为False
    apiName = "getBanbenList" if isVersion else "getLeixingList"

    sub_category_list=simple_get_request_with_cookie(
        url=f"http://211.154.30.100:8222/base/resource/{apiName}?categoryId={categoryId}",
        cookie_value=cookie_value,
    )

    sub_category_data = [
        { 
            "id": item['id'],
            "filterDetailName": item['filterDetailName'],
            "filterDetailCode": item['filterDetailCode'] 
        }
        for item in json.loads(sub_category_list) 
    ]
    # print("sub_category_data",sub_category_data)

    filtered_list = list(filter(lambda x: x['filterDetailName'] == thirdcategory, sub_category_data))

    if(filtered_list and len(filtered_list) == 1):
        detailCode = filtered_list[0]['filterDetailCode']
    else:
        print("未找到匹配项或匹配项不唯一")
        return ""

    return detailCode


def get_categoryId_with_parentId(
    file_path:str, 
    category_data_tuple:tuple,
    cookie_value:str
) -> Optional[List]:
    """
    根据文件路径获取对应的categoryId和parentId
    :param file_path: 文件路径
    :param category_data_tuple: 类别数据(元组)
    :param cookie_value: cookie值
    :return: [categoryId, parentId, categoryName, filterDetailCode2] 或 None
    """

    # 路径格式正确，如parent_category//category,否则返回None    
    processed_path = process_path(file_path)
    # print("processed_path",processed_path)

    if not processed_path or '\\' not in processed_path:
        return None

    parts = processed_path.split('\\')

    # 确保 parts 至少有三个元素，不足的部分用空字符串填充
    # 幼小衔接分类中，sub_category会返回空字符串
    parts += [''] * (3 - len(parts))
    # print("parts",parts)

    parent_category, category, sub_category = parts[:3]
    # parent_category, category, sub_category 
    # print("parent_category, category, sub_category",parent_category, category, sub_category)

    # 调用带缓存的版本
    result = get_category_id_pid_cached(category_data_tuple, category, parent_category)
    # print("result",result)

    if not result:
        return None
    
    # 调用get_detail_category获取filterDetailCode2
    # 如果sub_category为空字符串，则filterDetailCode2为空字符串
    isVersion = True if sub_category and "版" in sub_category else False
    detailCode = get_detail_category(
        cookie_value = cookie_value,
        categoryId = result[0],
        thirdcategory = sub_category,
        isVersion=isVersion
    )
         
    return [result[0], result[1], category,detailCode, isVersion]

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


def set_response_message(response):
    """
    设置响应消息
    :param response: 响应对象
    :param message: 消息内容
    :param status_code: 状态码（默认200）
    """
    message = response['data']
    # 使用正则表达式提取信息
    pattern = r"此次上传文件(\d+)个，成功<span style='color:blue;font-weight:bold'>(\d+)</span>个，失败<span style='color:red;font-weight:bold'>(\d+)</span>个"
    match = re.search(pattern, message)
    if match:
        total, success, fail = match.groups()
        result = f"该分块上传{total}个，成功{success}个，失败{fail}个"
        print(result)
        return [int(total), int(success), int(fail)]
    else:
        print("未找到匹配信息")
        return None



if __name__ == "__main__":
    # cookie_value = "wenku-session-id=4519526e-0bb2-4717-a6be-487b5e7b9434"
    # sub_category_list = get_sub_category(cookie_value, )
    filterDetailCode2 = get_detail_category(
        cookie_value = "wenku-session-id=4519526e-0bb2-4717-a6be-487b5e7b9434",
        categoryId = 231319,
        thirdcategory = "青岛版",
        isVersion=True
    )

    print(filterDetailCode2)

    # 输入先锋学霸资料\二年级\二年级上册\语文\预习资料\二年级（上）语文《识字表》生字音节音序部首组词.pdf
    # 先锋学霸资料\幼小衔接\口算计算\撒记得哦爱家哦上帝.pdf
    
    path1 = "先锋学霸资料\二年级\二年级上册\语文\预习资料\二年级（上）语文《识字表》生字音节音序部首组词.pdf"
    path2 = "先锋学霸资料\幼小衔接\口算计算\撒记得哦爱家哦上帝.pdf"
    print(process_path(path1))
    print(process_path(path2))

