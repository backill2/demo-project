import os
import re
import json
import html
import random
import time
import urllib.request

import streamlit as st
import streamlit.components.v1 as components

st.set_page_config(page_title="AI 메이드 코디", page_icon="🎀",
                   initial_sidebar_state="collapsed")

# ------------------------------------------------------------
# 1) 코디 데이터 (AI 키가 없을 때 사용)
# ------------------------------------------------------------
STYLES = {
    "캐주얼": {
        "words": ["캐주얼", "편한", "무난", "데일리"],
        "액세서리": ["볼캡", "실버 목걸이", "미니 크로스백"],
        "상의": ["오버핏 맨투맨", "그래픽 티셔츠", "후드 집업"],
        "하의": ["워싱 청바지", "조거 팬츠", "와이드 코튼 팬츠"],
        "신발": ["흰 스니커즈", "캔버스화"],
    },
    "고딕로리타": {
        "words": ["고딕", "로리타", "고스", "다크", "블랙"],
        "액세서리": ["레이스 초커", "리본 헤어핀", "미니 햇"],
        "상의": ["프릴 블라우스", "블랙 레이스 셔츠"],
        "하의": ["코르셋 스커트", "블랙 플리츠 스커트"],
        "신발": ["플랫폼 메리제인", "통굽 부츠"],
    },
    "러블리": {
        "words": ["러블리", "귀여", "걸리시", "달달", "핑크"],
        "액세서리": ["리본 머리핀", "하트 목걸이", "진주 헤어핀"],
        "상의": ["파스텔 니트 가디건", "퍼프 소매 블라우스"],
        "하의": ["플리츠 스커트", "A라인 미니스커트"],
        "신발": ["리본 스니커즈", "메리제인 슈즈"],
    },
    "스트릿": {
        "words": ["스트릿", "힙합", "힙한", "오버사이즈"],
        "액세서리": ["버킷햇", "체인 목걸이", "비니"],
        "상의": ["박시 후드티", "빅 로고 티셔츠", "바시티 자켓"],
        "하의": ["와이드 데님", "카고 팬츠"],
        "신발": ["청키 스니커즈", "하이탑 스니커즈"],
    },
    "단정": {
        "words": ["단정", "깔끔", "시티보이", "미니멀", "정장", "포멀"],
        "액세서리": ["심플 시계", "얇은 벨트", "깔끔한 에코백"],
        "상의": ["옥스포드 셔츠", "니트 베스트", "무지 라운드 니트"],
        "하의": ["슬랙스", "면바지", "미디 스커트"],
        "신발": ["로퍼", "깔끔한 흰 스니커즈"],
    },
    "고프코어": {
        "words": ["고프코어", "아웃도어", "등산", "테크웨어", "기능성"],
        "액세서리": ["클립 버클 벨트", "방수 크로스백", "바라클라바"],
        "상의": ["윈드브레이커", "플리스 집업"],
        "하의": ["나일론 카고 팬츠", "트랙 팬츠"],
        "신발": ["트레일 러닝화", "투박한 하이킹화"],
    },
}

MOODS = [
    (["우울", "슬", "힘들", "지침", "피곤", "졸", "무기력"],
     "포근하고 편안한 레이어드",
     "주인님… 오늘은 지치셨죠? 루나가 포근하게 감싸드릴 코디로 골랐어요."),
    (["신나", "설레", "기뻐", "행복", "좋아", "들뜬", "텐션"],
     "텐션 업! 컬러 포인트 코디",
     "와아~ 주인님 오늘 기분 최고예요! 그 반짝임을 옷에도 담아볼게요!"),
    (["화", "짜증", "빡", "예민"],
     "블랙 위주의 쿨한 무드",
     "으으… 오늘은 기분이 별로시군요. 강해 보이는 블랙 무드로 기세 올려요!"),
    (["긴장", "떨려", "불안", "걱정"],
     "차분하고 신뢰감 주는 무드",
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
    (["애니", "만화", "오타쿠", "굿즈", "아키하바라", "코믹"],
     "굿즈 뱃지를 달 수 있는 캔버스 가방"),
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


def basic_recommend(mood, situation, place, style):
    chosen = "캐주얼"
    for name, data in STYLES.items():
        if any(w in style for w in data["words"]):
            chosen = name
            break
    s = STYLES[chosen]
    m = find(mood, MOODS)
    p = find(place, PLACES)
    sit = find(situation, SITUATIONS)

    say = m[2] if m else "주인님, 어서 오세요! 오늘의 코디를 골라볼게요~"
    if place:
        say += f" {place}에 가신다니 설레네요!"
    vibe = f"{chosen} 스타일 · " + (m[1] if m else "오늘의 기본 코디")

    items = {
        "액세서리": random.choice(s["액세서리"]),
        "상의": random.choice(s["상의"]),
        "하의": random.choice(s["하의"]),
        "신발": random.choice(s["신발"]),
    }
    if p:
        items["소품"] = p[1]
    tip = sit[1] if sit else "마음에 안 들면 다시 주문해주세요. 매번 다른 조합으로 골라드려요!"
    return {"say": say, "vibe": vibe, "items": items, "tip": tip, "mode": "basic"}


# ------------------------------------------------------------
# 2) 진짜 AI(Claude) 추천 (API 키가 있을 때만)
# ------------------------------------------------------------
def ai_recommend(api_key, mood, situation, place, style):
    if not api_key:
        return None
    system = (
        "너는 코디 카페의 고양이 귀 메이드 '루나'야. 손님을 '주인님'이라고 부르고 "
        "귀엽고 상냥한 애니메이션 메이드 말투로 한국어로 말해. "
        "반드시 아래 JSON 형식으로만 답하고, 다른 말이나 코드블록은 쓰지 마.\n"
        '{"say":"주인님께 건네는 말 2문장","vibe":"코디 컨셉 한 줄",'
        '"items":{"액세서리":"","상의":"","하의":"","신발":"","소품":""},'
        '"tip":"코디 팁 한 문장"}'
    )
    user = (
        f"기분: {mood or '보통'}\n상황: {situation or '일상'}\n"
        f"장소: {place or '미정'}\n원하는 스타일: {style or '추천해줘'}\n"
        "이 조건에 맞는 옷을 구체적으로(색, 종류 포함) 추천해줘."
    )
    body = json.dumps({
        "model": "claude-sonnet-5-5",
        "max_tokens": 700,
        "system": system,
        "messages": [{"role": "user", "content": user}],
    }).encode("utf-8")
    req = urllib.request.Request(
        "https://api.anthropic.com/v1/messages",
        data=body,
        headers={"x-api-key": api_key, "anthropic-version": "2023-06-01",
                 "content-type": "application/json"},
    )
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


# ------------------------------------------------------------
# 3) 화면 꾸미기 (CSS / SVG)
# ------------------------------------------------------------
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
header[data-testid="stHeader"]{background:transparent}
#MainMenu, footer{visibility:hidden}
.block-container{max-width:640px; padding-top:1.5rem}
.stApp p, .stApp li{color:#fff}

/* 타이틀 */
.titlebox{text-align:center; padding:60px 0 24px}
.titlebox .jp{font-family:'DotGothic16',sans-serif; color:#62e6f2; letter-spacing:.2em; font-size:14px}
.titlebox h1{
  font-family:'Jua',sans-serif; font-weight:400; font-size:clamp(40px,11vw,72px);
  line-height:1.1; margin:10px 0; color:#fff; padding:0;
  text-shadow:0 0 8px #ff5fae,0 0 22px #ff5fae,0 0 48px #ff5faeaa;
  animation:flicker 4s infinite;
}
.titlebox .sub{font-size:17px}
@keyframes flicker{0%,92%,100%{opacity:1}94%{opacity:.7}96%{opacity:1}98%{opacity:.8}}

/* 버튼 공통 (입장 버튼 / 주문 버튼) */
.stButton button, [data-testid="stForm"] button{
  width:100%; border:0; border-radius:12px; padding:12px;
  background:linear-gradient(90deg,#ff5fae,#b86bff); box-shadow:0 5px 0 #7a2a9c;
}
.stButton button p, [data-testid="stForm"] button p{
  color:#fff !important; font-family:'Jua',sans-serif; font-size:21px;
}

/* 메이드 + 대사창 */
.maidwrap{display:flex; justify-content:center}
.maidwrap svg{width:min(52vw,210px); height:auto; animation:float 3.2s ease-in-out infinite;
  filter:drop-shadow(0 0 14px #ff5fae88)}
@keyframes float{50%{transform:translateY(-8px)}}
.eye{transform-box:fill-box; transform-origin:center; animation:eyes 4.5s infinite}
@keyframes eyes{0%,92%,100%{transform:scaleY(1)}95%{transform:scaleY(.08)}}
.dialog{
  position:relative; margin-top:-10px; background:#150c2eee; border:3px solid #ff5fae;
  border-radius:14px; padding:26px 18px 18px; min-height:110px; line-height:1.7; font-size:17px;
  color:#fff; box-shadow:0 0 0 3px #150c2e,0 0 0 5px #62e6f2,0 0 26px #ff5fae66;
}
.nameplate{
  position:absolute; left:14px; top:-16px; background:#ff5fae; color:#150c2e;
  padding:3px 16px; border-radius:8px; font-family:'Jua',sans-serif; font-size:17px;
  box-shadow:0 3px 0 #a21d62;
}
.say{white-space:pre-line}

/* 주문서 */
[data-testid="stForm"]{
  background:#fff7fc; border:3px solid #62e6f2; border-radius:16px;
  padding:20px 18px; box-shadow:6px 6px 0 #ff5fae;
}
[data-testid="stForm"] label p{color:#2b1646 !important; font-family:'Jua',sans-serif; font-size:17px}
[data-testid="stForm"] input{background:#fff !important; color:#2b1646 !important}
.ft{font-family:'Jua',sans-serif; font-weight:400; color:#c2257a !important; font-size:23px; margin:0; padding:0}
.fh{color:#2b1646 !important; font-size:14px; opacity:.75; margin:0 0 6px}

/* 장비창 */
.equip{
  margin-top:24px; background:#150c2ef2; border:3px solid #ffe27a; border-radius:16px;
  padding:18px; box-shadow:0 0 22px #ffe27a44;
}
.equip h2{font-family:'Jua',sans-serif; font-weight:400; margin:0; padding:0; font-size:21px; color:#ffe27a}
.vibe{margin:2px 0 12px; color:#62e6f2 !important; font-size:15px}
.equip ul{list-style:none; padding:0; margin:0; display:grid; gap:8px}
.equip li{
  display:flex; gap:12px; align-items:center; background:#ffffff12;
  border:1px solid #ffffff30; border-radius:10px; padding:9px 12px; animation:slide .4s both;
}
.equip li:nth-child(2){animation-delay:.12s}.equip li:nth-child(3){animation-delay:.24s}
.equip li:nth-child(4){animation-delay:.36s}.equip li:nth-child(5){animation-delay:.48s}
@keyframes slide{from{opacity:0; transform:translateX(-14px)}}
.slot{flex:none; width:100px; color:#ff5fae; font-family:'Jua',sans-serif; font-size:16px}
.nm{font-size:17px; color:#fff}
.tip{margin:14px 0 0; padding-top:12px; border-top:1px dashed #ffffff44; font-size:15px; line-height:1.6}
.tag{margin-top:10px; text-align:right; font-size:12px; opacity:.6; color:#fff}

/* 꽃잎 + 반짝이 */
.fall{position:fixed; top:-30px; z-index:999; pointer-events:none; color:#ffb3d9;
  animation:fall linear both}
@keyframes fall{to{transform:translateY(110vh) rotate(300deg)}}
.spark{position:fixed; z-index:999; pointer-events:none; color:#ffe27a; font-size:15px;
  animation:pop .7s ease-out forwards}
@keyframes pop{to{transform:translateY(-22px) scale(.2); opacity:0}}
@media (prefers-reduced-motion:reduce){
  .maidwrap svg,.eye,.titlebox h1,.equip li,.fall{animation:none}
}
</style>
"""

TITLE_HTML = """
<div class="titlebox">
<div class="jp">おかえりなさいませ、ご主人様</div>
<h1>AI 메이드<br>코디</h1>
<div class="sub">기분과 장소를 말하면, 루나가 오늘의 옷을 골라드려요</div>
</div>
"""

MAID_SVG = '''
<div class="maidwrap">
<svg viewBox="0 0 200 270" role="img" aria-label="메이드 루나">
<path d="M46 70C10 90 6 170 30 214C48 182 54 130 62 90Z" fill="#c9b6ff"/>
<path d="M154 70C190 90 194 170 170 214C152 182 146 130 138 90Z" fill="#c9b6ff"/>
<circle cx="50" cy="78" r="8" fill="#ff5fae"/><circle cx="150" cy="78" r="8" fill="#ff5fae"/>
<path d="M52 66L58 18L90 44Z" fill="#c9b6ff"/><path d="M148 66L142 18L110 44Z" fill="#c9b6ff"/>
<path d="M60 52L62 32L78 46Z" fill="#ffb3d9"/><path d="M140 52L138 32L122 46Z" fill="#ffb3d9"/>
<ellipse cx="100" cy="92" rx="58" ry="62" fill="#c9b6ff"/>
<path d="M62 168Q100 148 138 168L152 268H48Z" fill="#1d1233"/>
<path d="M78 170Q100 182 122 170L134 268H66Z" fill="#fff"/>
<path d="M48 268q10-12 20 0t20 0t20 0t20 0t20 0t20 0" fill="none" stroke="#fff" stroke-width="5"/>
<rect x="91" y="150" width="18" height="24" fill="#ffe3d3"/>
<ellipse cx="100" cy="104" rx="50" ry="54" fill="#ffe3d3"/>
<path d="M50 100C48 42 152 42 150 100C140 74 124 66 100 78C76 66 60 74 50 100Z" fill="#c9b6ff"/>
<g class="eye"><ellipse cx="78" cy="108" rx="9" ry="12" fill="#4b2a8a"/><circle cx="75" cy="103" r="3.6" fill="#fff"/></g>
<g class="eye"><ellipse cx="122" cy="108" rx="9" ry="12" fill="#4b2a8a"/><circle cx="119" cy="103" r="3.6" fill="#fff"/></g>
<ellipse cx="66" cy="124" rx="9" ry="5" fill="#ff8fc0" opacity=".55"/>
<ellipse cx="134" cy="124" rx="9" ry="5" fill="#ff8fc0" opacity=".55"/>
<path d="M92 130Q100 138 108 130" fill="none" stroke="#c2487e" stroke-width="3" stroke-linecap="round"/>
<path d="M68 54Q100 34 132 54Q124 68 100 62Q76 68 68 54Z" fill="#fff" stroke="#ff5fae" stroke-width="2.5"/>
<path d="M100 178L82 168V188Z M100 178L118 168V188Z" fill="#ff5fae"/><circle cx="100" cy="178" r="5" fill="#ff5fae"/>
</svg>
</div>
'''
MAID_SVG = " ".join(line.strip() for line in MAID_SVG.splitlines() if line.strip())

ICON = {"액세서리": "🎀", "상의": "👕", "하의": "👗", "신발": "👟", "소품": "🎒"}

# 마우스 반짝이 꼬리 (부모 페이지에 자바스크립트를 심어요)
SPARKLE_JS = """
<script>
try{
  const p = window.parent;
  if(!p.__sparkOn){
    p.__sparkOn = true; let last = 0;
    p.document.addEventListener('pointermove', e => {
      if(Date.now() - last < 70) return; last = Date.now();
      const s = p.document.createElement('span');
      s.className = 'spark'; s.textContent = '✦';
      s.style.left = e.clientX + 'px'; s.style.top = e.clientY + 'px';
      p.document.body.appendChild(s); setTimeout(() => s.remove(), 700);
    });
  }
}catch(e){}
</script>
"""


def dialog(text):
    return ('<div class="dialog"><div class="nameplate">루나</div><div class="say">'
            + html.escape(text) + '</div></div>')


def petals(n=26):
    icons = "✿❀✦♡"
    out = []
    for _ in range(n):
        out.append(
            f'<span class="fall" style="left:{random.randint(0, 98)}vw;'
            f'font-size:{random.randint(14, 30)}px;'
            f'animation-duration:{random.uniform(4, 8):.1f}s;'
            f'animation-delay:{random.uniform(0, 3):.1f}s">{random.choice(icons)}</span>')
    return "".join(out)


def equip_html(r):
    lis = "".join(
        f'<li><span class="slot">{ICON.get(k, "✦")} {html.escape(k)}</span>'
        f'<span class="nm">{html.escape(v)}</span></li>'
        for k, v in r["items"].items())
    mode = "AI(Claude) 연결됨" if r["mode"] == "ai" else "내장 코디 모드"
    return ('<div class="equip"><h2>오늘의 장비창</h2><p class="vibe">'
            + html.escape(r["vibe"]) + '</p><ul>' + lis + '</ul><p class="tip">💡 '
            + html.escape(r["tip"]) + '</p><div class="tag">' + mode + '</div></div>')


# ------------------------------------------------------------
# 4) 앱 실행 흐름
# ------------------------------------------------------------
st.markdown(CSS, unsafe_allow_html=True)

for k, v in {"entered": False, "greeted": False, "say": "", "result": None}.items():
    st.session_state.setdefault(k, v)


def enter():
    st.session_state.entered = True


# --- 타이틀 화면 ---
if not st.session_state.entered:
    st.markdown(TITLE_HTML, unsafe_allow_html=True)
    st.button("▶ 입장하기", on_click=enter, use_container_width=True)
    st.stop()

# --- 사이드바: AI 키 (선택) ---
with st.sidebar:
    st.markdown("**AI 연결 (선택)**")
    key_input = st.text_input("Anthropic API 키", type="password",
                              help="비워두면 내장 코디 모드로 작동해요.")
api_key = key_input or os.environ.get("ANTHROPIC_API_KEY", "")

# --- 메인 화면 ---
st.markdown(MAID_SVG, unsafe_allow_html=True)
dialog_ph = st.empty()
dialog_ph.markdown(dialog(st.session_state.say), unsafe_allow_html=True)

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

if submitted:
    with st.spinner("루나가 옷장을 뒤지는 중이에요… ✦"):
        args = (mood.strip()[:60], situation.strip()[:60],
                place.strip()[:60], style.strip()[:60])
        result = ai_recommend(api_key, *args) or basic_recommend(*args)
    st.session_state.result = result
    to_type = result["say"]

if st.session_state.result:
    st.markdown(equip_html(st.session_state.result), unsafe_allow_html=True)

if to_type:
    st.markdown(petals(), unsafe_allow_html=True)
    for i in range(1, len(to_type) + 1):          # 한 글자씩 말하는 효과
        dialog_ph.markdown(dialog(to_type[:i]), unsafe_allow_html=True)
        time.sleep(0.03)
    st.session_state.say = to_type

components.html(SPARKLE_JS, height=0)