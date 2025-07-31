import signal
import sys
from datetime import datetime
from functools import wraps

SHOULD_LOG = False  # 全局控制变量

# 单独为batchDownloadPDF使用
def log_exit_time(log_file):
    """装饰器：仅装饰的函数执行时正常退出的记录退出时间"""
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            global SHOULD_LOG
            SHOULD_LOG = True

            try:
                result = func(*args, **kwargs)
                
                if SHOULD_LOG:
                    # 记录退出时间
                    with open(log_file, "a", encoding='utf-8') as f:
                        f.write(f"程序终止于: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
                
                return result
            
            finally:
                SHOULD_LOG = False
        return wrapper
    return decorator


# 单独为getHtml中的download_article_by_date函数使用
def log_exit_time_with_date(log_file):
    """装饰器：记录函数退出时间和状态，特别处理'访问过于频繁'情况"""
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            exit_status = "SUCCESS"  # 默认标记为成功
            date = kwargs.get('date', None) or (args[1] if len(args) > 1 else None)  # 获取date参数
            
            try:
                result = func(*args, **kwargs)
                return result
            except Exception as e:
                exit_status = f"ERROR: {str(e)}"  # 标记异常退出
                raise
            finally:
                # 特殊处理"访问过于频繁"的情况
                if 'text_objects' in locals() and text_objects == "访问过于频繁":
                    exit_status = "ERROR: 访问过于频繁"
                
                with open(log_file, 'a', encoding="utf-8") as f:
                    # 构造日志消息
                    if exit_status == "SUCCESS":
                        log_message = f"[{exit_status}] 下载{date}的文件时正常退出"
                    # 如果是错误状态且能获取到日期，添加日期信息
                    elif "ERROR" in exit_status and date:
                        log_message = f"[{exit_status}] 下载{date}的文件时异常退出"
                    
                    f.write(log_message + "\n")
        return wrapper
    return decorator

def handle_interrupt(signum, frame):
    """统一的信号处理函数"""
    sys.exit(1)

# 注册信号处理（只需执行一次）
signal.signal(signal.SIGINT, handle_interrupt)