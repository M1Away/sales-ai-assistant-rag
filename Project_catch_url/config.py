# @Version : 1.0
# @Author  : Away
# @File    : config.py.py
# @Time    : 2026/3/30 20:15



"""配置文件（数据库连接、并发数等）"""
# config.py

# config.py

DB_CONFIG = {
    "host": "localhost",
    "port": 3306,          # MySQL 默认端口
    "user": "root",
    "password": "00000000",
    "db": "scrape_db",
    "charset": "utf8mb4"   # 必须设置 utf8mb4 以支持表情符等
}

SPIDER_CONFIG = {
    "concurrent_limit": 20,
    "timeout": 10,
    "user_agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) HttpxSpider/1.0"
}

RETRY_CONFIG = {
    "max_retries": 3,
    "backoff_factor": 2
}
