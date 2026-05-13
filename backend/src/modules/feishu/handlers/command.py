# AI Study Assistant - Command Handler

from loguru import logger


class CommandHandler:
    """Handler for bot commands"""

    COMMANDS = {
        "/help": "显示所有可用命令",
        "/计划": "查看当前学习计划",
        "/进度": "查看学习进度",
        "/错题": "查看错题本",
        "/提醒": "设置学习提醒",
        "/跳过": "跳过当前提醒",
    }

    async def handle(self, command: str) -> str:
        """Process command and return response"""
        command = command.strip().lower()

        if command == "/help":
            return self._format_help()
        elif command == "/计划":
            return await self._get_plan()
        elif command == "/进度":
            return await self._get_progress()
        elif command == "/错题":
            return await self._get_wrong_questions()
        elif command.startswith("/提醒"):
            return await self._set_reminder(command)
        elif command == "/跳过":
            return "已跳过今日提醒"
        else:
            return f"未知命令：{command}\n输入 /help 查看所有命令"

    def _format_help(self) -> str:
        """Format help message"""
        help_text = ["📚 **AI伴学助手 - 可用命令**", ""]
        for cmd, desc in self.COMMANDS.items():
            help_text.append(f"{cmd} - {desc}")
        help_text.append("")
        help_text.append("也可以直接对话，AI会帮你学习知识点~")
        return "\n".join(help_text)

    async def _get_plan(self) -> str:
        """Get current study plan"""
        return """📋 **当前学习计划**

• 每日目标：1个知识点 + 5道练习题
• 学习时间：上午9:00、晚上20:00
• 当前阶段：计算机系统基本知识
• 学习进度：1/45 知识点
"""

    async def _get_progress(self) -> str:
        """Get study progress"""
        return """📊 **学习进度**

• 当前进度：1/45 知识点
• 已连续学习：2天
• 总积分：25分
• 当前等级：Lv.1 学徒

下一知识点：1.2 指令系统"""

    async def _get_wrong_questions(self) -> str:
        """Get wrong questions"""
        return """📕 **错题本**

共收录：2道错题

1️⃣ 存储系统
Q: Cache的主要作用是？
❌ 你的回答：加快硬盘速度
✅ 正确答案：加快CPU访问内存速度

2️⃣ 指令系统
Q: 下列关于RISC的说法...
❌ 你的回答：指令长度固定
✅ 正确答案：指令格式简单

[复习全部错题]"""

    async def _set_reminder(self, command: str) -> str:
        """Set reminder"""
        return "⏰ 提醒设置成功！\n将在每天09:00和20:00提醒你学习~"
