import signal
import sys
from datetime import datetime
from functools import wraps

SHOULD_LOG = False  # 全局控制变量

def save_exit_time(filename):
    """安全记录退出时间"""
    if SHOULD_LOG:
        with open(filename, "a", encoding='utf-8') as f:
            f.write(f"程序终止于: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")

def log_exit_time(log_file):
    """装饰器：仅装饰的函数执行时正常退出的记录退出时间"""
    def decorator(func):
        
        @wraps(func)
        def wrapper(*args, **kwargs):
            global SHOULD_LOG
            SHOULD_LOG = True
            try:
                result = func(*args, **kwargs)
                save_exit_time(log_file)  # 只有正常执行完成才记录
                return result
            finally:
                SHOULD_LOG = False
        return wrapper
    return decorator

def handle_interrupt(signum, frame):
    """统一的信号处理函数"""
    sys.exit(1)

# 注册信号处理（只需执行一次）
signal.signal(signal.SIGINT, handle_interrupt)