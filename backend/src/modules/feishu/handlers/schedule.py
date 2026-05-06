# AI Study Assistant - Schedule Handler

from datetime import datetime
from loguru import logger

from src.config.settings import settings
from src.database.db import db


class ScheduleHandler:
    """Handler for scheduled reminders"""

    def __init__(self):
        self.reminder_times = settings.reminder.default_times

    async def check_and_send_reminders(self):
        """Check if any reminders should be sent now"""
        now = datetime.now()
        current_time = now.strftime("%H:%M")

        if current_time in self.reminder_times:
            await self._send_learning_reminder()

    async def _send_learning_reminder(self):
        """Send daily learning reminder"""
        # Get current knowledge point to learn
        next_kp = db.fetch_one("""
            SELECT code, name FROM knowledge_points
            WHERE status = 'unlocked'
            ORDER BY sort_order ASC
            LIMIT 1
        """)

        if next_kp:
            code, name = next_kp
            message = f"""📚 **学习时间到！**

⏰ 现在是 {datetime.now().strftime('%H:%M')}

今日任务：
• {code} {name}
• 预计学习时长：15分钟

[开始学习 ➤]"""
        else:
            message = """📚 **学习时间到！**

⏰ 现在是学习时间~

今天想学习什么内容？直接告诉我知识点名称吧！
"""

        # In production, this would send via FeishuClient
        logger.info(f"Sending reminder: {message}")

    async def send_milestone_notification(self, achievement: str):
        """Send milestone achievement notification"""
        message = f"""🎉 **恭喜达成成就！**

🌟 **{achievement}**

继续保持，加油！💪
"""
        logger.info(f"Sending milestone: {message}")
