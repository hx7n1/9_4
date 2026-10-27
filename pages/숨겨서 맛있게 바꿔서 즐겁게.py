import streamlit as st
import pandas as pd
from datetime import date
import sqlite3
import uuid
from io import StringIO

st.set_page_config(
    page_title="숨은 한입 | 잔반 감축 연구소",
    page_icon="🥟",
    layout="wide",
    initial_sidebar_state="expanded",
)

# 데모용 초기 데이터: 실제 측정값이 아니라 기능 확인용 예시입니다.
INITIAL_DATA = [
    {"날짜": "2026-10-26", "반찬": "당근볶음", "제공량(kg)": 8.0, "잔반량(kg)": 3.2, "조리법": "기본 제공", "메모": "식감 호불호"},
    {"날짜": "2026-10-26", "반찬": "버섯볶음", "제공량(kg)": 7.0, "잔반량(kg)": 2.1, "조리법": "기본 제공", "메모": "향에 대한 호불호"},
    {"날짜": "2026-10-26", "반찬": "시금치나물", "제공량(kg)": 6.0, "잔반량(kg)": 1.5, "조리법": "기본 제공", "메모": "질감 개선 필요"},
]

RECIPE_GUIDE = {
    "당근": {
        "제목": "🥟 당근 두부 만두소",
        "방법": [
            "당근을 깨끗이 씻어 잘게 다집니다.",
            "두부의 물기를 제거하고 으깬 뒤 당근과 섞습니다.",
            "기호에 따라 잘게 썬 양배추 등 다른 재료를 더하고 충분히 익힙니다.",
            "만두피에 넣어 속까지 완전히 익힙니다.",
        ],
        "팁": "당근의 단맛과 두부의 부드러운 식감을 활용합니다. 재료를 숨겨 알레르기 정보를 감추지 말고 메뉴에 표시하세요.",
    },
    "버섯": {
        "제목": "🥟 잘게 다진 버섯 만두",
        "방법": [
            "버섯을 깨끗이 손질하고 수분이 날아가도록 충분히 익힙니다.",
            "잘게 다진 버섯을 두부 또는 익힌 채소와 섞습니다.",
            "간은 싱겁게 조절하고 만두피에 소량씩 넣습니다.",
            "속까지 완전히 익힌 뒤 제공하고, 식감 선호도를 확인합니다.",
        ],
        "팁": "버섯 향이 강하게 느껴지는 경우 다른 재료와 균형을 맞춰 소량부터 시험해 보세요.",
    },
    "시금치": {
        "제목": "🥬 시금치 채소전",
        "방법": [
            "시금치를 깨끗이 씻고 데친 뒤 물기를 짭니다.",
            "시금치를 잘게 썰어 반죽에 고르게 섞습니다.",
            "작은 크기로 부쳐 먹기 편하게 제공합니다.",
            "중심부까지 충분히 익었는지 확인합니다.",
        ],
        "팁": "한입 크기로 제공하면 낯선 식재료를 조금씩 맛볼 수 있습니다.",
    },
    "브로콜리": {
        "제목": "🍙 브로콜리 한입 주먹밥",
        "방법": [
            "브로콜리를 충분히 익힌 뒤 잘게 다집니다.",
            "밥과 다진 브로콜리를 고르게 섞습니다.",
            "소금은 적게 사용하고 작은 주먹밥으로 빚습니다.",
            "재료와 알레르기 정보를 표시해 제공합니다.",
        ],
        "팁": "채소가 밥에 고르게 섞여 한입씩 먹기 쉽습니다.",
    },
    "콩": {
        "제목": "🥟 부드러운 콩 채소 만두소",
        "방법": [
            "콩은 식품 종류에 맞게 충분히 익혀 준비합니다.",
            "익힌 콩을 으깨고 잘게 다진 채소와 섞습니다.",
            "수분을 조절해 만두소를 만들고 만두피에 넣습니다.",
            "속까지 완전히 익혀 제공하며 재료를 메뉴에 표시합니다.",
        ],
        "팁": "콩의 종류와 조리법에 맞는 안전한 가열 방법을 따르세요.",
    },
}

EXTRA_RECIPES = {
    "가지": {"제목":"🍆 가지 두부 만두", "방법":["가지를 씻어 작게 깍둑썰기 합니다.","팬에서 수분을 날리며 충분히 익힙니다.","으깬 두부, 다진 파와 섞고 간을 약하게 합니다.","만두피에 넣어 속까지 완전히 익힙니다."], "팁":"가지는 충분히 익혀 부드럽게 만들면 식감 부담을 줄일 수 있어요."},
    "양파": {"제목":"🧅 달큰한 양파 만두소", "방법":["양파를 잘게 다집니다.","투명해지고 단맛이 올라올 때까지 볶아 식힙니다.","으깬 두부나 익힌 감자와 섞어 수분을 조절합니다.","만두피에 넣어 속까지 완전히 익힙니다."], "팁":"양파는 볶으면 매운 향이 줄고 단맛이 살아납니다."},
    "파프리카": {"제목":"🫑 파프리카 한입 만두", "방법":["파프리카의 씨를 제거하고 잘게 다집니다.","팬에서 살짝 볶아 수분을 줄입니다.","두부와 섞어 만두소를 만듭니다.","만두피에 넣고 속까지 완전히 익힙니다."], "팁":"색이 다양한 파프리카는 잘게 썰어 여러 재료와 섞어 보세요."},
    "양배추": {"제목":"🥬 양배추 포근 만두", "방법":["양배추를 깨끗이 씻어 잘게 다집니다.","살짝 데친 뒤 물기를 꼭 짭니다.","으깬 두부나 익힌 당면과 섞습니다.","만두피에 넣어 충분히 익힙니다."], "팁":"수분을 충분히 제거해야 만두가 쉽게 터지지 않아요."},
    "애호박": {"제목":"🥒 애호박 두부 만두", "방법":["애호박을 잘게 다집니다.","팬에 볶아 수분을 줄이고 식힙니다.","두부와 섞고 필요하면 빵가루를 소량 넣어 농도를 맞춥니다.","만두피에 넣어 속까지 완전히 익힙니다."], "팁":"애호박은 수분이 많아 먼저 볶는 것이 좋아요."},
    "김치": {"제목":"🌶️ 순한 김치 만두", "방법":["김치를 잘게 다지고 필요하면 물에 가볍게 헹굽니다.","김치의 물기를 꼭 짜고 볶습니다.","두부와 섞어 맵기와 간을 조절합니다.","만두피에 넣어 속까지 완전히 익힙니다."], "팁":"맵기와 염도를 확인하고 먹는 사람에게 재료를 안내하세요."},
    "감자": {"제목":"🥔 포슬포슬 감자 채소 만두", "방법":["감자를 완전히 익혀 부드럽게 으깹니다.","잘게 다진 익힌 채소를 섞습니다.","수분을 조절해 만두소를 만듭니다.","만두피에 넣어 속까지 충분히 익힙니다."], "팁":"감자가 재료를 부드럽게 묶어줘 만두소로 쓰기 좋아요."},
    "오이": {"제목":"🥒 오이 달걀 채소전", "방법":["오이를 잘게 다지고 물기를 짭니다.","달걀과 부침가루를 섞어 반죽을 만듭니다.","작은 크기로 노릇하게 부칩니다.","중심부까지 완전히 익혀 제공합니다."], "팁":"달걀 알레르기 여부를 확인하고 재료를 표시하세요."},
    "무": {"제목":"🤍 무채 두부전", "방법":["무를 곱게 채 썰거나 다집니다.","살짝 익힌 뒤 물기를 제거합니다.","두부와 부침가루를 섞어 작은 전으로 만듭니다.","양면을 노릇하게 굽고 속까지 익힙니다."], "팁":"무의 수분을 잘 빼면 전이 쉽게 부서지지 않아요."},
    "콩나물": {"제목":"🌱 콩나물 한입 만두", "방법":["콩나물을 깨끗이 씻어 충분히 익힙니다.","물기를 제거하고 잘게 다집니다.","두부와 섞어 만두소를 만듭니다.","만두피에 넣어 속까지 완전히 익힙니다."], "팁":"콩나물은 충분히 익힌 뒤 사용하세요."},
}

DEFAULT_RECIPE = {
    "제목": "🍳 잘게 다진 채소전",
    "방법": [
        "재료를 깨끗이 씻고 먹기 편한 크기로 잘게 다집니다.",
        "수분이 많은 재료는 적절히 제거하고 다른 재료와 섞습니다.",
        "작은 크기로 조리해 먹기 편하게 제공합니다.",
        "재료 특성에 맞게 속까지 충분히 익힙니다.",
    ],
    "팁": "반찬 이름을 숨기기보다 새 조리법과 재료를 함께 안내하고, 소량 시식으로 선호도를 확인하세요.",
}


# 투표 데이터는 SQLite에 저장해 서로 다른 브라우저 세션에서도 집계합니다.
# Streamlit Community Cloud의 로컬 파일은 재배포/재시작 시 초기화될 수 있습니다.
DB_PATH = "hidden_bite_votes.db"

def get_db_connection():
    """SQLite 연결을 열고 필요한 테이블을 준비합니다."""
    conn = sqlite3.connect(DB_PATH, timeout=10, check_same_thread=False)
    conn.execute("PRAGMA journal_mode=WAL")
    conn.execute("""
        CREATE TABLE IF NOT EXISTS foods (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL UNIQUE,
            created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
        )
    """)
    conn.execute("""
        CREATE TABLE IF NOT EXISTS votes (
            voter_id TEXT PRIMARY KEY,
            food_id INTEGER NOT NULL,
            created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY(food_id) REFERENCES foods(id)
        )
    """)
    conn.commit()
    return conn

def get_vote_data():
    """등록 음식별 득표수를 반환합니다."""
    conn = get_db_connection()
    try:
        rows = conn.execute("""
            SELECT foods.id, foods.name, COUNT(votes.voter_id) AS votes
            FROM foods
            LEFT JOIN votes ON foods.id = votes.food_id
            GROUP BY foods.id, foods.name
            ORDER BY votes DESC, foods.name COLLATE NOCASE ASC
        """).fetchall()
        return pd.DataFrame(rows, columns=["id", "음식", "득표수"])
    finally:
        conn.close()

def add_food_to_vote(name):
    """중복 음식 등록을 방지합니다."""
    clean_name = " ".join(str(name).strip().split())
    if not clean_name:
        return False, "음식 이름을 입력해 주세요."
    if len(clean_name) > 40:
        return False, "음식 이름은 40자 이내로 입력해 주세요."
    conn = get_db_connection()
    try:
        conn.execute("INSERT INTO foods(name) VALUES (?)", (clean_name,))
        conn.commit()
        return True, f"'{clean_name}'을(를) 투표 목록에 추가했습니다."
    except sqlite3.IntegrityError:
        return False, "이미 등록된 음식입니다."
    finally:
        conn.close()

def cast_vote(voter_id, food_id):
    """세션당 한 번만 투표하도록 저장합니다."""
    conn = get_db_connection()
    try:
        existing = conn.execute(
            "SELECT food_id FROM votes WHERE voter_id = ?", (voter_id,)
        ).fetchone()
        if existing:
            return False, "이미 투표했습니다. 한 세션에서는 한 번만 투표할 수 있어요."
        valid_food = conn.execute(
            "SELECT id FROM foods WHERE id = ?", (int(food_id),)
        ).fetchone()
        if not valid_food:
            return False, "선택한 음식이 목록에 없습니다. 새로고침 후 다시 시도해 주세요."
        conn.execute(
            "INSERT INTO votes(voter_id, food_id) VALUES (?, ?)",
            (voter_id, int(food_id)),
        )
        conn.commit()
        return True, "투표가 반영되었습니다!"
    except sqlite3.IntegrityError:
        return False, "이미 투표했거나 저장 중 문제가 발생했습니다."
    finally:
        conn.close()

def recipe_for_food_name(name):
    """음식 이름을 바탕으로 기존 레시피 안내를 연결합니다."""
    lowered = str(name).lower()
    for keyword, recipe in RECIPE_GUIDE.items():
        if keyword in lowered:
            return recipe
    return {
        "제목": f"🥟 {name} 만두소 아이디어",
        "방법": [
            f"{name}을(를) 깨끗하게 손질하고 만두소에 넣기 좋게 잘게 다집니다.",
            "재료 특성에 맞게 먼저 익히고, 수분이 많으면 적절히 제거합니다.",
            "두부나 잘게 다진 다른 채소와 섞어 만두소를 만듭니다.",
            "만두피에 넣어 속까지 완전히 익힌 뒤 제공합니다.",
        ],
        "팁": "재료와 알레르기 정보를 메뉴에 정확히 표시하고, 실제 조리 전 식품 안전성과 맛을 확인하세요.",
    }


def init_state():
    if "records" not in st.session_state:
        st.session_state.records = pd.DataFrame(INITIAL_DATA)
    if "experiments" not in st.session_state:
        st.session_state.experiments = []
    if "custom_recipes" not in st.session_state:
        st.session_state.custom_recipes = {}
    if "voter_id" not in st.session_state:
        st.session_state.voter_id = str(uuid.uuid4())

def safe_numeric(series):
    return pd.to_numeric(series, errors="coerce").fillna(0)

def prepare_records(df):
    expected = ["날짜", "반찬", "제공량(kg)", "잔반량(kg)", "조리법", "메모"]
    for col in expected:
        if col not in df.columns:
            df[col] = "" if col in ["날짜", "반찬", "조리법", "메모"] else 0
    df = df[expected].copy()
    df["제공량(kg)"] = safe_numeric(df["제공량(kg)"]).clip(lower=0)
    df["잔반량(kg)"] = safe_numeric(df["잔반량(kg)"]).clip(lower=0)
    df["반찬"] = df["반찬"].fillna("").astype(str)
    df["조리법"] = df["조리법"].fillna("").astype(str)
    df["메모"] = df["메모"].fillna("").astype(str)
    df["날짜"] = df["날짜"].fillna("").astype(str)
    # 잔반량이 제공량을 넘는 데이터는 입력 오류로 취급해 분석에서 안전하게 제한합니다.
    df["잔반량(kg)"] = df[["잔반량(kg)", "제공량(kg)"]].min(axis=1)
    return df

def waste_rate(row):
    served = float(row["제공량(kg)"])
    return (float(row["잔반량(kg)"]) / served * 100) if served > 0 else 0.0

def recipe_for(name):
    lowered = str(name).lower()
    for key, recipe in RECIPE_GUIDE.items():
        if key in lowered:
            return recipe
    return DEFAULT_RECIPE

init_state()
st.session_state.records = prepare_records(st.session_state.records)

st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=DM+Sans:wght@400;500;600;700&family=Noto+Sans+KR:wght@400;500;600;700;800&display=swap');
:root { --ink:#18372d; --muted:#68776e; --green:#2f6b4f; --mint:#e9f3e9; --cream:#faf8f2; --line:#e4e9df; }
html, body, [class*="css"] { font-family:'DM Sans','Noto Sans KR',sans-serif; }
.stApp { background:var(--cream); color:var(--ink); }
[data-testid="stHeader"] { background:rgba(250,248,242,.88); }
.block-container { max-width:1180px; padding-top:2rem; padding-bottom:3rem; }
[data-testid="stSidebar"] { background:#173c30; border-right:0; }
[data-testid="stSidebar"] * { color:#f5f8f2 !important; }
[data-testid="stSidebar"] [data-testid="stRadio"] label { padding:.55rem .65rem; border-radius:10px; }
[data-testid="stSidebar"] [data-testid="stRadio"] label:hover { background:#285341; }
[data-testid="stSidebar"] hr { border-color:#3d6653; }
.hero { padding:2.1rem 2.2rem; border-radius:24px; background:linear-gradient(115deg,#e0efdf 0%,#f5f0df 65%,#f7e6d7 100%); border:1px solid #dbe7d8; margin-bottom:1.5rem; box-shadow:0 12px 35px rgba(28,67,48,.06); }
.hero h1 { margin:0; color:#173c30; font-size:2.5rem; letter-spacing:-.06em; font-weight:800; }
.hero p { margin:.65rem 0 0; color:#52685a; font-size:1.02rem; }
h1,h2,h3 { color:#18372d; letter-spacing:-.035em; }
h2 { margin-top:.4rem; }
[data-testid="stMetric"] { background:white; border:1px solid var(--line); border-radius:18px; padding:1rem 1.1rem; box-shadow:0 4px 16px rgba(24,55,45,.035); }
[data-testid="stMetricLabel"] { color:#68776e; }
[data-testid="stMetricValue"] { color:#214e39; font-weight:800; }
.stButton > button, .stFormSubmitButton > button { border-radius:12px; border:1px solid #2f6b4f; font-weight:700; min-height:2.7rem; transition:all .15s ease; }
.stButton > button[kind="primary"], .stFormSubmitButton > button[kind="primary"] { background:#2f6b4f; color:white; }
.stButton > button:hover, .stFormSubmitButton > button:hover { transform:translateY(-1px); border-color:#214e39; }
[data-testid="stForm"], [data-testid="stExpander"] { border-radius:16px; border-color:var(--line); background:rgba(255,255,255,.72); }
[data-testid="stDataFrame"] { border:1px solid var(--line); border-radius:14px; overflow:hidden; }
[data-testid="stAlert"] { border-radius:14px; }
.stTextInput input, .stNumberInput input, .stTextArea textarea, [data-baseweb="select"] > div { border-radius:10px !important; }
.note { color:var(--muted); font-size:.9rem; }
.eyebrow { color:#2f6b4f; font-size:.78rem; font-weight:800; letter-spacing:.12em; text-transform:uppercase; }
.recipe-card { background:white; border:1px solid var(--line); border-radius:20px; padding:1.35rem 1.5rem; margin:.7rem 0 1rem; }
div[data-testid="stRadio"] > label { font-weight:600; }
@media (max-width: 700px) { .block-container {padding:1rem 1rem 2rem;} .hero {padding:1.4rem;} .hero h1 {font-size:2rem;} }
</style>
""", unsafe_allow_html=True)

with st.sidebar:
    st.markdown("<div style='font-size:2.1rem'>🥟</div><div style='font-size:1.35rem;font-weight:800;letter-spacing:-.04em'>숨은 한입</div><div style='color:#bdd4c3;font-size:.82rem;margin:.25rem 0 1rem'>WASTE LESS, TASTE MORE</div>", unsafe_allow_html=True)
    st.divider()
    page = st.radio("둘러보기", ["🗳️ 반찬 투표소", "🥟 숨은 한입 레시피", "🌱 환경 효과 계산기", "📝 실험 기록장", "📁 데이터 관리"], label_visibility="collapsed")
    st.divider()
    st.caption("작은 한입의 변화가 잔반을 줄여요.")

st.markdown("""
<div class="hero">
  <div class="eyebrow">A LITTLE BITE, A BIG CHANGE</div>
  <h1>숨은 한입 <span style="font-size:1.8rem">🥟</span></h1>
  <p>싫어하던 반찬도 새로운 한입으로. 함께 고르고, 맛있게 바꾸고, 잔반을 줄여요.</p>
</div>
""", unsafe_allow_html=True)

df = prepare_records(st.session_state.records)
if df.empty:
    total_served, total_waste, overall_rate = 0.0, 0.0, 0.0
else:
    total_served = float(df["제공량(kg)"].sum())
    total_waste = float(df["잔반량(kg)"].sum())
    overall_rate = (total_waste / total_served * 100) if total_served > 0 else 0.0

if page == "🗳️ 반찬 투표소":
    st.subheader("학생들이 직접 고르는 만두 속 재료")
    st.write(
        "먹기 부담스럽거나 호불호가 갈리는 반찬을 등록하고, "
        "만두소로 만들어 보고 싶은 음식에 투표해 보세요."
    )
    st.info(
        "투표는 이 앱 인스턴스의 SQLite 데이터베이스에 저장되어 "
        "서로 다른 브라우저 세션의 표도 합산됩니다. "
        "단, Community Cloud의 재시작·재배포 시 로컬 파일이 초기화될 수 있습니다."
    )

    with st.form("add_food_vote_form", clear_on_submit=True):
        new_food = st.text_input(
            "호불호가 갈리는 음식 등록",
            placeholder="예: 가지볶음, 버섯볶음, 당근볶음",
            max_chars=40,
        )
        add_food = st.form_submit_button("투표 목록에 음식 추가", type="primary")
        if add_food:
            try:
                ok, message = add_food_to_vote(new_food)
                if ok:
                    st.success(message)
                else:
                    st.warning(message)
            except sqlite3.Error:
                st.error("음식을 저장하지 못했습니다. 잠시 후 다시 시도해 주세요.")

    st.divider()

    try:
        vote_df = get_vote_data()
    except sqlite3.Error:
        vote_df = pd.DataFrame(columns=["id", "음식", "득표수"])
        st.error("투표 데이터를 불러오지 못했습니다. 페이지를 새로고침해 주세요.")

    if vote_df.empty:
        st.info("아직 등록된 음식이 없습니다. 위에서 첫 음식을 등록해 주세요.")
    else:
        total_votes = int(vote_df["득표수"].sum())
        st.metric("등록된 음식", f"{len(vote_df)}개")
        st.metric("전체 투표 수", f"{total_votes}표")

        st.markdown("### 🗳️ 만두 속에 넣고 싶은 음식에 투표")
        if "has_voted" not in st.session_state:
            st.session_state.has_voted = False

        food_options = {
            f"{row['음식']}  ·  {int(row['득표수'])}표": int(row["id"])
            for _, row in vote_df.iterrows()
        }

        with st.form("cast_vote_form"):
            selected_label = st.radio(
                "음식 하나를 선택해 주세요",
                options=list(food_options.keys()),
                index=0,
            )
            cast = st.form_submit_button("이 음식에 투표하기", type="primary")

            if cast:
                try:
                    ok, message = cast_vote(
                        st.session_state.voter_id,
                        food_options[selected_label],
                    )
                    if ok:
                        st.session_state.has_voted = True
                        st.success(message)
                        st.rerun()
                    else:
                        st.warning(message)
                except sqlite3.Error:
                    st.error("투표를 저장하지 못했습니다. 잠시 후 다시 시도해 주세요.")

        st.caption("중복 투표 방지를 위해 같은 브라우저 세션에서는 한 번만 투표할 수 있습니다.")

        # 득표 현황과 공동 1위 처리
        vote_df = get_vote_data()
        total_votes = int(vote_df["득표수"].sum())
        st.markdown("### 📊 현재 투표 결과")
        result_df = vote_df.copy()
        result_df["득표율(%)"] = (
            result_df["득표수"] / total_votes * 100
        ).round(1) if total_votes > 0 else 0.0

        st.bar_chart(result_df.set_index("음식")[["득표수"]])
        st.dataframe(
            result_df[["음식", "득표수", "득표율(%)"]],
            use_container_width=True,
            hide_index=True,
        )

        if total_votes == 0:
            st.info("아직 투표가 없습니다. 첫 투표를 해 주세요.")
        else:
            max_votes = int(vote_df["득표수"].max())
            winners = vote_df[vote_df["득표수"] == max_votes]
            if len(winners) == 1:
                winner = str(winners.iloc[0]["음식"])
                st.success(
                    f"🏆 현재 1위는 **{winner}**입니다! "
                    "이 음식을 만두소 재료로 실험해 보세요."
                )
                recipe = recipe_for_food_name(winner)
                st.markdown(f"### {recipe['제목']}")
                for i, step in enumerate(recipe["방법"], start=1):
                    st.write(f"**{i}.** {step}")
                st.info(recipe["팁"])
            else:
                tied_names = ", ".join(winners["음식"].astype(str).tolist())
                st.warning(
                    f"현재 공동 1위: **{tied_names}**. "
                    "동점이므로 공동 후보로 표시합니다."
                )
                chosen_winner = st.selectbox(
                    "공동 1위 중 먼저 시험할 음식 선택",
                    winners["음식"].astype(str).tolist(),
                )
                recipe = recipe_for_food_name(chosen_winner)
                st.markdown(f"### {recipe['제목']}")
                for i, step in enumerate(recipe["방법"], start=1):
                    st.write(f"**{i}.** {step}")
                st.info(recipe["팁"])

    st.warning(
        "투표는 선호도를 파악하기 위한 참고 자료입니다. "
        "재료를 숨겨 알레르기나 원재료 정보를 감추지 말고, "
        "조리 후 메뉴명과 재료를 명확히 안내하세요."
    )

elif page == "🥟 숨은 한입 레시피":
    st.markdown("<div class='eyebrow'>RECIPE STUDIO</div>", unsafe_allow_html=True)
    st.subheader("싫어하던 반찬을 새로운 한입으로")
    st.write("만두, 전, 주먹밥으로 바꿔 볼 수 있어요. 우리만의 레시피도 직접 등록해 보세요.")
    all_recipes = {**EXTRA_RECIPES, **RECIPE_GUIDE, **st.session_state.custom_recipes}
    names = list(all_recipes.keys())
    left, right = st.columns([1.05, 1.4], gap="large")
    with left:
        st.markdown("#### 🥬 레시피 둘러보기")
        food = st.selectbox("재료 선택", names, format_func=lambda x: f"{x}  ·  {all_recipes[x]['제목']}")
        recipe = all_recipes[food]
        st.markdown(f"<div class='recipe-card'><div class='eyebrow'>TODAY'S PICK</div><h2 style='margin:.45rem 0'>{recipe['제목']}</h2><p style='color:#68776e;margin:0'>재료의 식감은 부드럽게, 한입의 즐거움은 크게.</p></div>", unsafe_allow_html=True)
        st.info(recipe.get("팁", "재료와 알레르기 정보를 정확하게 표시하세요."))
    with right:
        st.markdown("#### 👩‍🍳 조리 순서")
        for i, step in enumerate(recipe["방법"], start=1):
            st.markdown(f"**{i:02d}**　{step}")
            if i < len(recipe["방법"]): st.markdown("<div style='border-bottom:1px solid #e4e9df;margin:.7rem 0'></div>", unsafe_allow_html=True)
        st.caption("※ 식재료는 충분히 익히고, 메뉴명·원재료·알레르기 정보를 반드시 안내하세요.")

    st.divider()
    st.markdown("### ✨ 나만의 레시피 추가하기")
    st.caption("음식 이름과 조리 순서를 입력하면 이 앱의 레시피 목록에 추가됩니다. 추가한 레시피는 현재 세션에서 유지됩니다.")
    with st.form("custom_recipe_form", clear_on_submit=True):
        c1, c2 = st.columns([1, 1])
        with c1:
            custom_name = st.text_input("재료 또는 반찬 이름", placeholder="예: 미역줄기")
            custom_title = st.text_input("레시피 이름", placeholder="예: 미역줄기 두부 만두")
            custom_tip = st.text_input("나만의 팁", placeholder="예: 물기를 충분히 제거해요")
        with c2:
            step1 = st.text_input("조리 순서 1", placeholder="재료를 깨끗이 씻고 잘게 다져요")
            step2 = st.text_input("조리 순서 2", placeholder="팬에서 충분히 익혀요")
            step3 = st.text_input("조리 순서 3", placeholder="두부와 섞어 만두소를 만들어요")
            step4 = st.text_input("조리 순서 4", placeholder="만두피에 넣어 속까지 익혀요")
        save_recipe = st.form_submit_button("＋ 레시피 등록하기", type="primary", use_container_width=True)
        if save_recipe:
            clean_name = custom_name.strip()
            steps = [x.strip() for x in [step1, step2, step3, step4] if x.strip()]
            if not clean_name or not custom_title.strip():
                st.error("재료 이름과 레시피 이름을 입력해 주세요.")
            elif len(steps) < 2:
                st.error("조리 순서를 두 단계 이상 입력해 주세요.")
            else:
                st.session_state.custom_recipes[clean_name] = {"제목": custom_title.strip(), "방법": steps, "팁": custom_tip.strip() or "재료와 알레르기 정보를 안내하고, 속까지 충분히 익혀 주세요."}
                st.success(f"'{clean_name}' 레시피를 등록했어요! 위 레시피 목록에서 확인할 수 있습니다.")
                st.rerun()

    with st.expander("🍴 조리 실험 체크리스트"):
        st.write("- 처음에는 소량으로 시식 테스트를 진행해요.")
        st.write("- 조리 전후 잔반량을 같은 단위(kg)로 측정해요.")
        st.write("- 재료를 잘게 다져도 메뉴명, 원재료, 알레르기 유발 식품을 숨기지 않아요.")
        st.write("- 먹기 싫다는 선택도 존중해요.")

elif page == "🌱 환경 효과 계산기":
    st.subheader("잔반 감축 목표를 숫자로 바꿔봐요")
    st.caption("환경 효과와 비용은 입력값에 따라 달라지는 추정치입니다. 공식 배출량 산정이나 실제 청구액을 대신하지 않습니다.")
    a, b = st.columns(2)
    with a:
        current = st.number_input("현재 하루 잔반량 (kg)", min_value=0.0, value=float(round(total_waste, 1)), step=0.5)
        target_percent = st.slider("잔반 감축 목표 (%)", min_value=0, max_value=80, value=20, step=5)
        days = st.number_input("운영 일수 (일)", min_value=1, max_value=366, value=200, step=10)
    with b:
        cost_per_kg = st.number_input("처리 비용 (원/kg)", min_value=0, value=150, step=10)
        co2_per_kg = st.number_input("가정한 배출계수 (kg CO₂e/kg 잔반)", min_value=0.0, value=0.5, step=0.1, format="%.2f")
        st.caption("배출계수 0.5는 계산 예시일 뿐, 실제 현장의 검증된 계수가 아닙니다.")
    reduced_daily = current * target_percent / 100
    reduced_total = reduced_daily * days
    saved_cost = reduced_total * cost_per_kg
    avoided_co2 = reduced_total * co2_per_kg
    st.divider()
    c1, c2, c3 = st.columns(3)
    c1.metric("하루 감축 목표", f"{reduced_daily:.2f} kg")
    c2.metric("기간 내 감축 목표", f"{reduced_total:.1f} kg")
    c3.metric("예상 처리비 절감", f"{saved_cost:,.0f} 원")
    st.metric("가정한 배출계수 기준 예상 배출 감소", f"{avoided_co2:,.1f} kg CO₂e")
    st.caption("실제 결과는 잔반 처리 방식, 지역별 계약, 음식물 구성 및 배출계수에 따라 달라집니다.")

elif page == "📝 실험 기록장":
    st.subheader("조리법을 바꾸고 결과를 기록해요")
    st.write("기록은 이 앱이 열려 있는 세션 동안 유지됩니다. 장기 보관하려면 CSV로 내려받으세요.")
    with st.form("experiment_form", clear_on_submit=True):
        exp_date = st.date_input("실험 날짜", value=date.today())
        exp_food = st.text_input("반찬 이름", placeholder="예: 당근볶음")
        exp_method = st.selectbox("시도한 조리법", ["잘게 다지기", "만두소로 활용", "전으로 만들기", "볶음밥에 섞기", "기타"])
        exp_before = st.number_input("변경 전 잔반량 (kg)", min_value=0.0, value=0.0, step=0.1)
        exp_after = st.number_input("변경 후 잔반량 (kg)", min_value=0.0, value=0.0, step=0.1)
        exp_note = st.text_area("관찰 메모", placeholder="식감 반응, 시식 의견, 제공량 변화 등")
        submitted = st.form_submit_button("실험 기록 저장", type="primary")
        if submitted:
            if not exp_food.strip():
                st.error("반찬 이름을 입력해 주세요.")
            elif exp_after > exp_before and exp_before == 0:
                st.warning("변경 전 잔반량이 0kg입니다. 입력값을 확인해 주세요.")
            else:
                improvement = ((exp_before - exp_after) / exp_before * 100) if exp_before > 0 else None
                st.session_state.experiments.append({
                    "날짜": exp_date.isoformat(),
                    "반찬": exp_food.strip(),
                    "조리법": exp_method,
                    "변경 전 잔반량(kg)": round(exp_before, 3),
                    "변경 후 잔반량(kg)": round(exp_after, 3),
                    "잔반 변화율(%)": round(improvement, 1) if improvement is not None else None,
                    "메모": exp_note.strip(),
                })
                st.success("실험 기록을 저장했습니다.")
    if st.session_state.experiments:
        exp_df = pd.DataFrame(st.session_state.experiments)
        st.dataframe(exp_df, use_container_width=True, hide_index=True)
        st.download_button(
            "실험 기록 CSV 다운로드",
            data=exp_df.to_csv(index=False).encode("utf-8-sig"),
            file_name="hidden_bite_experiments.csv",
            mime="text/csv",
        )
        if st.button("실험 기록 모두 지우기"):
            st.session_state.experiments = []
            st.rerun()
    else:
        st.info("아직 실험 기록이 없습니다. 첫 조리 실험을 기록해 보세요.")

elif page == "📁 데이터 관리":
    st.subheader("잔반 기록 추가 또는 CSV 관리")
    with st.form("record_form", clear_on_submit=True):
        r_date = st.date_input("측정 날짜", value=date.today())
        r_food = st.text_input("반찬 이름", placeholder="예: 당근볶음")
        r_served = st.number_input("제공량 (kg)", min_value=0.0, value=1.0, step=0.1)
        r_waste = st.number_input("잔반량 (kg)", min_value=0.0, value=0.2, step=0.1)
        r_method = st.selectbox("조리법", ["기본 제공", "잘게 다지기", "만두소로 활용", "전으로 만들기", "볶음밥에 섞기", "기타"])
        r_note = st.text_input("메모 (선택)")
        add_record = st.form_submit_button("기록 추가", type="primary")
        if add_record:
            if not r_food.strip():
                st.error("반찬 이름을 입력해 주세요.")
            elif r_waste > r_served:
                st.error("잔반량은 제공량보다 클 수 없습니다.")
            else:
                new_row = {
                    "날짜": r_date.isoformat(),
                    "반찬": r_food.strip(),
                    "제공량(kg)": float(r_served),
                    "잔반량(kg)": float(r_waste),
                    "조리법": r_method,
                    "메모": r_note.strip(),
                }
                st.session_state.records = pd.concat(
                    [st.session_state.records, pd.DataFrame([new_row])], ignore_index=True
                )
                st.success("잔반 기록을 추가했습니다.")
                st.rerun()

    st.markdown("#### 현재 잔반 데이터")
    current_df = prepare_records(st.session_state.records)
    st.dataframe(current_df, use_container_width=True, hide_index=True)
    st.download_button(
        "현재 데이터 CSV 다운로드",
        data=current_df.to_csv(index=False).encode("utf-8-sig"),
        file_name="hidden_bite_records.csv",
        mime="text/csv",
    )
    uploaded = st.file_uploader("CSV 파일로 데이터 불러오기", type=["csv"])
    if uploaded is not None:
        try:
            imported = pd.read_csv(uploaded)
            required = {"날짜", "반찬", "제공량(kg)", "잔반량(kg)"}
            if not required.issubset(set(imported.columns)):
                st.error("CSV에 날짜, 반찬, 제공량(kg), 잔반량(kg) 열이 필요합니다.")
            else:
                imported = prepare_records(imported)
                if (imported["잔반량(kg)"] > imported["제공량(kg)"]).any():
                    st.error("잔반량은 제공량보다 클 수 없습니다.")
                else:
                    st.dataframe(imported.head(10), use_container_width=True, hide_index=True)
                    if st.button("불러온 CSV로 현재 데이터 교체"):
                        st.session_state.records = imported
                        st.success("CSV 데이터를 불러왔습니다.")
                        st.rerun()
        except Exception as exc:
            st.error(f"CSV를 읽지 못했습니다. UTF-8 CSV 파일인지 확인해 주세요. ({exc})")

    with st.expander("초기 예시 데이터로 되돌리기"):
        st.warning("현재 세션에서 추가하거나 불러온 잔반 데이터가 초기화됩니다.")
        if st.button("예시 데이터 복원"):
            st.session_state.records = pd.DataFrame(INITIAL_DATA)
            st.success("예시 데이터로 복원했습니다.")
            st.rerun()

st.divider()
st.caption("숨은 한입 · 함께 고르고 맛있게 바꾸는 잔반 감축 프로젝트 | 실제 운영 시 데이터 저장소와 학교 식품안전 지침을 별도로 검토하세요.")
