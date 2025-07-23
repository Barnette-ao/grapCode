import sys
sys.path.append('..')

import json
import simple_download_pdf
import getContentList
from libs.postRequest import postRequest
from libs.helpFunc import (
    datetime_to_timestamp,
    compare_timestamps,
    build_query_params,
    get_resource_list
) 
import argparse
import os
from libs.getThresholdTime import get_threshold_time
from datetime import datetime, timedelta
from libs.logger import log_exit_time

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

def download(postUrl,queryData,firstcategory,secondcategory,thirdcategory=''):
    response = postRequest(postUrl, queryData)
    # print(json.dumps(response, indent=4, ensure_ascii=False))
    if response['code'] == 200:
        url = response['data']['link']
        file_ext = os.path.splitext(url)[1] # 获取文件扩展名 例如 .pdf

        filename = f"{response['data']['title']}{file_ext}"

        formatted_threshold_ctime = datetime.strptime(get_threshold_time(), "%Y-%m-%d %H:%M:%S").strftime("%Y%m%d")

        formatted_today_date = datetime.now().strftime("%Y%m%d")

        base_dir = f"{formatted_threshold_ctime}--{formatted_today_date}"

        params = {
            "base_dir": base_dir,
            "firstcategory": firstcategory,
            "secondcategory": secondcategory,
            "filename": filename,
            "thirdcategory": thirdcategory
        }
        
        # 构建路径
        save_path = simple_download_pdf.build_save_path(**params)
        simple_download_pdf.simple_download_pdf(url, save_path)


def download_resources_by_category(content_list, auth_token, threshold_ctime):
     """
     根据分类内容列表下载所有资源
    
     Args:
        content_list: 分类内容列表（含categoraylist）
        API_URL_RESOURCE_ITEM: 单个资源的信息API地址
        API_URL_RESOURCE_LIST: 资源列表API地址
        auth_token: 认证token
    """
     for content in content_list:
        if not content.get('categoraylist'):
            continue  # 跳过没有分类的内容

        firstcategory = content.get('title', '未命名分类')
        
        for secondcategory, item_list in content['categoraylist'].items():
            for item in item_list:
                # 判断是否为三级分类结构
                is_three_level = len(content['categoraylist']) > 1
                
                # 构建查询参数
                extra_params = {
                    'order': 0,
                    'keys': "",
                    'edition': 0
                } if is_three_level else None
                
                # 获取资源列表
                resource_list = get_resource_list(
                    API_URL_RESOURCE_LIST,
                    queryData=build_query_params(item['sort_id'], extra_params)
                )

                # 跳过resource_list为None的情况   
                if not resource_list:
                    continue

                # 下载每个资源
                for resource in resource_list:
                    # 下载之前，先根据pdf的创建事件判断筛选比该阈值要晚的时间创建的pdf，
                    # 假设阈值时间是2025-07-11 00:00:00
                    # 如果该pdf的创建时间比该阈值要早，则跳过下载
                    if not is_latest_than(threshold_ctime, resource):
                        continue

                    pdf_query = set_queryData_of_pdf(resource, auth_token)
                    
                    if is_three_level:
                        download(
                            API_URL_RESOURCE_ITEM,
                            pdf_query,
                            firstcategory,
                            secondcategory,  # 二级分类名
                            item['title']   # 三级分类名
                        )
                    else:
                        download(
                            API_URL_RESOURCE_ITEM,
                            pdf_query,
                            firstcategory,
                            item['title']  # 二级分类名
                        )

       
@log_exit_time
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

    threshold_ctime = get_threshold_time()
    print(f"时间阈值: {threshold_ctime}")

    try:
        batch_download_resources(args.token, threshold_ctime)
    except Exception as e:
        print(f"程序运行出错: {e}")
        raise
    

   