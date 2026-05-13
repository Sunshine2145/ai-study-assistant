# AI Study Assistant - Learning Routes

from fastapi import APIRouter
from typing import Optional
from loguru import logger

from src.database.db import db

router = APIRouter(prefix="/api/learning", tags=["学习"])


@router.get("/status")
async def get_learning_status():
    """获取学习状态"""
    # 获取用户信息
    user = db.fetch_one("SELECT id, score, streak FROM users LIMIT 1")
    if not user:
        return _default_status()

    # 获取知识点统计
    total = db.fetch_one("SELECT COUNT(*) as cnt FROM knowledge_points")['cnt']
    completed = db.fetch_one(
        "SELECT COUNT(*) as cnt FROM knowledge_points WHERE status = 'completed'"
    )['cnt']

    # 获取错题数
    wrong_count = db.fetch_one(
        "SELECT COUNT(*) as cnt FROM wrong_questions WHERE user_id = %s AND mastered = 0",
        (user['id'],)
    )['cnt']

    # 获取当前学习知识点
    current = db.fetch_one(
        "SELECT code, name FROM knowledge_points WHERE status = 'unlocked' LIMIT 1"
    )

    return {
        "user_name": "谭晓磊",
        "streak": user['streak'] or 0,
        "total_points": user['score'] or 0,
        "learn_days": user['streak'] or 1,
        "completed_count": completed or 0,
        "total_count": total or 0,
        "wrong_count": wrong_count or 0,
        "current_knowledge": current['name'] if current else "1.2.4 存储器",
        "estimated_time": "预计学习时长：15分钟",
        "next_learning_tip": "继续学习下一个知识点"
    }


@router.get("/current")
async def get_current_knowledge():
    """获取当前学习知识点"""
    result = db.fetch_one(
        """SELECT id, code, name, chapter, stage
           FROM knowledge_points
           WHERE status = 'unlocked'
           ORDER BY sort_order LIMIT 1"""
    )

    if not result:
        first_kp = db.fetch_one(
            "SELECT id, code, name, chapter, stage FROM knowledge_points ORDER BY sort_order LIMIT 1"
        )
        if first_kp:
            return {
                "id": first_kp['id'],
                "code": first_kp['code'],
                "name": first_kp['name'],
                "chapter": first_kp['chapter'],
                "stage": first_kp['stage'],
                "feynman_content": None,
                "socratic_hint": "请选择一个知识点开始学习"
            }
        return {"id": 1, "code": "1.1", "name": "计算机系统概述", "chapter": "计算机基础", "stage": "第一阶段"}

    return {
        "id": result['id'],
        "code": result['code'],
        "name": result['name'],
        "chapter": result['chapter'],
        "stage": result['stage'],
        "feynman_content": None,
        "socratic_hint": "请用一句话解释这个概念"
    }


@router.get("/feynman/{knowledge_id}")
async def generate_feynman_content(knowledge_id: int):
    """Generate Feynman explanation using AI for the knowledge point"""
    from src.modules.ai.service import AIService

    kp = db.fetch_one(
        "SELECT id, code, name FROM knowledge_points WHERE id = %s",
        (knowledge_id,)
    )

    if not kp:
        return {"success": False, "message": "知识点不存在"}

    try:
        ai_service = AIService()
        feynman_content = await ai_service.generate_feynman_explanation(kp['code'], kp['name'])

        if feynman_content:
            return {
                "success": True,
                "data": {
                    "content": feynman_content,
                    "knowledge_id": kp['id'],
                    "knowledge_name": kp['name']
                }
            }
        else:
            return {
                "success": False,
                "message": "AI服务暂时不可用，请稍后重试"
            }
    except Exception as e:
        logger.error(f"Feynman generation failed: {e}")
        return {
            "success": False,
            "message": f"生成费曼讲解失败: {str(e)}"
        }


def _get_feynman_content(code: str) -> str:
    """根据知识点代码获取费曼讲解内容"""
    contents = {
        "1.2.4": """<p>想象你在厨房做饭：</p>
<ul>
<li>🍽️ <strong>冰箱 = 主存（内存）</strong> - 存放大量食材，但取用较慢</li>
<li>🍳 <strong>料理台 = Cache（缓存）</strong> - 放最常用的配料，取用超快</li>
<li>👨‍🍳 <strong>你 = CPU</strong> - 厨师直接在料理台拿食材做饭</li>
</ul>
<p><strong>为什么需要Cache？</strong></p>
<p>CPU太快了，如果每次都去内存（冰箱）拿数据，CPU会饿死的（等待）。有了Cache（料理台），常用的数据就放在旁边，CPU不用等。</p>
<p><strong>Cache的工作原理：</strong></p>
<p>记住"最近用过的"数据，因为下次很可能还会用到。就像料理台放盐、酱油一样，常用的东西放手边。</p>"""
    }
    return contents.get(code, f"<p>知识点 {code} 的费曼讲解内容正在准备中...</p>")


def _default_status():
    return {
        "user_name": "谭晓磊",
        "streak": 2,
        "total_points": 25,
        "learn_days": 2,
        "completed_count": 1,
        "total_count": 45,
        "wrong_count": 5,
        "current_knowledge": "1.2.4 存储器",
        "estimated_time": "预计学习时长：15分钟",
        "next_learning_tip": "继续学习下一个知识点"
    }


@router.get("/progress/{knowledge_id}")
async def get_learning_progress(knowledge_id: int):
    """获取指定知识点的学习进度"""
    result = db.fetch_one(
        """SELECT feynman_completed, practice_completed, test_completed
           FROM learning_progress
           WHERE knowledge_point_id = %s""",
        (knowledge_id,)
    )
    if not result:
        return {"data": {"feynman": False, "practice": False, "test": False}}
    return {
        "data": {
            "feynman": bool(result['feynman_completed']),
            "practice": bool(result['practice_completed']),
            "test": bool(result['test_completed'])
        }
    }


@router.post("/progress/{knowledge_id}/complete")
async def complete_learning_step(knowledge_id: int, step: str):
    """标记学习步骤完成"""
    valid_steps = ["feynman", "practice", "test"]
    if step not in valid_steps:
        return {"success": False, "message": "无效的学习步骤"}

    db.execute("""
        INSERT INTO learning_progress (user_id, knowledge_point_id, feynman_completed, practice_completed, test_completed)
        VALUES (1, %s, %s, %s, %s)
        ON DUPLICATE KEY UPDATE
        feynman_completed = CASE WHEN %s THEN 1 ELSE feynman_completed END,
        feynman_completed_at = CASE WHEN %s THEN NOW() ELSE feynman_completed_at END,
        practice_completed = CASE WHEN %s THEN 1 ELSE practice_completed END,
        practice_completed_at = CASE WHEN %s THEN NOW() ELSE practice_completed_at END,
        test_completed = CASE WHEN %s THEN 1 ELSE test_completed END,
        test_completed_at = CASE WHEN %s THEN NOW() ELSE test_completed_at END,
        updated_at = NOW()
    """, (knowledge_id,
          1 if step == "feynman" else 0, 1 if step == "practice" else 0, 1 if step == "test" else 0,
          step == "feynman", step == "feynman",
          step == "practice", step == "practice",
          step == "test", step == "test"))

    return {"success": True, "message": f"{step}学习完成"}


@router.get("/can-practice/{knowledge_id}")
async def can_practice(knowledge_id: int):
    """检查是否可以开始练习"""
    result = db.fetch_one(
        "SELECT feynman_completed FROM learning_progress WHERE knowledge_point_id = %s",
        (knowledge_id,)
    )
    can_start = result and result['feynman_completed'] == 1
    return {
        "data": {
            "can_practice": can_start,
            "message": "必须先完成费曼学习才能开始练习" if not can_start else "可以开始练习"
        }
    }


@router.post("/select-unit/{knowledge_id}")
async def select_learning_unit(knowledge_id: int):
    """选择学习单元"""
    kp = db.fetch_one(
        "SELECT id, code, name, status FROM knowledge_points WHERE id = %s",
        (knowledge_id,)
    )
    if not kp:
        return {"success": False, "message": "知识点不存在"}

    if kp['status'] == 'locked':
        return {"success": False, "message": "请先完成前置知识点的学习"}

    db.execute(
        "UPDATE knowledge_points SET status = 'unlocked' WHERE id = %s",
        (knowledge_id,)
    )

    db.execute("""
        INSERT INTO learning_progress (user_id, knowledge_point_id, mastery_percentage, socratic_rounds, learning_phase)
        VALUES (1, %s, 0, 0, 'feynman')
        ON DUPLICATE KEY UPDATE
        learning_phase = 'feynman',
        mastery_percentage = 0,
        socratic_rounds = 0,
        updated_at = NOW()
    """, (knowledge_id,))

    return {"success": True, "message": "已选择该知识点开始学习"}


@router.get("/mastery/{knowledge_id}")
async def get_mastery_status(knowledge_id: int):
    """获取掌握度状态"""
    result = db.fetch_one("""
        SELECT mastery_percentage, socratic_rounds, feynman_completed, practice_completed, learning_phase
        FROM learning_progress
        WHERE knowledge_point_id = %s
    """, (knowledge_id,))

    if not result:
        return {
            "mastery_percentage": 0,
            "socratic_rounds": 0,
            "feynman_completed": False,
            "practice_completed": False,
            "learning_phase": "feynman",
            "threshold_met": False
        }

    return {
        "mastery_percentage": result['mastery_percentage'],
        "socratic_rounds": result['socratic_rounds'],
        "feynman_completed": bool(result['feynman_completed']),
        "practice_completed": bool(result['practice_completed']),
        "learning_phase": result['learning_phase'] or "feynman",
        "threshold_met": result['mastery_percentage'] >= 90,
        "message": "已达标，可以进入练习" if result['mastery_percentage'] >= 90 else f"还需{90 - result['mastery_percentage']}%掌握度"
    }


@router.post("/unlock-next/{knowledge_id}")
async def unlock_next_unit(knowledge_id: int):
    """检查90%阈值并解锁下一单元"""
    result = db.fetch_one("""
        SELECT mastery_percentage, socratic_rounds
        FROM learning_progress
        WHERE knowledge_point_id = %s
    """, (knowledge_id,))

    if not result:
        return {"success": False, "message": "未找到学习进度"}

    mastery = result['mastery_percentage']
    rounds = result['socratic_rounds']

    if mastery < 90:
        return {
            "success": False,
            "message": f"掌握度{mastery}%，还需达到90%才能解锁下一单元",
            "mastery": mastery,
            "rounds": rounds
        }

    db.execute("""
        UPDATE learning_progress
        SET feynman_completed = 1, feynman_completed_at = CURRENT_TIMESTAMP, learning_phase = 'completed'
        WHERE knowledge_point_id = %s
    """, (knowledge_id,))

    # 标记当前知识点为已完成
    db.execute(
        "UPDATE knowledge_points SET status = 'completed' WHERE id = %s",
        (knowledge_id,)
    )

    current_kp = db.fetch_one(
        "SELECT code, sort_order FROM knowledge_points WHERE id = %s",
        (knowledge_id,)
    )

    if current_kp:
        next_kp = db.fetch_one("""
            SELECT id, code, name FROM knowledge_points
            WHERE sort_order > %s AND status = 'locked'
            ORDER BY sort_order LIMIT 1
        """, (current_kp['sort_order'],))

        if next_kp:
            db.execute(
                "UPDATE knowledge_points SET status = 'unlocked' WHERE id = %s",
                (next_kp['id'],)
            )
            return {
                "success": True,
                "message": "太棒了！已掌握该知识点，下一单元已解锁",
                "next_knowledge_id": next_kp['id'],
                "next_knowledge_name": next_kp['name']
            }

    return {"success": True, "message": "太棒了！已掌握该知识点（暂无下一单元）"}


@router.post("/reset")
async def reset_learning_map():
    """重置学习地图"""
    db.execute("""
        UPDATE knowledge_points
        SET status = CASE
            WHEN sort_order = 1 THEN 'unlocked'
            ELSE 'locked'
        END
    """)

    db.execute("DELETE FROM learning_progress")

    return {"success": True, "message": "学习进度已重置，可以重新开始学习"}
