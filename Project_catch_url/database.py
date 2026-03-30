# @Version : 1.0
# @Author  : Away
# @File    : database.py
# @Time    : 2026/3/30 20:16



"""数据库操作层"""
import aiomysql
import re
import logging
from config import DB_CONFIG
from decorators import retry_on_exception

logger = logging.getLogger(__name__)

"""定义类"""
class AsyncMySQLPool:
    def __init__(self,config):
        """接收数据库，并初始化self.pool为None"""
        self.config = config
        self.pool = None

    """创建数据池没有retry"""
    async def create_pool(self):
        # 1. 使用 aiomysql.create_pool,创建数据池
        self.pool = await aiomysql.create_pool(
            host = self.config['host'],
            port = self.config['port'],
            user = self.config['user'],
            password=self.config['password'],
            db = self.config['db'],
            charset = self.config['charset'],
            minsize=5,      # 最小连接数
            maxsize=20,     # 最大连接数
            autocommit = True #自动提交事务
        )
        logger.info("MySQL 连接池已创建")

    @retry_on_exception(max_retries=3)
    async def insert_title(self,url:str,title:str,status_code:int):
        """异步插入数据到MySQL"""
        if not self.pool:
            raise Exception("数据库连接池未初始化")

        clean_title = self._clean_text(title)

        """2.获取连接"""
        async with self.pool.acquire() as conn:
            """3.创建游标"""
            async with conn.cursor() as cursor:
                # MySQL 使用 %s 作为占位符
                sql = "INSERT INTO web_titles (url,title,status_code) VALUES (%s,%s,%s)"
                await cursor.execute(sql,(url,clean_title,status_code))
                logger.debug(f"存入：{url} -> {clean_title}")


    def _clean_text(self,text):
        if not text:return "无标题"
        clean = re.compile('<.*?>')
        return re.sub(r'')














