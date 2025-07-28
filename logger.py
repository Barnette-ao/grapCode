import signal
import sys
from datetime import datetime
from functools import wraps
import os

SHOULD_LOG = False  # 全局控制变量

# 将所有的日志都记录到一个文件夹log中
def set_path(filename):
    """获取当前文件的绝对路径"""
    os.makedirs("log", exist_ok=True)
    return os.path.join(filename, "log")


def save_exit_time(filename, date=""):
    """安全记录退出时间"""
    if SHOULD_LOG:
        if filename == "success.log":
            with open(log_path, "a", encoding='utf-8') as f:
                f.write(f"程序终止于: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
        elif filename == "error.log":
            with open(log_path, "a", encoding='utf-8') as f:
                f.write(f"程序异常终止下载日期: {date}\n")

def log_exit_time():
    """装饰器：仅装饰的函数执行时正常退出的记录退出时间"""
    def decorator(func):
        
        @wraps(func)
        def wrapper(*args, **kwargs):
            global SHOULD_LOG
            SHOULD_LOG = True
            try:
                result = func(*args, **kwargs)
                save_exit_time("success.log")  # 只有正常执行完成才记录
                return result
            except Exception as e:
                save_exit_time("error.log")  # 记录异常信息
                raise e
            finally:
                SHOULD_LOG = False
        return wrapper
    return decorator

def handle_interrupt(signum, frame):
    """统一的信号处理函数"""
    sys.exit(1)

# 注册信号处理（只需执行一次）
signal.signal(signal.SIGINT, handle_interrupt)