# @Version : 1.0
# @Author  : Away
# @File    : main.py
# @Time    : 2026/3/30 20:25



"""程序入口（组装各模块并运行）"""
# main.py
import asyncio
import logging
from database import AsyncMySQLPool  # 导入修改后的类
from spider import HttpxSpider  # spider.py 不需要改动，httpx 依然通用
from config import DB_CONFIG

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)


async def main():
    # 1. 初始化 MySQL 数据库
    db_pool = AsyncMySQLPool(DB_CONFIG)
    await db_pool.create_pool()

    # 2. 准备数据
    target_urls = [f"https://httpbin.org/html/{i}" for i in range(1, 101)]

    # 3. 初始化爬虫
    spider = HttpxSpider(db_pool)

    try:
        await spider.run(target_urls)
    finally:
        await spider.close()
        await db_pool.close()


if __name__ == "__main__":
    asyncio.run(main())