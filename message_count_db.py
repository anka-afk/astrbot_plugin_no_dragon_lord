"""
消息计数数据库管理模块
用于存储和查询群组中用户的消息发送次数
"""
import os
import sqlite3
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
        
        logger.info(f"消息计数数据库已初始化，路径: {self.db_path}")
    
    def _init_db(self):
        """
        初始化数据库表结构
        创建消息计数表，如果表已存在则不重新创建
        """
        try:
            self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS message_counts (
                group_id TEXT,
                sender_id TEXT,
                count INTEGER DEFAULT 1,
                PRIMARY KEY (group_id, sender_id)
            )
            ''')
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
            self.cursor.execute('''
            INSERT INTO message_counts (group_id, sender_id, count)
            VALUES (?, ?, 1)
            ON CONFLICT(group_id, sender_id) 
            DO UPDATE SET count = count + 1
            ''', (str(group_id), str(sender_id)))
            
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
            self.cursor.execute('''
            SELECT MAX(count) FROM message_counts
            WHERE group_id = ?
            ''', (str(group_id),))
            
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
            self.cursor.execute('''
            SELECT count FROM message_counts
            WHERE group_id = ? AND sender_id = ?
            ''', (str(group_id), str(sender_id)))
            
            result = self.cursor.fetchone()
            return result[0] if result else 0
        except sqlite3.Error as e:
            logger.error(f"获取发送者消息计数失败: {e}")
            return 0
    
    def close(self):
        """
        关闭数据库连接
        在插件被卸载时调用
        """
        if hasattr(self, 'conn') and self.conn:
            self.conn.close()
            logger.info("消息计数数据库连接已关闭")
    
    def __del__(self):
        """
        析构函数，确保数据库连接被正确关闭
        """
        self.close()