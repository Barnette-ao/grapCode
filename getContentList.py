import requests
import json

# 目标 URL
content_url = "https://ht.axuex.top/api/Resource/allsort?from_id=&plat_form=mp-weixin"  # 示例 API

def simplify_tree(node):
    """
    递归：保留树形结构，只取 id 和 name
    """
    if not node:                      # 空节点返回 None
        return None
    
    simplified = {
        "id": node["id"],
        "name": node["name"],
        "children": []
    }
    
    # 递归处理子节点
    for child in node.get("children", []):
        simplified["children"].append(simplify_tree(child))
    return simplified

def getContentList():
    try:
        # 发送 GET 请求
        response = requests.get(content_url)
        
        # 检查请求是否成功（HTTP 状态码 200）
        if response.status_code == 200:
            # print(json.dumps(response.json(), indent=4, ensure_ascii=False))
            raw_list = response.json()["data"]["list"]
            contentList = [simplify_tree(node) for node in raw_list]
            # for index, list_item in enumerate(response.json()["data"]["list"]):
            #     result = transform_data(list_item)
            #     contentList.append(result)
            #     # print(json.dumps(result, indent=4, ensure_ascii=False))
            #     # print("------------------------")

            return contentList   
        else:
            print(f"请求失败，状态码：{response.status_code}")
            print("响应内容：", response.text)  # 原始响应文本

    except requests.exceptions.RequestException as e:
        print("请求异常：", e)




def normalize_content_list():
    contentList = getContentList()
    if not contentList:
        return []
    else: 
        return [x for x in contentList if x and x.get("children", [])]

# normalize_content_list()
# print(json.dumps(normalize_content_list(), indent=4, ensure_ascii=False))
