import sys
sys.path.append('..')

import os
import mimetypes

from libs.postRequest import postRequest_with_formdata 
from form_data import FormData
from util import get_categoryId_with_parentId,get_category_data 



def collect_pdf_files(base_dir):
    """
    递归收集三级目录结构中的所有PDF文件
    """
    files_list = []

    # 递归扫描函数
    def _scan_directory(current_dir):
        for entry in os.listdir(current_dir):
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
    files_path_list
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
    base_dir = "先锋学霸资料\\幼小衔接"
    all_file_path = collect_pdf_files(base_dir)
    print(all_file_path)

    category_data = get_category_data()
    [categoryId, parentId, categoryName] = get_categoryId_with_parentId(all_file_path[0], category_data)
    
    print(categoryId, parentId, categoryName)
    # files = get_files_data(all_file_path)

    # response = postRequest_with_formdata(
    #     postUrl="http://211.154.30.100:8222/base/resource/uploadMutiAPI2",
    #     cookie_value="wenku-session-id=40b76a5b-5c47-4eb2-bb27-44a4b8d6653c",
    #     files=files,
    #     form_data=FormData(categoryId, parentId, categoryName).to_dict()
    # )

    # print(response)
