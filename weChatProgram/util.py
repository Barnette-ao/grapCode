import sys
sys.path.append('..')

from libs.getRequest import simple_get_request_with_cookie
import re
import json 

# 在之后构建form-data时需要categoryId,和parentId,但是类别接口返回的数据和现在的目录结构不匹配
# 先锋学霸资料\二年级上册\语文\预习资料\二年级（上）语文《识字表》生字音节音序部首组词.pdf
# 先锋学霸资料去掉，二年级上册改为二年级上，预习资料\二年级（上）语文《识字表》生字音节音序部首组词.pdf去掉，二年级上册\语文
def process_path(path):
    # 1. 移除开头的"先锋学霸资料\"
    path = re.sub(r'^先锋学霸资料\\', '', path)
    
    # 2. 替换"上册"->"上"，"下册"->"下"
    path = path.replace('上册', '上').replace('下册', '下')

    parts = path.split('\\')
    if len(parts) >= 2:
        return f"{parts[0]}\\{parts[1]}"
    return path
    
def get_category_data():
    """
    准备表单数据
    """
    # 获取所有类别的编号
    category_tree=simple_get_request_with_cookie(
        url="http://211.154.30.100:8222/base/category/treeData",
        cookie_value="wenku-session-id=40b76a5b-5c47-4eb2-bb27-44a4b8d6653c"
    )
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

def get_category_id_pid(category_data, category_name, parent_category_name):
    """
    根据类别名称在类别数据中查找对应的ID和对应的父类别ID
    """
    candidates = [item for item in category_data if item['name'] == category_name]
    
    # 情况1：无匹配项
    if not candidates:
        print(f"未找到类别名称为 {category_name} 的项")
        return None
    
    # 情况2：唯一匹配项
    if len(candidates) == 1:
        return candidates[0]['id']
    
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

def get_categoryId_with_parentId(file_path,category_data):
    """
    根据文件路径获取对应的categoryId和parentId和categoryName
    """
    [parent_category, category] = process_path(file_path).split('\\')
    category_ids = get_category_id_pid(category_data, category, parent_category)
    if category_ids:
        [categoryId, parentId] = category_ids
    else:
        return None    
    return [categoryId, parentId, category]