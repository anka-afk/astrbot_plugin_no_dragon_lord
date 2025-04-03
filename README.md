# 🚫 AstrBot No Dragon Lord

<div align="center">

[![License: MIT](https://img.shields.io/badge/License-MIT-blue.svg)](https://opensource.org/licenses/MIT)
![Python Version](https://img.shields.io/badge/Python-3.10%2B-blue)
![Platform](https://img.shields.io/badge/Platform-Windows%20%7C%20Linux%20%7C%20macOS-lightgrey)
[![PRs Welcome](https://img.shields.io/badge/PRs-Welcome-brightgreen)](#贡献指南)

</div>

<div align="center">

[![Moe Counter](https://count.getloli.com/get/@NoDragonLord?theme=moebooru)](https://github.com/anka-afk/astrbot_plugin_no_dragon_lord)

</div>

禁止机器人抢龙王!

龙王一定要是人类

✍️✍️✍️✍️✍️✍️✍️✍️

😭😭😭😭😭😭😭😭

## ✨ 功能特性

- 🧮 自动记录群聊中每个成员发送的消息数量
- 🚫 防止机器人成为群聊"龙王"（消息数最多的成员）
- 🔄 当机器人即将超过群内最高消息数时，自动停止响应
- 🌟 支持群聊白名单，可以自定义在哪些群启用功能
- 💾 使用 SQLite 数据库持久化存储消息统计数据

## 🛠️ 配置说明

在插件配置中设置以下参数:

```json
{
  "white_list_groups": {
    "description": "白名单群组列表, 在这些群组中启用龙王控制",
    "type": "list",
    "hint": "白名单群组列表, 在这些群组中启用龙王控制, 请填写要控制的群号, 例如: [123456789, 987654321]",
    "default": []
  },
  "fault_tolerance": {
    "description": "为龙王控制提供容错(如果你开启了分段回复, 多段回复会被视为一条消息, 建议使用), 设置容错条数, 例如: 3(这个数字可能太小了), 最终消息上限将会减去这个数字",
    "type": "int",
    "hint": "为龙王控制提供容错(如果你开启了分段回复, 多段回复会被视为一条消息, 建议使用), 设置容错条数, 例如: 3(这个数字可能太小了), 最终消息上限将会减去这个数字",
    "default": 0
  }
}
```

## 🔄 工作原理

1. 插件会记录群聊中每个成员（包括机器人自己）发送的消息数量
2. 当机器人即将发送消息时，会检查发送后是否会超过群内消息数最多的成员
3. 如果会超过，则阻止消息发送，确保机器人不会成为"龙王"
4. 所有消息计数会保存在数据库中，重启后依然有效
5. 插件支持白名单配置，允许用户自定义在哪些群启用功能

## 💡 实际应用场景

- 保持群聊的互动性，防止机器人过度活跃
- 尊重人类用户的互动地位，不与人类争抢"龙王"位置
- 适合需要机器人辅助但不希望机器人过于活跃的群聊环境

## 🔄 版本历史

- v1.0.0
  - ✅ 实现基础的消息计数功能
  - ✅ 实现机器人龙王保护机制
  - ✅ 支持群聊白名单配置
  - ✅ 使用 SQLite 数据库持久化存储

## 👥 贡献指南

欢迎通过以下方式参与项目：

- 🐛 提交 Issue 报告问题
- 💡 提出新功能建议
- 🔧 提交 Pull Request 改进代码

## 🌟 鸣谢

感谢所有为这个项目做出贡献的开发者！

---

> 保护群聊活跃度，让人类成为龙王! 🐉👑
