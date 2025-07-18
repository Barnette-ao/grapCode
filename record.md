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
