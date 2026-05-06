# AI Study Assistant - Socratic Questioning Service

from loguru import logger

from src.config.settings import settings


class SocraticService:
    """Service for analyzing user responses and generating Socratic feedback"""

    def __init__(self, api_key: str = None, model: str = "MiniMax-M2.7"):
        self.api_key = api_key or settings.ai.api_key
        self.model = model
        self.base_url = "https://api.minimaxi.com/v1"

    def analyze(self, knowledge_code: str, user_answer: str) -> dict:
        """Analyze user answer and return feedback with follow-up question"""
        knowledge_info = self._get_knowledge_info(knowledge_code)

        answer_lower = user_answer.lower()
        answer_length = len(user_answer)

        correct_keywords = knowledge_info.get("keywords", [])
        wrong_keywords = knowledge_info.get("wrong_keywords", [])
        partial_keywords = knowledge_info.get("partial_keywords", [])

        has_correct = any(kw in answer_lower for kw in correct_keywords if len(kw) > 2)
        has_wrong = any(kw in answer_lower for kw in wrong_keywords if len(kw) > 2)
        has_partial = any(kw in answer_lower for kw in partial_keywords if len(kw) > 2)

        depth_indicators = ["为什么", "因为", "所以", "如果", "怎样", "如何", "原因", "原理", "例子"]
        has_depth = any(ind in user_answer for ind in depth_indicators)

        # 计算回答质量分数 (0-100)
        quality_score = 40  # 基础分

        if has_correct and not has_wrong:
            quality_score = 75
            if answer_length > 30:
                quality_score += 10
            if has_depth:
                quality_score += 15
            if "举例" in user_answer or "例子" in user_answer:
                quality_score += 10
        elif has_wrong:
            quality_score = 25
            if has_correct:
                quality_score = 45
        elif has_partial:
            quality_score = 55
            if answer_length > 20:
                quality_score += 10
            if has_depth:
                quality_score += 10
        else:
            if answer_length > 15:
                quality_score = 50
            if has_depth:
                quality_score += 10

        depth = 0
        if answer_length > 50:
            depth += 1
        if has_depth:
            depth += 1
        if has_correct and not has_wrong:
            depth += 1

        result = {
            "is_understanding_correct": has_correct and not has_wrong and quality_score >= 70,
            "needs_clarification": has_wrong or quality_score < 50,
            "depth_level": min(depth, 5),
            "question_asked": False,
            "answer_quality": min(quality_score, 100)
        }

        if has_correct and not has_wrong:
            result["feedback"] = self._get_correct_feedback(knowledge_code)
            result["follow_up_question"] = knowledge_info["follow_up"][depth % len(knowledge_info["follow_up"])]
            result["question_asked"] = True
        elif has_wrong:
            result["feedback"] = self._get_wrong_feedback(knowledge_code)
            result["follow_up_question"] = knowledge_info["clarify"][0]
        else:
            result["feedback"] = knowledge_info["partial"][depth % len(knowledge_info["partial"])]
            result["follow_up_question"] = knowledge_info["partial"][(depth + 1) % len(knowledge_info["partial"])]

        return result

    def _get_knowledge_info(self, code: str) -> dict:
        """获取知识点的提示信息"""
        info = {
            "1.2.4": {
                "keywords": ["缓存", "cache", "快", "高速", "临时", "存放", "cpu", "内存", "料理台", "厨房"],
                "wrong_keywords": ["硬盘", "磁盘", "永久", "慢", "外部"],
                "follow_up": ["很好！你能举一个生活中的例子吗？比如为什么厨房要有料理台而不是每次都去冰箱拿东西？", "你的理解很到位！那你能说说Cache和内存有什么区别吗？"],
                "clarify": ["嗯，我注意到你提到了硬盘。Cache和硬盘不一样哦，Cache是在CPU和内存之间的小而快的存储。你能重新描述一下吗？", "你说得有些道理，但不完全对。Cache不是硬盘，它是介于CPU和内存之间的高速缓存。能再想想吗？"],
                "partial": ["我明白你的意思，但可以更精确一些。你能用一句话概括Cache的作用吗？", "你的理解在正确的方向上，但还需要完善。想想CPU访问数据的过程，Cache扮演什么角色？"]
            },
            "1.2.1": {
                "keywords": ["存储", "程序", "控制", "运算", "冯诺依曼", "von", "neumann", "结构", "五大"],
                "wrong_keywords": ["并行", "实时", "专用"],
                "follow_up": ["很好！你能说说冯·诺依曼结构的核心思想是什么吗？", "理解正确！那存储器和运算器是怎么配合工作的？"],
                "clarify": ["你提到的是其他体系结构的特征。冯·诺依曼结构的核心是\"存储程序\"，能再解释一下吗？", "你的方向有点偏。冯·诺依曼结构最重要的特点是程序和数据都用二进制表示，存放在同一个存储器中。"],
                "partial": ["你的理解部分正确。能具体说说五个部分中哪几个是核心吗？", "基本正确，但不够完整。五个部分是如何相互协作的呢？"]
            }
        }
        return info.get(code, {
            "keywords": ["概念", "原理", "作用", "特点"],
            "wrong_keywords": [],
            "follow_up": ["很好！能深入解释一下为什么吗？", "理解正确！还有其他想补充的吗？"],
            "clarify": ["你提到了某个不相关的概念。让我们回到主题，这个概念的核心是什么？", "你的理解有些偏差。想想这个概念的原始定义。"],
            "partial": ["你说的有道理，但不够完整。核心要素是什么？", "基本方向对了，但还需要更深入的理解。"]
        })
