import requests
import os
from tqdm import tqdm

def build_save_path(base_dir, firstcategory, secondcategory, filename, thirdcategory=''):
    """构建完整的文件保存路径"""
    # 第一层目录结构
    save_top_dir = os.path.join(base_dir, firstcategory)
    
    # 根据是否有三级分类确定最终目录
    if thirdcategory:
        save_dir = os.path.join(save_top_dir, secondcategory, thirdcategory)
    else:
        save_dir = os.path.join(save_top_dir, secondcategory)
    
    # 确保目录存在
    os.makedirs(save_dir, exist_ok=True)
    
    # 返回完整文件路径
    return os.path.join(save_dir, filename)

def simple_download_pdf(url, save_path):
    try:
        if os.path.exists(save_path):
            print(f"文件已存在，且不允许覆盖。")
            return
        
        # 发送HTTP GET请求
        response = requests.get(url, stream=True)
        response.raise_for_status()  # 检查请求是否成功

        # 获取文件总大小（用于进度条）
        total_size = int(response.headers.get('content-length', 0))
        
        # 以二进制写入模式保存文件
        with open(save_path, 'wb') as file,tqdm(
            desc=os.path.basename(save_path),
            total=total_size,
            unit='B',
            unit_scale=True,
            unit_divisor=1024
        ) as progress:
            for chunk in response.iter_content(1024):
                file.write(chunk)
                progress.update(len(chunk))
        
        print(f"文件已成功下载到: {save_path}")
    except requests.exceptions.RequestException as e:
        print(f"下载文件时出错: {e} {url}")


# url = "https://cdn.axuex.top/uploads/20250704/ceabc02d6f01d1a37f9b84854f4c1de1.pdf"
# filename = "downloaded_file.pdf"

# simple_download_pdf(url, filename)
# Compare this snippet from simple_download_pdf.py:

if __name__ == "__main__":
    # 参数定义
    params = {
        "base_dir": "download1",
        "firstcategory": "教育资料",
        "secondcategory": "小学语文",
        "filename": "古诗三首.pdf",
        "thirdcategory": "一年级上册"
    }
    
    # 构建路径
    save_path = build_save_path(**params)
    
    # 执行下载
    simple_download_pdf(
        url="https://cdn.axuex.top/uploads/20250704/8eb5a5595b930b0388442ed7d302a89c.pdf",
        save_path=save_path,
    )