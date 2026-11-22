"""Generates index.html (main edit) and compositions/siteplan-overlay.html.

All on-screen timing is derived from the Whisper word timestamps in
build/transcript.json, remapped through the VO edit list below, so graphics
land on the spoken word. Run:  python3 build/gen.py
"""
import json, os, re, html

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
T = json.load(open(os.path.join(ROOT, "build/transcript.json")))
MAP = json.load(open(os.path.join(ROOT, "assets/map/map-meta.json")))
WARP = json.load(open(os.path.join(ROOT, "assets/siteplan/warp-meta.json")))

# ---------------------------------------------------------------- VO edit
# (source in, source out). Hook first: the price line, then the original opener.
EDIT = [
    ("hook",    2.70, 6.92),   # Rumah dua tingkat ni luas, tapi harga bawah RM500,000.
    ("cantik",  0.00, 2.58),   # Cuba korang tengok desain rumah ni. Cantik kan?
    ("lokasi",  7.28, 14.30),  # Dekat Jalan Kenanga ... 30 unit rumah teres dua tingkat.
    ("spec",   14.40, 24.26),  # 4 bilik tidur, 4 bilik air ... keluarga.
    ("harga",  24.38, 29.44),  # Status freehold ... RM488,000.
    ("amen",   29.96, 37.48),  # sekolah, klinik, pasaraya ... SKVE 8 minit.
    ("pakej",  37.72, 44.05),  # pakej free ... ditanggung pemaju.
    ("siap",   44.28, 47.08),  # siap Disember 2027.
    ("cta",    47.40, 53.66),  # Kalau nak tahu lebih lanjut ...
]
GAP = 0.10
SEG = {}
t = 0.0
for name, a, b in EDIT:
    SEG[name] = dict(src=a, end=b, start=round(t, 3), dur=round(b - a, 3))
    t += (b - a) + GAP
VO_END = t - GAP
TOTAL = round(VO_END + 1.6, 2)


def o(src):
    """Map a source VO time to output time."""
    for name, a, b in EDIT:
        if a - 0.05 <= src <= b + 0.05:
            return round(SEG[name]["start"] + (src - a), 3)
    raise ValueError(src)


WORDS = []
for s in T:
    for w in s["words"]:
        WORDS.append(dict(w=w["w"].strip(), s=w["s"], e=w["e"]))


def W(token, after=0.0):
    """Output time of first word matching token at/after source time `after`."""
    for w in WORDS:
        if w["s"] >= after - 0.01 and re.sub(r"[^\w]", "", w["w"].lower()) == token.lower():
            return o(w["s"])
    raise KeyError(token)


def sc(name):
    return SEG[name]["start"], SEG[name]["start"] + SEG[name]["dur"]


# -------------------------------------------------------- captions
FIX = {"teras": "teres", "desain": "design", "Desember": "Disember"}
cap_words = []
for name, a, b in EDIT:
    if name == "hook":
        continue
    for w in WORDS:
        if a - 0.02 <= w["s"] < b:
            tok = w["w"]
            if tok.startswith(",") and cap_words:
                cap_words[-1]["w"] += tok.rstrip(".")
                continue
            tok = FIX.get(tok.strip(".,?"), tok.strip(".,?")) + ("" if tok[-1] not in ".,?" else tok[-1])
            cap_words.append(dict(w=tok, s=o(w["s"]), e=o(min(w["e"], b)), seg=name))
chunks, cur = [], []
for w in cap_words:
    if cur and (len(cur) >= 4 or cur[-1]["seg"] != w["seg"] or cur[-1]["w"][-1] in ".,?"):
        chunks.append(cur); cur = []
    cur.append(w)
chunks.append(cur)

# ------------------------------------------------------------ helpers
els, js, audio = [], [], []


def clip(html_, start, dur, cls="clip", z=1, extra=""):
    pass


def A(src, start, dur=None, vol=1.0, media_start=0.0, fade_in=0, fade_out=0, idn=None):
    d = f' data-duration="{dur:.3f}"' if dur else ""
    f = (f' data-fade-in="{fade_in}"' if fade_in else "") + (f' data-fade-out="{fade_out}"' if fade_out else "")
    i = f' id="{idn}"' if idn else f' id="a{len(audio)}"'
    audio.append(f'<audio{i} src="{src}" data-start="{start:.3f}"{d} data-media-start="{media_start:.3f}" data-volume="{vol}"{f}></audio>')


SFX_LEN = dict(whoosh=0.7, impact=1.4, pop=0.12, ding=1.6, riser=1.6, stamp=0.6, tick=0.05, sparkle=1.2)


def sfx(name, at, vol=0.6):
    A(f"assets/audio/{name}.wav", max(0, at), SFX_LEN[name], vol)


def J(line):
    js.append(line)


# ---------------------------------------------------------------- scenes
CAP_HIDE = []
s, e = sc("hook")
H = dict(rumah=W("rumah", 2.7), luas=W("luas"), bawah=W("bawah"), rm=W("rm500"))
els.append(f'''
<section id="sc-hook" class="clip scene" data-start="0" data-duration="{e+0.06:.3f}">
  <img class="fill kb" id="hook-img" src="assets/img/render-front.png" alt="">
  <div class="shade-b"></div>
  <div class="hook-stack">
    <div class="hk hk1" id="hk1">RUMAH 2 TINGKAT</div>
    <div class="hk hk2" id="hk2">LUAS</div>
    <div class="hk hk3" id="hk3">TAPI HARGA BAWAH</div>
    <div class="hk hk4" id="hk4"><span class="rm">RM</span>500K</div>
  </div>
  <div class="flash" id="hook-flash"></div>
</section>''')
J(f'tl.fromTo("#hook-img",{{scale:1.32,yPercent:4}},{{scale:1.08,yPercent:0,duration:{e:.2f},ease:"power1.out"}},0);')
J('tl.fromTo("#hook-flash",{opacity:0.9},{opacity:0,duration:0.35,ease:"power2.out"},0);')
J(f'tl.fromTo("#hk1",{{opacity:0,y:60,scale:0.8}},{{opacity:1,y:0,scale:1,duration:0.35,ease:"back.out(2)"}},{H["rumah"]:.2f});')
J(f'tl.fromTo("#hk2",{{opacity:0,scale:2.2}},{{opacity:1,scale:1,duration:0.3,ease:"power4.out"}},{H["luas"]:.2f});')
J(f'tl.fromTo("#hk3",{{opacity:0,x:-80}},{{opacity:1,x:0,duration:0.3,ease:"power3.out"}},{H["bawah"]-0.45:.2f});')
J(f'tl.fromTo("#hk4",{{opacity:0,scale:3,rotation:-8}},{{opacity:1,scale:1,rotation:-3,duration:0.28,ease:"power4.in"}},{H["rm"]-0.28:.2f});')
J(f'tl.fromTo("#sc-hook",{{x:0}},{{x:14,duration:0.05,repeat:5,yoyo:true,ease:"none"}},{H["rm"]:.2f});')
J(f'tl.to(".hook-stack",{{scale:1.06,duration:{e-H["rm"]:.2f},ease:"none"}},{H["rm"]:.2f});')
sfx("whoosh", H["rumah"] - 0.3, 0.5)
sfx("pop", H["luas"], 0.6)
sfx("whoosh", H["bawah"] - 0.55, 0.35)
sfx("impact", H["rm"] - 0.02, 0.9)

# ---- cantik
s, e = sc("cantik")
cantik = W("cantik")
els.append(f'''
<section id="sc-cantik" class="clip scene" data-start="{s-0.06:.3f}" data-duration="{e-s+0.2:.3f}">
  <img class="fill" id="cantik-img" src="assets/img/render-corner.png" alt="">
  <div class="sweep" id="cantik-sweep"></div>
  <div class="sticker" id="cantik-sticker">CANTIK KAN?</div>
</section>''')
J(f'tl.fromTo("#cantik-img",{{scale:1.25,xPercent:6}},{{scale:1.05,xPercent:-4,duration:{e-s+0.2:.2f},ease:"sine.inOut"}},{s-0.06:.2f});')
J(f'tl.fromTo("#sc-cantik",{{clipPath:"circle(0% at 50% 55%)"}},{{clipPath:"circle(85% at 50% 55%)",duration:0.45,ease:"power3.out"}},{s-0.06:.2f});')
J(f'tl.fromTo("#cantik-sweep",{{xPercent:-120}},{{xPercent:120,duration:0.9,ease:"power2.inOut"}},{cantik-0.15:.2f});')
J(f'tl.fromTo("#cantik-sticker",{{opacity:0,scale:0.3,rotation:12}},{{opacity:1,scale:1,rotation:-4,duration:0.4,ease:"back.out(2.5)"}},{cantik:.2f});')
sfx("whoosh", s - 0.3, 0.5)
sfx("sparkle", cantik, 0.45)

# ---- lokasi: realistic satellite zoom, then site plan overlay on drone
s, e = sc("lokasi")
dekat, kenanga, ada, unit = W("dekat"), W("kenanga"), W("ada", 10.0), W("unit", 12.0)
MAP_END = ada - 0.05
mid, wide, close = MAP["mid"], MAP["wide"], MAP["close"]
sx, sy = mid["poi"]["site"]
wx, wy = wide["poi"]["site"]
cx_, cy_ = close["poi"]["site"]
# layers positioned in mid(z16) pixel space
lw = dict(l=sx - wx * 4, t=sy - wy * 4, w=wide["w"] * 4, h=wide["h"] * 4)
lc = dict(l=sx - cx_ / 4, t=sy - cy_ / 4, w=close["w"] / 4, h=close["h"] / 4)
POI = {k: v for k, v in mid["poi"].items()}


def map_block(idn, extra=""):
    pins = ""
    return f'''
  <div class="map-cam" id="{idn}-cam">
    <img class="map-layer" src="assets/map/map-wide.jpg" style="left:{lw['l']:.1f}px;top:{lw['t']:.1f}px;width:{lw['w']:.0f}px;height:{lw['h']:.0f}px" alt="">
    <img class="map-layer" id="{idn}-mid" src="assets/map/map-mid.jpg" style="left:0;top:0;width:{mid['w']}px;height:{mid['h']}px" alt="">
    <img class="map-layer" id="{idn}-close" src="assets/map/map-close.jpg" style="left:{lc['l']:.1f}px;top:{lc['t']:.1f}px;width:{lc['w']:.0f}px;height:{lc['h']:.0f}px" alt="">
  </div>
  <div class="map-ui" id="{idn}-ui">{extra}</div>'''


els.append(f'''
<section id="sc-map" class="clip scene" data-start="{s-0.06:.3f}" data-duration="{MAP_END-s+0.5:.3f}">
  {map_block("m1")}
  <div class="pin" id="m1-pin" style="left:540px;top:960px"><div class="pulse"></div><div class="pulse p2"></div><svg viewBox="0 0 64 84"><path d="M32 2C16 2 4 14 4 30c0 21 28 52 28 52s28-31 28-52C60 14 48 2 32 2z" fill="#FFD23F" stroke="#1a1a1a" stroke-width="4"/><circle cx="32" cy="30" r="11" fill="#1a1a1a"/></svg></div>
  <div class="loc-card" id="m1-card"><div class="loc-k">LOKASI</div><div class="loc-v">Jalan Kenanga</div><div class="loc-s">Teluk Panglima Garang, Kuala Langat</div></div>
  <div class="map-credit" data-layout-ignore>Imej satelit: Esri, Maxar, Earthstar Geographics</div>
</section>''')
# camera: scale s in mid px space, centered on site
J(f'''(function(){{const cam=document.getElementById("m1-cam");const st={{z:Math.log2(0.16),cx:{sx},cy:{sy}}};
 const set=()=>{{const k=Math.pow(2,st.z);cam.style.transform=`translate(${{540-st.cx*k}}px,${{960-st.cy*k}}px) scale(${{k}})`;
  document.getElementById("m1-mid").style.opacity=Math.min(1,Math.max(0,(k-0.35)/0.4));
  document.getElementById("m1-close").style.opacity=Math.min(1,Math.max(0,(k-1.6)/1.2));}};
 set();tl.to(st,{{z:Math.log2(3.6),duration:{MAP_END-s:.2f},ease:"power2.inOut",onUpdate:set}},{s-0.06:.2f});}})();''')
J(f'tl.fromTo("#sc-map",{{opacity:0}},{{opacity:1,duration:0.2}},{s-0.06:.2f});')
J(f'tl.fromTo("#m1-pin",{{opacity:0,y:-160,scale:0.6}},{{opacity:1,y:0,scale:1,duration:0.45,ease:"bounce.out"}},{dekat+0.1:.2f});')
J(f'tl.fromTo("#m1-card",{{opacity:0,y:40}},{{opacity:1,y:0,duration:0.4,ease:"power3.out"}},{kenanga-0.25:.2f});')
J(f'tl.fromTo("#m1-pin .pulse",{{scale:0.2,opacity:0.9}},{{scale:2.4,opacity:0,duration:1.2,repeat:3,ease:"power1.out"}},{dekat+0.4:.2f});')
sfx("whoosh", s - 0.25, 0.4)
sfx("riser", s, 0.25)
sfx("pop", dekat + 0.45, 0.7)
sfx("pop", kenanga - 0.2, 0.5)

SP_START = MAP_END
SP_DUR = e - SP_START + 0.06
REVEAL = 3.4  # reversed drone pull-back, ends on the exact frame the plan is warped to


def siteplan_markup(prefix, start, dur):
    q = WARP["quad"]
    pts = " ".join(f"{x},{y}" for x, y in q)
    return f'''
<section id="{prefix}" class="clip scene" data-start="{start:.3f}" data-duration="{dur:.3f}">
  <div class="sp-cam" id="{prefix}-cam">
    <video class="fill" id="{prefix}-vid" src="assets/footage/drone-reveal.mp4" muted playsinline data-start="{start:.3f}" data-duration="{REVEAL:.3f}" data-media-start="0"></video>
    <img class="fill" id="{prefix}-still" src="assets/siteplan/drone-still.jpg" alt="">
    <svg class="sp-svg" viewBox="0 0 1080 1920"><polygon id="{prefix}-outline" points="{pts}" fill="rgba(255,210,63,0.10)" stroke="#FFD23F" stroke-width="6" stroke-linejoin="round" pathLength="100" stroke-dasharray="100" /></svg>
    <img class="fill sp-layer" id="{prefix}-yellow2" src="assets/siteplan/layer-yellow2.png" alt="">
    <img class="fill sp-layer" id="{prefix}-yellow1" src="assets/siteplan/layer-yellow1.png" alt="">
    <img class="fill sp-layer" id="{prefix}-purple" src="assets/siteplan/layer-purple.png" alt="">
    <img class="fill sp-layer" id="{prefix}-lapang" src="assets/siteplan/layer-lapang.png" alt="">
    <div class="sp-road" id="{prefix}-road" style="left:300px;top:1252px">JALAN KENANGA</div>
  </div>
  <div class="sp-legend" id="{prefix}-legend">
    <div class="sp-title">PELAN TAPAK</div>
    <div class="sp-row"><i style="background:#8E5BB5"></i><b>8 UNIT</b><span>22' x 97'</span></div>
    <div class="sp-row"><i style="background:#F2C94C"></i><b>22 UNIT</b><span>20' x 75'</span></div>
  </div>
  <div class="sp-badge" id="{prefix}-badge"><span class="n">30</span><span class="u">UNIT<br>SAHAJA</span></div>
</section>'''


def siteplan_anim(prefix, start, unit_t, total):
    """Returns js lines. start=section start, unit_t=when '30 unit' is said."""
    r = start + REVEAL
    L = []
    L.append(f'tl.set("#{prefix}-still",{{opacity:0}},0);tl.set("#{prefix}-still",{{opacity:1}},{r-0.04:.2f});')
    L.append(f'tl.fromTo("#{prefix}",{{clipPath:"inset(0% 0% 100% 0%)"}},{{clipPath:"inset(0% 0% 0% 0%)",duration:0.4,ease:"power3.inOut"}},{start:.2f});')
    L.append(f'tl.fromTo("#{prefix}-cam",{{scale:1}},{{scale:1.12,yPercent:-4,duration:{total-REVEAL+0.01:.2f},ease:"sine.inOut"}},{r:.2f});')
    L.append(f'tl.fromTo("#{prefix}-outline",{{strokeDashoffset:100,opacity:1}},{{strokeDashoffset:0,duration:0.9,ease:"power2.inOut"}},{r-1.4:.2f});')
    L.append(f'tl.fromTo("#{prefix}-outline",{{fillOpacity:0}},{{fillOpacity:1,duration:0.5}},{r-0.6:.2f});')
    for i, k in enumerate(["purple", "yellow1", "yellow2", "lapang"]):
        at = r - 0.95 + i * 0.28
        L.append(f'tl.fromTo("#{prefix}-{k}",{{opacity:0,clipPath:"inset(0% 100% 0% 0%)"}},{{opacity:1,clipPath:"inset(0% 0% 0% 0%)",duration:0.5,ease:"power2.out"}},{at:.2f});')
    L.append(f'tl.fromTo("#{prefix}-road",{{opacity:0,y:20}},{{opacity:1,y:0,duration:0.4}},{r-1.1:.2f});')
    L.append(f'tl.fromTo("#{prefix}-legend",{{opacity:0,y:-50}},{{opacity:1,y:0,duration:0.45,ease:"power3.out"}},{r-0.9:.2f});')
    L.append(f'tl.fromTo("#{prefix}-badge",{{opacity:0,scale:0.2,rotation:-20}},{{opacity:1,scale:1,rotation:-6,duration:0.45,ease:"back.out(2.2)"}},{unit_t-0.25:.2f});')
    return L, [(r - 1.45, "whoosh", 0.35)] + [(r - 0.95 + i * 0.28, "pop", 0.45) for i in range(4)] + [(unit_t - 0.2, "impact", 0.55)]


els.append(siteplan_markup("sp", SP_START, SP_DUR))
lines, sp_sfx = siteplan_anim("sp", SP_START, unit, SP_DUR)
js.extend(lines)
for at, n, v in sp_sfx:
    sfx(n, at, v)

# ---- spec
s, e = sc("spec")
bt, ba, sz, kel = W("4", 16.0), W("4", 17.5), W("2", 20.0), W("memang")
els.append(f'''
<section id="sc-spec" class="clip scene dark" data-start="{s-0.06:.3f}" data-duration="{kel-s+0.25:.3f}">
  <video class="fill blurbg" src="assets/footage/drone-orbit-c.mp4" muted playsinline data-start="{s-0.06:.3f}" data-duration="{kel-s+0.25:.3f}" data-media-start="0"></video>
  <div class="spec-head" id="spec-head">YANG MENARIK</div>
  <div class="plan-card" id="plan-card"><img src="assets/img/plan-20x75.jpg" alt=""><div class="plan-tag">PELAN LANTAI</div></div>
  <div class="chips">
    <div class="chip" id="chip1"><svg viewBox="0 0 48 48"><path d="M4 34V14M4 26h40v8M44 34v-8a6 6 0 0 0-6-6H20v6" fill="none" stroke="currentColor" stroke-width="4" stroke-linecap="round" stroke-linejoin="round"/><circle cx="12" cy="21" r="4" fill="currentColor"/></svg><b>4</b><span>BILIK<br>TIDUR</span></div>
    <div class="chip" id="chip2"><svg viewBox="0 0 48 48"><path d="M6 24h36v6a10 10 0 0 1-10 10H16A10 10 0 0 1 6 30zM12 24V10a4 4 0 0 1 8 0M14 40l-2 4M34 40l2 4" fill="none" stroke="currentColor" stroke-width="4" stroke-linecap="round" stroke-linejoin="round"/></svg><b>4</b><span>BILIK<br>AIR</span></div>
  </div>
  <div class="bigstat" id="bigstat"><div class="bs-k">SAIZ BINAAN LEBIH</div><div class="bs-v"><span id="sqft">0</span><small>kps</small></div></div>
</section>''')
J(f'tl.fromTo("#sc-spec",{{opacity:0,scale:1.08}},{{opacity:1,scale:1,duration:0.3,ease:"power2.out"}},{s-0.06:.2f});')
J(f'tl.fromTo("#spec-head",{{opacity:0,y:-30}},{{opacity:1,y:0,duration:0.35}},{s:.2f});')
J(f'tl.fromTo("#plan-card",{{opacity:0,y:120,rotation:4}},{{opacity:1,y:0,rotation:-1.5,duration:0.6,ease:"power3.out"}},{s+0.25:.2f});')
J(f'tl.fromTo("#plan-card img",{{scale:1}},{{scale:1.12,duration:{kel-s:.2f},ease:"none"}},{s+0.25:.2f});')
J(f'tl.fromTo("#chip1",{{opacity:0,x:-200}},{{opacity:1,x:0,duration:0.4,ease:"back.out(1.6)"}},{bt-0.1:.2f});')
J(f'tl.fromTo("#chip2",{{opacity:0,x:200}},{{opacity:1,x:0,duration:0.4,ease:"back.out(1.6)"}},{ba-0.1:.2f});')
J(f'tl.fromTo("#bigstat",{{opacity:0,scale:0.6}},{{opacity:1,scale:1,duration:0.4,ease:"back.out(2)"}},{sz-0.15:.2f});')
J(f'(function(){{const o={{v:0}};const el=document.getElementById("sqft");tl.fromTo(o,{{v:0}},{{v:2300,duration:1.0,ease:"power2.out",onUpdate:()=>{{el.textContent=Math.round(o.v).toLocaleString("en-US")+"+";}}}},{sz:.2f});}})();')
sfx("whoosh", s - 0.3, 0.4)
sfx("pop", bt, 0.6); sfx("pop", ba, 0.6)
for i in range(10):
    sfx("tick", sz + i * 0.09, 0.25)
sfx("ding", sz + 1.0, 0.35)

# keluarga: render close-up on the family
els.append(f'''
<section id="sc-fam" class="clip scene" data-start="{kel-0.05:.3f}" data-duration="{e-kel+0.2:.3f}">
  <img class="fill" id="fam-img" src="assets/img/render-front.png" alt="">
  <div class="sticker green" id="fam-sticker">SELESA UNTUK KELUARGA</div>
</section>''')
J(f'tl.fromTo("#fam-img",{{scale:1.9,xPercent:22,yPercent:-26}},{{scale:1.55,xPercent:16,yPercent:-20,duration:{e-kel+0.2:.2f},ease:"sine.out"}},{kel-0.05:.2f});')
J(f'tl.fromTo("#sc-fam",{{opacity:0}},{{opacity:1,duration:0.25}},{kel-0.05:.2f});')
J(f'tl.fromTo("#fam-sticker",{{opacity:0,y:40}},{{opacity:1,y:0,duration:0.4,ease:"back.out(2)"}},{kel+0.5:.2f});')
sfx("whoosh", kel - 0.3, 0.35)

# ---- harga / freehold
s, e = sc("harga")
fh, rm = W("freehold"), W("rm488")
els.append(f'''
<section id="sc-harga" class="clip scene" data-start="{s-0.06:.3f}" data-duration="{e-s+0.2:.3f}">
  <video class="fill" src="assets/footage/drone-orbit-a.mp4" muted playsinline data-start="{s-0.06:.3f}" data-duration="{e-s+0.2:.3f}" data-media-start="0.5"></video>
  <div class="shade-c"></div>
  <div class="stamp" id="stamp">FREEHOLD</div>
  <div class="price" id="price"><div class="p-k">HARGA BERMULA</div><div class="p-v">RM<span id="pv">0</span></div></div>
</section>''')
J(f'tl.fromTo("#sc-harga",{{opacity:0}},{{opacity:1,duration:0.25}},{s-0.06:.2f});')
J(f'tl.fromTo("#stamp",{{opacity:0,scale:3.2,rotation:-30}},{{opacity:1,scale:1,rotation:-10,duration:0.25,ease:"power4.in"}},{fh-0.2:.2f});')
J(f'tl.fromTo("#price",{{opacity:0,y:80}},{{opacity:1,y:0,duration:0.4,ease:"power3.out"}},{rm-0.5:.2f});')
J(f'(function(){{const o={{v:0}};const el=document.getElementById("pv");tl.fromTo(o,{{v:300000}},{{v:488000,duration:1.1,ease:"power3.out",onUpdate:()=>{{el.textContent=(Math.round(o.v/1000)*1000).toLocaleString("en-US");}}}},{rm-0.3:.2f});}})();')
J(f'tl.fromTo("#price .p-v",{{scale:1}},{{scale:1.12,duration:0.15,yoyo:true,repeat:1}},{rm+0.8:.2f});')
sfx("whoosh", s - 0.3, 0.35)
sfx("stamp", fh + 0.04, 0.9)
for i in range(11):
    sfx("tick", rm - 0.3 + i * 0.1, 0.22)
sfx("ding", rm + 0.8, 0.5)

# ---- amenities map
s, e = sc("amen")
sek, kli, pas, skve = W("sekolah"), W("klinik"), W("pasaraya"), W("skve")
lok = W("lokasi")
pois = [("sekolah", sek, "SEKOLAH", "SMK Telok Panglima Garang",
         '<path d="M24 6 4 16l20 10 20-10zM10 19v10c0 4 6 8 14 8s14-4 14-8V19" fill="none" stroke="currentColor" stroke-width="4" stroke-linejoin="round"/>'),
        ("klinik", kli, "KLINIK", "Klinik Kesihatan Kebun Baru",
         '<path d="M18 6h12v12h12v12H30v12H18V30H6V18h12z" fill="currentColor"/>'),
        ("pasaraya", pas, "PASARAYA", "Lotus's & Econsave Jenjarom",
         '<path d="M4 8h6l5 22h22l5-16H13" fill="none" stroke="currentColor" stroke-width="4" stroke-linejoin="round" stroke-linecap="round"/><circle cx="18" cy="38" r="3.5" fill="currentColor"/><circle cx="34" cy="38" r="3.5" fill="currentColor"/>')]
pins_html = ""
for k, at, title, sub, icon in pois:
    pins_html += f'<div class="poi{ {"pasaraya":" left","sekolah":" below"}.get(k,"") }" id="poi-{k}" data-x="{POI[k][0]:.1f}" data-y="{POI[k][1]:.1f}"><div class="poi-dot"><svg viewBox="0 0 48 48">{icon}</svg></div><div class="poi-label"><b>{title}</b><span>{sub}</span></div></div>'
pins_html += f'<div class="poi skve" id="poi-tol" data-x="{POI["tol"][0]:.1f}" data-y="{POI["tol"][1]:.1f}"><div class="poi-dot"><b>E26</b></div><div class="poi-label"><b>SKVE</b><span>Tol Teluk Panglima Garang</span></div></div>'
pins_html += f'<div class="poi site" id="poi-site" data-x="{POI["site"][0]:.1f}" data-y="{POI["site"][1]:.1f}"><div class="pin small"><svg viewBox="0 0 64 84"><path d="M32 2C16 2 4 14 4 30c0 21 28 52 28 52s28-31 28-52C60 14 48 2 32 2z" fill="#FFD23F" stroke="#1a1a1a" stroke-width="4"/><circle cx="32" cy="30" r="11" fill="#1a1a1a"/></svg></div></div>'
tx, ty = POI["tol"]
svgline = f'<svg class="route" id="route" viewBox="0 0 {mid["w"]} {mid["h"]}" style="width:{mid["w"]}px;height:{mid["h"]}px"><path id="route-path" d="M{sx:.0f},{sy:.0f} Q{(sx+tx)/2+140:.0f},{(sy+ty)/2-40:.0f} {tx:.0f},{ty:.0f}" fill="none" stroke="#FFD23F" stroke-width="9" stroke-linecap="round" stroke-dasharray="1 0" pathLength="100"/></svg>'
els.append(f'''
<section id="sc-amen" class="clip scene" data-start="{s-0.06:.3f}" data-duration="{e-s+0.18:.3f}">
  <div class="map-cam" id="m2-cam">
    <img class="map-layer" src="assets/map/map-wide.jpg" style="left:{lw['l']:.1f}px;top:{lw['t']:.1f}px;width:{lw['w']:.0f}px;height:{lw['h']:.0f}px" alt="">
    <img class="map-layer" src="assets/map/map-mid.jpg" style="left:0;top:0;width:{mid['w']}px;height:{mid['h']}px" alt="">
    {svgline}
  </div>
  <div class="poi-layer" id="poi-layer">{pins_html}</div>
  <div class="time-card" id="time-card"><div class="tc-v">±8</div><div class="tc-k">MINIT<br>KE SKVE</div></div>
  <div class="map-credit" data-layout-ignore>Imej satelit: Esri, Maxar, Earthstar Geographics</div>
</section>''')
# camera keyframes in mid-pixel space
amid_cx = (POI["sekolah"][0] + POI["site"][0]) / 2 - 90
J(f'''(function(){{const cam=document.getElementById("m2-cam");const st={{z:Math.log2(2.4),cx:{sx},cy:{sy}}};
 const pois=[...document.querySelectorAll("#poi-layer .poi")];
 const set=()=>{{const k=Math.pow(2,st.z);const ox=540-st.cx*k,oy=960-st.cy*k;cam.style.transform=`translate(${{ox}}px,${{oy}}px) scale(${{k}})`;
  for(const p of pois){{p.style.left=(ox+parseFloat(p.dataset.x)*k)+"px";p.style.top=(oy+parseFloat(p.dataset.y)*k)+"px";}}}};
 set();
 tl.to(st,{{z:Math.log2(1.05),cx:{amid_cx:.0f},cy:{(POI["sekolah"][1]+POI["site"][1])/2+60:.0f},duration:{sek-s+0.3:.2f},ease:"power2.inOut",onUpdate:set}},{s-0.06:.2f});
 tl.to(st,{{z:Math.log2(0.5),cx:{(POI["sekolah"][0]+POI["pasaraya"][0])/2:.0f},cy:{POI["klinik"][1]+(960-280)/0.5:.0f},duration:{pas-sek-0.25:.2f},ease:"power2.inOut",onUpdate:set}},{sek+0.3:.2f});
 tl.to(st,{{z:Math.log2(1.6),cx:{(sx+tx)/2:.0f},cy:{(sy+ty)/2+60:.0f},duration:{e-skve+0.3:.2f},ease:"power2.inOut",onUpdate:set}},{skve-0.1:.2f});
}})();''')
J(f'tl.fromTo("#sc-amen",{{opacity:0}},{{opacity:1,duration:0.3}},{s-0.06:.2f});')
J(f'tl.fromTo("#poi-site",{{opacity:0,y:-80}},{{opacity:1,y:0,duration:0.4,ease:"bounce.out"}},{lok:.2f});')
for k, at, *_ in pois:
    J(f'tl.fromTo("#poi-{k} .poi-dot",{{scale:0}},{{scale:1,duration:0.35,ease:"back.out(3)"}},{at-0.05:.2f});')
    J(f'tl.fromTo("#poi-{k} .poi-label",{{opacity:0,x:-20}},{{opacity:1,x:0,duration:0.3}},{at+0.1:.2f});')
    sfx("pop", at, 0.6)
J(f'tl.fromTo("#route-path",{{strokeDasharray:"0 100"}},{{strokeDasharray:"100 0",duration:0.8,ease:"power2.inOut"}},{skve-0.25:.2f});')
J(f'tl.fromTo("#poi-tol .poi-dot",{{scale:0}},{{scale:1,duration:0.35,ease:"back.out(3)"}},{skve+0.2:.2f});')
J(f'tl.fromTo("#poi-tol .poi-label",{{opacity:0,x:-20}},{{opacity:1,x:0,duration:0.3}},{skve+0.3:.2f});')
J(f'tl.fromTo("#time-card",{{opacity:0,y:60}},{{opacity:1,y:0,duration:0.4,ease:"back.out(2)"}},{W("8",36.5)-0.15:.2f});')
sfx("whoosh", s - 0.3, 0.4)
sfx("whoosh", skve - 0.25, 0.35)
sfx("pop", skve + 0.2, 0.6)
sfx("ding", W("8", 36.5), 0.35)

# ---- pakej
s, e = sc("pakej")
pm, guam, duty, tang = W("paling"), W("guaman"), W("duty"), W("ditanggung")
els.append(f'''
<section id="sc-pakej" class="clip scene" data-start="{s-0.06:.3f}" data-duration="{e-s+0.2:.3f}">
  <video class="fill" src="assets/footage/drone-orbit-b.mp4" muted playsinline data-start="{s-0.06:.3f}" data-duration="{e-s+0.2:.3f}" data-media-start="0"></video>
  <div class="shade-c"></div>
  <div class="pk-card" id="pk-card">
    <div class="pk-head" id="pk-head">PAKEJ <em>PERCUMA</em></div>
    <div class="pk-row" id="pk1"><i>&#10003;</i>Kos guaman</div>
    <div class="pk-row" id="pk2"><i>&#10003;</i>Duti setem</div>
  </div>
  <div class="stamp green" id="pk-stamp">DITANGGUNG PEMAJU</div>
</section>''')
J(f'tl.fromTo("#sc-pakej",{{opacity:0}},{{opacity:1,duration:0.25}},{s-0.06:.2f});')
J(f'tl.fromTo("#pk-card",{{opacity:0,scale:0.7}},{{opacity:1,scale:1,duration:0.45,ease:"back.out(1.8)"}},{pm+0.1:.2f});')
J(f'tl.fromTo("#pk1",{{opacity:0,x:-80}},{{opacity:1,x:0,duration:0.35,ease:"power3.out"}},{guam-0.4:.2f});')
J(f'tl.fromTo("#pk2",{{opacity:0,x:-80}},{{opacity:1,x:0,duration:0.35,ease:"power3.out"}},{duty-0.1:.2f});')
J(f'tl.fromTo("#pk-stamp",{{opacity:0,scale:3,rotation:20}},{{opacity:1,scale:1,rotation:-6,duration:0.25,ease:"power4.in"}},{tang-0.1:.2f});')
sfx("riser", pm - 1.2, 0.3)
sfx("impact", pm + 0.1, 0.5)
sfx("pop", guam - 0.35, 0.6); sfx("pop", duty - 0.05, 0.6)
sfx("stamp", tang + 0.15, 0.9)

# ---- siap
s, e = sc("siap")
dis = W("desember")
els.append(f'''
<section id="sc-siap" class="clip scene" data-start="{s-0.06:.3f}" data-duration="{e-s+0.2:.3f}">
  <video class="fill" src="assets/footage/drone-forward.mp4" muted playsinline data-start="{s-0.06:.3f}" data-duration="{e-s+0.2:.3f}" data-media-start="0"></video>
  <div class="shade-c"></div>
  <div class="cal" id="cal"><div class="cal-top">DIJANGKA SIAP</div><div class="cal-m" id="cal-m">DIS</div><div class="cal-y" id="cal-y">2027</div></div>
</section>''')
J(f'tl.fromTo("#sc-siap",{{clipPath:"inset(50% 0% 50% 0%)"}},{{clipPath:"inset(0% 0% 0% 0%)",duration:0.4,ease:"power3.inOut"}},{s-0.06:.2f});')
J(f'tl.fromTo("#cal",{{opacity:0,rotationX:-90,y:60}},{{opacity:1,rotationX:0,y:0,duration:0.5,ease:"back.out(1.6)"}},{dis-0.55:.2f});')
J(f'tl.fromTo("#cal-y",{{opacity:0,y:30}},{{opacity:1,y:0,duration:0.3}},{dis+0.4:.2f});')
sfx("whoosh", s - 0.3, 0.4)
sfx("pop", dis - 0.4, 0.5)
sfx("ding", dis + 0.4, 0.35)

# ---- cta
s, e = sc("cta")
lanjut, mana = W("kalau", 47.0), W("mana", 50.5)
els.append(f'''
<section id="sc-cta" class="clip scene" data-start="{s-0.06:.3f}" data-duration="{TOTAL-s+0.06:.3f}">
  <img class="fill" id="cta-img" src="assets/img/render-corner.png" alt="">
  <div class="shade-t"></div>
  <div class="cta-top" id="cta-top">NAK TAHU<br><em>LEBIH LANJUT?</em></div>
  <div class="cta-recap" id="cta-recap">
    <div><b>4+4</b><span>Bilik tidur &amp; air</span></div>
    <div><b>2,300+</b><span>Kaki persegi</span></div>
    <div><b>RM488K</b><span>Harga bermula</span></div>
  </div>
  <div class="cta-btn" id="cta-btn">HUBUNGI SAYA SEKARANG</div>
</section>''')
J(f'tl.fromTo("#sc-cta",{{opacity:0}},{{opacity:1,duration:0.35}},{s-0.06:.2f});')
J(f'tl.fromTo("#cta-img",{{scale:1.05}},{{scale:1.22,duration:{TOTAL-s:.2f},ease:"none"}},{s-0.06:.2f});')
J(f'tl.fromTo("#cta-top",{{opacity:0,y:-40}},{{opacity:1,y:0,duration:0.45,ease:"power3.out"}},{lanjut+0.1:.2f});')
J(f'tl.fromTo("#cta-recap > div",{{opacity:0,y:40}},{{opacity:1,y:0,duration:0.35,stagger:0.15,ease:"back.out(1.8)"}},{lanjut+0.9:.2f});')
J(f'tl.fromTo("#cta-btn",{{opacity:0,scale:0.6}},{{opacity:1,scale:1,duration:0.4,ease:"back.out(2)"}},{mana:.2f});')
J(f'tl.to("#cta-btn",{{scale:1.06,duration:0.45,yoyo:true,repeat:5,ease:"sine.inOut"}},{mana+0.5:.2f});')
J(f'tl.to("#sc-cta",{{opacity:0,duration:0.6}},{TOTAL-0.6:.2f});')
sfx("whoosh", s - 0.3, 0.4)
for i in range(3):
    sfx("pop", lanjut + 0.9 + i * 0.15, 0.4)
sfx("sparkle", mana, 0.4)

# -------------------------------------------------------- captions markup
cap = ['<div id="captions">']
for i, ch in enumerate(chunks):
    st_ = ch[0]["s"]
    nxt = chunks[i + 1][0]["s"] if i + 1 < len(chunks) else ch[-1]["e"] + 0.4
    en = min(nxt, ch[-1]["e"] + 0.5)
    spans = " ".join(f'<span id="cw{i}_{j}">{html.escape(w["w"])}</span>' for j, w in enumerate(ch))
    cap.append(f'<div class="cap clip" id="cap{i}" data-start="{st_:.3f}" data-duration="{en-st_:.3f}">{spans}</div>')
    J(f'tl.fromTo("#cap{i}",{{scale:0.85,opacity:0}},{{scale:1,opacity:1,duration:0.12,ease:"back.out(2)"}},{st_:.2f});')
    for j, w in enumerate(ch):
        J(f'tl.set("#cw{i}_{j}",{{color:"#FFD23F"}},{w["s"]:.2f});')
cap.append("</div>")

# ------------------------------------------------------------ audio beds
for name, a, b in EDIT:
    sg = SEG[name]
    A("assets/audio/vo.mp3", sg["start"], sg["dur"], 1.0, a, fade_in=0.02, fade_out=0.04, idn=f"vo-{name}")
A("assets/audio/music.wav", 0, TOTAL, 0.16, 0, fade_in=0.3, fade_out=1.5, idn="music")

CSS = open(os.path.join(ROOT, "build/style.css")).read()


def hoist_videos(body, scripts):
    """Videos may not sit inside a timed element: lift each one out to sit just
    before its section, and let the section's entrance tween drive it too."""
    out = []
    for part in re.split(r"(?=<section )", body):
        m = re.match(r'<section id="([^"]+)"', part)
        vids = re.findall(r"\s*<video [^>]*></video>", part)
        if m and vids:
            sid = m.group(1)
            for k, v in enumerate(vids):
                part = part.replace(v, "")
                vid = f"v-{sid}-{k}"
                v2 = v.strip().replace("<video ", f'<video id="{vid}" ', 1) if ' id="' not in v else v.strip()
                v2 = v2.replace('class="', 'class="clip ', 1)
                vid = re.search(r'id="([^"]+)"', v2).group(1)
                out.append(v2 + "\n")
                scripts = scripts.replace(f'tl.fromTo("#{sid}",', f'tl.fromTo(["#{sid}","#{vid}"],', 1)
        out.append(part)
    return "".join(out), scripts


def page(body, scripts, total, comp="main"):
    body, scripts = hoist_videos(body, scripts)
    return f'''<!doctype html>
<html lang="ms" data-resolution="portrait">
<head>
<meta charset="UTF-8" />
<meta name="viewport" content="width=1080, height=1920" />
<script src="assets/lib/gsap.min.js"></script>
<style>
{CSS}
</style>
</head>
<body>
<div id="root" data-composition-id="{comp}" data-start="0" data-duration="{total:.2f}" data-width="1080" data-height="1920">
{body}
</div>
<script>
window.__timelines = window.__timelines || {{}};
const tl = gsap.timeline({{ paused: true }});
{scripts}
window.__timelines["{comp}"] = tl;
tl.seek(0);
</script>
</body>
</html>
'''


body = "\n".join(els) + "\n" + "\n".join(cap) + "\n" + "\n".join(audio)
open(os.path.join(ROOT, "index.html"), "w").write(page(body, "\n".join(js), TOTAL))

# ---------------------------------------------- standalone site-plan overlay clip
els, js, audio = [], [], []
SPT = 7.0
els.append(siteplan_markup("sp", 0, SPT))
lines, sp_sfx = siteplan_anim("sp", 0, 4.6, SPT)
js.extend(lines)
for at, n, v in sp_sfx:
    sfx(n, at, v)
A("assets/audio/music.wav", 0, SPT, 0.2, 8.0, fade_in=0.2, fade_out=0.8, idn="music")
js.append(f'tl.to("#sp",{{opacity:0,duration:0.4}},{SPT-0.4:.2f});')
open(os.path.join(ROOT, "..", "siteplan-overlay", "index.html"), "w").write(
    page("\n".join(els) + "\n" + "\n".join(audio), "\n".join(js), SPT, "siteplan"))

print("TOTAL", TOTAL)
for k, v in SEG.items():
    print(f"{k:7} {v['start']:6.2f} -> {v['start']+v['dur']:6.2f}")
