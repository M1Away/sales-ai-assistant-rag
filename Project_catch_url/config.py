# @Version : 1.0
# @Author  : Away
# @File    : config.py.py
# @Time    : 2026/3/30 20:15



"""配置文件（数据库连接、并发数等）"""
# config.py

DB_CONFIG = {
    "user": "root",
    "password": "20020520",
    "host": "localhost",
    "port": 3306,
    "database": "scrape_db",
    "charset": "utf8mb4"
}

# 爬虫配置
SPIDER_CONFIG = {
    "concurrent_limit": 20,  # 并发数
    "timeout": 10,           # 超时时间
    "user_agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) Spider/1.0"
}

# 重试配置
RETRY_CONFIG = {
    "max_retries": 3,
    "backoff_factor": 2
}

