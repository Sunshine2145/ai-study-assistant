# AI Study Assistant - PDF Parser Service

import aiohttp
import re
import json
from loguru import logger


class PDFParser:
    """Service for parsing questions from PDF text using AI"""

    PROMPT_TEMPLATE = """Extract questions from the following text and return as JSON array.

Text:
{text}

Return format (JSON array):
[
  {{
    "type": "single/multi/judge",
    "content": "question text",
    "options": {{"A": "option A", "B": "option B", "C": "option C", "D": "option D"}},
    "answer": "answer letter or true/false",
    "analysis": "explanation if available"
  }}
]

Rules:
- type: single=single choice, multi=multiple choice, judge=true/false
- options: JSON object, empty object {{}} for judge questions
- answer: A/B/C/D for single/multi, true/false for judge
- If cannot extract, return empty array []
"""

    def __init__(self, api_key: str, model: str = "MiniMax-M2.7", base_url: str = None):
        self.api_key = api_key
        self.model = model
        self.base_url = base_url or "https://api.minimaxi.com/v1"

    async def parse(self, text: str) -> list:
        """Parse questions from PDF text"""
        # Clean and truncate text if too long
        text = self._clean_text(text)

        prompt = self.PROMPT_TEMPLATE.format(text=text)

        try:
            async with aiohttp.ClientSession() as session:
                async with session.post(
                    f"{self.base_url}/chat/completions",
                    headers={
                        "Authorization": f"Bearer {self.api_key}",
                        "Content-Type": "application/json"
                    },
                    json={
                        "model": self.model,
                        "messages": [{"role": "user", "content": prompt}],
                        "stream": False
                    }
                ) as response:
                    if response.status == 200:
                        result = await response.json()
                        content = result["choices"][0]["message"]["content"]
                        # Log raw response for debugging
                        logger.info(f"AI response length: {len(content)}")
                        return self._parse_json_response(content)
                    else:
                        error = await response.text()
                        logger.error(f"AI API error: {error}")
                        return []
        except Exception as e:
            logger.error(f"PDF parser error: {e}")
            return []

    def _clean_text(self, text: str, max_length: int = 6000) -> str:
        """Clean and truncate text"""
        # Remove excessive whitespace
        text = re.sub(r'\s+', ' ', text)
        # Truncate if too long
        if len(text) > max_length:
            text = text[:max_length]
        return text

    def _parse_json_response(self, content: str) -> list:
        """Parse JSON from AI response"""
        try:
            # Use regex to find complete JSON array
            # This handles cases where there's text before/after the array
            match = re.search(r'(\[[\s\S]*\])', content)
            if match:
                json_str = match.group(1)
                logger.info(f"Extracted JSON string length: {len(json_str)}")

                # Try to parse
                try:
                    return json.loads(json_str)
                except json.JSONDecodeError as e:
                    logger.error(f"JSON parse error: {e}")

                    # Try to fix by finding balanced braces
                    result = self._fix_and_parse_json(json_str)
                    if result:
                        return result
            else:
                logger.warning("No JSON array found in AI response")

            return []
        except Exception as e:
            logger.error(f"Parse error: {e}")
            return []

    def _fix_and_parse_json(self, json_str: str) -> list:
        """Attempt to fix malformed JSON and extract questions"""
        try:
            # Find all complete JSON objects
            objects = []
            stack = []
            obj_start = -1

            for i, char in enumerate(json_str):
                if char == '{':
                    if not stack:
                        obj_start = i
                    stack.append(char)
                elif char == '}':
                    if stack:
                        stack.pop()
                        if not stack and obj_start >= 0:
                            obj_str = json_str[obj_start:i + 1]
                            try:
                                obj = json.loads(obj_str)
                                objects.append(obj)
                            except:
                                pass
                            obj_start = -1

            if objects:
                logger.info(f"Extracted {len(objects)} objects by brace matching")
                return objects
        except Exception as e:
            logger.error(f"Fix JSON error: {e}")

        return None