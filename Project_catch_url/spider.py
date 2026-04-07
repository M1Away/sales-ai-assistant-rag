# spider.py
import httpx
import asyncio
import re
import logging
from typing import List
from config import SPIDER_CONFIG, RETRY_CONFIG
from decorators import retry_on_exception
from database import AsyncMySQLPool

logger = logging.getLogger(__name__)


class HttpxSpider:
    # 外部创建这个爬虫实例时，必须喂给他一个已经配置好的连接池
    def __init__(self, db_pool: AsyncMySQLPool):
        self.db_pool = db_pool
        # 使用配置中的并发数
        self.semaphore = asyncio.Semaphore(SPIDER_CONFIG['concurrent_limit'])

        self.client = httpx.AsyncClient(
            limits=httpx.Limits(max_connections=SPIDER_CONFIG['concurrent_limit']),
            timeout=httpx.Timeout(SPIDER_CONFIG['timeout']),
            headers={"User-Agent": SPIDER_CONFIG['user_agent']}
        )

    @retry_on_exception(**RETRY_CONFIG)
    async def fetch(self, url: str):
        """单个页面的抓取逻辑"""
        async with self.semaphore:
            try:
                response = await self.client.get(url)

                title = "未找到标题"
                if response.status_code == 200:
                    match = re.search(r'<title>(.*?)</title>', response.text, re.IGNORECASE | re.DOTALL)
                    if match:
                        title = match.group(1)

                # 调用数据库模块保存
                await self.db_pool.insert_title(url, title, response.status_code)
                return True

            except httpx.TimeoutException as e:
                logger.error(f"请求超时: {url} - {e}")
                return False
            except httpx.HTTPError as e:
                logger.error(f"HTTP 错误: {url} - {e}")
                return False
            except Exception as e:
                logger.error(f"未知错误: {url} - {e}")
                return False

    async def run(self, urls: List[str]):
        logger.info(f"🚀 任务启动，共 {len(urls)} 个URL...")
        tasks = [self.fetch(url) for url in urls]
        results = await asyncio.gather(*tasks, return_exceptions=True)

        success_count = sum(1 for r in results if r is True)
        logger.info(f"✅ 任务结束。成功: {success_count}, 失败/异常: {len(urls) - success_count}")

    async def close(self):
        await self.client.aclose()