import random
from datetime import datetime
from typing import Dict, List, Tuple

import gspread
import pandas as pd
import streamlit as st
from google.oauth2.service_account import Credentials


st.set_page_config(page_title="國內旅遊推薦平台", page_icon="🧭", layout="wide")


# =========================
# 基本設定
# =========================
# 改成你自己的 Google Sheet 網址
SHEET_URL = "https://docs.google.com/spreadsheets/d/1n5AwsF_eLQluhVpYrj6YhU27gOOsDYK0KrBuz7AfAeA/edit?gid=0#gid=0"

SHEET_HEADERS = [
    "timestamp", "name", "travel_style", "budget_level",
    *[f"q{i}" for i in range(1, 26)]
]


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

def init_state() -> None:
    if "draft_name" not in st.session_state:
        st.session_state.draft_name = ""
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


def reset_draft() -> None:
    st.session_state.draft_name = ""
    st.session_state.draft_travel_style = "朋友"
    st.session_state.draft_budget_level = "中等"
    st.session_state.draft_answers = [3] * len(QUESTIONS)
    for idx in range(len(QUESTIONS)):
        key = f"q_{idx}"
        if key in st.session_state:
            del st.session_state[key]


@st.cache_resource
def get_gsheet():
    scope = [
        "https://www.googleapis.com/auth/spreadsheets",
        "https://www.googleapis.com/auth/drive",
    ]
    creds = Credentials.from_service_account_info(
        st.secrets["gcp_service_account"],
        scopes=scope,
    )
    client = gspread.authorize(creds)
    return client.open_by_url(SHEET_URL).sheet1


def ensure_sheet_headers(sheet) -> None:
    values = sheet.get_all_values()
    if not values:
        sheet.append_row(SHEET_HEADERS)
        return

    first_row = values[0]
    if len(first_row) < len(SHEET_HEADERS):
        sheet.clear()
        sheet.append_row(SHEET_HEADERS)
        if len(values) > 1:
            for row in values[1:]:
                normalized = row[:len(SHEET_HEADERS)] + [""] * max(0, len(SHEET_HEADERS) - len(row))
                sheet.append_row(normalized)


def get_current_answers() -> List[int]:
    answers = []
    for idx in range(len(QUESTIONS)):
        answers.append(int(st.session_state.get(f"q_{idx}", st.session_state.draft_answers[idx])))
    st.session_state.draft_answers = answers[:]
    return answers


def save_response_to_gsheet(sheet, name: str, travel_style: str, budget_level: str, answers: List[int]) -> None:
    row = [
        datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        name,
        travel_style,
        budget_level,
        *answers,
    ]
    sheet.append_row(row)


def load_members_from_gsheet(sheet) -> List[Dict]:
    records = sheet.get_all_records()
    members = []

    for idx, row in enumerate(records):
        try:
            answers = [int(row.get(f"q{i}", 3) or 3) for i in range(1, 26)]
            profile = average_dimension_scores(answers)
            persona = persona_label(profile)
            recs = recommend_destinations(profile, top_n=3)
            members.append({
                "row_id": idx + 2,
                "timestamp": str(row.get("timestamp", "")),
                "name": str(row.get("name", "")).strip() or f"未命名_{idx+1}",
                "travel_style": str(row.get("travel_style", "朋友")),
                "budget_level": str(row.get("budget_level", "中等")),
                "answers": answers,
                "profile": profile,
                "persona": persona,
                "recommendations": recs,
            })
        except Exception:
            continue

    members.sort(key=lambda x: x["timestamp"], reverse=True)
    return members


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
    bonus = 0.0
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

    scored_spots = [(spot, spot_match_score(profile, spot)) for spot in destination["spots"]]
    scored_spots.sort(key=lambda x: x[1], reverse=True)

    selected = []
    used_types = set()
    for spot, score in scored_spots:
        if spot["type"] not in used_types or len(selected) < 3:
            selected.append({**spot, "fit_score": score})
            used_types.add(spot["type"])
        if len(selected) >= 6:
            break

    if len(selected) < 6:
        for spot, score in scored_spots:
            if spot["name"] not in [x["name"] for x in selected]:
                selected.append({**spot, "fit_score": score})
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
        "分數": [profile[d] for d in DIMENSIONS],
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
        agg_scores.append((dest, round(final_score, 2)))

    agg_scores.sort(key=lambda x: x[1], reverse=True)
    return agg_scores[:top_n]


def to_download_rows(members: List[Dict]) -> pd.DataFrame:
    rows = []
    for m in members:
        row = {
            "填答時間": m["timestamp"],
            "姓名": m["name"],
            "旅伴型態": m["travel_style"],
            "預算感受": m["budget_level"],
            "人格類型": m["persona"],
        }
        for dim in DIMENSIONS:
            row[DIMENSION_LABELS[dim]] = m["profile"][dim]
        for idx, rec in enumerate(m["recommendations"], start=1):
            row[f"個人推薦{idx}"] = rec[0]["name"]
            row[f"個人推薦{idx}分數"] = rec[1]
        rows.append(row)
    return pd.DataFrame(rows)


def submit_current_response(sheet) -> None:
    name = st.session_state.draft_name.strip()
    if not name:
        st.warning("請先輸入姓名或暱稱。")
        return

    answers = get_current_answers()
    save_response_to_gsheet(
        sheet=sheet,
        name=name,
        travel_style=st.session_state.draft_travel_style,
        budget_level=st.session_state.draft_budget_level,
        answers=answers,
    )
    st.session_state.success_message = f"已成功送出 {name} 的填答資料！"
    st.session_state.reset_draft_pending = True
    st.cache_data.clear()
    st.rerun()


@st.cache_data(ttl=5)
def get_members_data() -> List[Dict]:
    sheet = get_gsheet()
    ensure_sheet_headers(sheet)
    return load_members_from_gsheet(sheet)


# =========================
# UI
# =========================

init_state()

if st.session_state.reset_draft_pending:
    reset_draft()
    st.session_state.reset_draft_pending = False

st.title("🧭 國內旅遊人格 AI 推薦平台")
st.caption("多人手機填答 → 自動寫入 Google Sheets → 個人推薦 → 動態兩天一夜行程 → 全體綜合推薦")

sheet = get_gsheet()
ensure_sheet_headers(sheet)
members = get_members_data()

if st.session_state.success_message:
    st.success(st.session_state.success_message)
    st.session_state.success_message = ""

with st.sidebar:
    st.header("平台說明")
    st.write(
        "這個版本已改成 Google Sheets 雲端儲存：\n"
        "1. 每位朋友都可用自己的手機填答\n"
        "2. 送出後會自動寫入同一份試算表\n"
        "3. 平台會直接從雲端資料計算個人與群體推薦\n"
        "4. 同一個網址即可收集所有人資料"
    )
    st.markdown("---")
    st.metric("目前雲端填答筆數", len(members))
    if st.button("重新讀取雲端資料", use_container_width=True):
        st.cache_data.clear()
        st.rerun()

    st.markdown("---")
    st.subheader("最近填答名單")
    if members:
        for member in members[:8]:
            st.write(f"- {member['name']}｜{member['persona']}")
    else:
        st.caption("目前尚無資料")


tab1, tab2, tab3 = st.tabs(["填寫問卷", "個人推薦結果", "群體綜合分析"])

with tab1:
    st.subheader("填寫旅遊問卷")
    st.info("先輸入姓名，再往下填所有問題；只有按下最下面的「送出問卷並分析」才會真的寫入 Google Sheets。")

    col_name, col_hint = st.columns([1.4, 1])
    with col_name:
        st.text_input("姓名 / 暱稱", key="draft_name", placeholder="例如：小美")
    with col_hint:
        st.write("")
        st.write("")
        st.caption("輸入名字後直接往下填，不會立刻送出")

    col1, col2 = st.columns(2)
    with col1:
        st.selectbox("偏好旅伴型態", ["朋友", "情侶", "家人", "不限"], key="draft_travel_style")
    with col2:
        st.selectbox("預算感受", ["偏精省", "中等", "願意多花一些"], key="draft_budget_level")

    st.markdown("### 請依 1～5 分回答")
    st.caption("1 = 非常不同意，5 = 非常同意")

    for idx, (_, question) in enumerate(QUESTIONS):
        default_value = st.session_state.draft_answers[idx]
        st.slider(
            f"{idx + 1}. {question}",
            min_value=1,
            max_value=5,
            value=default_value,
            key=f"q_{idx}",
            help="這一題目前的分數會先暫存，最後按送出才會寫入。",
        )

    action_col1, action_col2 = st.columns(2)
    with action_col1:
        if st.button("送出問卷並分析", type="primary", use_container_width=True):
            submit_current_response(sheet)
    with action_col2:
        if st.button("清空這份問卷", use_container_width=True):
            st.session_state.reset_draft_pending = True
            st.rerun()

with tab2:
    st.subheader("每位朋友的個人推薦結果")
    if not members:
        st.info("目前還沒有任何雲端填答資料，請先到「填寫問卷」送出至少 1 份問卷。")
    else:
        member_labels = [f"{m['name']}｜{m['timestamp']}" for m in members]
        selected_label = st.selectbox("選擇想查看的填答者", member_labels)
        member = members[member_labels.index(selected_label)]

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
    if not members:
        st.info("請先至少送出 1 份問卷。")
    else:
        st.markdown("### 全體綜合前三推薦")
        group_top = group_recommendation(members, top_n=3)
        for i, (dest, score) in enumerate(group_top, start=1):
            st.markdown(f"**Top {i}. {dest['name']}**｜綜合分數：`{score}`")
            st.write(f"適合原因：{', '.join(dest['tags'])}")

        st.markdown("---")
        st.markdown("### 全體平均人格分數")
        avg_profile = {
            dim: round(sum(m["profile"][dim] for m in members) / len(members), 2)
            for dim in DIMENSIONS
        }
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
            mime="text/csv",
        )
