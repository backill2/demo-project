import os
import re
import json
import html
import math
import random
import time
import urllib.request

import streamlit as st
import streamlit.components.v1 as components

st.set_page_config(page_title="AI 메이드 코디", page_icon="🎀",
                   initial_sidebar_state="collapsed")

# ============================================================
# 1) 코디 데이터
# ============================================================
STYLES = {
    "캐주얼": {"words": ["캐주얼", "편한", "무난", "데일리"],
            "액세서리": ["볼캡", "실버 목걸이", "미니 크로스백"],
            "상의": ["오버핏 맨투맨", "그래픽 티셔츠", "후드 집업"],
            "하의": ["워싱 청바지", "조거 팬츠", "와이드 코튼 팬츠"],
            "신발": ["흰 스니커즈", "캔버스화"]},
    "고딕로리타": {"words": ["고딕", "로리타", "고스", "다크", "블랙"],
              "액세서리": ["레이스 초커", "리본 헤어핀", "미니 햇"],
              "상의": ["프릴 블라우스", "블랙 레이스 셔츠"],
              "하의": ["코르셋 스커트", "블랙 플리츠 스커트"],
              "신발": ["플랫폼 메리제인", "통굽 부츠"]},
    "러블리": {"words": ["러블리", "귀여", "걸리시", "달달", "핑크"],
            "액세서리": ["리본 머리핀", "하트 목걸이", "진주 헤어핀"],
            "상의": ["파스텔 니트 가디건", "퍼프 소매 블라우스"],
            "하의": ["플리츠 스커트", "A라인 미니스커트"],
            "신발": ["리본 스니커즈", "메리제인 슈즈"]},
    "스트릿": {"words": ["스트릿", "힙합", "힙한", "오버사이즈"],
            "액세서리": ["버킷햇", "체인 목걸이", "비니"],
            "상의": ["박시 후드티", "빅 로고 티셔츠", "바시티 자켓"],
            "하의": ["와이드 데님", "카고 팬츠"],
            "신발": ["청키 스니커즈", "하이탑 스니커즈"]},
    "단정": {"words": ["단정", "깔끔", "시티보이", "미니멀", "정장", "포멀"],
           "액세서리": ["심플 시계", "얇은 벨트", "깔끔한 에코백"],
           "상의": ["옥스포드 셔츠", "니트 베스트", "무지 라운드 니트"],
           "하의": ["슬랙스", "면바지", "미디 스커트"],
           "신발": ["로퍼", "깔끔한 흰 스니커즈"]},
    "고프코어": {"words": ["고프코어", "아웃도어", "등산", "테크웨어", "기능성"],
              "액세서리": ["클립 버클 벨트", "방수 크로스백", "바라클라바"],
              "상의": ["윈드브레이커", "플리스 집업"],
              "하의": ["나일론 카고 팬츠", "트랙 팬츠"],
              "신발": ["트레일 러닝화", "투박한 하이킹화"]},
}

MOODS = [
    (["우울", "슬", "힘들", "지침", "피곤", "졸", "무기력"], "포근하고 편안한 레이어드",
     "주인님… 오늘은 지치셨죠? 루나가 포근하게 감싸드릴 코디로 골랐어요."),
    (["신나", "설레", "기뻐", "행복", "좋아", "들뜬", "텐션"], "텐션 업! 컬러 포인트 코디",
     "와아~ 주인님 오늘 기분 최고예요! 그 반짝임을 옷에도 담아볼게요!"),
    (["화", "짜증", "빡", "예민"], "블랙 위주의 쿨한 무드",
     "으으… 오늘은 기분이 별로시군요. 강해 보이는 블랙 무드로 기세 올려요!"),
    (["긴장", "떨려", "불안", "걱정"], "차분하고 신뢰감 주는 무드",
     "긴장되시죠? 괜찮아요! 편안하고 단정한 옷이 자신감을 지켜줄 거예요."),
]
PLACES = [
    (["카페"], "작은 토트백과 텀블러"),
    (["학교", "교실", "학원"], "가벼운 백팩과 필통 파우치"),
    (["놀이공원", "롯데월드", "에버랜드"], "편한 운동화와 미니 백팩"),
    (["콘서트", "공연", "페스티벌", "팬미팅"], "응원봉을 걸 수 있는 크로스백"),
    (["pc방", "피시방", "게임"], "냉방 대비 얇은 후드와 편한 양말"),
    (["도서관", "독서실"], "무릎담요 대신 큰 가디건"),
    (["바다", "해변", "계곡", "수영"], "챙 넓은 모자와 샌들"),
    (["애니", "만화", "오타쿠", "굿즈", "아키하바라", "코믹"], "굿즈 뱃지를 달 수 있는 캔버스 가방"),
]
SITUATIONS = [
    (["데이트", "소개팅"], "첫인상이 중요해요! 포인트 액세서리는 딱 하나만 해보세요."),
    (["면접", "발표"], "구김 없이 단정하게! 색은 3가지 이하로 맞춰주세요."),
    (["친구", "약속", "놀"], "친구랑 사진 찍을 거라면 색을 2~3가지로 맞춰보세요."),
    (["시험", "공부"], "몸을 조이지 않는 편한 옷이 집중력에 좋아요."),
    (["생일", "파티"], "오늘의 주인공이니까 반짝이는 소품을 하나 더해도 좋아요!"),
]


def find(text, table):
    t = text.lower()
    for row in table:
        if any(k in t for k in row[0]):
            return row
    return None


def guess_style(text):
    for name, data in STYLES.items():
        if any(w in text for w in data["words"]):
            return name
    return "캐주얼"


def basic_recommend(mood, situation, place, style):
    chosen = guess_style(style)
    s = STYLES[chosen]
    m, p, sit = find(mood, MOODS), find(place, PLACES), find(situation, SITUATIONS)
    say = m[2] if m else "주인님, 어서 오세요! 오늘의 코디를 골라볼게요~"
    if place:
        say += f" {place}에 가신다니 설레네요!"
    vibe = f"{chosen} 스타일 · " + (m[1] if m else "오늘의 기본 코디")
    items = {k: random.choice(s[k]) for k in ["액세서리", "상의", "하의", "신발"]}
    if p:
        items["소품"] = p[1]
    tip = sit[1] if sit else "마음에 안 들면 다시 주문해주세요. 매번 다른 조합으로 골라드려요!"
    return {"say": say, "vibe": vibe, "items": items, "tip": tip, "mode": "basic"}


def ai_recommend(api_key, mood, situation, place, style):
    if not api_key:
        return None
    system = (
        "너는 코디 카페의 고양이 귀 메이드 '루나'야. 손님을 '주인님'이라고 부르고 "
        "귀엽고 상냥한 애니메이션 메이드 말투로 한국어로 말해. "
        "반드시 아래 JSON 형식으로만 답하고, 다른 말이나 코드블록은 쓰지 마. "
        "각 옷 이름에는 색(예: 블랙, 핑크, 네이비)과 종류(예: 블라우스, 후드, 자켓, 스커트, 팬츠, 부츠, 스니커즈)를 꼭 넣어줘.\n"
        '{"say":"주인님께 건네는 말 2문장","vibe":"코디 컨셉 한 줄",'
        '"items":{"액세서리":"","상의":"","하의":"","신발":"","소품":""},'
        '"tip":"코디 팁 한 문장"}'
    )
    user = (f"기분: {mood or '보통'}\n상황: {situation or '일상'}\n"
            f"장소: {place or '미정'}\n원하는 스타일: {style or '추천해줘'}\n"
            "이 조건에 맞는 옷을 구체적으로 추천해줘.")
    body = json.dumps({"model": "claude-sonnet-5-5", "max_tokens": 700, "system": system,
                       "messages": [{"role": "user", "content": user}]}).encode("utf-8")
    req = urllib.request.Request(
        "https://api.anthropic.com/v1/messages", data=body,
        headers={"x-api-key": api_key, "anthropic-version": "2023-06-01",
                 "content-type": "application/json"})
    try:
        with urllib.request.urlopen(req, timeout=30) as r:
            text = json.load(r)["content"][0]["text"]
        data = json.loads(re.search(r"\{.*\}", text, re.S).group(0))
        items = {str(k): str(v) for k, v in data["items"].items() if v}
        if not items:
            return None
        return {"say": str(data.get("say", "주인님, 코디 완성이에요!")),
                "vibe": str(data.get("vibe", "")), "items": items,
                "tip": str(data.get("tip", "")), "mode": "ai"}
    except Exception as e:
        print("AI 호출 실패 -> 내장 코디로 대체:", e)
        return None


# ============================================================
# 2) 옷 이름 -> 그림 정보 (색/종류를 글자에서 읽어요)
# ============================================================
COLORS = [
    (["블랙", "검정", "검은"], "#2a2438"), (["화이트", "흰", "하얀"], "#fbf4ff"),
    (["크림", "아이보리"], "#fff1d6"), (["핑크", "분홍", "파스텔"], "#ffa8cf"),
    (["보라", "라벤더", "퍼플"], "#a98bff"), (["네이비", "남색"], "#2c3e78"),
    (["블루", "파랑", "하늘", "스카이", "청바지", "데님"], "#5b9cf0"),
    (["민트", "그린", "초록", "카키"], "#7fd9b8"), (["레드", "빨강", "버건디", "와인"], "#d23c64"),
    (["노랑", "옐로", "머스타드", "버터"], "#ffd86b"), (["오렌지", "주황"], "#ff9a5c"),
    (["베이지", "카멜", "브라운", "모카"], "#d2a67e"), (["그레이", "회색", "차콜"], "#9a98ac"),
]
TOP_KINDS = [("jacket", ["자켓", "재킷", "점퍼", "윈드브레이커", "코트", "패딩", "가디건"]),
             ("hoodie", ["후드", "맨투맨", "집업", "플리스"]),
             ("blouse", ["블라우스", "셔츠", "레이스"]),
             ("knit", ["니트", "베스트", "스웨터", "터틀"])]
BOT_KINDS = [("skirt", ["스커트", "치마", "원피스"]), ("wide", ["와이드", "카고", "조거", "트랙"])]
SHOE_KINDS = [("boots", ["부츠", "하이킹", "통굽"]), ("mary", ["메리제인", "로퍼", "플랫폼"])]
ACC_KINDS = [("hat", ["햇", "모자", "캡", "비니", "버킷", "바라클라바"]),
             ("choker", ["초커"]), ("necklace", ["목걸이", "체인"]),
             ("belt", ["벨트"]), ("ribbon", ["리본", "머리핀", "헤어핀"])]
BAG_WORDS = ["가방", "백", "토트", "에코"]
TINT = {"고딕로리타": "#2a2438", "러블리": "#ffa8cf", "스트릿": "#9a98ac",
        "단정": "#fbf4ff", "고프코어": "#7fb89a", "캐주얼": "#8fb4ff"}


def pick_color(text, default):
    for words, c in COLORS:
        if any(w in text for w in words):
            return c
    return default


def kind_of(text, table, default):
    for kind, words in table:
        if any(w in text for w in words):
            return kind
    return default


def build_outfit(items, style):
    goth = style == "고딕로리타"
    top, bot, sh = items.get("상의", ""), items.get("하의", ""), items.get("신발", "")
    acc = items.get("액세서리", "")
    allacc = acc + " " + items.get("소품", "")
    return {
        "top": kind_of(top, TOP_KINDS, "tee"), "tc": pick_color(top, TINT.get(style, "#c9b6ff")),
        "bot": kind_of(bot, BOT_KINDS, "pants"), "bc": pick_color(bot, "#2a2438" if goth else "#3a3358"),
        "shoe": kind_of(sh, SHOE_KINDS, "sneakers"),
        "sc": pick_color(sh, "#2a2438" if goth else "#fbf4ff"),
        "acc": kind_of(allacc, ACC_KINDS, "ribbon"), "ac": pick_color(acc, "#ff5fae"),
        "bag": any(w in allacc for w in BAG_WORDS),
    }


DEFAULT_OUTFIT = {"top": "blouse", "tc": "#fbf4ff", "bot": "skirt", "bc": "#2a2438",
                  "shoe": "mary", "sc": "#2a2438", "acc": "ribbon", "ac": "#ff5fae", "bag": False}

# ============================================================
# 3) 루나 그리기 (입은 옷이 그림에 그대로 반영돼요)
# ============================================================
def maid_svg(o, small=False):
    sk = "#ffe3d3"
    tc, bc, sc, ac = o["tc"], o["bc"], o["sc"], o["ac"]
    top, bot, shoe, acc = o["top"], o["bot"], o["shoe"], o["acc"]
    p = []
    a = p.append
    if not small:  # 뒤에서 도는 마법진
        pts = " ".join(
            f"{100 + 90 * math.cos(math.radians(-90 + 144 * k)):.1f},"
            f"{190 + 90 * math.sin(math.radians(-90 + 144 * k)):.1f}" for k in range(5))
        a('<g class="mc"><circle cx="100" cy="190" r="108" fill="none" stroke="#ff5fae" '
          'stroke-width="1.5" stroke-dasharray="3 7"/><circle cx="100" cy="190" r="96" fill="none" '
          'stroke="#62e6f2" stroke-width="1.2" opacity=".7"/>'
          f'<polygon points="{pts}" fill="none" stroke="#ffe27a" stroke-width="1.2" opacity=".8"/></g>')
    # 머리카락 뒤 + 귀
    a('<path d="M46 70C10 90 6 170 30 214C48 182 54 130 62 90Z" fill="#c9b6ff"/>'
      '<path d="M154 70C190 90 194 170 170 214C152 182 146 130 138 90Z" fill="#c9b6ff"/>'
      '<circle cx="50" cy="78" r="8" fill="#ff5fae"/><circle cx="150" cy="78" r="8" fill="#ff5fae"/>'
      '<path d="M52 66L58 18L90 44Z" fill="#c9b6ff"/><path d="M148 66L142 18L110 44Z" fill="#c9b6ff"/>'
      '<path d="M60 52L62 32L78 46Z" fill="#ffb3d9"/><path d="M140 52L138 32L122 46Z" fill="#ffb3d9"/>'
      '<ellipse cx="100" cy="92" rx="58" ry="62" fill="#c9b6ff"/>')
    # 다리
    a(f'<rect x="80" y="286" width="14" height="34" rx="6" fill="{sk}"/>'
      f'<rect x="106" y="286" width="14" height="34" rx="6" fill="{sk}"/>')
    # 신발
    if shoe == "boots":
        a(f'<rect x="72" y="296" width="28" height="30" rx="8" fill="{sc}"/>'
          f'<rect x="100" y="296" width="28" height="30" rx="8" fill="{sc}"/>'
          '<rect x="70" y="324" width="32" height="6" rx="3" fill="#150c2e"/>'
          '<rect x="98" y="324" width="32" height="6" rx="3" fill="#150c2e"/>')
    elif shoe == "mary":
        a(f'<path d="M71 318Q86 306 102 318V326H71Z" fill="{sc}"/>'
          f'<path d="M98 318Q114 306 129 318V326H98Z" fill="{sc}"/>'
          '<path d="M74 316H100M100 316H126" stroke="#ff5fae" stroke-width="2.5"/>'
          '<rect x="70" y="325" width="32" height="5" rx="2.5" fill="#150c2e"/>'
          '<rect x="98" y="325" width="32" height="5" rx="2.5" fill="#150c2e"/>')
    else:
        a(f'<ellipse cx="86" cy="320" rx="17" ry="9" fill="{sc}"/><ellipse cx="114" cy="320" rx="17" ry="9" fill="{sc}"/>'
          '<rect x="69" y="324" width="34" height="6" rx="3" fill="#fff"/>'
          '<rect x="97" y="324" width="34" height="6" rx="3" fill="#fff"/>'
          '<path d="M78 314L90 318M110 318L122 314" stroke="#9a98ac" stroke-width="2"/>')
    # 하의
    if bot == "skirt":
        a(f'<path d="M70 230H130L154 294Q100 306 46 294Z" fill="{bc}"/>'
          '<path d="M84 240L74 298M100 240V302M116 240L126 298" stroke="#fff" stroke-width="1.5" opacity=".22"/>'
          '<path d="M47 293Q100 305 153 293" stroke="#fff" stroke-width="3" fill="none" opacity=".5"/>')
    elif bot == "wide":
        a(f'<path d="M68 230H100L104 308H60Z" fill="{bc}"/><path d="M100 230H132L140 308H96Z" fill="{bc}"/>'
          '<path d="M100 232V300" stroke="#000" stroke-width="1.5" opacity=".25"/>')
    else:
        a(f'<rect x="73" y="230" width="28" height="78" rx="6" fill="{bc}"/>'
          f'<rect x="99" y="230" width="28" height="78" rx="6" fill="{bc}"/>'
          '<path d="M100 234V300" stroke="#000" stroke-width="1.5" opacity=".25"/>')
    # 팔 (맨살) + 손
    a(f'<rect x="48" y="196" width="14" height="50" rx="7" fill="{sk}"/><rect x="138" y="196" width="14" height="50" rx="7" fill="{sk}"/>'
      f'<circle cx="55" cy="248" r="8" fill="{sk}"/><circle cx="145" cy="248" r="8" fill="{sk}"/>')
    # 몸통
    tf = "#fbf4ff" if top == "jacket" else tc
    a(f'<path d="M66 170Q100 160 134 170L132 238Q100 246 68 238Z" fill="{tf}"/>')
    # 소매
    h = 36 if top == "tee" else 70
    a(f'<rect x="44" y="172" width="22" height="{h}" rx="11" fill="{tc}"/>'
      f'<rect x="134" y="172" width="22" height="{h}" rx="11" fill="{tc}"/>')
    # 상의 디테일
    if top == "jacket":
        a(f'<path d="M66 170L97 166L93 242L68 238Z" fill="{tc}"/><path d="M134 170L103 166L107 242L132 238Z" fill="{tc}"/>'
          '<circle cx="90" cy="206" r="2.5" fill="#ffe27a"/><circle cx="90" cy="222" r="2.5" fill="#ffe27a"/>'
          '<path d="M97 166L86 190L93 192Z M103 166L114 190L107 192Z" fill="#fff" opacity=".35"/>')
    elif top == "hoodie":
        a(f'<path d="M72 168Q100 150 128 168Q124 188 100 190Q76 188 72 168Z" fill="{tc}"/>'
          '<path d="M92 178V204M108 178V204" stroke="#fff" stroke-width="2.5" stroke-linecap="round"/>'
          '<path d="M78 216H122L126 238H74Z" fill="#000" opacity=".14"/>')
    elif top == "blouse":
        a('<rect x="42" y="236" width="26" height="7" rx="3.5" fill="#fff"/><rect x="132" y="236" width="26" height="7" rx="3.5" fill="#fff"/>'
          '<circle cx="100" cy="206" r="2.2" fill="#ff5fae"/><circle cx="100" cy="220" r="2.2" fill="#ff5fae"/>')
    elif top == "knit":
        a('<rect x="66" y="232" width="68" height="9" rx="4" fill="#fff" opacity=".28"/>'
          '<path d="M78 192V228M90 192V228M110 192V228M122 192V228" stroke="#fff" stroke-width="1.5" opacity=".18"/>')
    else:
        a('<text x="100" y="214" text-anchor="middle" font-size="24" fill="#fff" opacity=".9">✦</text>')
    if acc == "belt":
        a(f'<rect x="66" y="228" width="68" height="8" rx="3" fill="{ac}"/><rect x="94" y="226" width="12" height="12" rx="2" fill="#ffe27a"/>')
    # 목 + 칼라
    a(f'<rect x="91" y="150" width="18" height="24" fill="{sk}"/>')
    if top == "blouse":
        a('<path d="M76 168Q100 192 124 168Q112 182 100 184Q88 182 76 168Z" fill="#fff"/>'
          '<path d="M100 180L84 172V190Z M100 180L116 172V190Z" fill="#ff5fae"/><circle cx="100" cy="180" r="4.5" fill="#ff5fae"/>')
    elif top == "knit":
        a('<path d="M84 168Q100 186 116 168" stroke="#fff" stroke-width="4" fill="none" opacity=".4"/>')
    # 가방
    if o["bag"]:
        a('<path d="M130 174L72 238" stroke="#d2a67e" stroke-width="5"/>'
          '<rect x="52" y="228" width="34" height="26" rx="7" fill="#b86bff"/>'
          '<path d="M52 238H86" stroke="#fff" stroke-width="2" opacity=".5"/><circle cx="69" cy="238" r="3" fill="#ffe27a"/>')
    # 얼굴
    a(f'<ellipse cx="100" cy="104" rx="50" ry="54" fill="{sk}"/>'
      '<path d="M50 100C48 42 152 42 150 100C140 74 124 66 100 78C76 66 60 74 50 100Z" fill="#c9b6ff"/>'
      '<g class="eye"><ellipse cx="78" cy="108" rx="9" ry="12" fill="#4b2a8a"/><circle cx="75" cy="103" r="3.6" fill="#fff"/></g>'
      '<g class="eye"><ellipse cx="122" cy="108" rx="9" ry="12" fill="#4b2a8a"/><circle cx="119" cy="103" r="3.6" fill="#fff"/></g>'
      '<ellipse cx="66" cy="124" rx="9" ry="5" fill="#ff8fc0" opacity=".55"/><ellipse cx="134" cy="124" rx="9" ry="5" fill="#ff8fc0" opacity=".55"/>'
      '<path d="M92 130Q100 138 108 130" fill="none" stroke="#c2487e" stroke-width="3" stroke-linecap="round"/>')
    # 머리 액세서리
    if acc == "hat":
        a(f'<ellipse cx="100" cy="50" rx="48" ry="9" fill="{ac}"/><path d="M66 50Q70 12 100 12Q130 12 134 50Z" fill="{ac}"/>'
          '<rect x="66" y="40" width="68" height="7" fill="#fff" opacity=".6"/><circle cx="100" cy="12" r="4" fill="#ffe27a"/>')
    else:
        a('<path d="M68 54Q100 34 132 54Q124 68 100 62Q76 68 68 54Z" fill="#fff" stroke="#ff5fae" stroke-width="2.5"/>')
        if acc == "ribbon":
            a(f'<path d="M152 72L132 60V84Z M152 72L174 60V84Z" fill="{ac}"/><circle cx="152" cy="72" r="6" fill="{ac}"/>')
    if acc == "choker":
        a(f'<path d="M83 158Q100 170 117 158V165Q100 177 83 165Z" fill="{ac}"/><circle cx="100" cy="173" r="4.5" fill="#ffe27a"/>')
    if acc == "necklace":
        a(f'<path d="M82 166Q100 198 118 166" stroke="{ac}" stroke-width="2.5" fill="none"/><circle cx="100" cy="192" r="5" fill="#ffe27a"/>')
    return '<svg viewBox="0 0 200 340" role="img" aria-label="메이드 루나">' + "".join(p) + "</svg>"


def maid_html(o):
    cols = ["#ffe27a", "#ff5fae", "#62e6f2", "#ffffff", "#b86bff", "#ffb3d9"]
    orbs = "".join(f'<i class="orb" style="animation-delay:-{k * 7 / 6:.2f}s;color:{c}">✦</i>'
                   for k, c in enumerate(cols))
    return ('<div class="maidwrap"><div class="stage"><div class="aura"></div>' + orbs
            + maid_svg(o) + '<div class="flash"></div></div></div>')


# ============================================================
# 4) 꾸미기 (CSS / 효과)
# ============================================================
CSS = """
<style>
@import url('https://fonts.googleapis.com/css2?family=Jua&family=Gowun+Dodum&family=DotGothic16&display=swap');
.stApp{
  background:
    radial-gradient(2px 2px at 20% 30%,#fff8,transparent),
    radial-gradient(2px 2px at 70% 20%,#fff8,transparent),
    radial-gradient(1.5px 1.5px at 40% 70%,#fff7,transparent),
    radial-gradient(2px 2px at 85% 60%,#fff8,transparent),
    linear-gradient(180deg,#150c2e 0%,#2a1650 100%);
  background-attachment:fixed; font-family:'Gowun Dodum',sans-serif;
}
.stApp::before{ /* 오로라 */
  content:""; position:fixed; inset:-5%; pointer-events:none; z-index:0;
  background:radial-gradient(60% 40% at 15% 10%,#ff5fae33,transparent),
             radial-gradient(50% 40% at 88% 30%,#62e6f233,transparent),
             radial-gradient(60% 40% at 50% 100%,#b86bff44,transparent);
  animation:aurora 12s ease-in-out infinite alternate;
}
@keyframes aurora{to{transform:translate(2%,3%) scale(1.1); opacity:.7}}
header[data-testid="stHeader"]{background:transparent}
#MainMenu, footer{visibility:hidden}
.block-container{max-width:640px; padding-top:1.5rem}
.stApp p, .stApp li{color:#fff}

/* 별 + 유성 */
.st{position:fixed; z-index:1; border-radius:50%; width:var(--s); height:var(--s);
  pointer-events:none; animation:tw var(--d) ease-in-out var(--dl) infinite}
@keyframes tw{0%,100%{opacity:.15; transform:scale(.6)}50%{opacity:1; transform:scale(1.5)}}
.mt{position:fixed; z-index:1; top:-8vh; width:2px; height:110px; pointer-events:none; opacity:0;
  background:linear-gradient(transparent,#fff); border-radius:2px; filter:drop-shadow(0 0 6px #62e6f2);
  animation:meteor var(--t) linear var(--w) infinite}
@keyframes meteor{0%{opacity:0; transform:translate(0,0) rotate(37deg)}
  2%{opacity:1} 14%{opacity:0; transform:translate(-55vw,75vh) rotate(37deg)} 100%{opacity:0}}

/* 타이틀 */
.titlebox{text-align:center; padding:60px 0 24px}
.titlebox .jp{font-family:'DotGothic16',sans-serif; color:#62e6f2; letter-spacing:.2em; font-size:14px}
.titlebox h1{
  font-family:'Jua',sans-serif; font-weight:400; font-size:clamp(40px,11vw,72px);
  line-height:1.1; margin:10px 0; color:#fff; padding:0;
  text-shadow:0 0 8px #ff5fae,0 0 22px #ff5fae,0 0 48px #ff5faeaa,0 0 80px #b86bff;
  animation:flicker 4s infinite;
}
.titlebox .sub{font-size:17px}
.titlebox .row{letter-spacing:.6em; color:#ffe27a; animation:tw 2s infinite; margin-top:10px}
@keyframes flicker{0%,92%,100%{opacity:1}94%{opacity:.7}96%{opacity:1}98%{opacity:.8}}

/* 버튼 */
.stButton button, [data-testid="stForm"] button{
  width:100%; border:0; border-radius:12px; padding:12px;
  background:linear-gradient(90deg,#ff5fae,#b86bff,#62e6f2,#ff5fae); background-size:300% 100%;
  box-shadow:0 5px 0 #7a2a9c,0 0 18px #ff5fae88; animation:holo 5s linear infinite;
}
.stButton button p, [data-testid="stForm"] button p{
  color:#fff !important; font-family:'Jua',sans-serif; font-size:21px;
}
[class*="st-key-wear"] button p, [class*="st-key-clear"] button p{font-size:15px}
@keyframes holo{to{background-position:300% 0}}
@keyframes bflow{to{background-position:0 0,300% 0}}

/* 루나 무대 */
.maidwrap{display:flex; justify-content:center; padding-top:30px}
.stage{position:relative; width:min(60vw,230px)}
.stage svg{display:block; width:100%; height:auto; overflow:visible; position:relative; z-index:2;
  animation:float 3.2s ease-in-out infinite; filter:drop-shadow(0 0 14px #ff5fae99)}
@keyframes float{50%{transform:translateY(-8px)}}
.mc{transform-box:fill-box; transform-origin:center; animation:spin 22s linear infinite}
@keyframes spin{to{transform:rotate(360deg)}}
.aura{position:absolute; inset:-8% -35% 0; border-radius:50%;
  background:radial-gradient(circle,#ff5fae55,#62e6f233 45%,transparent 70%); animation:breathe 3s ease-in-out infinite}
@keyframes breathe{50%{transform:scale(1.12); opacity:.7}}
.orb{position:absolute; left:50%; top:46%; z-index:3; font-style:normal; font-size:18px;
  text-shadow:0 0 10px currentColor; animation:orbit 7s linear infinite; pointer-events:none}
@keyframes orbit{from{transform:rotate(0) translateX(132px) rotate(0)}
  to{transform:rotate(360deg) translateX(132px) rotate(-360deg)}}
.flash{position:absolute; inset:-30%; z-index:4; pointer-events:none; opacity:0;
  background:radial-gradient(circle,#fff,#ff5fae88 35%,transparent 65%); animation:flash 1.2s ease-out}
@keyframes flash{0%{opacity:1; transform:scale(.2)}100%{opacity:0; transform:scale(1.7)}}
.eye{transform-box:fill-box; transform-origin:center; animation:eyes 4.5s infinite}
@keyframes eyes{0%,92%,100%{transform:scaleY(1)}95%{transform:scaleY(.08)}}

/* 대사창 */
.dialog{
  position:relative; margin-top:-6px; border:3px solid transparent; border-radius:14px;
  padding:26px 18px 18px; min-height:110px; line-height:1.7; font-size:17px; color:#fff;
  background:linear-gradient(#150c2eee,#150c2eee) padding-box,
             linear-gradient(90deg,#ff5fae,#62e6f2,#ffe27a,#ff5fae) border-box;
  background-size:100% 100%,300% 100%; animation:bflow 6s linear infinite;
  box-shadow:0 0 26px #ff5fae66,0 0 60px #b86bff44;
}
.nameplate{
  position:absolute; left:14px; top:-16px; background:#ff5fae; color:#150c2e;
  padding:3px 16px; border-radius:8px; font-family:'Jua',sans-serif; font-size:17px;
  box-shadow:0 3px 0 #a21d62,0 0 14px #ff5fae;
}
.say{white-space:pre-line}

/* 주문서 */
[data-testid="stForm"]{
  background:#fff7fc; border:3px solid #62e6f2; border-radius:16px;
  padding:20px 18px; box-shadow:6px 6px 0 #ff5fae,0 0 30px #62e6f255;
}
[data-testid="stForm"] label p{color:#2b1646 !important; font-family:'Jua',sans-serif; font-size:17px}
[data-testid="stForm"] input{background:#fff !important; color:#2b1646 !important}
.ft{font-family:'Jua',sans-serif; font-weight:400; color:#c2257a !important; font-size:23px; margin:0; padding:0}
.fh{color:#2b1646 !important; font-size:14px; opacity:.75; margin:0 0 6px}

/* 장비창 + 뽑기 */
.equip{
  margin-top:24px; border:3px solid transparent; border-radius:16px; padding:18px;
  background:linear-gradient(#150c2ef5,#150c2ef5) padding-box,
             linear-gradient(90deg,#ffe27a,#ff5fae,#62e6f2,#ffe27a) border-box;
  background-size:100% 100%,300% 100%; animation:bflow 6s linear infinite;
  box-shadow:0 0 30px #ffe27a55;
}
.holo{font-family:'Jua',sans-serif; font-weight:400; margin:0; padding:0; font-size:22px;
  background:linear-gradient(90deg,#ffe27a,#ff5fae,#62e6f2,#ffe27a); background-size:300% 100%;
  -webkit-background-clip:text; background-clip:text; color:transparent !important;
  animation:holo 5s linear infinite}
.gacha{position:relative; overflow:hidden; text-align:center; padding:8px; border-radius:10px;
  font-family:'Jua',sans-serif; font-size:18px; margin-bottom:12px; color:#150c2e}
.gacha span{letter-spacing:.1em}
.gSSR{background:linear-gradient(90deg,#ffe27a,#ff8fc0,#ffe27a); box-shadow:0 0 22px #ffe27a}
.gSR{background:linear-gradient(90deg,#62e6f2,#b86bff); box-shadow:0 0 16px #62e6f2}
.gR{background:#c9b6ff}
.gacha::after{content:""; position:absolute; top:0; left:-60%; width:40%; height:100%;
  background:linear-gradient(100deg,transparent,#ffffffaa,transparent); transform:skewX(-20deg);
  animation:sweep 2.4s infinite}
@keyframes sweep{to{left:140%}}
.vibe{margin:2px 0 12px; color:#62e6f2 !important; font-size:15px}
.equip ul{list-style:none; padding:0; margin:0; display:grid; gap:8px}
.equip li{display:flex; gap:12px; align-items:center; background:#ffffff12;
  border:1px solid #ffffff30; border-radius:10px; padding:9px 12px; animation:slide .4s both}
.equip li:nth-child(2){animation-delay:.12s}.equip li:nth-child(3){animation-delay:.24s}
.equip li:nth-child(4){animation-delay:.36s}.equip li:nth-child(5){animation-delay:.48s}
@keyframes slide{from{opacity:0; transform:translateX(-14px)}}
.slot{flex:none; width:100px; color:#ff5fae; font-family:'Jua',sans-serif; font-size:16px}
.nm{font-size:17px; color:#fff}
.tip{margin:14px 0 0; padding-top:12px; border-top:1px dashed #ffffff44; font-size:15px; line-height:1.6}
.tag{margin-top:10px; text-align:right; font-size:12px; opacity:.6; color:#fff}

/* 옷장 */
.closet{margin-top:28px; border:3px solid transparent; border-radius:16px 16px 4px 4px; padding:14px 16px 10px;
  background:linear-gradient(#1b1040f5,#1b1040f5) padding-box,
             linear-gradient(90deg,#ffe27a,#ff5fae,#62e6f2,#ffe27a) border-box;
  background-size:100% 100%,300% 100%; animation:bflow 6s linear infinite;
  box-shadow:0 0 26px #b86bff66}
.closet h2{margin:0; font-family:'Jua',sans-serif; font-weight:400; font-size:21px; color:#ffe27a; padding:0}
.closet .rail{height:7px; border-radius:4px; margin-top:10px;
  background:linear-gradient(#ffe27a,#c49a2a); box-shadow:0 0 12px #ffe27a99}
.closet p{margin:8px 0 0; font-size:14px; opacity:.8}
.hang{text-align:center; margin-top:2px}
.hang .hk{display:block; margin:0 auto -4px; filter:drop-shadow(0 0 5px #ffe27a)}
.thumb svg{width:92px; height:auto; overflow:visible; filter:drop-shadow(0 0 6px #ff5fae77)}
.cap{font-size:12px; line-height:1.35; min-height:34px; color:#fff}

/* 꽃잎 + 반짝이 */
.fall{position:fixed; top:-30px; z-index:999; pointer-events:none; animation:fall linear both;
  text-shadow:0 0 8px currentColor}
@keyframes fall{0%{transform:translate(0,0) rotate(0)} 50%{transform:translate(36px,55vh) rotate(150deg)}
  100%{transform:translate(-24px,110vh) rotate(320deg)}}
.spark{position:fixed; z-index:999; pointer-events:none; text-shadow:0 0 8px currentColor;
  animation:pop .9s ease-out forwards}
@keyframes pop{to{transform:translate(var(--dx),var(--dy)) scale(.2) rotate(180deg); opacity:0}}
@media (prefers-reduced-motion:reduce){*{animation:none !important}}
</style>
"""

TITLE_HTML = """
<div class="titlebox">
<div class="jp">おかえりなさいませ、ご主人様</div>
<h1>AI 메이드<br>코디</h1>
<div class="sub">기분과 장소를 말하면, 루나가 오늘의 옷을 입고 보여드려요</div>
<div class="row">✦ ✧ ✦ ✧ ✦</div>
</div>
"""

ICON = {"액세서리": "🎀", "상의": "👕", "하의": "👗", "신발": "👟", "소품": "🎒"}
RAR = {"SSR": ("★★★★★", "SSR 전설 코디 획득!"), "SR": ("★★★★☆", "SR 레어 코디 획득!"),
       "R": ("★★★☆☆", "R 오늘의 코디")}

SPARKLE_JS = """
<script>
try{
  const p = window.parent, d = p.document;
  if(!p.__sparkOn){
    p.__sparkOn = true; let last = 0;
    const cols = ['#ffe27a','#ff5fae','#62e6f2','#ffffff','#b86bff'];
    const shp = ['✦','✧','★','♡','✿'];
    const make = (x, y, dx, dy, size) => {
      const s = d.createElement('span');
      s.className = 'spark';
      s.textContent = shp[Math.floor(Math.random()*shp.length)];
      s.style.cssText = 'left:'+x+'px;top:'+y+'px;color:'+cols[Math.floor(Math.random()*cols.length)]+
        ';font-size:'+size+'px;--dx:'+dx+'px;--dy:'+dy+'px';
      d.body.appendChild(s); setTimeout(() => s.remove(), 900);
    };
    d.addEventListener('pointermove', e => {
      if(Date.now() - last < 45) return; last = Date.now();
      make(e.clientX, e.clientY, (Math.random()-.5)*50, -10-Math.random()*40, 12+Math.random()*12);
    });
    d.addEventListener('pointerdown', e => {
      for(let i = 0; i < 14; i++){
        const a = i/14*6.283, r = 40+Math.random()*50;
        make(e.clientX, e.clientY, Math.cos(a)*r, Math.sin(a)*r, 14+Math.random()*14);
      }
    });
  }
}catch(e){}
</script>
"""


def decor():
    rnd = random.Random(7)
    out = []
    cs = ["#fff", "#ffb3d9", "#9ff3fa", "#ffe27a"]
    for i in range(48):
        c = cs[i % 4]
        out.append(f'<i class="st" style="left:{rnd.uniform(0, 100):.1f}vw;top:{rnd.uniform(0, 100):.1f}vh;'
                   f'--s:{rnd.choice([2, 2, 3, 4])}px;--d:{rnd.uniform(1.8, 4.5):.1f}s;'
                   f'--dl:{rnd.uniform(0, 4):.1f}s;background:{c};box-shadow:0 0 7px 1px {c}"></i>')
    for _ in range(6):
        out.append(f'<b class="mt" style="left:{rnd.randint(35, 100)}vw;'
                   f'--t:{rnd.randint(7, 13)}s;--w:{rnd.uniform(0, 8):.1f}s"></b>')
    return "".join(out)


def dialog(text):
    return ('<div class="dialog"><div class="nameplate">루나</div><div class="say">'
            + html.escape(text) + '</div></div>')


def petals(n=36):
    icons, cols = "✿❀✦♡★", ["#ffb3d9", "#ffe27a", "#9ff3fa", "#ffffff", "#d9b8ff"]
    return "".join(
        f'<span class="fall" style="left:{random.randint(0, 98)}vw;font-size:{random.randint(14, 32)}px;'
        f'color:{random.choice(cols)};animation-duration:{random.uniform(4, 8):.1f}s;'
        f'animation-delay:{random.uniform(0, 3):.1f}s">{random.choice(icons)}</span>' for _ in range(n))


def equip_html(r):
    stars, name = RAR[r["rarity"]]
    lis = "".join(f'<li><span class="slot">{ICON.get(k, "✦")} {html.escape(k)}</span>'
                  f'<span class="nm">{html.escape(v)}</span></li>' for k, v in r["items"].items())
    mode = "AI(Claude) 연결됨" if r["mode"] == "ai" else "내장 코디 모드"
    return ('<div class="equip"><div class="gacha g' + r["rarity"] + '"><span>' + stars + '</span> ' + name
            + '</div><h2 class="holo">오늘의 장비창</h2><p class="vibe">' + html.escape(r["vibe"])
            + '</p><ul>' + lis + '</ul><p class="tip">💡 ' + html.escape(r["tip"])
            + '</p><div class="tag">' + mode + '</div></div>')


def card_html(r):
    return ('<div class="hang"><svg class="hk" viewBox="0 0 40 22" width="38"><path d="M20 3a4 4 0 1 1 4 4L20 10L4 19H36L20 10" '
            'fill="none" stroke="#ffe27a" stroke-width="2"/></svg><div class="thumb">'
            + maid_svg(r["outfit"], small=True) + '</div><div class="cap">' + RAR[r["rarity"]][0]
            + '<br>' + html.escape(r["vibe"][:16]) + '</div></div>')


# ============================================================
# 5) 앱 실행 흐름
# ============================================================
st.markdown(CSS, unsafe_allow_html=True)
st.markdown(decor(), unsafe_allow_html=True)

for k, v in {"entered": False, "greeted": False, "say": "", "current": None,
             "wardrobe": [], "pending": None}.items():
    st.session_state.setdefault(k, v)


def enter():
    st.session_state.entered = True


def wear(i):
    st.session_state.current = st.session_state.wardrobe[i]
    st.session_state.pending = "이 코디로 갈아입었어요, 주인님! 어때요? ✦"


def clear_closet():
    st.session_state.wardrobe = []


if not st.session_state.entered:
    st.markdown(TITLE_HTML, unsafe_allow_html=True)
    st.button("▶ 입장하기", on_click=enter, use_container_width=True)
    st.stop()

with st.sidebar:
    st.markdown("**AI 연결 (선택)**")
    key_input = st.text_input("Anthropic API 키", type="password",
                              help="비워두면 내장 코디 모드로 작동해요.")
api_key = key_input or os.environ.get("ANTHROPIC_API_KEY", "")

maid_ph = st.empty()
dialog_ph = st.empty()

with st.form("order"):
    st.markdown('<h2 class="ft">코디 주문서</h2>'
                '<p class="fh">비워두면 루나가 알아서 골라요. 입력 후 Enter를 눌러도 돼요.</p>',
                unsafe_allow_html=True)
    mood = st.text_input("지금 기분은?", placeholder="예: 월요일이라 피곤해요")
    situation = st.text_input("어떤 상황이에요?", placeholder="예: 친구랑 약속, 데이트, 발표")
    place = st.text_input("어디에 가요?", placeholder="예: 애니 굿즈샵, 카페, 학교")
    style = st.text_input("원하는 스타일은?", placeholder="예: 고딕 로리타, 스트릿, 단정, 러블리")
    submitted = st.form_submit_button("코디 소환! ▶")

to_type = None
if not st.session_state.greeted:
    to_type = ("おかえりなさいませ、ご主人様~ ♡\n"
               "어서오세요, 주인님! 메이드 루나예요. 기분, 상황, 장소, 스타일을 알려주세요!")
    st.session_state.greeted = True
if st.session_state.pending:
    to_type = st.session_state.pending
    st.session_state.pending = None

big_rain = False
if submitted:
    with st.spinner("루나가 옷장을 뒤지는 중이에요… ✦"):
        args = (mood.strip()[:60], situation.strip()[:60], place.strip()[:60], style.strip()[:60])
        r = ai_recommend(api_key, *args) or basic_recommend(*args)
        r["outfit"] = build_outfit(r["items"], guess_style(args[3] + " " + r["vibe"]))
        r["rarity"] = random.choices(["R", "SR", "SSR"], [60, 30, 10])[0]
    st.session_state.current = r
    st.session_state.wardrobe.insert(0, r)
    del st.session_state.wardrobe[6:]
    to_type = r["say"]
    big_rain = r["rarity"] == "SSR"

cur = st.session_state.current
maid_ph.markdown(maid_html(cur["outfit"] if cur else DEFAULT_OUTFIT), unsafe_allow_html=True)
dialog_ph.markdown(dialog(st.session_state.say), unsafe_allow_html=True)

if cur:
    st.markdown(equip_html(cur), unsafe_allow_html=True)

# --- 옷장 ---
st.markdown('<div class="closet"><h2>👗 루나의 옷장</h2><div class="rail"></div>'
            '<p>소환한 코디가 자동으로 걸려요. (최대 6벌)</p></div>', unsafe_allow_html=True)
wd = st.session_state.wardrobe
if not wd:
    st.markdown('<p style="text-align:center;margin-top:14px">🪝 🪝 🪝<br>아직 텅 비었어요. 코디를 소환하면 여기에 걸려요!</p>',
                unsafe_allow_html=True)
else:
    for row in range(0, len(wd), 3):
        cols = st.columns(3)
        for j, c in enumerate(cols):
            i = row + j
            if i < len(wd):
                with c:
                    st.markdown(card_html(wd[i]), unsafe_allow_html=True)
                    st.button("입혀보기", key=f"wear{i}", on_click=wear, args=(i,),
                              use_container_width=True)
    st.button("옷장 비우기", key="clear_all", on_click=clear_closet)

components.html(SPARKLE_JS, height=0)

if to_type:
    st.markdown(petals(60 if big_rain else 36), unsafe_allow_html=True)
    for i in range(1, len(to_type) + 1):  # 한 글자씩 말하는 효과
        dialog_ph.markdown(dialog(to_type[:i]), unsafe_allow_html=True)
        time.sleep(0.03)
    st.session_state.say = to_type