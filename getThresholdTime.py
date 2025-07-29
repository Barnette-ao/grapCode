from datetime import datetime,timedelta
import os
import re
from typing import Tuple, Optional
from abc import ABC, abstractmethod

'''
这个类是我用来从日志文件中提取最后一次记录的时间而创造的类。这个类和logger.py是耦合的，
小程序下载器的日志文件是program_interrupt_weChat.log，思享公文的日志文件是program_interrupt_web.log,
小程序和网页的日志文件的内容是不一样的，
小程序的日志格式：
程序终止于: YYYY-MM-DD HH:MM:SS
思享公文的日志格式：
成功下载了date日期的文章，没有出现访问过于频繁的错误，则日志为
[SUCCESS] 下载{date}的文件时正常退出
下载date日期的文章时出现了访问过于频繁的错误，则日志为
[ERROR: 访问过于频繁] 下载{date}的文件时异常退出
'''
class TimeThresholdExtractor:
    def __init__(self, log_file : str ="program_interrupt.log", default_time: str="2025-07-14 00:00:00"):
        self.log_file = log_file
        self.default_time = default_time

    """
        获取最后记录的时间的午夜时间
        time: 时间字符串，格式为 "YYYY-MM-DD HH:MM:SS"

        Returns:
            time的当天午夜时间的字符串，格式为 "YYYY-MM-DD 00:00:00"
    """
    @staticmethod
    def get_midnight(time: str | datetime) -> str:
        
        # 统一转换为 datetime 对象
        if isinstance(time, str):
            dt = datetime.strptime(time, "%Y-%m-%d %H:%M:%S")
        elif isinstance(time, datetime):
            dt = time.strftime("%Y-%m-%d %H:%M:%S")
        else:
            raise TypeError("time 必须是字符串或 datetime 对象")
        
        # 当前执行程序的时间的年月日晚于记录的最后一行的时间的，
        # 所以设置的下载开始时间为记录最后一行的时间的第二天的午夜时间
        if datetime.now().strftime("%Y-%m-%d") > dt.strftime("%Y-%m-%d"):
            midnight = dt.replace(hour=0, minute=0, second=0, microsecond=0) + timedelta(days=1)
        # 当前执行程序的时间的年月日等于记录的最后一行的时间的，
        # 所以设置的下载开始时间为记录最后一行的时间的当日的午夜时间
        elif datetime.now().strftime("%Y-%m-%d") == dt.strftime("%Y-%m-%d") :
            midnight = dt.replace(hour=0, minute=0, second=0, microsecond=0)
        
        return midnight.strftime("%Y-%m-%d %H:%M:%S")

    def _safe_read_log(self) -> Optional[str]:
        """安全读取日志（公共方法不变）"""
        try:
            with open(self.log_file, 'r', encoding='utf-8') as f:
                return f.read()
     
        except FileNotFoundError:
            print(f"日志文件不存在: {self.log_file}")
            return None

        except Exception as e:
            print(f"日志解析失败: {str(e)}")
            return None

    @abstractmethod
    def _extract_last_timestamp(self) -> str:
        """从日志文件中提取最后一次记录的时间(子类必须实现)"""
        pass

    @abstractmethod    
    def get_threshold_time(self) -> str:
        """获取时间阈值(子类必须实现)"""
        pass


class MiniProgramTimeExtractor(TimeThresholdExtractor):
    """小程序专用时间提取器"""
    def _extract_last_timestamp(self) -> Optional[str]:
        """从日志文件中提取最后一次记录的时间"""
        content = self._safe_read_log()

        if not content:
            return None

        # 匹配格式：程序终止于: YYYY-MM-DD HH:MM:SS
        matches = re.findall(r'程序终止于: (\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2})', content)
        return matches[-1] if matches else None

    def get_threshold_time(self) -> str:
        """获取时间阈值"""
        # 1. 检查日志文件是否存在
        if not os.path.exists(self.log_file):
            return self.default_time

        # 2. 尝试从日志提取最后时间
        threshold_time = self._extract_last_timestamp()
        if threshold_time:
            return self.get_midnight(threshold_time)
        
        # 3. 如果读取日志失败，使用当天午夜时间
        return self.get_midnight(datetime.now())


class GwsxwkTimeExtractor(TimeThresholdExtractor):
    """思享公文专用时间提取器"""
    def _extract_last_timestamp(self) -> tuple:
        """从日志文件中提取最后一次记录的时间"""
        content = self._safe_read_log()
        
        if not content:
            return None

        # 匹配格式："[SUCCESS] 下载20250102的文件时正常退出",或者
        #"[ERROR: 访问过于频繁] 下载20250102的文件时异常退出"
        matches = re.findall(r'^$$(.*?)$$.*?(\d{8})', content)
        return match.group(1), match.group(2) if matches else None, None

    def get_threshold_time(self) -> str:
        """
        获取网页版的开始日期
        """
        # 1. 获取基础时间（优先日志，降级用默认值）
        base_time = self._get_base_datetime()
        
        # 2. 根据状态调整时间
        if not os.path.exists(self.log_file):
            return self._format_date(base_time + timedelta(days=1))
        
        status, _ = self._extract_last_timestamp()
        
        return self._calculate_final_date(base_time, status)

    def _get_base_datetime(self) -> datetime:
        """获取日志文件的最后一行时间信息，没有日志文件，就返回默认时间
        并且格式为"%Y-%m-%d"，这只是中间格式，最终是要获得的是%Y%m%d格式
        所以需要再进行格式化
        """
        if os.path.exists(self.log_file):
            
            _, time_str = self._extract_last_timestamp()
            
            return datetime.strptime(time_str, "%Y-%m-%d")
        
        return datetime.strptime(self.default_time, "%Y-%m-%d")

    def _calculate_final_date(self, base_time: datetime, status: str) -> str:
        """
        如果成功下载的date日期的文章，那么下一次再执行时，就应该将开始日期设置为date+1
        如果下载date日期的文章时出现了访问过于频繁的错误，则下一次再执行时，
        就应该将开始日期设置为date

        date格式为%Y%m%d
        """
        delta_days = 1 if "SUCCESS" in status else 0
        
        return self._format_date(base_time + timedelta(days=delta_days))

    def get_date_of_today(self) -> str:
        """
        获取今天的日期
        """
        return self._format_date(datetime.now())  

    @staticmethod
    def _format_date(dt: datetime) -> str:
        """统一日期格式化比如20210212"""
        return dt.strftime("%Y%m%d")


# 主程序逻辑
if __name__ == "__main__":
    # # 实例化提取器
    # gwsxwk_extractor = GwsxwkTimeExtractor(log_file="program_interrupt_web.log")

    # # 获取阈值时间
    # threshold_time = gwsxwk_extractor.get_threshold_time()
    # print(f"阈值时间: {threshold_time}")

    weChat_extractor = MiniProgramTimeExtractor(log_file="program_interrupt_weChat.log")

    # 获取阈值时间
    threshold_time = weChat_extractor.get_threshold_time()
    print(f"阈值时间: {threshold_time}")