import sys
import os
import mimetypes

from getRequest import simple_get_request_with_cookie
from postRequest import postRequest_with_formdata 
from form_data import FormData
from util import (
    get_categoryId_with_parentId,
    get_subfolder_paths,
    smart_split_files,
    convert_category_data_to_tuple,
)
import json
from tqdm import tqdm
import argparse

def get_category_data(cookie_value):
    """
    准备表单数据
    """
    # 获取所有类别的编号
    category_tree=simple_get_request_with_cookie(
        url="http://211.154.30.100:8222/base/category/treeData",
        cookie_value=cookie_value
    )
    # print("category_tree",category_tree)
    """
    category_data数据结构如下
    [
        {
            "id": item['id'],
            "pid": item['pId'],
            "name": item['name']
        }
    ]
    """
    category_data = [
        { 
            "id": item['id'],
            "pid": item['pId'],
            "name": item['name'] 
        }
        for item in json.loads(category_tree)
    ]
    return category_data


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

def upload_by_chunks(root_dir,cookie_value):
    """
    分块上传文件
    """ 
    category_data_tuple = convert_category_data_to_tuple(
        get_category_data(cookie_value)
    )

    paths = get_subfolder_paths(root_dir)
    for path in paths:
        print(path)
        all_file_path = collect_pdf_files(path)
        path_chunks = smart_split_files(all_file_path)
        # print("path_chunk", path_chunks)
        for path_chunk in path_chunks:
            # 准备文件数据
            files = get_files_data(path_chunk)    

            if not get_categoryId_with_parentId(path_chunk[0],category_data_tuple):
                print("获取categoryId和parentId失败")
                continue
   
            [categoryId, parentId, categoryName] = get_categoryId_with_parentId(path_chunk[0],category_data_tuple)

            response = postRequest_with_formdata(
                postUrl="http://211.154.30.100:8222/base/resource/uploadMutiAPI2",
                cookie_value=cookie_value,
                files=files,
                form_data=FormData(categoryId, parentId, categoryName).to_dict()
            )
        
            print(response)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="批量上传文件")
    parser.add_argument("--root_dir",required=True, type=str, help="存放资料的文件目录")
    parser.add_argument("--cookie_value",required=True, type=str, help="cookie值")
    args = parser.parse_args()

    root_dir = "先锋学霸资料"
    cookie_value = "wenku-session-id=7dfd9d80-58fa-4468-aa4d-79d4c01dc273"
    upload_by_chunks(args.root_dir,args.cookie_value)    

