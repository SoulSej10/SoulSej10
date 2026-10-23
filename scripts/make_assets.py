"""Builds the StocklaneOS card and the contribution graph in the night-sky style.

Reuses the sky, stars, fonts and panel from assets/card-peniko*.svg.
Usage: gh api graphql -f query='...' > scripts/.calendar.json && python scripts/make_assets.py
"""
import json, re, pathlib
from datetime import date

root = pathlib.Path(__file__).resolve().parent.parent
assets = root / "assets"

PAL = {
    "": dict(title="#F0F6FC", body="#C9D1D9", mute="#8B949E", accent="#7EE2B8", star="#FFF4C8",
             base="peniko", levels=["#161B22", "#0E4429", "#00753A", "#26A641", "#7EE2B8"],
             box="#7EE2B8", crate="#2F8F72", crate2="#1F6B55", tape="#F2CC60"),
    "-light": dict(title="#0B2545", body="#1F3B5C", mute="#4A6A8A", accent="#0B7A55", star="#FFFFFF",
                   base="peniko", levels=["#CFE3F5", "#9BE9A8", "#40C463", "#1E9E4A", "#0B7A55"],
                   box="#0B7A55", crate="#1E9E7A", crate2="#0B7A55", tape="#B7700A"),
}


def head(suffix):
    s = (assets / f"card-peniko{suffix}.svg").read_text(encoding="utf8")
    m = re.search(r'<rect x="40" y="12"[^>]*/>', s)
    return s[: m.end()]


def px(x, y, c, n=7):
    return f'<rect x="{x}" y="{y}" width="{n}" height="{n}" fill="{c}"/>'


def crate(p):
    # 14x12 pixel crate with a strap and a price tag
    rows = [
        "..############..",
        ".#aaaaaaaaaaaa#.",
        ".#abbbbbbbbbba#.",
        ".#abttbbbbbbba#.",
        ".#abttbbbbbbba#.",
        ".#abbbbbbbbbba#.",
        ".#aaaaaaaaaaaa#.",
        ".#abbbbbbbbbba#.",
        ".#abbbbbbbbbba#.",
        ".#abbbbbbbbbba#.",
        ".#aaaaaaaaaaaa#.",
        "..############..",
    ]
    cmap = {"#": p["crate2"], "a": p["crate"], "b": p["crate2"], "t": p["tape"]}
    out = []
    for r, row in enumerate(rows):
        for c, ch in enumerate(row):
            if ch in cmap:
                out.append(px(120 + c * 7, 78 + r * 7, cmap[ch]))
    return "".join(out)


def stocklane(suffix):
    p = PAL[suffix]
    feats = [("live stock", "levels"), ("built-in POS", "checkout"), ("alerts", "low stock")]
    xs = [250, 440, 660]
    body = [
        f'<circle cx="162" cy="115" r="70" fill="url(#glow)" opacity=".28" class="pulse"/>',
        f'<g class="bob"><g shape-rendering="crispEdges">{crate(p)}</g></g>',
        f'<text x="232" y="104" class="m" font-weight="700" font-size="34" fill="{p["title"]}">StocklaneOS</text>',
        f'<text x="232" y="136" class="m" font-size="16" fill="{p["body"]}">inventory + POS for small stores</text>',
    ]
    for x, (a, b) in zip(xs, feats):
        body.append(f'<g shape-rendering="crispEdges">{px(x - 14, 163, p["box"], 8)}</g>')
        body.append(f'<text x="{x}" y="171" class="m" font-size="13.5" fill="{p["title"]}">{a} '
                    f'<tspan fill="{p["mute"]}">- {b}</tspan></text>')
    body.append(f'<text x="232" y="200" class="m" font-size="13" fill="{p["accent"]}">$ stack '
                f'<tspan fill="{p["mute"]}">react . typescript . .net 10 . postgresql</tspan>'
                f'<tspan class="blink">_</tspan></text></svg>')
    return head(suffix) + "".join(body)


def graph(suffix, cal):
    p = PAL[suffix]
    weeks = cal["weeks"]
    counts = [d["contributionCount"] for w in weeks for d in w["contributionDays"]]
    top = max(counts)
    def level(n):
        if n == 0: return 0
        q = n / top
        return 1 if q <= .25 else 2 if q <= .5 else 3 if q <= .75 else 4
    cell, gap = 13, 3
    x0, y0 = 76, 70
    out = [
        f'<text x="76" y="44" class="m" font-size="13" fill="{p["accent"]}">$ git log --since="1 year ago" '
        f'<tspan fill="{p["mute"]}">--graph</tspan></text>',
        f'<text x="924" y="44" text-anchor="end" class="m" font-weight="700" font-size="13" fill="{p["title"]}">'
        f'{cal["totalContributions"]} <tspan font-weight="400" fill="{p["mute"]}">contributions</tspan></text>',
        '<g shape-rendering="crispEdges">',
    ]
    last_month = None
    months = []
    for wi, w in enumerate(weeks):
        for d in w["contributionDays"]:
            y = y0 + d["weekday"] * (cell + gap)
            x = x0 + wi * (cell + gap)
            lv = level(d["contributionCount"])
            tw = ' class="tw" style="animation-delay:%.1fs"' % ((wi * 7 + d["weekday"]) % 13 * 0.3) if lv == 4 else ""
            out.append(f'<rect x="{x}" y="{y}" width="{cell}" height="{cell}" rx="2" fill="{p["levels"][lv]}"{tw}/>')
        m = date.fromisoformat(w["contributionDays"][0]["date"]).strftime("%b")
        if m != last_month and wi < len(weeks) - 2:
            months.append((x0 + wi * (cell + gap), m))
        last_month = m
    out.append("</g>")
    for x, m in months:
        out.append(f'<text x="{x}" y="{y0 + 7 * (cell + gap) + 14}" class="m" font-size="10.5" fill="{p["mute"]}">{m.lower()}</text>')
    lx = 640
    out.append(f'<text x="{lx - 8}" y="44" text-anchor="end" class="m" font-size="10.5" fill="{p["mute"]}">quiet</text>')
    for i, c in enumerate(p["levels"]):
        out.append(f'<rect x="{lx + i * 16}" y="33" width="12" height="12" rx="2" fill="{c}"/>')
    out.append(f'<text x="{lx + 5 * 16 + 4}" y="44" class="m" font-size="10.5" fill="{p["mute"]}">busy</text>')
    out.append("</svg>")
    return head(suffix) + "".join(out)


cal = json.loads((root / "scripts" / ".calendar.json").read_text())["data"]["user"]["contributionsCollection"]["contributionCalendar"]
for suf in PAL:
    (assets / f"card-stocklaneos{suf}.svg").write_text(stocklane(suf), encoding="utf8")
    (assets / f"graph-contributions{suf}.svg").write_text(graph(suf, cal), encoding="utf8")
print("ok")
