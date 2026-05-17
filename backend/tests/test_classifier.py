"""Document classifier unit tests (no real API calls)."""

import json
from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from src.modules.ai.classifier import DocumentClassifier


class TestClassifierParseJson:
    def setup_method(self):
        self.classifier = DocumentClassifier(api_key="test", model="test-model")

    def test_parse_valid_json(self):
        text = '{"classification": "practice_questions", "confidence": 0.9, "reasoning": "含题目"}'
        result = self.classifier._parse_json(text)
        assert result["classification"] == "practice_questions"
        assert result["confidence"] == 0.9

    def test_parse_json_embedded_in_text(self):
        text = '分析结果如下：\n{"classification": "knowledge_points", "confidence": 0.8, "reasoning": "讲解"}'
        result = self.classifier._parse_json(text)
        assert result["classification"] == "knowledge_points"

    def test_parse_invalid_returns_fallback(self):
        result = self.classifier._parse_json("not json at all")
        assert result["classification"] == "other"
        assert result["confidence"] == 0.5


@pytest.mark.asyncio
class TestClassifierClassify:
    async def test_classify_success_mocked(self):
        classifier = DocumentClassifier(api_key="test-key", model="test")
        mock_response = {
            "choices": [
                {
                    "message": {
                        "content": json.dumps(
                            {
                                "classification": "mixed",
                                "confidence": 0.85,
                                "reasoning": "混合内容",
                            }
                        )
                    }
                }
            ]
        }

        mock_resp = AsyncMock()
        mock_resp.status = 200
        mock_resp.json = AsyncMock(return_value=mock_response)

        mock_ctx = AsyncMock()
        mock_ctx.__aenter__ = AsyncMock(return_value=mock_resp)
        mock_ctx.__aexit__ = AsyncMock(return_value=None)

        mock_session = MagicMock()
        mock_session.post = MagicMock(return_value=mock_ctx)
        mock_session.__aenter__ = AsyncMock(return_value=mock_session)
        mock_session.__aexit__ = AsyncMock(return_value=None)

        with patch("aiohttp.ClientSession", return_value=mock_session):
            result = await classifier.classify("这是一段测试文档内容")

        assert result["classification"] == "mixed"
        assert result["confidence"] == 0.85

    async def test_classify_api_failure_returns_fallback(self):
        classifier = DocumentClassifier(api_key="test-key", model="test")

        with patch("aiohttp.ClientSession") as mock_session_cls:
            mock_session_cls.side_effect = Exception("network error")
            result = await classifier.classify("测试")

        assert result["classification"] == "other"
        assert "失败" in result["reasoning"]
