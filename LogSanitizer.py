# @Version : 1.0
# @Author  : Away
# @File    : LogSanitizer.py
# @Time    : 2026/3/15 21:39
import functools
import random
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
def retry_on_error(max_retries=3, delay=1, exception=(Exception,)):
    def decorator(func):
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            attempts = 0
            while attempts < max_retries:
                try:
                    return func(*args, **kwargs)
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

@log_execution
def _apply_masks(text, patterns):
    """辅助函数：应用所有正则掩码 (无重试，因为纯内存操作快)"""
    for key, regex in patterns.items():
        if key == 'email':
            text = regex.sub('[EMAIL_HIDDEN]', text)
        elif key == 'phone':
            text = regex.sub('[PHONE_HIDDEN]', text)
        elif key == 'ip':
            text = regex.sub('[IP_HIDDEN]', text)
    return key

<<<<<<< HEAD
"""
PermissionError是权限错误，IOError是输入/输出错误
这个PermissionError主要解决进程短暂否定、网络文件瞬间抖动、磁盘繁忙，几百毫秒可能就好了
该函数的作用：
1.尝试打开文件
2.如果遇到权限或者IO错误，重试几次
3.一旦打开成功，读取文件中所有行
4.将所有行组成的列表返回
5.全程记录日志
"""
@retry_on_error(max_retries=3, delay=0.5, exception=(IOError, PermissionError))
=======

@retry_on_error(max_retries=3, delay=0.5, exception=(IOError, PermissionError))
# PermissionError是权限错误，IOError是输入/输出错误
# 这个PermissionError主要解决进程短暂否定、网络文件瞬间抖动、磁盘繁忙，几百毫秒可能就好了
>>>>>>> d4466ef9591f9c23a841d08776c16c3cb6f5bd57
@log_execution
def read_file_safely(file_path):
    """
    read_file_safely：读取文件内容
    先重试再记录日志
    """
    # 模拟一个随机故障用于测试重试机制
    if random.random() < 0.3: raise IOError("Simulated IO Error")
    with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
<<<<<<< HEAD
        # 为了程序不崩溃，选择牺牲数据的完整性,read_line会一次性读取文件中所有内容
=======
        # 为了程序不崩溃，选择牺牲数据的完整性
>>>>>>> d4466ef9591f9c23a841d08776c16c3cb6f5bd57
        return f.readline()


@log_execution
def process_logs(*file_paths, output_file='secure_file.txt',
                 mask_email=True, mask_ip=True, mask_phone=True,
                 error_keywords=None, **kwargs):
    """
    :param file_paths: 要读取的文件
    :param output_file: 输出的清晰好的文件的数据
    :param mask_email: 邮件掩码
    :param mask_ip: ip掩码
    :param mask_phone: 手机号掩码
    :param error_keywords:
    :param kwargs:
    """
    if error_keywords is None:
        error_keywords = ['ERROR', 'CRITICAL', 'FATAL']

    # 预编译正则
    patterns = {}
<<<<<<< HEAD
    # 判断标准和规则，规则名字叫'email'等，规则的内容是后面的预编译正则表达式
=======
>>>>>>> d4466ef9591f9c23a841d08776c16c3cb6f5bd57
    if mask_email: patterns['email'] = re.compile(r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b')
    if mask_phone: patterns['phone'] = re.compile(r'\b1[3-9]\d{9}\b|\b\d{3}-\d{8}\b')
    if mask_ip: patterns['ip'] = re.compile(r'\b\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}\b')

    stats = {'total_lines': 0, 'error_count': 0, 'file_processed': 0}
    # 用来存放所有文件处理完之后的完整脱敏日志，随着循环进行，它会越来越大
    all_cleaned_lines = []
    # 存放所有文件中提取的错误行的摘要
    error_details = []
    # 日志头，执行多少个文件
    print(f"\n🛡️  LogGuard Pro 启动 | 目标文件: {len(file_paths)}")

<<<<<<< HEAD
    for f_file in file_paths:
        # 判断f_file是否存在
        if not os.path.exists(f_file):
            print(f"⚠️ 跳过: {f_file}")
            continue
        try:
            # 对文件的开始读取
            raw_lines = read_file_safely(f_file)
            stats['file_processed'] += 1
            stats['total_lines'] = len(raw_lines)

            # 列表推导式：脱敏
            cleaned_lines = [_apply_masks(line,patterns) for line in raw_lines]

            # 列表推导式+any():过滤错误
            file_error = [line for line in cleaned_lines if any(kw in line for kw in error_keywords)]
            stats['error_count'] += len(file_error)
=======

























>>>>>>> d4466ef9591f9c23a841d08776c16c3cb6f5bd57












