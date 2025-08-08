import json
import simple_download_pdf
import getContentList
from postRequest import postRequest
from helpFunc import (
    datetime_to_timestamp,
    compare_timestamps,
    build_query_params,
    get_resource_list,
    walk_tree
) 
import argparse
import os
from getThresholdTime import MiniProgramTimeExtractor
from datetime import datetime, timedelta
from logger import log_exit_time
from numbers import Number

# API_URL_RESOURCE_ITEM: 单个资源的信息API地址
# API_URL_RESOURCE_LIST: 资源列表API地址
API_URL_RESOURCE_ITEM = "https://ht.axuex.top/api/Resource/resdetail?from_id="  # 示例 API

API_URL_RESOURCE_LIST = "https://ht.axuex.top/api/Resource/resource?from_id="  # 示例 API

def is_latest_than(threshold_ctime,resource):
    threshold_timestamp = datetime_to_timestamp(threshold_ctime)

    result = compare_timestamps(
        threshold_timestamp, 
        datetime_to_timestamp(resource['ctime'])
    )

    # 如果result等于-1，说明该pdf的创建时间比阈值时间要晚，没有下载过
    return result == -1
        

def set_queryData_of_pdf(resource,token):
    return dict(
        id = resource['id'],
        token = token,
        plat_form = "mp-weixin"
    )

def download(postUrl,queryData,firstcategory,secondcategory,thirdcategory='',fourthcategory='' ):
    response = postRequest(postUrl, queryData)
    print(json.dumps(response, indent=4, ensure_ascii=False))
    if response['code'] == 200:
        url = response['data']['link']
        file_ext = os.path.splitext(url)[1] # 获取文件扩展名 例如 .pdf

        filename = f"{response['data']['title']}{file_ext}"

        base_dir = f"先锋学霸资料"

        params = {
            "base_dir": base_dir,
            "firstcategory": firstcategory,
            "secondcategory": secondcategory,
            "filename": filename,
            "thirdcategory": thirdcategory,
            "fourthcategory": fourthcategory,
        }
        
        # 构建路径
        save_path = simple_download_pdf.build_save_path(**params)
        print("执行到了这里")
        simple_download_pdf.simple_download_pdf(url, save_path)


def download_resources_by_category(content_list, auth_token, threshold_ctime):
     """
     根据分类内容列表下载所有资源
    
     Args:
        content_list: 分类内容列表（含categoraylist）
        API_URL_RESOURCE_ITEM: 单个资源的信息API地址
        API_URL_RESOURCE_LIST: 资源列表API地址
        auth_token: 认证token

        walk_tree(content_list)因为是yield生成器，所以不用等所有的节点都遍历完，只要有一条路径遍历完，就会yield一次
        返回的数据结构是 前者为最后的叶子结点，后者为从根节点到叶子结点的路径，也就是说从根目录到最小子目录的路径
        {'id': 1561, 'name': '拼音资料', 'children': []},['幼小衔接', '幼小衔接', '幼小衔接', '拼音资料']
        {'id': 307, 'name': '电子课本', 'children': []} ['一年级', '一年级上册', '语文', '电子课本']
        
        幼小衔接和其他分类的区别在于，幼小衔接的分类在下载的时候的动态参数只有两个，其他分类的分类在下载的时候的动态参数有四个
        如上，幼小衔接的目录为幼小衔接，拼音资料。其他分类的目录为一年级，一年级上册，语文，电子课本
    """
     for leaf, path in walk_tree(content_list):
        # 获取文件路径，path的长度=树的深度
        print(leaf, path)
        first, *rest = path

        # 如果是幼小衔接，那么下载时只需要一级分类和二级分类
        # 其他分类则需要一级分类、二级分类、三级分类、四级分类
        # fold_path作为download函数的动态参数容器
        if first == '幼小衔接':
            folder_path = [rest[1],rest[2]]
        else:
            folder_path = path

        extra_params = {
            'order': 0,
            'keys': "",
            'edition': 0
        } if first != "幼小衔接" else None

        
        resource_list = get_resource_list(
            API_URL_RESOURCE_LIST,
            queryData=build_query_params(leaf['id'], extra_params)
        )
        print(resource_list[:2] if resource_list else "没有找到资源列表")

        # 跳过resource_list为None的情况   
        if not resource_list:
            print(f"没有找到资源列表，跳过下载 {leaf['name'],resource_list}")
            continue

        # 下载每个资源
        for resource in resource_list:
            # 下载之前，先根据pdf的创建事件判断筛选比该阈值要晚的时间创建的pdf，
            # 假设阈值时间是2025-07-11 00:00:00
            # 如果该pdf的创建时间比该阈值要早，则跳过下载
            if not is_latest_than(threshold_ctime, resource):
                print(f"跳过下载 {resource['title']}，因为它的创建时间比阈值时间 {threshold_ctime} 早")
                continue

            pdf_query = set_queryData_of_pdf(resource, auth_token)
            print("pdf_query", pdf_query)

            # 根据实际层级动态解包
            *cats, item_name = folder_path
            download(
                API_URL_RESOURCE_ITEM,
                pdf_query,
                *cats,  # 如果不是幼小衔接就是前三级目录否则是一级目录
                item_name   # 如果不是幼小衔接就是四级分类名否则就是二级目录
            )

log_file="program_interrupt_weChat.log"
       
@log_exit_time(log_file)
def batch_download_resources(auth_token, threshold_ctime):
    contentlist = getContentList.normalize_content_list()

    download_resources_by_category(
        content_list = contentlist, 
        auth_token = auth_token,
        threshold_ctime = threshold_ctime
    )


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="批量下载PDF资源")
    parser.add_argument("--token",required=True, type=str, help="认证token")
    args = parser.parse_args()

    weChat_extractor = MiniProgramTimeExtractor(log_file=log_file)
    threshold_ctime = weChat_extractor.get_threshold_time()
    print(f"时间阈值: {threshold_ctime}")

    try:
        batch_download_resources(args.token, threshold_ctime)
    except Exception as e:
        print(f"程序运行出错: {e}")
        raise
    
    

   