"""
Red or Black! — a picture-first card game for little kids.

The robot dealer shuffles a real 52-card deck and deals. Kids can play alone
(vs. the robot) or pass the iPad around (up to 4 kids).

Kid-facing screens use only pictures, colors and a talking dealer (iPad speech),
so non-readers can play. Text is only on the grown-up setup screen.
"""

import html
import json
import random

import streamlit as st

st.set_page_config(
    page_title="Red or Black!",
    page_icon="🃏",
    layout="centered",
    initial_sidebar_state="collapsed",
)

# ---------------------------------------------------------------- constants
BG = "#FFF8E7"
MAX_KIDS = 4
AVATARS = ["🐶", "🐱", "🦁", "🐸", "🐵", "🦄", "🐼", "🦖", "🐧", "🐰"]
ANIMAL_NAMES = {
    "🐶": "Puppy", "🐱": "Kitty", "🦁": "Lion", "🐸": "Froggy", "🐵": "Monkey",
    "🦄": "Unicorn", "🐼": "Panda", "🦖": "Dino", "🐧": "Penguin", "🐰": "Bunny",
}
PRIZES = [
    ("🦄", "a magic unicorn"), ("🚀", "a rocket ship"), ("🐶", "a puppy"),
    ("🦖", "a dinosaur"), ("🍦", "a giant ice cream"), ("🏰", "a castle"),
    ("🎸", "a rock star guitar"), ("🧸", "a teddy bear"), ("🚂", "a choo choo train"),
    ("👑", "a royal crown"), ("🦈", "a shark buddy"), ("🍕", "a pizza party"),
    ("🐉", "a dragon"), ("🏎️", "a race car"), ("🎂", "a birthday cake"),
]
STICKERS = ["⭐", "🌈", "🍭", "🎈", "🦋", "🌻", "🍪", "🌟"]
SUITS = [("♥", "red"), ("♦", "red"), ("♠", "black"), ("♣", "black")]
RANKS = ["A", "2", "3", "4", "5", "6", "7", "8", "9", "10", "J", "Q", "K"]
MEDALS = {1: "🥇", 2: "🥈", 3: "🥉", 4: "🏅"}
T = "︎"  # forces text (not emoji) style so suits can be colored white

ss = st.session_state

# ---------------------------------------------------------------- page CSS
BIG_BUTTONS = {
    # key: (height, background, text color, label size)
    "pick_red": ("210px", "radial-gradient(circle at 30% 25%, #ff7373, #c62828)", "#fff", "84px"),
    "pick_black": ("210px", "radial-gradient(circle at 30% 25%, #5a5a5a, #0b0b0b)", "#fff", "84px"),
    "next_btn": ("130px", "linear-gradient(#ffd54f, #ffa000)", "#000", "64px"),
    "again_btn": ("110px", "linear-gradient(#81c784, #388e3c)", "#fff", "54px"),
    "setup_btn": ("110px", "linear-gradient(#e0e0e0, #9e9e9e)", "#000", "54px"),
    "start_btn": ("100px", "linear-gradient(#81c784, #388e3c)", "#fff", "40px"),
}


def page_css() -> str:
    rules = []
    for key, (h, bg, fg, fs) in BIG_BUTTONS.items():
        sel = f".st-key-{key} button"
        rules.append(f"""
        {sel}, {sel}:hover, {sel}:focus, {sel}:active, {sel}:focus:not(:active) {{
            background: {bg} !important; color: {fg} !important;
            height: {h}; border-radius: 30px !important; border: 6px solid #fff !important;
            box-shadow: 0 9px 0 rgba(0,0,0,.22), 0 12px 24px rgba(0,0,0,.18) !important;
            touch-action: manipulation; transition: transform .07s, box-shadow .07s;
        }}
        {sel}:active {{ transform: translateY(7px); box-shadow: 0 2px 0 rgba(0,0,0,.22) !important; }}
        {sel} p, {sel} div {{ font-size: {fs} !important; line-height: 1.05 !important;
            font-weight: 800 !important; color: {fg} !important; }}
        """)
    return f"""
    <style>
    {"".join(rules)}
    #MainMenu, footer, [data-testid="stToolbar"], [data-testid="stDecoration"],
    header[data-testid="stHeader"] {{ display: none !important; }}
    .block-container {{ padding-top: 1rem !important; padding-bottom: 2rem !important; max-width: 860px; }}
    * {{ -webkit-tap-highlight-color: transparent; }}
    .av, .medal, .stk, .stars, .vs {{ font-family: "Apple Color Emoji","Segoe UI Emoji","Noto Color Emoji",sans-serif; }}
    .title {{ text-align:center; font-size:60px; font-weight:900; line-height:1.05; margin:0 0 4px;
              letter-spacing:-1px; }}
    .title .r {{ color:#e53935; }} .title .b {{ color:#111; }}
    .sub {{ text-align:center; color:#888; font-size:14px; margin-bottom:10px; }}
    .board {{ display:flex; justify-content:center; gap:10px; flex-wrap:wrap; margin:2px 0 6px; }}
    .seat {{ background:#fff; border-radius:20px; padding:6px 10px 10px; min-width:118px; text-align:center;
             box-shadow:0 3px 8px rgba(0,0,0,.12); border:5px solid transparent; }}
    .seat.now {{ border-color:#ffb300; box-shadow:0 0 0 4px #ffe082, 0 6px 14px rgba(0,0,0,.18); }}
    .seat.robot {{ opacity:.75; min-width:90px; }}
    .seat .av {{ font-size:46px; line-height:1.15; }}
    .seat .num {{ font-size:34px; font-weight:900; line-height:1; margin:2px 0 6px; }}
    .pile {{ display:flex; flex-wrap:wrap; justify-content:center; gap:7px; max-width:140px; margin:auto; }}
    .grp {{ display:flex; gap:2px; }}
    .mini {{ width:10px; height:15px; border-radius:2px; border:1px solid #fff;
             background:linear-gradient(135deg,#42a5f5,#0d47a1); box-shadow:0 0 0 1px #0d47a1; }}
    .rank {{ display:flex; align-items:center; gap:14px; background:#fff; border-radius:22px;
             padding:10px 16px; margin:10px 0; box-shadow:0 3px 8px rgba(0,0,0,.12); }}
    .rank.first {{ background:linear-gradient(135deg,#fff8d6,#ffe082); border:4px solid #ffc107; }}
    .rank .medal {{ font-size:54px; }}
    .rank .av {{ font-size:58px; }}
    .rank .num {{ font-size:44px; font-weight:900; min-width:56px; text-align:center; }}
    .rank .stars {{ font-size:34px; letter-spacing:2px; }}
    .rank .stars .off {{ opacity:.18; filter:grayscale(1); }}
    .rank .who {{ font-size:15px; color:#777; }}
    .rank .grow {{ flex:1; }}
    .rank .stk {{ font-size:44px; }}
    .vs {{ text-align:center; font-size:40px; margin:-4px 0; }}
    </style>
    """


# collapse to one line: blank/indented lines would make Markdown treat CSS as a code block
st.markdown(" ".join(page_css().split()), unsafe_allow_html=True)


# ---------------------------------------------------------------- helpers
def new_deck():
    deck = [(r, s, c) for s, c in SUITS for r in RANKS]
    random.shuffle(deck)
    return deck


def spoken_name(p) -> str:
    return p["name"].strip() or ANIMAL_NAMES.get(p["avatar"], "friend")


def esc(s: str) -> str:
    return html.escape(s or "")


def pile_html(n: int) -> str:
    """Little cards in groups of 5 so kids can count them."""
    if n == 0:
        return '<div class="pile" style="height:15px"></div>'
    groups, out = [5] * (n // 5) + ([n % 5] if n % 5 else []), []
    for g in groups:
        out.append('<div class="grp">' + '<div class="mini"></div>' * g + "</div>")
    return '<div class="pile">' + "".join(out) + "</div>"


def stars_for(p) -> int:
    if p["turns"] == 0:
        return 1
    pct = p["cards"] / p["turns"]
    return 3 if pct >= 0.6 else 2 if pct >= 0.4 else 1


def speak_js(text: str, auto: bool) -> str:
    return f"""
    <script>
    const SAY = {json.dumps(text).replace('</', '<\\/')};
    function say(t) {{
      try {{
        const u = new SpeechSynthesisUtterance(t || SAY);
        u.rate = 0.92; u.pitch = 1.25;
        speechSynthesis.cancel(); speechSynthesis.speak(u);
      }} catch (e) {{}}
    }}
    {"setTimeout(() => say(), 350);" if auto else ""}
    </script>"""


SPEAKER_BTN = """<button class="spk" onclick="say()">🔊</button>"""

COMPONENT_BASE_CSS = f"""
<meta name="viewport" content="width=device-width,initial-scale=1">
<style>
  html,body {{ margin:0; background:{BG}; font-family:-apple-system,system-ui,sans-serif;
              overflow:hidden; user-select:none; -webkit-user-select:none; }}
  .spk {{ position:absolute; right:6px; top:6px; font-size:32px; width:62px; height:62px;
          border:none; border-radius:50%; background:#fff; box-shadow:0 3px 8px rgba(0,0,0,.2); }}
  .confetti {{ position:fixed; top:-20px; width:10px; height:16px; border-radius:2px;
               animation: fall linear forwards; z-index:9; }}
  @keyframes fall {{ to {{ transform: translateY(120vh) rotate(720deg); }} }}
</style>
<script>
function confetti(n) {{
  const colors = ['#e53935','#fdd835','#43a047','#1e88e5','#8e24aa','#fb8c00','#ec407a'];
  for (let i = 0; i < n; i++) {{
    const d = document.createElement('div');
    d.className = 'confetti';
    d.style.left = Math.random() * 100 + 'vw';
    d.style.background = colors[i % colors.length];
    d.style.animationDuration = (1.6 + Math.random() * 1.6) + 's';
    d.style.animationDelay = (Math.random() * 0.5) + 's';
    document.body.appendChild(d);
    setTimeout(() => d.remove(), 4000);
  }}
}}
</script>"""


# ---------------------------------------------------------------- components
def turn_component(avatar: str, text: str, talk: bool, token: int):
    doc = f"""<!doctype html><html><head>{COMPONENT_BASE_CSS}
    <style>
      .wrap {{ display:flex; align-items:center; justify-content:center; gap:26px; height:230px; }}
      .av {{ font-size:124px; line-height:1; animation:bounce 1.1s ease-in-out infinite; }}
      @keyframes bounce {{ 0%,100% {{ transform:translateY(0) }} 50% {{ transform:translateY(-16px) }} }}
      .q {{ font-size:72px; animation:pulse 1s ease-in-out infinite; }}
      @keyframes pulse {{ 50% {{ transform:scale(1.2) }} }}
      .card {{ width:124px; height:176px; border-radius:16px; border:6px solid #fff;
               box-shadow:0 8px 16px rgba(0,0,0,.25);
               background:repeating-linear-gradient(45deg,#1e88e5 0 10px,#1565c0 10px 20px);
               animation:wig 1.8s ease-in-out infinite; }}
      @keyframes wig {{ 0%,100% {{ transform:rotate(-5deg) }} 50% {{ transform:rotate(5deg) }} }}
    </style></head><body>
    <div class="wrap"><div class="av">{avatar}</div><div class="q">❓</div><div class="card"></div></div>
    {SPEAKER_BTN if talk else ""}
    {speak_js(text, talk)}
    <!-- turn {token} -->
    </body></html>"""
    st.iframe(doc, height=236)


def reveal_component(card, correct: bool, avatar: str, dealer: str, text: str, talk: bool, token: int):
    if card:
        rank, suit, color = card
        col = "#d32f2f" if color == "red" else "#111"
        card_html = f"""
        <div class="scene"><div class="flip">
          <div class="face back"></div>
          <div class="face front" style="color:{col}">
            <div class="c tl">{rank}<br>{suit}{T}</div>
            <div class="big">{suit}{T}</div>
            <div class="c br">{rank}<br>{suit}{T}</div>
          </div>
        </div></div>"""
        delay = "1.05s"
    else:
        card_html, delay = "", "0.1s"

    if correct:
        result = f"""<div class="mark">✅</div>
                     <div class="move"><span class="mc"></span><span class="arrow">➜</span><span>{avatar}</span></div>
                     <div class="face2">😃</div>"""
    else:
        result = f"""<div class="mark">❌</div>
                     <div class="move"><span class="mc"></span><span class="arrow">➜</span><span>{dealer}</span></div>
                     <div class="face2">🙈</div>"""

    doc = f"""<!doctype html><html><head>{COMPONENT_BASE_CSS}
    <style>
      .wrap {{ display:flex; align-items:center; justify-content:center; gap:34px; height:270px; }}
      .scene {{ width:150px; height:214px; perspective:900px; }}
      .flip {{ position:relative; width:100%; height:100%; transform-style:preserve-3d;
               animation: flip .8s ease-in-out .25s forwards; }}
      @keyframes flip {{ to {{ transform: rotateY(180deg) scale(1.04); }} }}
      .face {{ position:absolute; inset:0; border-radius:18px; border:6px solid #fff;
               box-shadow:0 10px 20px rgba(0,0,0,.25);
               backface-visibility:hidden; -webkit-backface-visibility:hidden; }}
      .back {{ background:repeating-linear-gradient(45deg,#1e88e5 0 10px,#1565c0 10px 20px); }}
      .front {{ background:#fff; transform:rotateY(180deg); border-color:#eee; }}
      .big {{ position:absolute; inset:0; display:flex; align-items:center; justify-content:center;
              font-size:110px; }}
      .c {{ position:absolute; font-size:26px; font-weight:800; line-height:1; text-align:center; }}
      .tl {{ top:10px; left:12px; }} .br {{ bottom:10px; right:12px; transform:rotate(180deg); }}
      .res {{ display:flex; flex-direction:column; align-items:center; gap:4px; opacity:0;
              transform:scale(.2); animation: pop .55s cubic-bezier(.2,1.7,.4,1) {delay} forwards; }}
      @keyframes pop {{ to {{ opacity:1; transform:scale(1); }} }}
      .mark {{ font-size:92px; line-height:1; }}
      .face2 {{ font-size:64px; line-height:1; }}
      .move {{ display:flex; align-items:center; gap:8px; font-size:58px; }}
      .arrow {{ font-size:40px; color:#555; }}
      .mc {{ display:inline-block; width:30px; height:44px; border-radius:5px; border:3px solid #fff;
             background:linear-gradient(135deg,#42a5f5,#0d47a1); box-shadow:0 0 0 2px #0d47a1;
             animation: slide 1s ease-in-out infinite alternate; }}
      @keyframes slide {{ to {{ transform: translateX(14px); }} }}
    </style></head><body>
    <div class="wrap">{card_html}<div class="res">{result}</div></div>
    {SPEAKER_BTN if talk else ""}
    {speak_js(text, talk)}
    <script>{"setTimeout(() => confetti(90), " + ("1100" if card else "150") + ");" if correct else ""}</script>
    <!-- reveal {token} -->
    </body></html>"""
    st.iframe(doc, height=276)


def prize_component(boxes, talk: bool, token: int):
    """boxes: list of dicts(avatar, stars, emoji, say, big)"""
    items = []
    for i, b in enumerate(boxes):
        stars = "".join(
            f'<span class="st {"on" if k < b["stars"] else "off"}" style="animation-delay:{0.3 + k * 0.45}s">⭐</span>'
            for k in range(3)
        )
        size = "big" if b["big"] else "small"
        items.append(f"""
        <div class="slot {size}">
          <div class="stars">{stars}</div>
          <div class="box" data-say="{esc(b["say"])}" onclick="openBox(this)">
            <div class="rays"></div>
            <div class="prize">{b["emoji"]}</div>
            <div class="base"><div class="tag">{b["avatar"]}</div><div class="shine"></div></div>
            <div class="lid"><div class="bow">🎀</div></div>
            <div class="tap">👆</div>
          </div>
        </div>""")
    many = len(boxes) > 2
    doc = f"""<!doctype html><html><head>{COMPONENT_BASE_CSS}
    <style>
      .row {{ display:flex; justify-content:center; align-items:flex-end; flex-wrap:wrap;
              gap:{"10px" if many else "40px"}; padding-top:8px; }}
      .slot {{ display:flex; flex-direction:column; align-items:center; transform:scale({"0.8" if many else "1"}); }}
      .slot.small {{ transform:scale(.78); }}
      .stars {{ height:70px; margin-bottom:105px; }}
      .st {{ display:inline-block; font-size:56px; opacity:0; transform:scale(0);
             animation: starpop .5s cubic-bezier(.2,1.8,.4,1) forwards; }}
      .st.off {{ filter: grayscale(1); }}
      .st.off {{ animation-name: starpopoff; }}
      @keyframes starpop {{ to {{ opacity:1; transform:scale(1); }} }}
      @keyframes starpopoff {{ to {{ opacity:.2; transform:scale(.85); }} }}
      .box {{ position:relative; width:170px; height:170px; cursor:pointer; opacity:0;
              animation: drop .6s cubic-bezier(.2,1.5,.4,1) 1.7s forwards; }}
      @keyframes drop {{ from {{ opacity:0; transform:translateY(-60px) scale(.6); }}
                         to {{ opacity:1; transform:none; }} }}
      .box.ready {{ animation: wobble 1.4s ease-in-out infinite; opacity:1; }}
      @keyframes wobble {{ 0%,60%,100% {{ transform:rotate(0) }} 70% {{ transform:rotate(-6deg) }}
                           80% {{ transform:rotate(6deg) }} 90% {{ transform:rotate(-3deg) }} }}
      .base {{ position:absolute; bottom:0; left:8px; width:154px; height:116px; border-radius:12px; overflow:hidden;
               background:linear-gradient(135deg,#ff5fa8,#c2185b); box-shadow:0 10px 20px rgba(0,0,0,.25); }}
      .base::before {{ content:""; position:absolute; left:63px; top:0; width:28px; height:100%;
                       background:linear-gradient(#ffe082,#ffb300); }}
      .tag {{ position:absolute; bottom:8px; left:8px; font-size:38px; z-index:2; }}
      .shine {{ position:absolute; top:-50%; left:-80%; width:50%; height:200%; transform:rotate(25deg);
                background:linear-gradient(90deg,transparent,rgba(255,255,255,.75),transparent);
                animation: shine 2.2s ease-in-out infinite; }}
      @keyframes shine {{ 0% {{ left:-80% }} 60%,100% {{ left:150% }} }}
      .lid {{ position:absolute; top:22px; left:0; width:170px; height:42px; border-radius:10px; z-index:3;
              background:linear-gradient(135deg,#ff80bf,#d81b60); box-shadow:0 4px 8px rgba(0,0,0,.2); }}
      .lid::before {{ content:""; position:absolute; left:71px; top:0; width:28px; height:100%;
                      background:linear-gradient(#ffe082,#ffb300); }}
      .bow {{ position:absolute; top:-46px; left:50%; transform:translateX(-50%); font-size:58px; }}
      .tap {{ position:absolute; right:-28px; bottom:-14px; font-size:52px; z-index:5;
              animation: tapme 1s ease-in-out infinite; }}
      @keyframes tapme {{ 50% {{ transform: translate(-8px,-10px) scale(.9); }} }}
      .prize {{ position:absolute; left:50%; bottom:40px; font-size:110px; z-index:2;
                transform:translateX(-50%) scale(0); }}
      .rays {{ position:absolute; left:50%; top:-60px; width:300px; height:300px; margin-left:-150px;
               border-radius:50%; opacity:0; z-index:1;
               background:repeating-conic-gradient(rgba(255,214,0,.55) 0 12deg, transparent 12deg 24deg);
               -webkit-mask: radial-gradient(circle, #000 35%, transparent 70%);
                       mask: radial-gradient(circle, #000 35%, transparent 70%); }}
      .box.open {{ animation:none; opacity:1; }}
      .box.open .lid {{ animation: lidoff .8s ease-out forwards; }}
      @keyframes lidoff {{ to {{ transform: translate(90px,-200px) rotate(50deg); opacity:0; }} }}
      .box.open .prize {{ animation: rise 1s cubic-bezier(.2,1.6,.4,1) .25s forwards; }}
      @keyframes rise {{ to {{ transform: translate(-50%,-70px) scale(1.15); }} }}
      .box.open .rays {{ animation: spin 6s linear .3s infinite, fadein .5s .3s forwards; }}
      @keyframes spin {{ to {{ transform: translateY(-40px) rotate(360deg); }} }}
      @keyframes fadein {{ to {{ opacity:1; }} }}
      .box.open .tap {{ display:none; }}
    </style></head><body>
    <div class="row">{"".join(items)}</div>
    {SPEAKER_BTN if talk else ""}
    {speak_js("", False)}
    <script>
      setTimeout(() => document.querySelectorAll('.box').forEach(b => b.classList.add('ready')), 2400);
      function openBox(el) {{
        if (el.classList.contains('open')) return;
        el.classList.remove('ready'); el.classList.add('open');
        confetti(140);
        {"say(el.dataset.say);" if talk else ""}
      }}
      // speaker button repeats the first box's message
      const _first = document.querySelector('.box');
      window.say = (function(orig) {{ return function(t) {{ orig(t || (_first && _first.dataset.say)); }}; }})(say);
    </script>
    <!-- prize {token} -->
    </body></html>"""
    st.iframe(doc, height=440 if len(boxes) <= 2 else 720)


# ---------------------------------------------------------------- game logic
def default_cfg():
    return {"n": 2, "names": [""] * MAX_KIDS,
            "avatars": AVATARS[:MAX_KIDS], "talk": True}


def start_game():
    cfg = ss.cfg
    ss.players = [
        {"name": cfg["names"][i], "avatar": cfg["avatars"][i], "cards": 0, "turns": 0}
        for i in range(cfg["n"])
    ]
    ss.dealer_cards = 0
    ss.deck = new_deck()
    ss.turn = 0
    ss.cur = 0
    ss.total = cfg["n"] * (52 // cfg["n"])  # whole deck split evenly: 52, 26, 17, 13
    ss.last = None
    ss.results = None
    ss.phase = "turn"


def on_start():
    n = ss.w_n
    names = [ss.get(f"w_name{i}", "") for i in range(MAX_KIDS)]
    avatars = [ss.get(f"w_av{i}", AVATARS[i]) for i in range(MAX_KIDS)]
    if len(set(avatars[:n])) < n:
        ss.setup_error = "Each kid needs a different animal so they can find themselves."
        return
    ss.setup_error = None
    ss.cfg = {"n": n, "names": names, "avatars": avatars,
              "talk": ss.w_talk}
    start_game()


def record(correct: bool, card=None, guess=None):
    p = ss.players[ss.cur]
    p["turns"] += 1
    if correct:
        p["cards"] += 1
    else:
        ss.dealer_cards += 1
    ss.last = {"card": card, "guess": guess, "correct": correct, "player": ss.cur}
    ss.phase = "reveal"


def on_pick(color: str):
    if ss.phase != "turn":  # ignore double taps
        return
    card = ss.deck.pop()
    record(card[2] == color, card=card, guess=color)


def on_next():
    if ss.phase != "reveal":
        return
    ss.turn += 1
    if ss.turn >= ss.total:
        finish()
    else:
        ss.cur = ss.turn % len(ss.players)
        ss.phase = "turn"


def finish():
    players = ss.players
    for p in players:
        p["stars"] = stars_for(p)
    if len(players) == 1:
        winners = [0] if players[0]["cards"] >= ss.dealer_cards else []
    else:
        top = max(p["cards"] for p in players)
        winners = [i for i, p in enumerate(players) if p["cards"] == top]
    prizes = random.sample(PRIZES, k=max(1, len(winners)))
    ss.results = {
        "winners": winners,
        "prizes": {w: prizes[k] for k, w in enumerate(winners)},
        "stickers": {i: random.choice(STICKERS) for i in range(len(players))},
        "token": random.randint(0, 10**9),
    }
    ss.phase = "results"


def on_again():
    start_game()


def on_setup():
    ss.phase = "setup"


# ---------------------------------------------------------------- screens
def title():
    st.markdown('<div class="title"><span class="r">♥ Red</span> or <span class="b">Black ♠</span></div>',
                unsafe_allow_html=True)


def scoreboard(highlight=None):
    seats = []
    for i, p in enumerate(ss.players):
        cls = "seat now" if i == highlight else "seat"
        seats.append(f'<div class="{cls}"><div class="av">{p["avatar"]}</div>'
                     f'<div class="num">{p["cards"]}</div>{pile_html(p["cards"])}</div>')
    seats.append(f'<div class="seat robot"><div class="av">🤖</div>'
                 f'<div class="num">{ss.dealer_cards}</div></div>')
    st.markdown('<div class="board">' + "".join(seats) + "</div>", unsafe_allow_html=True)


def grown_up_controls():
    with st.expander("Grown-up controls"):
        c1, c2 = st.columns(2)
        c1.button("🏁 End game now", on_click=finish, width="stretch")
        c2.button("⚙️ Back to setup", on_click=on_setup, width="stretch")
        st.caption(f"Turn {ss.turn + 1} of {ss.total}. Tip: in Safari, Share ➜ Add to Home Screen "
                   "makes this open like an app.")


def setup_screen():
    cfg = ss.cfg
    # seed widget values (Streamlit forgets widget state while they're hidden)
    ss.setdefault("w_n", cfg["n"])
    ss.setdefault("w_talk", cfg["talk"])
    for i in range(MAX_KIDS):
        ss.setdefault(f"w_name{i}", cfg["names"][i])
        ss.setdefault(f"w_av{i}", cfg["avatars"][i])

    title()
    st.markdown('<div class="sub">Grown-up setup</div>', unsafe_allow_html=True)

    st.radio("How many kids?", [1, 2, 3, 4], horizontal=True, key="w_n")
    if ss.w_n == 1:
        st.caption("Playing alone: the kid tries to keep more cards than the robot.")

    for i in range(ss.w_n):
        c1, c2 = st.columns([1, 2])
        c1.selectbox(f"Kid {i + 1}", AVATARS, key=f"w_av{i}")
        c2.text_input("Name (optional, the dealer says it out loud)", key=f"w_name{i}",
                      placeholder=ANIMAL_NAMES.get(ss[f"w_av{i}"], ""))

    st.toggle("🔊 Talking dealer", key="w_talk")

    if ss.get("setup_error"):
        st.error(ss.setup_error)
    st.button("▶️  PLAY", key="start_btn", on_click=on_start, width="stretch")


def turn_screen():
    p = ss.players[ss.cur]
    scoreboard(highlight=ss.cur)
    talk = ss.cfg["talk"]
    turn_component(p["avatar"], f"{spoken_name(p)}, red or black?", talk, ss.turn)
    c1, c2 = st.columns(2, gap="medium")
    c1.button(f"♥{T} ♦{T}", key="pick_red", on_click=on_pick, args=("red",), width="stretch")
    c2.button(f"♠{T} ♣{T}", key="pick_black", on_click=on_pick, args=("black",), width="stretch")
    grown_up_controls()


def reveal_screen():
    last = ss.last
    p = ss.players[last["player"]]
    name = spoken_name(p)
    color = last["card"][2].capitalize()
    text = (f"{color}! Yay {name}, you keep the card!" if last["correct"]
            else f"{color}. Oh no! The robot keeps that one.")
    scoreboard(highlight=last["player"])
    reveal_component(last["card"], last["correct"], p["avatar"], "🤖", text,
                     ss.cfg["talk"], ss.turn)

    nxt = ss.turn + 1
    label = "🏆" if nxt >= ss.total else f"➡️ {ss.players[nxt % len(ss.players)]['avatar']}"
    st.button(label, key="next_btn", on_click=on_next, width="stretch")
    grown_up_controls()


def results_screen():
    res = ss.results
    players = ss.players
    solo = len(players) == 1
    winners = res["winners"]

    title()
    # ----- prize boxes
    boxes = []
    for w in winners:
        emoji, name = res["prizes"][w]
        p = players[w]
        boxes.append({"avatar": p["avatar"], "stars": p["stars"], "emoji": emoji, "big": True,
                      "say": f"Wow! {spoken_name(p)} won {name}!"})
    if solo and not winners:  # lost to the robot: still gets a little sticker box
        p = players[0]
        boxes.append({"avatar": p["avatar"], "stars": p["stars"], "emoji": res["stickers"][0],
                      "big": False, "say": f"Nice try {spoken_name(p)}! Here is a sticker!"})
    prize_component(boxes, ss.cfg["talk"], res["token"])

    # ----- ranking
    order = sorted(range(len(players)), key=lambda i: -players[i]["cards"])
    rows, prev, place = [], None, 0
    for pos, i in enumerate(order):
        p = players[i]
        if p["cards"] != prev:
            place, prev = pos + 1, p["cards"]
        stars = "".join(f'<span class="{"" if k < p["stars"] else "off"}">⭐</span>' for k in range(3))
        won = i in winners
        extra = res["prizes"][i][0] if won else res["stickers"][i]
        medal = MEDALS[place] if not solo else ("🥇" if won else "🙂")
        name = f'<div class="who">{esc(p["name"])}</div>' if p["name"].strip() else ""
        rows.append(f"""
        <div class="rank {"first" if won else ""}">
          <div class="medal">{medal}</div>
          <div class="av">{p["avatar"]}</div>
          <div class="grow"><div class="stars">{stars}</div>{name}{pile_html(p["cards"])}</div>
          <div class="num">{p["cards"]}</div>
          <div class="stk">{extra}</div>
        </div>""")
    if solo:
        rows.append('<div class="vs">🆚</div>')
        rows.append(f"""
        <div class="rank {"first" if not winners else ""}">
          <div class="medal">{"🥇" if not winners else "🙂"}</div>
          <div class="av">🤖</div>
          <div class="grow">{pile_html(ss.dealer_cards)}</div>
          <div class="num">{ss.dealer_cards}</div><div class="stk"></div>
        </div>""")
    st.markdown("".join(rows), unsafe_allow_html=True)

    c1, c2 = st.columns(2, gap="medium")
    c1.button("🔁", key="again_btn", on_click=on_again, width="stretch")
    c2.button("⚙️", key="setup_btn", on_click=on_setup, width="stretch")


# ---------------------------------------------------------------- router
ss.setdefault("cfg", default_cfg())
ss.setdefault("phase", "setup")

{"setup": setup_screen, "turn": turn_screen,
 "reveal": reveal_screen, "results": results_screen}[ss.phase]()
