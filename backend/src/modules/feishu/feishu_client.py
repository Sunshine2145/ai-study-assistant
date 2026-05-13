# AI Study Assistant - Feishu Client

import aiohttp
from loguru import logger

from src.config.settings import settings


class FeishuClient:
    """Client for Feishu API operations"""

    def __init__(self):
        self.app_id = settings.feishu.app_id
        self.app_secret = settings.feishu.app_secret
        self.base_url = "https://open.feishu.cn/open-apis"

    async def get_access_token(self) -> str:
        """Get tenant access token"""
        url = f"{self.base_url}/auth/v3/tenant_access_token/internal"
        payload = {
            "app_id": self.app_id,
            "app_secret": self.app_secret
        }

        try:
            async with aiohttp.ClientSession() as session:
                async with session.post(url, json=payload) as response:
                    if response.status == 200:
                        result = await response.json()
                        if result.get("code") == 0:
                            return result.get("tenant_access_token")
                        else:
                            logger.error(f"Get token error: {result}")
                            return ""
                    else:
                        logger.error(f"HTTP error: {response.status}")
                        return ""
        except Exception as e:
            logger.error(f"Get token exception: {e}")
            return ""

    async def send_message(self, receive_id: str, content: str, msg_type: str = "text") -> dict:
        """Send message to user"""
        token = await self.get_access_token()
        if not token:
            return {"code": 1, "msg": "Failed to get access token"}

        url = f"{self.base_url}/im/v1/messages?receive_id_type=open_id"
        headers = {
            "Authorization": f"Bearer {token}",
            "Content-Type": "application/json"
        }
        payload = {
            "receive_id": receive_id,
            "msg_type": msg_type,
            "content": content
        }

        try:
            async with aiohttp.ClientSession() as session:
                async with session.post(url, headers=headers, json=payload) as response:
                    result = await response.json()
                    return result
        except Exception as e:
            logger.error(f"Send message error: {e}")
            return {"code": 1, "msg": str(e)}

    async def send_text_message(self, receive_id: str, text: str) -> dict:
        """Send text message"""
        import json
        content = json.dumps({"text": text}, ensure_ascii=False)
        return await self.send_message(receive_id, content, "text")

    async def send_interactive_card(self, receive_id: str, card_content: dict) -> dict:
        """Send interactive card message"""
        import json
        content = json.dumps(card_content)
        return await self.send_message(receive_id, content, "interactive")
