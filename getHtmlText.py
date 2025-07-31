from getRequest import simple_get_request_with_cookie
from helpFunc import (
    isDoc,
    extract_page_number_bs4,
    process_html_to_links,
    extract_p_bs4,
    get_article_title,
    generate_date_range,
    extract_keyword_match_number_bs4,
    save_all_article_links,
    load_article_links_by,
    remove_date_from_cache,
)
from getThresholdTime import GwsxwkTimeExtractor
from logger import log_exit_time_with_date
from postRequest import postRequest_with_cookie
import saveToWord
import os
import json
import argparse  
import re
from datetime import datetime
from urllib.parse import quote
import pydash as _


BASE_URL = "https://www.gwsxwk.cn"

LOG_FILE="program_interrupt_web.log"

def get_html_text(date, cookie_str, page):
    """
    获取HTML文本
    """
    target_url = f"https://www.gwsxwk.cn/index/search/index.html?keyword={date}&search_type=10&page={page}"

    html_text = simple_get_request_with_cookie(target_url, cookie_str)
    # print("html_text",html_text)
    return html_text


def get_max_page(html_text):
    """
    获取最大页数
    """
    if(html_text):
        max_page = extract_page_number_bs4(html_text)
        return max_page


def get_article_links(html_text, date):
    """
    获取文章链接
    """ 
    if(html_text):
        unique_links = process_html_to_links(html_text)
    
        filtered_unique_links = list(
            filter(
                lambda x: str(x.get('title', '')).startswith(date),
                unique_links
            )
        )
        # print(filtered_unique_links)
        return filtered_unique_links


def get_all_article_links(date, cookie_str):
    """
    获取某一日所有的文章链接
    """
    def safe_extend(target_list, source_items):
        """安全扩展列表，自动过滤空值和非可迭代对象"""
        if source_items and isinstance(source_items, (list, tuple, set, frozenset)):
            target_list.extend(source_items)

    all_article_links = []

    # 1.首先访问第一页的文章情况
    html_text = get_html_text(date, cookie_str, 1)
    if not html_text:
        print(f"[ERROR] 无法获取页面内容: {date} - {cookie_str}")
        return None
    
    # 2. 提取最大页数
    max_page = get_max_page(html_text)
    print(max_page)
    

    # 3. 获取第一页的文章链接文章链接,并安全加入all_article_links
    safe_extend(all_article_links, get_article_links(html_text, date))

    # 4. page > 1 的情况,分别遍历每一页，找到每一页的文章链接并安全加入all_article_links
    if max_page > 1:
        for page in range(2, max_page + 1):
            html_text = get_html_text(date, cookie_str, page)
            if not html_text:
                print(f"[ERROR] 无法获取页面内容: {date} - {cookie_str}")
                return None

            safe_extend(all_article_links, get_article_links(html_text,date))

    return all_article_links



def get_article_link(href):
    """
    获取文章链接
    """
    return f"{BASE_URL}{href}"
    

# 访问链接1次
def request_article_html(article_link, cookie_str, date):
    """
    下载文章内容
    Args:
        article_link: 文章URL
        cookie_str: 认证Cookie
        date: 日期
        
    Returns:
        str: 成功时返回特定文章的Html文本内容，失败时返回None
    """
    # 1. 获取文章的HTML链接
    article_link_href = f"{BASE_URL}{article_link['href']}"

    # 2. 获取文章的HTML内容
    html_text = simple_get_request_with_cookie(article_link_href, cookie_str)
    if not html_text:
        print(f"[ERROR] 无法获取文章内容: {article_link_href}")
        return None

    # 3. 解析文章的文本对象
    try:
        text_objects = extract_p_bs4(html_text)
        return text_objects
    except Exception as e:
        print(f"[ERROR] 解析失败: {str(e)}")
        return None



def download_article_content(date, text_objects):
    # 4. 保存文件
    output_path = f"{date}/{text_objects[0]['text']}.docx"  # 使用第二段作为文件名
    try:
        saveToWord.save_to_word(text_objects, output_path)
        return output_path
    except Exception as e:
        print(f"[ERROR] 文件保存失败: {str(e)}")
        return None

def is_exist_in_gongwenwang(keyword, gongwen_cookie_value):
    """
    检查文章是否已存在于公网网
    """
    # 1. 构建请求参数，将关键词进行URL编码
    print("keyword",keyword)
    q_param = quote(keyword)

    response = simple_get_request_with_cookie(
        url= f"https://wx.06179.com/doc/search.html?q={q_param}",
        cookie_value = gongwen_cookie_value, 
    )

    # print("response",response)
    return extract_keyword_match_number_bs4(response) > 0



def is_not_need_download(article_link, date, gongwen_cookie):
    """
    检查文件是否需要下载
    """
    if not isDoc(article_link['title']):
        print(f"文件不是doc类型，不允许下载。")
        return True

    
    # get_article_title(article_link['title'])会返回不带有扩展名的文件名
    title = get_article_title(article_link['title'], False)
    # 过滤掉title是""，空字符串的情况
    if not title:
        print(f"[ERROR] 无法解析文章标题: {article_link['title']}")
        return True
    

    # get_article_title(article_link['title'])会返回带有扩展名的文件名
    filepath = f"{date}/{get_article_title(article_link['title'])}"
    if os.path.exists(filepath):
        print(f"文件已下载，且不允许覆盖。")
        return True

    elif is_exist_in_gongwenwang(
            keyword = title,
            gongwen_cookie_value = gongwen_cookie
         ):
         print(f"文件已上传，且不允许覆盖。")
         return True
    
    return False



@log_exit_time_with_date(LOG_FILE)
def download_article_by_date(gwsxwk_cookie_str, date, gongwen_cookie):
    # 如果缓存中不存在该日期的article_links，则从思享公文网获取所有article_links并保存到缓存中   
    if not load_article_links_by(date):
        article_links = get_all_article_links(date, gwsxwk_cookie_str)
        print("抓取的全部文章链接,article_links",article_links)    
        save_all_article_links(article_links, date)
    # 如果缓存中已经存在该日期的article_links，则直接读取缓存中的article_links
    else:
        article_links = load_article_links_by(date)

    print("article_links",article_links)

    # 3. 遍历该date下每一篇文章链接字典元素
    for article_link in article_links:
        # 检查文件是否需要下载
        if is_not_need_download(article_link, date, gongwen_cookie):
            continue
        # 4. 请求文章html内容
        text_objects = request_article_html(article_link, gwsxwk_cookie_str, date)
        # 5. 如果text_objects访问过于频繁
        if text_objects == "访问过于频繁":
            print(f"[ERROR] 访问过于频繁: {get_article_link(article_link['href'])}")
            # 查找当前article_link在article_links中的索引
            index = _.find_index(article_links, article_link)
            # 从article_links中删除当前article_link之前的所有元素
            article_links = article_links[index:]
            save_all_article_links(article_links, date)          
            # 手动触发异常
            raise Exception("访问过于频繁")  

        # 6. 下载文章内容
        download_article_content(date, text_objects)
    
    # 7. 清空date这一日的缓存
    remove_date_from_cache(date)

    

def batched_download_article_by_date():
    parser = argparse.ArgumentParser(description="批量下载DOCX资源")
    parser.add_argument("--gwsxwk_cookie",required=True, type=str, help="思享公文认证Cookie")
    parser.add_argument("--gongwen_cookie",required=True, type=str, help="公文网认证Cookie")
    
    args = parser.parse_args()
    
    # 1. 获取开始日期和结束日期
    gwsxwk_extractor = GwsxwkTimeExtractor(log_file=LOG_FILE)
    start_date = gwsxwk_extractor.get_threshold_time()
    end_date = gwsxwk_extractor.get_date_of_today()

    dates = generate_date_range(start_date, end_date)
    if not dates:
        print("没有需要下载的日期")
        exit()
    
    print("dates",dates)

    
    for date in dates:
        print(f"----{date}-----")
        download_article_by_date(args.gwsxwk_cookie, date, args.gongwen_cookie) 

if __name__ == "__main__":
    date = "20250726"
    # page = 2
    gongwen_cookie = "gws_keeplogin=B19UDAVRAwVKAwwBAxcMAQlJAwUACQUFSQQCAAEBAQEJAQBJAgMGVFwMWgwCVgEFVQcNUlUJAA0NUwIHUV0BDAEBAVETCg___c___c; PHPSESSID=misgoeguk7i8f7lgsq99if8sjv; gws_search_history=U10CVAcFBARYAwgPQlwPBQpGDwQBCxfSjrHSjrLSoarXgY7Ria4TDkQ___c; Hm_lvt_1f013c54a127ce2677327e03b2f2dcaf=1752713947,1753080385,1753318311,1753864190; HMACCOUNT=7A74DE55FF3EA8AC; Hm_lpvt_1f013c54a127ce2677327e03b2f2dcaf=1753864383"
    gwsxwk_cookie_str="Hm_lvt_17a6d79f196bd7dceed5aefb62507766=1752462197,1752478580,1753318471; Hm_lvt_4e353b346bb9049b942dfe452e3934f8=1752462197,1752478580,1753318471; PHPSESSID=5eu5kc5cmjlpuoki5vmn2uva1n; HMACCOUNT=7A74DE55FF3EA8AC; Hm_lvt_17a6d79f196bd7dceed5aefb62507766=1752462197,1752478580,1753318471; Hm_lvt_4e353b346bb9049b942dfe452e3934f8=1752462197,1752478580,1753318471; Hm_lpvt_17a6d79f196bd7dceed5aefb62507766=1753864383; Hm_lpvt_4e353b346bb9049b942dfe452e3934f8=1753864383"
    # article_links = get_article_links(date, page, gwsxwk_cookie_str)
    # print("article_links",article_links)
   
    # max_page = get_max_page(date, gwsxwk_cookie_str)
    # print("max_page",max_page)
    # batched_download_article_by_date()

    # download_article_by_date(gwsxwk_cookie_str, date, gongwen_cookie)

    batched_download_article_by_date()

    


    

