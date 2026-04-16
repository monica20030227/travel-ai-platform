
import random
from typing import Dict, List, Tuple

import pandas as pd
import streamlit as st


st.set_page_config(page_title="國內旅遊推薦平台", page_icon="🧭", layout="wide")


# =========================
# 資料區
# =========================

QUESTIONS = [
    ("planning", "我喜歡在出發前就把交通、景點與時間安排清楚。"),
    ("planning", "我不喜歡臨時改變行程。"),
    ("planning", "我會事先查好餐廳、景點或住宿評價。"),
    ("planning", "行程越詳細，我旅行時越有安全感。"),
    ("planning", "我旅行時傾向照著原本規劃走。"),

    ("relax", "我旅行時喜歡放慢步調、放鬆為主。"),
    ("relax", "我不喜歡一天跑太多景點。"),
    ("relax", "我覺得『耍廢』也是旅行的一部分。"),
    ("relax", "我可以接受花很多時間待在同一個地方。"),
    ("relax", "我比較不喜歡趕行程。"),

    ("adventure", "我喜歡嘗試新奇或刺激的活動。"),
    ("adventure", "我旅行時願意挑戰沒做過的事情。"),
    ("adventure", "我喜歡戶外活動勝過室內行程。"),
    ("adventure", "我會主動找特別體驗活動。"),
    ("adventure", "我不介意比較累或需要體力的行程。"),

    ("food", "我旅行最在意的是吃到好吃的東西。"),
    ("photo", "我會為了拍照好看而去某些景點。"),
    ("culture", "我喜歡了解當地文化、歷史或故事。"),
    ("photo", "我會特別安排熱門打卡景點。"),
    ("culture", "我很重視旅行中的氛圍感與地方特色。"),

    ("spend", "我願意為了住宿品質多花一點錢。"),
    ("budget", "我旅行時會精打細算。"),
    ("spend", "對我來說，舒服比省錢更重要。"),
    ("budget", "我偏好 CP 值高的方案。"),
    ("spend", "我願意為了特別體驗額外花錢。"),
]

DIMENSIONS = [
    "planning", "relax", "adventure", "food", "photo", "culture", "spend", "budget"
]

DIMENSION_LABELS = {
    "planning": "規劃傾向",
    "relax": "放鬆傾向",
    "adventure": "冒險傾向",
    "food": "美食傾向",
    "photo": "拍照傾向",
    "culture": "文化傾向",
    "spend": "享受傾向",
    "budget": "精省傾向",
}

DESTINATIONS = [
    {
        "name": "苗栗懶人露營",
        "region": "苗栗",
        "tags": ["露營", "放鬆", "拍照", "朋友", "情侶"],
        "scores": {"planning": 2.8, "relax": 4.9, "adventure": 2.6, "food": 3.1, "photo": 4.7, "culture": 2.0, "spend": 4.3, "budget": 2.1},
        "spots": [
            {"name": "豪華露營園區 check-in", "type": "stay", "time": "中午", "duration": 1.5, "scores": {"relax": 5.0, "photo": 4.8, "spend": 4.5}},
            {"name": "森林步道散步", "type": "nature", "time": "下午", "duration": 1.5, "scores": {"relax": 4.6, "adventure": 2.3, "photo": 4.1}},
            {"name": "園區下午茶", "type": "food", "time": "下午", "duration": 1.0, "scores": {"food": 3.4, "relax": 4.5, "photo": 4.2}},
            {"name": "夕陽拍照時段", "type": "photo", "time": "傍晚", "duration": 1.0, "scores": {"photo": 4.9, "relax": 4.4}},
            {"name": "BBQ 晚餐", "type": "food", "time": "晚上", "duration": 1.5, "scores": {"food": 4.0, "relax": 4.2, "spend": 3.8}},
            {"name": "營火／星空活動", "type": "night", "time": "晚上", "duration": 1.0, "scores": {"relax": 4.8, "photo": 4.0}},
            {"name": "營區早餐", "type": "food", "time": "早上", "duration": 1.0, "scores": {"food": 3.3, "relax": 4.2}},
            {"name": "附近景觀咖啡廳", "type": "cafe", "time": "上午", "duration": 1.5, "scores": {"photo": 4.5, "relax": 4.4, "food": 3.5}},
            {"name": "在地伴手禮小店", "type": "shopping", "time": "中午", "duration": 1.0, "scores": {"culture": 2.4, "photo": 3.1}},
        ],
    },
    {
        "name": "花蓮慢旅",
        "region": "花蓮",
        "tags": ["海景", "慢旅", "放鬆", "夜市"],
        "scores": {"planning": 2.9, "relax": 4.8, "adventure": 3.2, "food": 4.1, "photo": 4.5, "culture": 3.1, "spend": 3.6, "budget": 2.8},
        "spots": [
            {"name": "花蓮市區早午餐", "type": "food", "time": "中午", "duration": 1.0, "scores": {"food": 4.2, "relax": 3.5}},
            {"name": "七星潭散步", "type": "nature", "time": "下午", "duration": 1.5, "scores": {"relax": 5.0, "photo": 4.8}},
            {"name": "海景咖啡廳", "type": "cafe", "time": "下午", "duration": 1.5, "scores": {"relax": 4.9, "photo": 4.6, "food": 3.4}},
            {"name": "東大門夜市", "type": "night", "time": "晚上", "duration": 2.0, "scores": {"food": 4.8, "photo": 3.0, "culture": 3.0}},
            {"name": "文創園區／散步街區", "type": "culture", "time": "上午", "duration": 1.5, "scores": {"culture": 3.8, "photo": 4.0, "relax": 3.7}},
            {"name": "山線景觀點", "type": "nature", "time": "上午", "duration": 2.0, "scores": {"photo": 4.4, "relax": 4.3, "adventure": 3.1}},
            {"name": "在地小吃午餐", "type": "food", "time": "中午", "duration": 1.0, "scores": {"food": 4.5}},
            {"name": "伴手禮採買", "type": "shopping", "time": "下午", "duration": 0.8, "scores": {"food": 3.0, "culture": 2.2}},
        ],
    },
    {
        "name": "台南美食文化行",
        "region": "台南",
        "tags": ["美食", "古蹟", "散步", "文青"],
        "scores": {"planning": 3.9, "relax": 3.4, "adventure": 1.9, "food": 5.0, "photo": 4.0, "culture": 4.8, "spend": 3.0, "budget": 4.0},
        "spots": [
            {"name": "牛肉湯早餐", "type": "food", "time": "早上", "duration": 1.0, "scores": {"food": 5.0}},
            {"name": "神農街散步", "type": "culture", "time": "上午", "duration": 1.5, "scores": {"culture": 4.6, "photo": 4.5, "relax": 3.2}},
            {"name": "藍晒圖／文創街區", "type": "photo", "time": "下午", "duration": 1.2, "scores": {"photo": 4.7, "culture": 3.5}},
            {"name": "老宅咖啡廳", "type": "cafe", "time": "下午", "duration": 1.2, "scores": {"food": 3.8, "photo": 4.0, "relax": 3.6}},
            {"name": "花園夜市", "type": "night", "time": "晚上", "duration": 2.0, "scores": {"food": 4.9, "photo": 3.2}},
            {"name": "安平老街", "type": "culture", "time": "上午", "duration": 1.5, "scores": {"culture": 4.8, "food": 4.0, "photo": 4.1}},
            {"name": "古蹟景點", "type": "culture", "time": "中午", "duration": 1.3, "scores": {"culture": 4.9, "photo": 3.8}},
            {"name": "甜點冰品收尾", "type": "food", "time": "下午", "duration": 1.0, "scores": {"food": 4.7, "photo": 3.6}},
        ],
    },
    {
        "name": "台中網美放鬆行",
        "region": "台中",
        "tags": ["咖啡", "拍照", "市區", "輕鬆"],
        "scores": {"planning": 3.4, "relax": 4.1, "adventure": 2.0, "food": 4.4, "photo": 4.9, "culture": 3.0, "spend": 3.8, "budget": 2.8},
        "spots": [
            {"name": "早午餐名店", "type": "food", "time": "早上", "duration": 1.2, "scores": {"food": 4.5, "photo": 4.0}},
            {"name": "審計新村", "type": "photo", "time": "上午", "duration": 1.5, "scores": {"photo": 4.9, "culture": 3.2}},
            {"name": "咖啡廳巡禮", "type": "cafe", "time": "下午", "duration": 1.5, "scores": {"photo": 4.8, "food": 4.0, "relax": 4.2}},
            {"name": "草悟道散步", "type": "nature", "time": "下午", "duration": 1.0, "scores": {"relax": 4.0, "photo": 4.0}},
            {"name": "逢甲夜市", "type": "night", "time": "晚上", "duration": 2.0, "scores": {"food": 4.8, "photo": 3.2}},
            {"name": "文青選物店", "type": "shopping", "time": "上午", "duration": 1.0, "scores": {"photo": 4.3, "culture": 2.6}},
            {"name": "景觀餐廳午餐", "type": "food", "time": "中午", "duration": 1.3, "scores": {"food": 4.2, "photo": 4.3, "spend": 3.8}},
            {"name": "甜點名店收尾", "type": "food", "time": "下午", "duration": 1.0, "scores": {"food": 4.6, "photo": 3.9}},
        ],
    },
    {
        "name": "清境山林療癒行",
        "region": "南投",
        "tags": ["山景", "自然", "拍照", "放鬆"],
        "scores": {"planning": 3.2, "relax": 4.7, "adventure": 3.3, "food": 3.0, "photo": 4.7, "culture": 2.5, "spend": 3.9, "budget": 2.5},
        "spots": [
            {"name": "山景民宿 check-in", "type": "stay", "time": "中午", "duration": 1.0, "scores": {"relax": 4.6, "photo": 4.4, "spend": 4.0}},
            {"name": "青青草原", "type": "nature", "time": "下午", "duration": 1.8, "scores": {"photo": 4.8, "relax": 4.2}},
            {"name": "山景下午茶", "type": "cafe", "time": "下午", "duration": 1.0, "scores": {"relax": 4.5, "photo": 4.4}},
            {"name": "觀星時段", "type": "night", "time": "晚上", "duration": 1.0, "scores": {"relax": 4.7, "photo": 4.2}},
            {"name": "清晨觀景點", "type": "nature", "time": "早上", "duration": 1.2, "scores": {"photo": 4.9, "relax": 4.7}},
            {"name": "高山步道", "type": "adventure", "time": "上午", "duration": 1.5, "scores": {"adventure": 3.8, "photo": 4.1}},
            {"name": "特色午餐", "type": "food", "time": "中午", "duration": 1.0, "scores": {"food": 3.3}},
        ],
    },
    {
        "name": "台東冒險海岸行",
        "region": "台東",
        "tags": ["海岸", "冒險", "活動", "公路"],
        "scores": {"planning": 2.6, "relax": 3.8, "adventure": 4.9, "food": 3.5, "photo": 4.4, "culture": 2.8, "spend": 3.5, "budget": 2.6},
        "spots": [
            {"name": "海邊早午餐", "type": "food", "time": "中午", "duration": 1.0, "scores": {"food": 3.7, "photo": 3.9}},
            {"name": "飛行傘／滑翔傘體驗", "type": "adventure", "time": "下午", "duration": 2.0, "scores": {"adventure": 5.0, "photo": 4.7, "spend": 4.0}},
            {"name": "海岸公路拍照點", "type": "photo", "time": "傍晚", "duration": 1.0, "scores": {"photo": 4.8, "relax": 3.4}},
            {"name": "台東市區晚餐", "type": "food", "time": "晚上", "duration": 1.2, "scores": {"food": 3.8}},
            {"name": "看日出", "type": "nature", "time": "早上", "duration": 1.0, "scores": {"photo": 4.6, "relax": 4.1}},
            {"name": "衝浪／SUP 體驗", "type": "adventure", "time": "上午", "duration": 2.0, "scores": {"adventure": 4.8, "photo": 4.3}},
            {"name": "鐵花村散步", "type": "night", "time": "晚上", "duration": 1.0, "scores": {"culture": 3.0, "relax": 3.4, "photo": 3.8}},
        ],
    },
    {
        "name": "宜蘭溫泉美食行",
        "region": "宜蘭",
        "tags": ["溫泉", "美食", "輕旅行", "朋友"],
        "scores": {"planning": 3.2, "relax": 4.8, "adventure": 2.2, "food": 4.4, "photo": 3.9, "culture": 3.2, "spend": 3.8, "budget": 3.0},
        "spots": [
            {"name": "羅東早午餐", "type": "food", "time": "早上", "duration": 1.0, "scores": {"food": 4.1}},
            {"name": "特色咖啡廳", "type": "cafe", "time": "上午", "duration": 1.2, "scores": {"relax": 4.3, "photo": 4.0}},
            {"name": "溫泉旅宿 check-in", "type": "stay", "time": "下午", "duration": 1.0, "scores": {"relax": 5.0, "spend": 4.1}},
            {"name": "泡湯放鬆", "type": "relax", "time": "下午", "duration": 1.5, "scores": {"relax": 5.0}},
            {"name": "羅東夜市", "type": "night", "time": "晚上", "duration": 2.0, "scores": {"food": 4.7}},
            {"name": "文青小店／伴手禮", "type": "shopping", "time": "上午", "duration": 1.0, "scores": {"culture": 3.3, "photo": 3.4}},
            {"name": "景觀午餐", "type": "food", "time": "中午", "duration": 1.2, "scores": {"food": 4.2, "relax": 3.8}},
        ],
    },
]


# =========================
# 工具函式
# =========================

def init_state():
    if "members" not in st.session_state:
        st.session_state.members = []
    if "member_counter" not in st.session_state:
        st.session_state.member_counter = 1
    if "draft_name" not in st.session_state:
        st.session_state.draft_name = f"朋友{st.session_state.member_counter}"
    if "draft_travel_style" not in st.session_state:
        st.session_state.draft_travel_style = "朋友"
    if "draft_budget_level" not in st.session_state:
        st.session_state.draft_budget_level = "中等"
    if "draft_answers" not in st.session_state:
        st.session_state.draft_answers = [3] * len(QUESTIONS)
    if "reset_draft_pending" not in st.session_state:
        st.session_state.reset_draft_pending = False
    if "success_message" not in st.session_state:
        st.session_state.success_message = ""


def reset_draft():
    st.session_state.draft_name = f"朋友{st.session_state.member_counter}"
    st.session_state.draft_travel_style = "朋友"
    st.session_state.draft_budget_level = "中等"
    st.session_state.draft_answers = [3] * len(QUESTIONS)
    for idx in range(len(QUESTIONS)):
        key = f"q_{idx}"
        if key in st.session_state:
            del st.session_state[key]


def average_dimension_scores(answers: List[int]) -> Dict[str, float]:
    grouped = {k: [] for k in DIMENSIONS}
    for (dim, _), answer in zip(QUESTIONS, answers):
        grouped[dim].append(answer)
    return {dim: round(sum(vals) / len(vals), 2) if vals else 0 for dim, vals in grouped.items()}


def persona_label(profile: Dict[str, float]) -> str:
    planning = profile["planning"]
    relax = profile["relax"]
    adventure = profile["adventure"]
    food = profile["food"]
    photo = profile["photo"]
    culture = profile["culture"]

    if adventure >= 4.1:
        return "冒險探索型"
    if food >= 4.3 and culture >= 4.0:
        return "美食文化型"
    if relax >= 4.3 and planning <= 3.0:
        return "隨性療癒型"
    if photo >= 4.3:
        return "打卡風格型"
    if planning >= 4.0 and relax <= 3.3:
        return "計畫行軍型"
    if culture >= 4.2:
        return "文青探索型"
    if relax >= 4.0:
        return "慢旅放鬆型"
    return "均衡旅遊型"


def destination_match_score(profile: Dict[str, float], dest: Dict) -> float:
    d = dest["scores"]
    score = 0.0
    weights = {
        "planning": 0.12,
        "relax": 0.18,
        "adventure": 0.16,
        "food": 0.16,
        "photo": 0.14,
        "culture": 0.12,
        "spend": 0.07,
        "budget": 0.05,
    }
    for key, weight in weights.items():
        score += (5 - abs(profile[key] - d.get(key, 3))) * weight * 20

    top_dims = sorted(profile.items(), key=lambda x: x[1], reverse=True)[:2]
    bonus = 0
    for dim, value in top_dims:
        bonus += d.get(dim, 3) * value * 0.8
    return round(score + bonus, 2)


def recommend_destinations(profile: Dict[str, float], top_n: int = 3) -> List[Tuple[Dict, float]]:
    scored = [(dest, destination_match_score(profile, dest)) for dest in DESTINATIONS]
    scored.sort(key=lambda x: x[1], reverse=True)
    return scored[:top_n]


def spot_match_score(profile: Dict[str, float], spot: Dict) -> float:
    base = 0.0
    ss = spot.get("scores", {})
    for dim, user_score in profile.items():
        spot_score = ss.get(dim, 2.8)
        base += (5 - abs(user_score - spot_score))
    noise = random.uniform(-0.45, 0.45)
    return round(base + noise, 3)


def build_dynamic_itinerary(profile: Dict[str, float], destination: Dict, seed: int = 42) -> Dict[str, List[Dict]]:
    random.seed(seed)

    spots = destination["spots"][:]
    scored_spots = [(spot, spot_match_score(profile, spot)) for spot in spots]
    scored_spots.sort(key=lambda x: x[1], reverse=True)

    selected = []
    used_types = set()

    for spot, s in scored_spots:
        if spot["type"] not in used_types or len(selected) < 3:
            selected.append({**spot, "fit_score": s})
            used_types.add(spot["type"])
        if len(selected) >= 6:
            break

    if len(selected) < 6:
        for spot, s in scored_spots:
            if spot["name"] not in [x["name"] for x in selected]:
                selected.append({**spot, "fit_score": s})
            if len(selected) >= 6:
                break

    relax = profile["relax"]
    planning = profile["planning"]
    adventure = profile["adventure"]

    if relax >= 4.2:
        day1_count = 3
    elif planning >= 4.2 or adventure >= 4.2:
        day1_count = 4
    else:
        day1_count = 3

    day1 = selected[:day1_count]
    day2 = selected[day1_count:]

    time_order = {"早上": 1, "上午": 2, "中午": 3, "下午": 4, "傍晚": 5, "晚上": 6}
    day1 = sorted(day1, key=lambda x: time_order.get(x["time"], 9))
    day2 = sorted(day2, key=lambda x: time_order.get(x["time"], 9))

    return {"Day 1": day1, "Day 2": day2}


def build_reason_text(profile: Dict[str, float], destination: Dict) -> str:
    strong = sorted(profile.items(), key=lambda x: x[1], reverse=True)[:3]
    dim_names = [DIMENSION_LABELS[d] for d, _ in strong]
    return (
        f"系統判斷你在「{dim_names[0]}、{dim_names[1]}、{dim_names[2]}」的傾向較高，"
        f"而 {destination['name']} 在這些特徵上的匹配度也較高，因此列為你的推薦地點之一。"
    )


def itinerary_comment(profile: Dict[str, float], itinerary: Dict[str, List[Dict]]) -> str:
    if profile["relax"] >= 4.2:
        style = "整體節奏偏慢，安排了較多停留與放鬆時間"
    elif profile["adventure"] >= 4.2:
        style = "整體節奏較有活力，安排了較多活動型與戶外型體驗"
    elif profile["planning"] >= 4.2:
        style = "整體節奏較緊湊，景點銜接會比較明確"
    else:
        style = "整體節奏均衡，兼顧景點、用餐與休息"
    total = sum(len(v) for v in itinerary.values())
    return f"這份兩天一夜行程是依照你的問卷分數動態組合而成，{style}，共挑選 {total} 個適合你的停留點。"


def radar_df(profile: Dict[str, float]) -> pd.DataFrame:
    return pd.DataFrame({
        "構面": [DIMENSION_LABELS[d] for d in DIMENSIONS],
        "分數": [profile[d] for d in DIMENSIONS]
    })


def group_recommendation(members: List[Dict], top_n: int = 3) -> List[Tuple[Dict, float]]:
    if not members:
        return []

    agg_scores = []
    for dest in DESTINATIONS:
        per_member = [destination_match_score(m["profile"], dest) for m in members]
        avg_score = sum(per_member) / len(per_member)
        spread = max(per_member) - min(per_member) if len(per_member) > 1 else 0
        final_score = avg_score - (spread * 0.15)
        agg_scores.append((dest, round(final_score, 2), per_member))

    agg_scores.sort(key=lambda x: x[1], reverse=True)
    return [(dest, score) for dest, score, _ in agg_scores[:top_n]]


def to_download_rows(members: List[Dict]) -> pd.DataFrame:
    rows = []
    for m in members:
        row = {"姓名": m["name"], "人格類型": m["persona"]}
        for dim in DIMENSIONS:
            row[DIMENSION_LABELS[dim]] = m["profile"][dim]
        for idx, rec in enumerate(m["recommendations"], start=1):
            row[f"個人推薦{idx}"] = rec[0]["name"]
            row[f"個人推薦{idx}分數"] = rec[1]
        rows.append(row)
    return pd.DataFrame(rows)


def get_current_answers() -> List[int]:
    answers = []
    for idx in range(len(QUESTIONS)):
        answers.append(int(st.session_state.get(f"q_{idx}", st.session_state.draft_answers[idx])))
    st.session_state.draft_answers = answers[:]
    return answers


def add_current_member():
    name = st.session_state.draft_name.strip()
    if not name:
        st.warning("請先輸入姓名或暱稱。")
        return

    answers = get_current_answers()
    profile = average_dimension_scores(answers)
    persona = persona_label(profile)
    recs = recommend_destinations(profile, top_n=3)

    st.session_state.members.append({
        "name": name,
        "travel_style": st.session_state.draft_travel_style,
        "budget_level": st.session_state.draft_budget_level,
        "answers": answers,
        "profile": profile,
        "persona": persona,
        "recommendations": recs
    })
    st.session_state.member_counter += 1
    st.session_state.success_message = f"已完成 {name} 的分析！人格類型：{persona}"
    st.session_state.reset_draft_pending = True
    st.rerun()


# =========================
# UI
# =========================

init_state()

if st.session_state.reset_draft_pending:
    reset_draft()
    st.session_state.reset_draft_pending = False

st.title("🧭 國內旅遊人格 AI 推薦平台")
st.caption("多人問卷蒐集 → 個人化推薦 → 動態兩天一夜行程 → 全體綜合推薦")

if st.session_state.success_message:
    st.success(st.session_state.success_message)
    st.session_state.success_message = ""

with st.sidebar:
    st.header("平台說明")
    st.write(
        "這個版本採用混合式推薦：\n"
        "1. 問卷轉成旅遊人格分數\n"
        "2. 依個人偏好動態計算目的地匹配度\n"
        "3. 從景點資料庫中動態挑選兩天一夜行程\n"
        "4. 最後整合朋友們的結果，輸出綜合前三推薦"
    )
    st.markdown("---")
    st.subheader("目前已加入成員")
    if st.session_state.members:
        for idx, member in enumerate(st.session_state.members, start=1):
            st.write(f"{idx}. {member['name']}｜{member['persona']}")
    else:
        st.caption("尚未加入任何朋友")

    if st.button("清除所有成員資料"):
        st.session_state.members = []
        st.session_state.member_counter = 1
        st.session_state.success_message = ""
        st.session_state.reset_draft_pending = True
        st.rerun()


tab1, tab2, tab3 = st.tabs(["新增朋友問卷", "個人推薦結果", "群體綜合分析"])

with tab1:
    st.subheader("新增一位朋友的旅遊問卷")
    st.info("先輸入姓名，再直接往下填所有問題；只有按下最下面的「加入這位朋友並分析」才會真的送出。")

    name_col1, name_col2 = st.columns([1.4, 1])
    with name_col1:
        st.text_input(
            "姓名 / 暱稱",
            key="draft_name",
            placeholder=f"例如：朋友{st.session_state.member_counter}",
        )
    with name_col2:
        st.write("")
        st.write("")
        st.caption("輸入名字後直接繼續往下填即可，不會立刻送出")

    col1, col2 = st.columns(2)
    with col1:
        st.selectbox("偏好旅伴型態", ["朋友", "情侶", "家人", "不限"], key="draft_travel_style")
    with col2:
        st.selectbox("預算感受", ["偏精省", "中等", "願意多花一些"], key="draft_budget_level")

    st.markdown("### 請依 1～5 分回答")
    st.caption("1 = 非常不同意，5 = 非常同意")

    for idx, (_, q) in enumerate(QUESTIONS):
        default_value = st.session_state.draft_answers[idx]
        st.slider(
            f"{idx + 1}. {q}",
            min_value=1,
            max_value=5,
            value=default_value,
            key=f"q_{idx}",
            help="這一題目前的分數會先暫存，最後按加入才會送出。"
        )

    action_col1, action_col2 = st.columns([1, 1])
    with action_col1:
        if st.button("加入這位朋友並分析", type="primary", use_container_width=True):
            add_current_member()
    with action_col2:
        if st.button("清空這份問卷", use_container_width=True):
            st.session_state.reset_draft_pending = True
            st.rerun()

with tab2:
    st.subheader("每位朋友的個人推薦結果")
    if not st.session_state.members:
        st.info("目前還沒有資料，請先到「新增朋友問卷」加入成員。")
    else:
        member_names = [m["name"] for m in st.session_state.members]
        selected_name = st.selectbox("選擇想查看的朋友", member_names)
        member = next(m for m in st.session_state.members if m["name"] == selected_name)

        c1, c2 = st.columns([1.1, 1.4])
        with c1:
            st.metric("旅遊人格", member["persona"])
            profile_df = radar_df(member["profile"])
            st.bar_chart(profile_df.set_index("構面"))

        with c2:
            st.markdown("### 個人前三推薦")
            for i, (dest, score) in enumerate(member["recommendations"], start=1):
                st.markdown(f"**Top {i}. {dest['name']}**｜匹配分數：`{score}`")
                st.write(build_reason_text(member["profile"], dest))

        st.markdown("---")
        st.markdown("### 依第一名推薦地點動態生成兩天一夜行程")
        top_dest = member["recommendations"][0][0]

        seed = st.number_input("行程隨機種子（修改可得到不同版本）", min_value=1, max_value=9999, value=42, step=1)
        itinerary = build_dynamic_itinerary(member["profile"], top_dest, seed=seed)

        st.write(f"**推薦地點：{top_dest['name']}**")
        st.info(itinerary_comment(member["profile"], itinerary))

        for day, items in itinerary.items():
            st.markdown(f"#### {day}")
            for idx, item in enumerate(items, start=1):
                st.write(f"{idx}. **{item['time']}｜{item['name']}**（適配分數：{item['fit_score']}）")

with tab3:
    st.subheader("全體朋友綜合分析")
    members = st.session_state.members
    if not members:
        st.info("請先至少加入 1 位朋友。")
    else:
        st.markdown("### 全體綜合前三推薦")
        group_top = group_recommendation(members, top_n=3)
        for i, (dest, score) in enumerate(group_top, start=1):
            st.markdown(f"**Top {i}. {dest['name']}**｜綜合分數：`{score}`")
            st.write(f"適合原因：{', '.join(dest['tags'])}")

        st.markdown("---")
        st.markdown("### 全體平均人格分數")
        avg_profile = {}
        for dim in DIMENSIONS:
            avg_profile[dim] = round(sum(m["profile"][dim] for m in members) / len(members), 2)

        avg_df = radar_df(avg_profile)
        st.bar_chart(avg_df.set_index("構面"))

        st.markdown("### 推薦一個綜合兩天一夜行程")
        best_group_dest = group_top[0][0]
        group_itinerary = build_dynamic_itinerary(avg_profile, best_group_dest, seed=77)
        st.write(f"**綜合推薦地點：{best_group_dest['name']}**")
        st.info("這份行程是以全體平均偏好生成，並考慮成員之間的差異不要太大。")

        for day, items in group_itinerary.items():
            st.markdown(f"#### {day}")
            for idx, item in enumerate(items, start=1):
                st.write(f"{idx}. **{item['time']}｜{item['name']}**（適配分數：{item['fit_score']}）")

        st.markdown("---")
        st.markdown("### 匯出結果")
        export_df = to_download_rows(members)
        st.dataframe(export_df, use_container_width=True)
        csv_data = export_df.to_csv(index=False).encode("utf-8-sig")
        st.download_button(
            label="下載分析結果 CSV",
            data=csv_data,
            file_name="travel_group_analysis.csv",
            mime="text/csv"
        )
