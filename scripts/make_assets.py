"""Builds the StocklaneOS card and the languages / commit-hours panel in the night-sky style.

Reuses the sky, stars, fonts and panel from assets/card-peniko*.svg.
Usage: put language shares and commit hours in scripts/.stats.json, then python scripts/make_assets.py
"""
import json, re, pathlib

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
    body.append(f'<text x="232" y="200" class="m" font-size="13" fill="{p["accent"]}">-&gt; visit peniko.vercel.app/stocklaneos'
                f'<tspan class="blink">_</tspan></text></svg>')
    return head(suffix) + "".join(body)


def insights(suffix, st):
    p = PAL[suffix]
    langs = [(k, v) for k, v in st["langs"] if v >= 1][:6]
    hours = {int(k): v for k, v in st["hours"].items()}
    out = [f'<text x="76" y="44" class="m" font-size="13" fill="{p["accent"]}">$ top languages '
           f'<tspan fill="{p["mute"]}">--by-project</tspan></text>']
    top = langs[0][1]
    for i, (name, pct) in enumerate(langs):
        y = 74 + i * 24
        w = max(4, round(pct / top * 210))
        out.append(f'<text x="76" y="{y}" class="m" font-size="12.5" fill="{p["title"]}">{name}</text>')
        out.append(f'<rect x="170" y="{y - 11}" width="210" height="12" rx="3" fill="{p["levels"][0]}"/>')
        out.append(f'<rect x="170" y="{y - 11}" width="{w}" height="12" rx="3" fill="{p["levels"][4 if i == 0 else 3]}"/>')
        out.append(f'<text x="392" y="{y}" class="m" font-size="12" fill="{p["mute"]}">{pct:.0f}%</text>')
    peak = max(hours, key=hours.get)
    h12 = (peak % 12) or 12
    out.append(f'<text x="540" y="44" class="m" font-size="13" fill="{p["accent"]}">$ commits <tspan fill="{p["mute"]}">--by-hour</tspan></text>')
    out.append(f'<text x="924" y="44" text-anchor="end" class="m" font-size="13" fill="{p["mute"]}">peak <tspan font-weight="700" fill="{p["title"]}">{h12}{"am" if peak < 12 else "pm"}</tspan></text>')
    mx, base, bw, step = max(hours.values()), 166, 11, 16
    out.append('<g shape-rendering="crispEdges">')
    for h in range(24):
        n = hours.get(h, 0)
        ht = max(3, round(n / mx * 100)) if n else 3
        col = p["levels"][4] if h == peak else p["levels"][3] if n / mx > .5 else p["levels"][2] if n else p["levels"][0]
        tw = ""
        out.append(f'<rect x="{540 + h * step}" y="{base - ht}" width="{bw}" height="{ht}" rx="2" fill="{col}"{tw}/>')
    out.append("</g>")
    for h, lab in ((0, "12a"), (6, "6a"), (12, "12p"), (18, "6p"), (23, "11p")):
        out.append(f'<text x="{540 + h * step + 5}" y="{base + 16}" text-anchor="middle" class="m" font-size="10.5" fill="{p["mute"]}">{lab}</text>')
    out.append(f'<text x="540" y="208" class="m" font-size="10.5" fill="{p["mute"]}">{sum(hours.values())} commits across my repos, local time</text>')
    out.append("</svg>")
    return head(suffix) + "".join(out)


st = json.loads((root / "scripts" / ".stats.json").read_text())
for suf in PAL:
    (assets / f"card-stocklaneos{suf}.svg").write_text(stocklane(suf), encoding="utf8")
    (assets / f"insights{suf}.svg").write_text(insights(suf, st), encoding="utf8")
print("ok")
