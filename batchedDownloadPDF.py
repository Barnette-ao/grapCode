import json
import simple_download_pdf
import getContentList
import postRequest

# API_URL_RESOURCE_ITEM: 单个资源的信息API地址
# API_URL_RESOURCE_LIST: 资源列表API地址
API_URL_RESOURCE_ITEM = "https://ht.axuex.top/api/Resource/resdetail?from_id="  # 示例 API

API_URL_RESOURCE_LIST = "https://ht.axuex.top/api/Resource/resource?from_id="  # 示例 API


def set_queryData_of_pdf(resource,token):
    return dict(
        id = resource['id'],
        token = token,
        plat_form = "mp-weixin"
    )
        
# print(postRequest(postUrl, queryData))
def get_resource_list(postUrl, queryData):
    response = postRequest.postRequest(postUrl, queryData)
    if response['code'] == 200:
        print("请求成功！")
        # print(json.dumps(response, indent=4, ensure_ascii=False))
        return response['data']['list']


def download(postUrl,queryData,firstcategory,secondcategory,thirdcategory=''):
    response = postRequest.postRequest(postUrl, queryData)
    # print(json.dumps(response, indent=4, ensure_ascii=False))
    if response['code'] == 200:
        url = response['data']['link']
        filename = response['data']['title'] + '.pdf'

        params = {
            "base_dir": "先锋学霸资料",
            "firstcategory": firstcategory,
            "secondcategory": secondcategory,
            "filename": filename,
            "thirdcategory": thirdcategory
        }
        
        # 构建路径
        save_path = simple_download_pdf.build_save_path(**params)
        simple_download_pdf.simple_download_pdf(url, save_path)

def build_query_params(sort_id, extra_params=None):
        """构建资源查询参数"""
        params = {
            'sort_id': sort_id,
            'page': 1,
            'limit': 9999,
            'type': 0,
            'plat_form': "mp-weixin"
        }
        if extra_params:
            params.update(extra_params)
        return params

def download_resources_by_category(content_list, auth_token):
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

                # 下载每个资源
                for resource in resource_list:
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

if __name__ == "__main__":
    contentlist = getContentList.normalize_content_list()
    # print(len(contentlist))
    # download_resources_by_category(
    #     content_list = contentlist, 
    #     auth_token = "386c0d996d9bee266b55f4aa938e374d"
    # )

    for content in contentlist:
        if(len(content['categoraylist']) == 1):
            for firstcategory, itemList in content['categoraylist'].items():
                for item in itemList:
                    sort_id, secondcategory = item['sort_id'], item['title']
                    resource_list = get_resource_list(API_URL_RESOURCE_LIST, dict(
                        sort_id = sort_id,
                        page = 1,
                        limit = 9999,
                        type = 0,
                        plat_form = "mp-weixin"
                    ))
                    # print(resource_list)
                    for resource in resource_list:
                        pdf_queryData = set_queryData_of_pdf(resource,"386c0d996d9bee266b55f4aa938e374d")
                        # print(pdf_queryData)
                        download(API_URL_RESOURCE_ITEM, pdf_queryData, firstcategory, secondcategory)

        elif(len(content['categoraylist']) > 1):
            for secondcategory, itemList in content['categoraylist'].items():
                for item in itemList:
                    sort_id, thirdcategory = item['sort_id'], item['title']
                    resource_list = get_resource_list(API_URL_RESOURCE_LIST, dict(
                        sort_id = sort_id,
                        page = 1,
                        limit = 9999,
                        order = 0,
                        keys = "",
                        edition = 0,
                        type = 0,
                        plat_form = "mp-weixin"
                    ))
                    for resource in resource_list:
                        pdf_queryData = set_queryData_of_pdf(resource,"386c0d996d9bee266b55f4aa938e374d")
                        download(API_URL_RESOURCE_ITEM, pdf_queryData, content['title'], secondcategory, thirdcategory)
    # print(lens)

    # queryData = set_queryData_of_pdf(resouce,"386c0d996d9bee266b55f4aa938e374d")

    # download(postUrl, queryData3, "一年级上册", "语文", "词句专项")