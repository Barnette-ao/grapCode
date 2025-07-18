import signal
import sys
from datetime import datetime

LOG_FILE = "program_interrupt.log"
SHOULD_LOG = False  # 全局控制变量

def save_exit_time():
    """安全记录退出时间"""
    if SHOULD_LOG:
        with open(LOG_FILE, "a", encoding='utf-8') as f:
            f.write(f"程序终止于: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")

def log_exit_time(command_func):
    """装饰器：仅装饰的函数执行时正常退出的记录退出时间"""
    def wrapper(*args, **kwargs):
        global SHOULD_LOG
        SHOULD_LOG = True
        try:
            result = command_func(*args, **kwargs)
            save_exit_time()  # 只有正常执行完成才记录
            return result
        finally:
            SHOULD_LOG = False
    return wrapper


# 注册信号处理（只需执行一次）
signal.signal(signal.SIGINT, lambda s,f: sys.exit(1))