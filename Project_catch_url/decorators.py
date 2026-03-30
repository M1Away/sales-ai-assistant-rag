# @Version : 1.0
# @Author  : Away
# @File    : decorators.py
# @Time    : 2026/3/30 20:16



"""自定义装饰器（重试逻辑）"""
# decorators.py
import asyncio
import logging
from functools import wraps

logger = logging.getLogger(__name__)

def retry_on_exception(max_retries=3, backoff_factor=2):
    """
    带指数退避的自定义重试装饰器
    """
    def decorator(func):
        @wraps(func)  # 保留原函数的元信息
        async def wrapper(*args, **kwargs):
            retries = 0
            while retries < max_retries:
                try:
                    return await func(*args, **kwargs)
                except Exception as e:
                    retries += 1
                    wait_time = backoff_factor ** retries
                    logger.warning(f"{func.__name__} 执行失败: {e}。第 {retries} 次重试，等待 {wait_time}秒...")
                    if retries == max_retries:
                        logger.error(f"{func.__name__} 达到最大重试次数，放弃。")
                        raise e
                    await asyncio.sleep(wait_time)
        return wrapper
    return decorator