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
            # 这是一个无用的导入，且 result 在装饰器中只是作为局部变量赋值 result = func(*args, **kwargs)，与导入无关。这属于代码污染。
            # result = func(*args, **kwargs)
            end_time = time.time()
            duration = end_time - start_time
            print(f"✅ [LOG] 完成执行: {func.__name__} | 耗时: {duration}")
            # return result
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
    """text，之前写的key"""
    return text


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
@log_execution
def read_file_safely(file_path):
    """
    read_file_safely：读取文件内容
    先重试再记录日志
    """
    # 模拟一个随机故障用于测试重试机制
    if random.random() < 0.3: raise IOError("Simulated IO Error")
    with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
        # 为了程序不崩溃，选择牺牲数据的完整性,read_line会一次性读取文件中所有内容
        # f.readline()是读取一行，readlines是读取全文
        return f.readlines()


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
    # 判断标准和规则，规则名字叫'email'等，规则的内容是后面的预编译正则表达式
    if mask_email: patterns['email'] = re.compile(r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b')
    if mask_phone: patterns['phone'] = re.compile(r'\b1[3-9]\d{9}\b|\b\d{3}-\d{8}\b')
    if mask_ip: patterns['ip'] = re.compile(r'\b\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}\b')

    stats = {'total_lines': 0, 'error_count': 0, 'file_processed': 0} # 注意这里是单数 file_processed
    # 用来存放所有文件处理完之后的完整脱敏日志，随着循环进行，它会越来越大
    all_cleaned_lines = []
    # 存放所有文件中提取的错误行的摘要
    error_details = []
    # 日志头，执行多少个文件
    print(f"\n🛡️  LogGuard Pro 启动 | 目标文件: {len(file_paths)}")

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
            cleaned_lines = [_apply_masks(line, patterns) for line in raw_lines]

            # 列表推导式+any():过滤错误
            file_errors = [line for line in cleaned_lines if any(kw in line for kw in error_keywords)]
            stats['error_count'] += len(file_errors)

            # 切片操作：简化错误信息展示（去掉前20字符时间戳）
            # os.path.basename(f_path)这个文件只提取文件名部分
            # [(...,err) for err in simplified]为每一个处理过的错误信息err创建一个元组(Tuple)
            # error_details.extend(...):将生成的这些元组添加到error_details这个大列表中
            simplified = [line[20:] + "..." if len(line) > 20 else line for line in file_errors]
            error_details.extend([(os.path.basename(f_file), err) for err in simplified])

            all_cleaned_lines.extend(cleaned_lines)

        except Exception as e:
            # 如果重试后依然失败，记录并继续
            print(f"❌ 最终无法处理文件 {f_file}: {e}")
            continue

    # 结束了，生成报告
    _write_report(output_file, all_cleaned_lines, error_details, stats)
    return stats


@log_execution
def _write_report(filename, clean_lines, error_details, stats):
    """写入报告文件"""
    with open(filename, 'w', encoding='utf-8') as f:
        f.write(f"🛡️ LogGuard Pro 安全报告 - {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
        f.write("=" * 60 + "\n")
        f.write(
            # 就是file_processed里面的file之前加了s就完犊子了...服了
            f"📊 统计: {stats['total_lines']} 行 | {stats['error_count']} 错误 | {stats['file_processed']} 文件\n\n")
        f.write("🚨 关键错误摘录 (已脱敏):\n")

        # 切片：只取前10条
        for source, err in error_details[:10]:
            f.write(f"  [{source}] {err.strip()}\n")

        if len(error_details) > 10:
            f.write(f"  ... 还有 {len(error_details) - 10} 条错误\n")

        f.write("\n📝 脱敏日志预览 (前 50 行):\n")
        # 切片：只取前50行
        for line in clean_lines[:50]:
            f.write(line)
        if len(clean_lines) > 50:
            f.write(f"\n...(省略{len(clean_lines) - 50}行)\n")


# ==========================================
# 3. 运行入口
# ==========================================

if __name__ == '__main__':
    # 1. 准备测试数据
    test_files = ['log_a.txt', 'log_b.txt']
    content = """
    2026-03-19 10:00:01 INFO User admin@secret.com logged in from 192.168.1.10
    2026-03-19 10:00:02 ERROR DB failed for user 13912345678
    2026-03-19 10:00:03 CRITICAL Attack detected from 10.0.0.5
    2026-03-19 10:00:04 INFO Normal operation.
    """

    for fname in test_files:
        with open(fname, 'w') as f:
            f.write(content * 20)  # 制造一点数据量
        print(f"📄 生成测试文件: {fname}")

    # 2. 执行处理
    # 演示：传入自定义关键词，开启所有脱敏
    final_stats = process_logs(
        *test_files,
        output_file="final_secure_log.txt",
        mask_email=True,
        mask_phone=True,
        mask_ip=True,
        error_keywords=['ERROR', 'CRITICAL', 'Attack'],
        custom_debug_mode=True  # 通过 **kwargs 传递，虽未使用但展示了扩展性
    )

    print("\n🎉 任务全部完成！请查看 final_secure_log.txt")

    # 清理 (可选)
    # for f in test_files: os.remove(f)
