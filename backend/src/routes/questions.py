# AI Study Assistant - Questions Routes

from fastapi import APIRouter
from typing import Optional

from src.database.db import db
import json

router = APIRouter(prefix="/api/questions", tags=["题目"])


@router.get("/{knowledge_id}")
async def get_questions(knowledge_id: int):
    """获取知识点的题目"""
    # 先尝试从数据库获取题目
    results = db.fetch_all(
        """SELECT id, type, content, options, answer, analysis
           FROM questions WHERE knowledge_point = ? AND status = 'approved'
           ORDER BY difficulty LIMIT 5""",
        (str(knowledge_id),)
    )

    if results:
        return {
            "data": [
                {
                    "id": r[0],
                    "type": r[1],
                    "content": r[2],
                    "options": json.loads(r[3]) if r[3] else {},
                    "answer": r[4],
                    "analysis": r[5]
                }
                for r in results
            ]
        }

    # 如果没有题目，生成示例题目
    sample_questions = _get_sample_questions(knowledge_id)
    return {"data": sample_questions}


def _get_sample_questions(knowledge_id: int) -> list:
    """获取示例题目"""
    if knowledge_id == 1:  # 存储器
        return [
            {
                "id": 1001,
                "type": "single",
                "content": "下列关于Cache的说法，错误的是？",
                "options": {
                    "A": "位于CPU和内存之间",
                    "B": "容量比内存大",
                    "C": "访问速度比内存快",
                    "D": "由高速SRAM组成"
                },
                "answer": "B",
                "analysis": "Cache的容量通常比内存小很多，一般只有几MB到几十MB，而内存可以达到几GB甚至更多。所以B选项是错误的。"
            },
            {
                "id": 1002,
                "type": "single",
                "content": "在Cache系统中，采用的替换算法不包括？",
                "options": {
                    "A": "FIFO",
                    "B": "LRU",
                    "C": "OPT",
                    "D": "LFU"
                },
                "answer": "C",
                "analysis": "OPT（最优替换算法）是理想状态下的算法，无法实际实现。常用的替换算法包括FIFO、LRU和LFU。"
            },
            {
                "id": 1003,
                "type": "judge",
                "content": "Cache的命中率越高越好，没有负面影响。",
                "options": {"A": "对", "B": "错"},
                "answer": "false",
                "analysis": "提高Cache命中率会增加复杂度，可能导致访问延迟增加。在某些场景下，简单快速的Cache反而更有效。"
            },
            {
                "id": 1004,
                "type": "single",
                "content": "多级Cache比单级Cache更能提高命中率。",
                "options": {
                    "A": "正确，级数越多越好",
                    "B": "错误，多级Cache会降低命中率",
                    "C": "正确，但级数过多会增加延迟",
                    "D": "错误，多级Cache没有意义"
                },
                "answer": "C",
                "analysis": "多级Cache（如L1、L2、L3）确实能提高整体命中率，但级数过多会增加访问延迟，需要权衡。"
            },
            {
                "id": 1005,
                "type": "multi",
                "content": "下列属于Cache写策略的有？",
                "options": {
                    "A": "写直达",
                    "B": "写回法",
                    "C": "预取",
                    "D": "替换"
                },
                "answer": ["A", "B"],
                "analysis": "Cache写策略主要包括写直达（Write Through）和写回法（Write Back）。预取和替换属于Cache的其他机制。"
            }
        ]
    return [
        {
            "id": knowledge_id * 100,
            "type": "single",
            "content": f"关于知识点{knowledge_id}的练习题，答案选择最合适的选项。",
            "options": {"A": "选项A", "B": "选项B", "C": "选项C", "D": "选项D"},
            "answer": "B",
            "analysis": "这是示例题目的解析。"
        }
    ]