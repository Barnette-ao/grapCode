from datetime import datetime,timedelta
import os
import re


def extract_last_timestamp(log_file="program_interrupt.log"):
    """读取日志文件最后一行并提取时间戳"""
    try:
        # 读取最后一行
        with open(log_file, 'r', encoding='utf-8') as f:
            content = f.read()


        # 匹配格式：程序终止于: YYYY-MM-DD HH:MM:SS
        matches = re.findall(r'程序终止于: (\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2})', content)
        return matches[-1] if matches else None

    except Exception as e:
        print(f"读取日志失败: {str(e)}")
        return None


def get_midnight(time):
    """
    获取最后记录的时间的午夜时间
    time: 时间字符串，格式为 "YYYY-MM-DD HH:MM:SS"

    Returns:
        time的当天午夜时间的字符串，格式为 "YYYY-MM-DD 00:00:00"
    """
    # 统一转换为 datetime 对象
    if isinstance(time, str):
        dt = datetime.strptime(time, "%Y-%m-%d %H:%M:%S")
    elif isinstance(time, datetime):
        dt = time
    else:
        raise TypeError("time 必须是字符串或 datetime 对象")
    
    # 记录的最后一次执行程序的时间在今天之前，那么使用记录的最后一次执行程序的时间的后一天午夜时间
    if datetime.now() > dt:
        midnight = dt.replace(hour=0, minute=0, second=0, microsecond=0) + timedelta(days=1)
    # 记录的最后一次执行程序的时间就是今天之前
    elif datetime.now() == dt :
        midnight = dt.replace(hour=0, minute=0, second=0, microsecond=0)
    
    return midnight.strftime("%Y-%m-%d %H:%M:%S")   

def get_threshold_time(
    log_file: str = "program_interrupt.log",
    default_time: str = "2025-07-14 00:00:00"
) -> str:
    """
    获取时间阈值，优先级：
    1. 从日志文件提取最后记录时间
    2. 使用前一天午夜时间
    3. 使用默认时间
    
    Args:
        log_file: 日志文件路径
        default_time: 保底默认时间
        
    Returns:
        格式化的时间字符串 "%Y-%m-%d %H:%M:%S"
    """
    # 1. 检查日志文件是否存在
    if not os.path.exists(log_file):
        return default_time
    
    # 2. 尝试从日志提取最后时间
    try:
        threshold_time = extract_last_timestamp(log_file)
        if threshold_time:
            return get_midnight(timestamp)
    except Exception:
        pass
    
    # 3. 使用当天午夜时间
    return get_midnight(datetime.now())


# 主程序逻辑
if __name__ == "__main__":
   print(get_threshold_time())