公文网，cookie = “Hm_lvt_1f013c54a127ce2677327e03b2f2dcaf=1752462376; gws_keeplogin=CQ4EBAxXCQBKAwwBAxcMAQlJAwUACQUFSQQCAAYFAwIADQBJBVBXBAtUDAYFAgdQUgwEUlMHVFdaUFZRAF0HAFFRBAwTCg___c___c; PHPSESSID=v966cok4relipmqlo5kc2j5mls; breadcrumb_0=; menu_0=[{%22title%22:%22%E6%96%87%E7%AB%A0%E7%AE%A1%E7%90%86%22%2C%22url%22:%22https://wx.06179.com/article/article/init.html%22%2C%22fullurl%22:%22https://wx.06179.com/article/article/init.html%22}]”

可以从标题来判断文章是否是PPT
XXX PPT / ppt / 讲稿+PPT / PPT+讲稿

先来下载一个PPT

写一段伪代码：
现在知道搜出来的文件只有两种类型，一种是ppt，一种是doc或者docx
根据搜出来的各个标题做判断，判断其是PPT还是DOC

用字符串包含的方式
```pytho
title = "Hello, World"
substring = "ppt"

if substring.lower() in title.lower():
    print("是ppt")
    if 只是ppt:
        下载ppt
    elif 是ppt+doc:
        下载ppt+doc
else:
    print("是doc")
    下载doc
```
--------------------------------------------------------------------------------
这里需要注意新建的文件名不能包含：，但是有些PPT的标题是用doc的方式提取文件名是会有冒号的
比如：2025031506：PPT：2025年“两会”政府工作报告新变化新提法解读

用doc的方式提取，返回PPT：2025年“两会”政府工作报告新变化新提法解读
不能将其作为文件名

自动化设置时间下载
日志的格式：
下载的开始时间：20250715 结束时间：20250715

开始时间设置为日志的结束时间的后一天，一开始没有日志，那么开始时间默认为20250715
结束时间设置为命令执行的当天
然后在命令执行完后，将命令执行的当天作为结束时间写入日志

这分为存和取两个步骤

-----------------------------------------------------------------------------------------------------

现在getHtml.py没有进一步测试，我昨天修改了检查公文网是否有改文章的函数，单元测试是过了，但是没有继承到getHtml.py中测试
此外，在执行getHtml.py时，执行命令需要两个参数，gwsxwk_cookie(思享公文网的cookie)和gongwen_cookie(公文网的cookie)
执行命令如下：
python getHtml.py --gwsxwk_cookie “具体的思享公文网的cookie” --gongwen_cookie “公文网的cookie”

测试完成

---------------------------------------------------------------------------------------------------

http://211.154.30.100:8222/base/resource/addMuti
Get
批量新增的URL地址
cookie:wenku-session-id=40b76a5b-5c47-4eb2-bb27-44a4b8d6653c

树型类别结构
http://211.154.30.100:8222/base/category/treeData
Get
cookie:wenku-session-id=40b76a5b-5c47-4eb2-bb27-44a4b8d6653c 

批量上传接口
http://211.154.30.100:8222/base/resource/uploadMutiAPI2
Post
cookie:wenku-session-id=40b76a5b-5c47-4eb2-bb27-44a4b8d6653c
content-type:multipart/form-data
form-data:{
    files: (binary),
    pointPrice:10.00,
    downType:2,
    attachAttrFormat:"",
    attachAttrNum:0,
    attachAttrSize:0,
    title:"",
    content:"",
    categoryId:231381,
    parentId:231380,
    categoryName:综合资料,
    filterDetailCode1:"",
    filterDetailCode2:"",
    status:1,
    isTop:0,
    openJili:0,
    vipOnly:1,
}

form-data = {
    categoryId:231381,
    parentId:231380,
    categoryName:综合资料,

    pointPrice:10.00,
    downType:2,
    attachAttrFormat:"",
    attachAttrNum:0,
    attachAttrSize:0,
    title:"",
    content:"",
    filterDetailCode1:"",
    filterDetailCode2:"",
    status:1,
    isTop:0,
    openJili:0,
    vipOnly:1,
}

categoryId:231381,
parentId:231380,
categoryName:综合资料,

如果批量上传5个文件，那form-data中就会有5个files，全是文件的二进制

def upload_all_pdfs():
    # 1. 收集所有PDF文件
    base_dir = "weChatProgram/先锋学霸资料"
    pdf_files = collect_pdf_files(base_dir)
    
    if not pdf_files:
        print("未找到任何PDF文件")
        return
    
    # 2. 准备上传数据
    files = []
    for file_path in pdf_files:
        file_name = os.path.basename(file_path)
        files.append(('files', (file_name, open(file_path, 'rb'), 'application/pdf')))
    
    # 3. 其他表单数据（根据API要求）
    form_data = {
        "pointPrice": "10.00",
        # ...其他字段...
    }
    
    # 4. 发送请求（使用您的原始上传逻辑）
    try:
        response = requests.post(
            API_URL,
            files=files,
            data=form_data,
            headers={"Cookie": COOKIE}
        )
        print("上传结果:", response.json())
    finally:
        # 确保关闭所有文件
        for file_tuple in files:
            file_tuple[1][1].close()


['拼音资料', '笔画练习', '识字描红', '口算计算', '暑假预习', '专项练习', '知识汇总', '古诗背诵', '数学试卷', '语文试卷', '英语资料', '综合分类']
---------------------------------------------------------------------
小程序   | 先锋网络
------------------
已确定的分类对应关系
拼音资料 | 拼音资料 
笔画练习 | 控笔练习
识边描红 | 识边描红
暑假预习 | 暑假预习
口算计算 | 口算计算
古诗背诵 | 古诗背诵
数学试卷 | 数学试卷
语文试卷 | 语文试卷
英语资料 | 英语资料
综合分类   综合资料
--------------------- 
不确定的分类对应关系
专项练习 | 数学专项，语文专项
知识汇总

import requests
import json
from . import helpFunc
import os
from weChatProgram import simple_download_pdf
from tqdm import tqdm
from requests_toolbelt import MultipartEncoder
from requests_toolbelt.multipart.encoder import CustomBytesIO


# 目标 URL


------------------------------------------
测试上传记录
1.会报POST 请求失败，状态码：502，就是主要的request请求会502的错误,因为一次传了68个文件
2.不好贸然去做上传进度条
3.如果一个文件夹上传成功了，仅仅根据response的反馈信息来看，我并不知道那个文件夹里面的文件上传成功了
4.要单独测试幼小衔接
5.上传的诸多限制并没有在代码中体现出来，一次最多上传50个文件，总大小不能超过500M，单文件最多不超过200M     

------------------------------------------
20250725 思享公文搜索cookie
Hm_lvt_17a6d79f196bd7dceed5aefb62507766=1752462197,1752478580,1753318471; HMACCOUNT=7A74DE55FF3EA8AC; Hm_lvt_4e353b346bb9049b942dfe452e3934f8=1752462197,1752478580,1753318471; PHPSESSID=tq7ucm9l7gh2o3e19octg37klo; Hm_lpvt_17a6d79f196bd7dceed5aefb62507766=1753405770; Hm_lpvt_4e353b346bb9049b942dfe452e3934f8=1753405770
20250725 公文网搜索cookie
PHPSESSID=lmdl6uhpqs1cr7v7ts6hcdh46o; breadcrumb_0=; menu_0=[{%22title%22:%22%E6%96%87%E7%AB%A0%E7%AE%A1%E7%90%86%22%2C%22url%22:%22https://wx.06179.com/article/article/init.html%22%2C%22fullurl%22:%22https://wx.06179.com/article/article/init.html%22}]; Hm_lvt_1f013c54a127ce2677327e03b2f2dcaf=1752462376,1752713947,1753080385,1753318311; HMACCOUNT=7A74DE55FF3EA8AC; gws_keeplogin=Bw0GBw1RAAFKAwwBAxcMAQlJAwUACQUFSQQCAAYMBwADDABJBQcJDQ1WCA1WVgxRUlBXUQFVBVZYAFEBUl0AAABUBwATCg___c___c; gws_search_history=U10CVAcFBARYAwgPQlwPBQpGDwQBCxfSjrHSjrLSoarXgY7Ria4TDkQ___c; Hm_lpvt_1f013c54a127ce2677327e03b2f2dcaf=1753405872

0725 getHtmlText.py的命令
python getHtmlText.py --gwsxwk_cookie "Hm_lvt_17a6d79f196bd7dceed5aefb62507766=1752462197,1752478580,1753318471; HMACCOUNT=7A74DE55FF3EA8AC; Hm_lvt_4e353b346bb9049b942dfe452e3934f8=1752462197,1752478580,1753318471; PHPSESSID=tq7ucm9l7gh2o3e19octg37klo; Hm_lpvt_17a6d79f196bd7dceed5aefb62507766=1753405770; Hm_lpvt_4e353b346bb9049b942dfe452e3934f8=1753405770" --gongwen_cookie "PHPSESSID=lmdl6uhpqs1cr7v7ts6hcdh46o; breadcrumb_0=; menu_0=[{%22title%22:%22%E6%96%87%E7%AB%A0%E7%AE%A1%E7%90%86%22%2C%22url%22:%22https://wx.06179.com/article/article/init.html%22%2C%22fullurl%22:%22https://wx.06179.com/article/article/init.html%22}]; Hm_lvt_1f013c54a127ce2677327e03b2f2dcaf=1752462376,1752713947,1753080385,1753318311; HMACCOUNT=7A74DE55FF3EA8AC; gws_keeplogin=Bw0GBw1RAAFKAwwBAxcMAQlJAwUACQUFSQQCAAYMBwADDABJBQcJDQ1WCA1WVgxRUlBXUQFVBVZYAFEBUl0AAABUBwATCg___c___c; gws_search_history=U10CVAcFBARYAwgPQlwPBQpGDwQBCxfSjrHSjrLSoarXgY7Ria4TDkQ___c; Hm_lpvt_1f013c54a127ce2677327e03b2f2dcaf=1753405872"

./getHtmlText.exe --gwsxwk_cookie "Hm_lvt_17a6d79f196bd7dceed5aefb62507766=1752462197,1752478580,1753318471; HMACCOUNT=7A74DE55FF3EA8AC; Hm_lvt_4e353b346bb9049b942dfe452e3934f8=1752462197,1752478580,1753318471; PHPSESSID=tq7ucm9l7gh2o3e19octg37klo; Hm_lpvt_17a6d79f196bd7dceed5aefb62507766=1753405770; Hm_lpvt_4e353b346bb9049b942dfe452e3934f8=1753405770" --gongwen_cookie "PHPSESSID=lmdl6uhpqs1cr7v7ts6hcdh46o; breadcrumb_0=; menu_0=[{%22title%22:%22%E6%96%87%E7%AB%A0%E7%AE%A1%E7%90%86%22%2C%22url%22:%22https://wx.06179.com/article/article/init.html%22%2C%22fullurl%22:%22https://wx.06179.com/article/article/init.html%22}]; Hm_lvt_1f013c54a127ce2677327e03b2f2dcaf=1752462376,1752713947,1753080385,1753318311; HMACCOUNT=7A74DE55FF3EA8AC; gws_keeplogin=Bw0GBw1RAAFKAwwBAxcMAQlJAwUACQUFSQQCAAYMBwADDABJBQcJDQ1WCA1WVgxRUlBXUQFVBVZYAFEBUl0AAABUBwATCg___c___c; gws_search_history=U10CVAcFBARYAwgPQlwPBQpGDwQBCxfSjrHSjrLSoarXgY7Ria4TDkQ___c; Hm_lpvt_1f013c54a127ce2677327e03b2f2dcaf=1753405872" 
---------------------------------------------------------------------

python uploadFile.py --root_dir "先锋学霸资料" --cookie_value "wenku-session-id=7dfd9d80-58fa-4468-aa4d-79d4c01dc273"

batchedDownloadPDF.py --token 386c0d996d9bee266b55f4aa938e374d
-------------------------------------------------------------------------

python getHtmlText.py --gwsxwk_cookie "Hm_lvt_17a6d79f196bd7dceed5aefb62507766=1752462197,1752478580; Hm_lvt_4e353b346bb9049b942dfe452e3934f8=1752462197,1752478580; Hm_lvt_17a6d79f196bd7dceed5aefb62507766=1752462197,1752478580,1753318471; HMACCOUNT=7A74DE55FF3EA8AC; Hm_lvt_4e353b346bb9049b942dfe452e3934f8=1752462197,1752478580,1753318471; Hm_lpvt_17a6d79f196bd7dceed5aefb62507766=1753411543; Hm_lpvt_4e353b346bb9049b942dfe452e3934f8=1753411543; PHPSESSID=k9lqjtij112m7cmp75g36rfna7; Hm_lpvt_17a6d79f196bd7dceed5aefb62507766=1753502232; Hm_lpvt_4e353b346bb9049b942dfe452e3934f8=1753502232" --gongwen_cookie "PHPSESSID=lmdl6uhpqs1cr7v7ts6hcdh46o; breadcrumb_0=; menu_0=[{%22title%22:%22%E6%96%87%E7%AB%A0%E7%AE%A1%E7%90%86%22%2C%22url%22:%22https://wx.06179.com/article/article/init.html%22%2C%22fullurl%22:%22https://wx.06179.com/article/article/init.html%22}]; Hm_lvt_1f013c54a127ce2677327e03b2f2dcaf=1752462376,1752713947,1753080385,1753318311; HMACCOUNT=7A74DE55FF3EA8AC; gws_keeplogin=Bw0GBw1RAAFKAwwBAxcMAQlJAwUACQUFSQQCAAYMBwADDABJBQcJDQ1WCA1WVgxRUlBXUQFVBVZYAFEBUl0AAABUBwATCg___c___c; gws_search_history=U10CVAcFBARYAwgPQlwPBQpGDwQBCxfSjrHSjrLSoarXgY7Ria4TDkQ___c; Hm_lpvt_1f013c54a127ce2677327e03b2f2dcaf=1753405879"

debug过程记录
bug描述：访问文章链接，然后得到的text_object是空数组，找到这个原因
找到原因发现是因为一次访问了100次，标记访问过于频繁

现在我要做的是，每次从代码层面计算和减少访问次数，然后在做到断点续传，每次出现访问过于频繁，之后需要记录一下

_______________________________________________________________
20250728
工作总结：完成了断点续传的基本的框架搭建，
发现了在访问过于频繁的情况下，如何记录断点，然后在下次访问的时候，从断点处继续访问
决定将正常结束的日志文件和异常结束的日志文件分开，分别记录正常结束的日期和异常结束的日期

决定用OOP方法重写getThresholdTime.py中所有代码，因为异常的日志信息和正常结束的日志信息的格式不一样，所以需要分开处理
而且获取最后一次访问的时间也需要分开处理

为了让代码具有单一职责，易于维护，将getThresholdTime.py用OOP实现是我的决定，这是明天的工作。


------------------------------------------------------------------------------
20250825
现在知道

resource_list = get_resource_list(
            API_URL_RESOURCE_LIST,
            queryData=build_query_params(
                430, 
                extra_params = {
                    'order': 0,
                    'keys': "",
                    'edition': 0
                }
            )
        )

结论：get_resource_list这个函数只能连续执行100次，超过之后，就会找不到资源列表。

进一步用真实的数据测试
不再重复一百次，同一id为430的查询，而是用真实的数据查询。


经过测试，如果执行一百次之后，结合time.sleep(60)，先暂停一分钟，然后继续执行，是可以查询到资源列表的。


count += 1  # 每遍历一个叶子节点，计数器加 1
if count >= max_count:  # 如果计数器达到 max_count
    print(f"已遍历 {max_count} 个节点，暂停 1 分钟")
    time.sleep(60)  # 暂停 1 分钟
    count = 0  # 重置计数器


公文下载
党课:坚守初心使命,勇于担当作为.docx
:不能被识别，被截掉了

get_all_article_links，返回的结果不对
下载成功之后，有很多不必要的信息打印