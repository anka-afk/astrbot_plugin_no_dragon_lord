from astrbot.api.event import filter, AstrMessageEvent, MessageEventResult
from astrbot.api.star import Context, Star, register
from astrbot.api import logger, AstrBotConfig
from .message_count_db import MessageCountDB
import os
import sqlite3


@register(
    "astrbot_plugin_no_dragon_lord",
    "anka",
    "禁止机器人抢龙王! 龙王一定要是人类 ✍️✍️✍️✍️✍️✍️✍️✍️ 😭😭😭😭😭😭😭😭",
    "1.0.0",
)
class NoDragonLord(Star):
    def __init__(self, context: Context, config: AstrBotConfig):
        super().__init__(context)
        self.config = config
        data_dir = os.path.join(
            os.path.join(
                os.path.dirname(os.path.abspath(__file__)),
                os.pardir,
                os.pardir,
                "dragon_lord_data",
            ),
            "no_dragon_lord",
        )
        self.db = MessageCountDB(data_dir)

    @filter.event_message_type(
        filter.EventMessageType.GROUP_MESSAGE, priority=999999999
    )
    async def record_message(self, event: AstrMessageEvent):
        """记录消息计数

        Args:
            event (AstrMessageEvent): 消息事件
        """
        # 获取群组id
        group_id = event.get_group_id()

        # 检查群组id是否在白名单中, 若没填写白名单则不检查
        if len(self.config.get("white_list_groups")) != 0:
            # 检查群组id是否在白名单中
            if not self.check_group_id(group_id):
                logger.info(f"<龙王> 群组 {group_id} 不在白名单中")
                return

        # 获取消息发送者id
        sender_id = event.get_sender_id()

        # 存储到数据库
        self.db.increment_message_count(group_id, sender_id)

        # 获取消息计数
        max_count = self.db.get_max_message_count(group_id) - self.config.get(
            "fault_tolerance"
        )
        bot_count = self.db.get_sender_message_count(group_id, event.get_self_id())

        if bot_count >= max_count:
            # 不做出相应
            logger.info(f"<龙王> 达到该群组最大消息计数, 停止响应事件")
            event.clear_result()
            event.stop_event()
        else:
            if self.config.get("fault_tolerance") != 0:
                logger.info(
                    f"<龙王> 发送消息计数: {bot_count}, 最大消息计数: {max_count} - {self.config.get('fault_tolerance')}(容错)"
                )
            else:
                logger.info(
                    f"<龙王> 发送消息计数: {bot_count}, 最大消息计数: {max_count}"
                )

        return

    @filter.after_message_sent()
    async def record_self_message(self, event: AstrMessageEvent):
        """记录自己发送的消息

        Args:
            event (AstrMessageEvent): 消息事件
        """
        # 获取群组id
        group_id = event.get_group_id()

        # 检查群组id是否在白名单中, 若没填写白名单则不检查
        if len(self.config.get("white_list_groups")) != 0:
            # 检查群组id是否在白名单中
            if not self.check_group_id(group_id):
                logger.info(f"<龙王> 群组 {group_id} 不在白名单中")
                return

        # 获取自身id
        sender_id = event.get_self_id()

        # 存储到数据库
        self.db.increment_message_count(group_id, sender_id)

        # 打印日志
        bot_count = self.db.get_sender_message_count(group_id, sender_id)
        max_count = self.db.get_max_message_count(group_id)
        if self.config.get("fault_tolerance") != 0:
            logger.info(
                f"<龙王> 发送消息计数: {bot_count}, 最大消息计数: {max_count} - {self.config.get('fault_tolerance')}(容错)"
            )
        else:
            logger.info(f"<龙王> 发送消息计数: {bot_count}, 最大消息计数: {max_count}")

        return

    def check_group_id(self, group_id: str) -> bool:
        """检查群号是否在白名单中

        Args:
            group_id (str): 群号

        Returns:
            bool: 是否在白名单中
        """
        if group_id in self.config.get("white_list_groups"):
            return True
        return False

    async def terminate(self):
        if hasattr(self, "db"):
            self.db.close()
