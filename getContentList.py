import requests
import json

# 目标 URL
content_url = "https://ht.axuex.top/api/Resource/allsort?from_id=&plat_form=mp-weixin"  # 示例 API

def transform_data(input_data):
    output = {
        "sort_id": input_data["id"],
        "title": input_data["name"],        
        "categoraylist": {}
    }

    # 没有children字段或者children列表为空，这返回
    if (not input_data.get("children")): 
        return 

    if (len(input_data["children"][0]["children"]) == 0): return 
    
    for category in input_data["children"]:
      # 遍历第一层的children（小学、初中、高中分类）
      categoryname = category["name"]
      output["categoraylist"][categoryname] = []

      for subcategory in category["children"]:  
        output["categoraylist"][categoryname].append({
            "sort_id": subcategory["id"],
            "title": subcategory["name"]
        })
    
    return output

def getContentList():
    try:
        contentList = []
        # 发送 GET 请求
        response = requests.get(content_url)
        
        # 检查请求是否成功（HTTP 状态码 200）
        if response.status_code == 200:
            # print("请求成功！")
            for index, list_item in enumerate(response.json()["data"]["list"]):
                result = transform_data(list_item)
                contentList.append(result)
                # print(json.dumps(result, indent=4, ensure_ascii=False))
                # print("------------------------")

            return contentList   
        else:
            print(f"请求失败，状态码：{response.status_code}")
            print("响应内容：", response.text)  # 原始响应文本

    except requests.exceptions.RequestException as e:
        print("请求异常：", e)




def normalize_content_list():
    contentList = getContentList()
    return list(filter(lambda x: x is not None, contentList))

# print(json.dumps(filtered_list, indent=4, ensure_ascii=False))
# print(normalize_content_list()) 