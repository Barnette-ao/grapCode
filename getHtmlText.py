import getRequest
import helpFunc
import saveToWord
import os
import json
from postRequest import postRequest_with_cookie


BASE_URL = "https://www.gwsxwk.cn"

def get_max_page(date, cookie_str):
    """
    获取最大页数
    """
    target_url = f"https://www.gwsxwk.cn/index/search/index.html?keyword={date}&search_type=10"

    html_text = getRequest.simple_get_request_with_cookie(target_url, cookie_str)
    if(html_text):
        max_page = helpFunc.extract_page_number_bs4(html_text)
        return max_page


def get_article_links(date, page, cookie_str):
    """
    获取文章链接
    """ 
    target_url = f"https://www.gwsxwk.cn/index/search/index.html?keyword={date}&search_type=10&page={page}"

    html_text = getRequest.simple_get_request_with_cookie(target_url, cookie_str)
    # print(html_text)

    if(html_text):
        unique_links = helpFunc.process_html_to_links(html_text)
        filtered_unique_links = list(
            filter(
                lambda x: str(x.get('title', '')).startswith('20250713'),
                unique_links
            )
        )
        # print(filtered_unique_links)
        return filtered_unique_links


def get_article_link(href):
    """
    获取文章链接
    """
    return f"{BASE_URL}{href}"
    


def dowbload_article_content(article_link, cookie_str, date):
    """
    下载文章内容
    Args:
        article_link: 文章URL
        cookie_str: 认证Cookie
        
    Returns:
        str: 成功时返回文件路径，失败返回None
    """
    # 1. 获取HTML内容
    html_text = getRequest.simple_get_request_with_cookie(article_link, cookie_str)
    if not html_text:
        print(f"[ERROR] 无法获取文章内容: {article_link}")
        return None

    # 2. 解析文本对象
    try:
        text_objects = helpFunc.extract_p_bs4(html_text)
        if not text_objects or len(text_objects) < 2:
            print(f"[WARNING] 无有效内容: {article_link}")
            return None
    except Exception as e:
        print(f"[ERROR] 解析失败: {str(e)}")
        return None
   
    # 3. 保存文件
    output_path = f"{date}/{text_objects[1]['text']}.docx"  # 使用第二段作为文件名
    try:
        saveToWord.save_to_word(text_objects, output_path)
        return output_path
    except Exception as e:
        print(f"[ERROR] 文件保存失败: {str(e)}")
        return None

def is_exist_in_gongwenwang(cookie_value,queryData):
    """
    检查文章是否已存在于公网网
    """
    resource = postRequest_with_cookie(
        postUrl= "https://wx.06179.com/article/article/init.html",
        cookie_value = cookie_value, 
        queryData = queryData 
    )
    print("请求成功",json.dumps(resource, indent=4, ensure_ascii=False))
    if resource["status"] == 200:
        return len(resource["data"]) > 0


def is_not_need_download(article_link, date):
    """
    检查文件是否需要下载
    """
    # 不能直接写死docx格式，以及标题不能正确获取到，要进行验证才知道
    filepath = f"{date}/{article_link['title'][12:]}.docx"
    if os.path.exists(filepath):
        print(f"文件已下载，且不允许覆盖。")
        return True
    elif is_exist_in_gongwenwang(
        cookie_value = "Hm_lvt_1f013c54a127ce2677327e03b2f2dcaf=1752462376; gws_keeplogin=CQ4EBAxXCQBKAwwBAxcMAQlJAwUACQUFSQQCAAYFAwIADQBJBVBXBAtUDAYFAgdQUgwEUlMHVFdaUFZRAF0HAFFRBAwTCg___c___c; PHPSESSID=v966cok4relipmqlo5kc2j5mls; breadcrumb_0=; menu_0=[{%22title%22:%22%E6%96%87%E7%AB%A0%E7%AE%A1%E7%90%86%22%2C%22url%22:%22https://wx.06179.com/article/article/init.html%22%2C%22fullurl%22:%22https://wx.06179.com/article/article/init.html%22}]"
        ,queryData = { "sort": "", "order": "", "limit": 20, "page": 1, "title": "在单身青年联谊会上的致辞：以爱搭桥促良缘，携手同行谱新篇"}
        ):
        print(f"文件已上传，且不允许覆盖。")
        return True
    else:
        return False

if __name__ == "__main__":
    date = "20250713"
    cookie_str = "Hm_lvt_4e353b346bb9049b942dfe452e3934f8=1752462197,1752478572; HMACCOUNT=7A74DE55FF3EA8AC; Hm_lvt_17a6d79f196bd7dceed5aefb62507766=1752462197,1752478572; Hm_lvt_17a6d79f196bd7dceed5aefb62507766=1752462197,1752478580; Hm_lpvt_17a6d79f196bd7dceed5aefb62507766=1752478580; HMACCOUNT=7A74DE55FF3EA8AC; Hm_lvt_4e353b346bb9049b942dfe452e3934f8=1752462197,1752478580; Hm_lpvt_4e353b346bb9049b942dfe452e3934f8=1752478580; PHPSESSID=vauj75ff4r2t4vgcm01fjr5fjc; Hm_lpvt_17a6d79f196bd7dceed5aefb62507766=1752550245; Hm_lpvt_4e353b346bb9049b942dfe452e3934f8=1752550245"

    # 1. 获取最大页数
    max_page = get_max_page(date, cookie_str)

    for page in range(1, max_page + 1):
        # 2. 获取每一页文章链接
        article_links = get_article_links(date, page, cookie_str)

        # 3. 遍历文章
        for article_link in article_links:
            
            # 检查文件是否已存在
            if is_need_download(article_link, date):
                
                continue

            # 4. 构建完整URL
            article_link = get_article_link(article_link["href"])
            print(f"[INFO] 开始下载: {article_link}")
            
            # 5. 下载文章
            dowbload_article_content(article_link, cookie_str, date)


    # article_link = "https://www.gwsxwk.cn/index/article/detail/detail_id/183742.html"
    # html_text = getRequest.simple_get_request_with_cookie(article_link, cookie_str)
    # print(html_text)
    # text_objects = helpFunc.extract_p_bs4(html_text)
    # print(text_objects)
