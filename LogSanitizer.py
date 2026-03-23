# @Version : 1.0
# @Author  : Away
# @File    : LogSanitizer.py
# @Time    : 2026/3/15 21:39
import functools
import re
import os
import time
from datetime import datetime

from django.db.models.expressions import result


# ==========================================
# 1. 装饰器模块 (核心亮点)
# ==========================================

def log_execution(func):
    """
    装饰器：记录函数执行的开始、结束、耗时及参数
    展示：*args和*kwargs在装饰器中的透传
    """

    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        start_time = time.time()
        print(f"⏳ [LOG] 开始执行:{func.__name__} | 位置参数:{len(args)}个| 关键字参数:{len(kwargs)}个")

        try:
            result = func(*args, **kwargs)
            end_time = time.time()
            duration = end_time - start_time
            print(f"✅ [LOG] 完成执行: {func.__name__} | 耗时: {duration}")
            return result
        except Exception as e:
            end_time = time.time()
            print(f"❌ [LOG] 执行失败: {func.__name__} | 错误: {str(e)} | 耗时: {end_time - start_time:.4f} 秒")
            raise

    return wrapper

# 工厂函数
def retry_on_error(max_retries = 3,delay = 1,exception = (Exception,)):
    def decorator(func):
        @functools.wraps(func)
        def wrapper(*args,**kwargs):
            attempts = 0
            while attempts < max_retries:
                try:
                    return func(*args,**kwargs)
                except exception as e:
                    attempts += 1
                    if attempts == max_retries:
                        print(f"💥 [RETRY] {func.__name__} 失败 {max_retries} 次，放弃。最后错误: {e}")
                        raise
                    print(f"⚠️ [RETRY] {func.__name__} 出错 ({e})，{delay}秒后重试 ({attempts}/{max_retries})...")
                    time.sleep(delay)
        return wrapper
    return decorator

# ==========================================
# 2. 核心业务逻辑
# ==========================================










































