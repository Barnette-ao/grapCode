from getRequest import simple_get_request_with_cookie
from helpFunc import (
    isDoc,
    extract_page_number_bs4,
    process_html_to_links,
    extract_p_bs4,
    get_article_title,
    generate_date_range,
    extract_keyword_match_number_bs4
)
from getThresholdTime import get_threshold_time, get_date_of_today
from logger import log_exit_time
from postRequest import postRequest_with_cookie
import saveToWord
import os
import json
import argparse  
import re
from datetime import datetime
from urllib.parse import quote

BASE_URL = "https://www.gwsxwk.cn"

def get_html_text(date, cookie_str, page):
    """
    获取HTML文本
    """
    target_url = f"https://www.gwsxwk.cn/index/search/index.html?keyword={date}&search_type=10&page={page}"

    html_text = simple_get_request_with_cookie(url, cookie_str)
    print("html_text",html_text)
    return html_text


def get_max_page(html_text):
    """
    获取最大页数
    """
    if(html_text):
        max_page = extract_page_number_bs4(html_text)
        return max_page


def get_article_links(html_text):
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




def download_article_content(text_objects):
    if text_objects == "访问过于频繁":
        print(f"[ERROR] 访问过于频繁: {article_link_href}")
    
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
    # 1. 构建请求参数
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

    title_with_ext = get_article_title(article_link['title'])
    filepath = f"{date}/{title_with_ext}"
    
    title = get_article_title(article_link['title'], False)
    if not title:
        print(f"[ERROR] 无法解析文章标题: {article_link['title']}")
        return True
    
    if os.path.exists(filepath):
        print(f"文件已下载，且不允许覆盖。")
        return True
    elif is_exist_in_gongwenwang(
            keyword = title,
            gongwen_cookie_value = gongwen_cookie
         ):
         print(f"文件已上传，且不允许覆盖。")
         return True
    else:
        return False

def download_article_by_date(gwsxwk_cookie_str, date, gongwen_cookie):
    # 1. 获取最大页数
    max_page = get_max_page(date, gwsxwk_cookie_str)
    print("max_page",max_page)

    for page in range(1, max_page + 1):
        print(f"----{date}-----{page}-----")
        # 2. 获取每一页文章链接
        article_links = get_article_links(date, page, gwsxwk_cookie_str)

        # 3. 遍历文章
        for article_link in article_links:
            
            # 检查文件是否需要下载
            if is_not_need_download(article_link, date, gongwen_cookie):
                continue

            # 4. 构建完整URL
            article_link_href = get_article_link(article_link["href"])
            
            # 5. 下载文章
            dowbload_article_content(article_link_href, gwsxwk_cookie_str, date)
        

    

log_file="program_interrupt_web.log"

@log_exit_time(log_file)
def batched_download_article_by_date():
    parser = argparse.ArgumentParser(description="批量下载DOCX资源")
    parser.add_argument("--gwsxwk_cookie",required=True, type=str, help="思享公文认证Cookie")
    parser.add_argument("--gongwen_cookie",required=True, type=str, help="公文网认证Cookie")
    
    args = parser.parse_args()
    
    start_date = get_threshold_time(log_file=log_file ,is_gwsxwk=True)
    end_date = get_date_of_today()

    dates = generate_date_range(start_date, end_date)
    if not dates:
        print("没有需要下载的日期")
        exit()
    
    
    for date in dates:
        print(f"----{date}-----")
        download_article_by_date(args.gwsxwk_cookie, date, args.gongwen_cookie)

if __name__ == "__main__":
    # date = "20250725"
    # page = 2
    # gwsxwk_cookie_str="Hm_lvt_17a6d79f196bd7dceed5aefb62507766=1752462197,1752478580; Hm_lvt_4e353b346bb9049b942dfe452e3934f8=1752462197,1752478580; Hm_lvt_17a6d79f196bd7dceed5aefb62507766=1752462197,1752478580,1753318471; HMACCOUNT=7A74DE55FF3EA8AC; Hm_lvt_4e353b346bb9049b942dfe452e3934f8=1752462197,1752478580,1753318471; Hm_lpvt_17a6d79f196bd7dceed5aefb62507766=1753411543; Hm_lpvt_4e353b346bb9049b942dfe452e3934f8=1753411543; PHPSESSID=k9lqjtij112m7cmp75g36rfna7; Hm_lpvt_17a6d79f196bd7dceed5aefb62507766=1753502232; Hm_lpvt_4e353b346bb9049b942dfe452e3934f8=1753502232"
    # article_links = get_article_links(date, page, gwsxwk_cookie_str)
    # print("article_links",article_links)
   
    # max_page = get_max_page(date, gwsxwk_cookie_str)
    # print("max_page",max_page)
    batched_download_article_by_date()

    


    

