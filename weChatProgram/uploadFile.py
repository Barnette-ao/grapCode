import sys
sys.path.append('..')

import os
import mimetypes
import numpy as np

from libs.postRequest import postRequest_with_formdata 
from form_data import FormData
from util import (
    get_categoryId_with_parentId,
    get_category_data,
    build_tree,print_tree,
    get_subfolder_paths
)
import getContentList 
import json
from tqdm import tqdm

def split_numpy_array(arr, chunk_size=50):
    """
    Numpy数组分块（避免内存复制）
    :param arr: numpy数组
    :param chunk_size: 每份大小
    :return: 数组视图列表
    """
    return np.array_split(arr, np.ceil(len(arr)/chunk_size))


def collect_pdf_files(base_dir):
    """
    递归收集三级目录结构中的所有PDF文件
    """
    files_list = []

    # 递归扫描函数
    def _scan_directory(current_dir):
        for entry in os.listdir(current_dir):
            # 忽略幼小衔接下可能存在的知识汇总和专项练习目录
            if os.path.basename(current_dir) == "幼小衔接" and entry in ['知识汇总','专项练习']:
                continue

            full_path = os.path.normpath(os.path.join(current_dir, entry))
            
            if os.path.isdir(full_path):
                # 如果是目录，递归扫描
                _scan_directory(full_path)
            else:
                # 如果是PDF文件，添加到列表
                files_list.append(os.path.normpath(full_path))

    base_dir = os.path.normpath(base_dir)
    # 开始扫描
    _scan_directory(base_dir)
    
    return files_list

def get_files_data(files_path_list):
    """
    准备文件数据（二进制模式打开）
    """
    def get_mime_type(file_path):
        """根据文件扩展名获取MIME类型"""
        mime_type, _ = mimetypes.guess_type(file_path)
        return mime_type or 'application/octet-stream'  # 默认二进制流

    files = []
    for file_path in files_path_list:
        if not os.path.exists(file_path):
            print(f"文件不存在: {file_path}")
            continue
        file_name = os.path.basename(file_path)
        mime_type = get_mime_type(file_name)
        files.append(('files', (file_name, open(file_path, 'rb'), mime_type)))
    
    if not files:
        raise ValueError("没有有效的PDF文件可上传")

    return files




if __name__ == "__main__":
    root_dir = "先锋学霸资料"
    paths = get_subfolder_paths(root_dir)
    for path in paths:
        print(path)
        all_file_path = collect_pdf_files(path)
        chunk_list = [len(chunk.tolist()) for chunk in split_numpy_array(all_file_path)]  # 每个子数组转Python列表
        for chunk in chunk_list:
            print(chunk)
            
            

    # cookie_value = "wenku-session-id=7dfd9d80-58fa-4468-aa4d-79d4c01dc273"
    # root_dir = "先锋学霸资料"
    # paths = get_subfolder_paths(root_dir)
    # # print(paths)
    # for path in tqdm(paths, desc="处理文件夹"):
    #     all_file_path = collect_pdf_files(path)
    #     files = get_files_data(all_file_path)

    #     category_data = get_category_data(cookie_value)
    #     if not get_categoryId_with_parentId(all_file_path[0],category_data):
    #         print("获取categoryId和parentId失败")
    #         continue

            
    #     [categoryId, parentId, categoryName] = get_categoryId_with_parentId(all_file_path[0],category_data)

    #     response = postRequest_with_formdata(
    #         postUrl="http://211.154.30.100:8222/base/resource/uploadMutiAPI2",
    #         cookie_value=cookie_value,
    #         files=files,
    #         form_data=FormData(categoryId, parentId, categoryName).to_dict()
    #     )
    
    #     print(response)
