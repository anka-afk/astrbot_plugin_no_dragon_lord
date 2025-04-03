"""
消息计数数据库管理模块
用于存储和查询群组中用户的消息发送次数
"""

import os
import sqlite3
import asyncio
import datetime
from astrbot.api import logger


class MessageCountDB:
    """
    消息计数数据库管理类
    负责记录群聊中每个用户发送消息的次数，并提供查询接口
    """

    def __init__(self, data_dir: str):
        """
        初始化数据库连接

        Args:
            data_dir: 数据存储目录
        """
        # 确保数据目录存在
        os.makedirs(data_dir, exist_ok=True)

        # 设置数据库文件路径
        self.db_path = os.path.join(data_dir, "message_counts.db")

        # 连接数据库
        self.conn = sqlite3.connect(self.db_path)
        self.cursor = self.conn.cursor()

        # 初始化数据库表
        self._init_db()

        # 设置自动重置任务
        self.reset_task = None
        asyncio.create_task(self.schedule_daily_reset())

        logger.info(f"消息计数数据库已初始化，路径: {self.db_path}")

    def _init_db(self):
        """
        初始化数据库表结构
        创建消息计数表，如果表已存在则不重新创建
        """
        try:
            self.cursor.execute(
                """
            CREATE TABLE IF NOT EXISTS message_counts (
                group_id TEXT,
                sender_id TEXT,
                count INTEGER DEFAULT 1,
                PRIMARY KEY (group_id, sender_id)
            )
            """
            )
            self.conn.commit()
        except sqlite3.Error as e:
            logger.error(f"初始化数据库表失败: {e}")

    def increment_message_count(self, group_id: str, sender_id: str) -> bool:
        """
        增加指定群组和发送者的消息计数
        如果记录不存在则创建新记录，存在则将计数加1

        Args:
            group_id: 群组ID
            sender_id: 发送者ID

        Returns:
            bool: 操作是否成功
        """
        try:
            # 使用UPSERT语法：如果记录存在则更新count，不存在则插入新记录
            self.cursor.execute(
                """
            INSERT INTO message_counts (group_id, sender_id, count)
            VALUES (?, ?, 1)
            ON CONFLICT(group_id, sender_id) 
            DO UPDATE SET count = count + 1
            """,
                (str(group_id), str(sender_id)),
            )

            self.conn.commit()
            return True
        except sqlite3.Error as e:
            logger.error(f"更新消息计数失败: {e}")
            self.conn.rollback()
            return False

    def get_max_message_count(self, group_id: str) -> int:
        """
        获取指定群组中的最大消息计数

        Args:
            group_id: 群组ID

        Returns:
            int: 该群组中的最大消息计数，如果群组不存在则返回0
        """
        try:
            self.cursor.execute(
                """
            SELECT MAX(count) FROM message_counts
            WHERE group_id = ?
            """,
                (str(group_id),),
            )

            result = self.cursor.fetchone()
            # 如果没有记录或者最大值为NULL，返回0
            return result[0] if result and result[0] is not None else 0
        except sqlite3.Error as e:
            logger.error(f"获取最大消息计数失败: {e}")
            return 0

    def get_sender_message_count(self, group_id: str, sender_id: str) -> int:
        """
        获取指定群组中特定发送者的消息计数

        Args:
            group_id: 群组ID
            sender_id: 发送者ID

        Returns:
            int: 该发送者在群组中的消息计数，如果不存在则返回0
        """
        try:
            self.cursor.execute(
                """
            SELECT count FROM message_counts
            WHERE group_id = ? AND sender_id = ?
            """,
                (str(group_id), str(sender_id)),
            )

            result = self.cursor.fetchone()
            return result[0] if result else 0
        except sqlite3.Error as e:
            logger.error(f"获取发送者消息计数失败: {e}")
            return 0

    def reset_all_counts(self) -> bool:
        """
        重置所有消息计数
        每天下午5点自动执行

        Returns:
            bool: 操作是否成功
        """
        try:
            self.cursor.execute("DELETE FROM message_counts")
            self.conn.commit()
            logger.info("消息计数已重置")
            return True
        except sqlite3.Error as e:
            logger.error(f"重置消息计数失败: {e}")
            self.conn.rollback()
            return False

    async def schedule_daily_reset(self):
        """
        安排每天下午5点自动重置消息计数的任务
        """
        while True:
            # 计算距离下一个下午5点的时间
            now = datetime.datetime.now()
            target_time = now.replace(hour=17, minute=0, second=0, microsecond=0)

            # 如果当前时间已经过了今天的下午5点，则目标时间为明天下午5点
            if now >= target_time:
                target_time += datetime.timedelta(days=1)

            # 计算需要等待的秒数
            seconds_to_wait = (target_time - now).total_seconds()

            logger.info(
                f"计划在 {target_time.strftime('%Y-%m-%d %H:%M:%S')} 重置消息计数，等待 {seconds_to_wait:.1f} 秒"
            )

            # 等待到指定时间
            await asyncio.sleep(seconds_to_wait)

            # 执行重置
            self.reset_all_counts()

            # 等待一分钟再进行下一次检查，避免在时间边界上重复执行
            await asyncio.sleep(60)

    def close(self):
        """
        关闭数据库连接
        在插件被卸载时调用
        """
        if hasattr(self, "reset_task") and self.reset_task:
            self.reset_task.cancel()

        if hasattr(self, "conn") and self.conn:
            self.conn.close()
            logger.info("消息计数数据库连接已关闭")

    def __del__(self):
        """
        析构函数，确保数据库连接被正确关闭
        """
        self.close()
