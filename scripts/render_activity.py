#!/usr/bin/env python3
"""Render the three pixel-themed GitHub Activity cards (428px wide, same look as the rest).

    cards/activity-overview.svg stars / repos / commits / PRs + top languages
    cards/activity-streak.svg   contributions, current streak, longest streak
    cards/activity-graph.svg    12-month contribution grid with a sweeping scan line

Modes
  live      (default when GH_TOKEN / GITHUB_TOKEN is set) reads the GitHub GraphQL API
            for the user and the orgs listed in ORGS. This is what the workflow runs daily.
  snapshot  (no token, or --snapshot) uses the numbers from ALL-REPOS.md (2026-11-20).
            Stars, repos, commits and languages are real; PRs / issues / followers and
            the contribution calendar are unknown offline, so those cards show "-" and
            a "waiting for first workflow run" state instead of invented numbers.
  --fixture FILE.json   render already-normalised data (used for previews/tests).

Usage:  python scripts/render_activity.py [--snapshot] [--fixture data.json]
Env:    GH_TOKEN | GITHUB_TOKEN   token (a PAT with read:user also counts private contributions)
        GH_LOGIN (default truepushkar)    GH_ORGS (comma list, default nullstacks)
"""
import datetime as dt
import json
import os
import sys
import urllib.request

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import render_cards as rc  # noqa: E402  (shared fonts, CSS, helpers)

LOGIN = os.environ.get("GH_LOGIN", "truepushkar")
ORGS = [o for o in os.environ.get("GH_ORGS", "nullstacks").split(",") if o]
LANG_CAP = 1_500_000  # bytes per language per repo, so data-heavy repos can't drown out the rest
W = rc.WIDE

# ---- snapshot data (from ALL-REPOS.md, 2026-11-20) ---------------------------------------------
SNAPSHOT = dict(
    mode="snapshot", asof="2026-11-20",
    stars=64, repos=28, commits=233, prs=None, issues=None, followers=None,
    langs=[("JavaScript", 8), ("Python", 7), ("HTML", 6), ("TypeScript", 4),
           ("PowerShell", 1), ("Dockerfile", 1), ("Markdown", 1)],
    lang_note="BY PRIMARY LANGUAGE, REPO COUNT",
    total=None, current=None, longest=None, weeks=None,
)


# ---- GitHub API (live mode) ---------------------------------------------------------------------
REPO_FIELDS = """nodes{ name stargazerCount
  defaultBranchRef{ target{ ... on Commit{ history{ totalCount } } } }
  languages(first:10, orderBy:{field:SIZE, direction:DESC}){ edges{ size node{ name } } } }"""


def build_query(orgs):
    org_parts = "\n".join(
        f'o{i}: organization(login:"{o}"){{ repositories(first:100, privacy:PUBLIC, isFork:false){{ totalCount {REPO_FIELDS} }} }}'
        for i, o in enumerate(orgs))
    return f"""query($login:String!){{
  user(login:$login){{
    followers{{ totalCount }}
    contributionsCollection{{
      totalPullRequestContributions totalIssueContributions
      contributionCalendar{{ totalContributions weeks{{ contributionDays{{ date contributionCount }} }} }}
    }}
    repositories(first:100, ownerAffiliations:OWNER, privacy:PUBLIC, isFork:false){{ totalCount {REPO_FIELDS} }}
  }}
  {org_parts}
}}"""


def gql(query, variables, token):
    req = urllib.request.Request(
        "https://api.github.com/graphql",
        data=json.dumps({"query": query, "variables": variables}).encode(),
        headers={"Authorization": f"bearer {token}", "Content-Type": "application/json", "User-Agent": "profile-cards"},
    )
    with urllib.request.urlopen(req, timeout=60) as r:
        body = json.load(r)
    if body.get("errors") and not body.get("data"):
        raise RuntimeError(body["errors"])
    return body


def streaks(counts):
    cur = 0
    seq = list(counts)
    if seq and seq[-1] == 0:  # today may not have a contribution yet
        seq = seq[:-1]
    for c in reversed(seq):
        if c > 0:
            cur += 1
        else:
            break
    best = run = 0
    for c in counts:
        run = run + 1 if c > 0 else 0
        best = max(best, run)
    return cur, best


def normalize(resp, asof):
    """GraphQL response -> the dict the renderers use. Pure function (unit-testable)."""
    data = resp["data"]
    user = data["user"]
    repo_sets = [user["repositories"]] + [v["repositories"] for k, v in data.items() if k.startswith("o") and v]
    stars = commits = repos = 0
    langs = {}
    for rs in repo_sets:
        for n in rs["nodes"]:
            repos += 1
            stars += n["stargazerCount"]
            ref = n.get("defaultBranchRef")
            if ref and ref.get("target"):
                commits += ref["target"]["history"]["totalCount"]
            for e in n["languages"]["edges"]:
                langs[e["node"]["name"]] = langs.get(e["node"]["name"], 0) + min(e["size"], LANG_CAP)
    total_bytes = sum(langs.values()) or 1
    top = sorted(langs.items(), key=lambda kv: -kv[1])[:7]
    cc = user["contributionsCollection"]
    cal = cc["contributionCalendar"]
    weeks = [[(d["date"], d["contributionCount"]) for d in w["contributionDays"]] for w in cal["weeks"]]
    flat = [c for w in weeks for _, c in w]
    cur, best = streaks(flat)
    return dict(
        mode="live", asof=asof, stars=stars, repos=repos, commits=commits,
        prs=cc["totalPullRequestContributions"], issues=cc["totalIssueContributions"],
        followers=user["followers"]["totalCount"],
        langs=[(k, v) for k, v in top], lang_total=total_bytes, lang_note="BY BYTES, CAPPED PER REPO",
        total=cal["totalContributions"], current=cur, longest=best, weeks=weeks,
    )


def fetch_live(token):
    asof = dt.date.today().isoformat()
    for orgs in (ORGS, []):  # if an org name fails (typo / renamed), fall back to the user only
        try:
            return normalize(gql(build_query(orgs), {"login": LOGIN}, token), asof)
        except RuntimeError as err:
            print("GraphQL error with orgs", orgs, "->", err, file=sys.stderr)
    raise SystemExit("could not read the GitHub API")


# ---- card renderers -------------------------------------------------------------------------------
def num(val, x, y, cell, col, delay, max_w=112):
    """Bold pixel number; shrinks the pixel size until it fits max_w so columns never collide."""
    s = "-" if val is None else str(val)
    while cell > 1 and len(s) * 7 * (cell + 1) - (cell + 1) > max_w:
        cell -= 1
    return rc.pixel_text(s, x, y, cell, 1, f'class="flick" style="--d:{delay:.2f}s;fill:var(--{col})"', bold=True), 7 * (cell + 1) - 1


def footer(d, extra=""):
    if d["mode"] == "snapshot":
        txt = f'SNAPSHOT {d["asof"]} \u00b7 UPDATES AFTER FIRST WORKFLOW RUN'
    else:
        txt = f'UPDATED {d["asof"]} \u00b7 {LOGIN.upper()} + ' + " + ".join(o.upper() for o in ORGS) if ORGS else f'UPDATED {d["asof"]}'
    return f'<text class="mono mute" x="18" y="{{y}}" font-size="8.5" letter-spacing=".5">{rc.esc(txt)}{extra}</text>'


def numc(val, x, y, col, delay, max_w):
    """Small bold pixel number (cell 2, drops to 1 if it would not fit max_w)."""
    s = "-" if val is None else f"{val:,}" if isinstance(val, int) and val >= 10000 else str(val)
    cell = 2
    while cell > 1 and len(s) * 7 * (cell + 1) - (cell + 1) > max_w:
        cell -= 1
    return rc.pixel_text(s, x, y, cell, 1, f'class="flick" style="--d:{delay:.2f}s;fill:var(--{col})"', bold=True)


STAR = ["00011000", "00011000", "11111111", "01111110", "00111100", "01111110", "01100110", "01000010"]
REPO = ["01111110", "01000011", "01011011", "01000011", "01011011", "01000011", "01111111", "00000000"]
COMMIT = ["00000000", "00111100", "01000010", "11100111", "11100111", "01000010", "00111100", "00000000"]
PR = ["11000100", "11001110", "01000100", "01000100", "01000100", "01000100", "11000100", "11000100"]
CAL = ["11111111", "10000001", "11111111", "10101011", "11111111", "10101011", "10000001", "11111111"]
TROPHY = ["11111111", "10111101", "10111101", "01111110", "00111100", "00011000", "00011000", "01111110"]
FLAME = ["00010000", "00110000", "01110100", "01111100", "11111110", "11111110", "01111100", "00111000"]
PALETTE = ["blue", "red", "amber", "teal"]


def _sep(x, y1, y2):
    return f'<line class="march" x1="{x}" y1="{y1}" x2="{x}" y2="{y2}" stroke="var(--line)" stroke-width="2" stroke-dasharray="3 3"/>'


def card_overview(d):
    """Four stat tiles (icon + number + label), then a proportional language bar and per-language rows."""
    H = 216
    inner = W - rc.SHADOW - 36
    out = [rc.frame(W, H, "blue")]
    items = [("STARS", d["stars"], "blue", STAR), ("REPOS", d["repos"], "red", REPO),
             ("COMMITS", d["commits"], "amber", COMMIT), ("PRS \u00b7 1Y", d["prs"], "teal", PR)]
    pitch = inner // len(items)
    for i, (lab, val, col, spr) in enumerate(items):
        x = 18 + i * pitch + (14 if i else 0)
        if i:
            out.append(_sep(18 + i * pitch, 20, 62))
        out.append(rc.sprite(spr, x, 24, 3, col, 0.2 + i * 0.1))
        out.append(num(val, x + 38, 16, 3, col, 0.2 + i * 0.1, max_w=pitch - 70)[0])
        out.append(f'<text class="mono mute" x="{x + 38}" y="54" font-size="8.5" letter-spacing="1">{lab}</text>')
    out.append(f'<line class="march" x1="18" y1="74" x2="{W - rc.SHADOW - 18}" y2="74" stroke="var(--line)" stroke-width="2" stroke-dasharray="4 4"/>')

    langs = d["langs"][:7]
    total = sum(v for _, v in langs) or 1
    all_total = d.get("lang_total") or total
    top = max(v for _, v in langs) if langs else 1
    out.append('<text class="mono mute" x="18" y="94" font-size="8.5" letter-spacing="1.5">TOP LANGUAGES</text>')
    # proportional bar, one block per language
    BW, x = inner, 18
    for i, (name, val) in enumerate(langs):
        w = max(6, round(BW * val / total)) - 2
        col, op = PALETTE[i % 4], (1 if i < 4 else .55)
        out.append(f'<rect class="pop" style="--d:{0.2 + i * 0.08:.2f}s;fill:var(--{col});opacity:{op}" x="{x}" y="102" width="{w}" height="10"/>')
        x += w + 2
    SEGS, COLW = 30, inner // 2
    for i, (name, val) in enumerate(langs):
        r, c = divmod(i, 2)
        x0, y = 18 + c * COLW + (12 if c else 0), 128 + r * 20
        col, op = PALETTE[i % 4], (1 if i < 4 else .55)
        filled = max(1, round(SEGS * val / top))
        out.append(f'<rect x="{x0}" y="{y}" width="8" height="8" style="fill:var(--{col});opacity:{op}"/>')
        out.append(f'<text class="mono" x="{x0 + 16}" y="{y + 8}" font-size="10">{rc.esc(name)}</text>')
        for sgi in range(SEGS):
            on = sgi < filled
            fill = f"var(--{col})" if on else "var(--line)"
            cls = f'class="pop" style="--d:{0.2 + i * 0.08 + sgi * 0.02:.2f}s"' if on else ""
            out.append(f'<rect {cls} x="{x0 + 96 + sgi * 6}" y="{y}" width="5" height="9" fill="{fill}"/>')
        out.append(f'<text class="mono mute" x="{x0 + COLW - 24}" y="{y + 8}" font-size="10" text-anchor="end">{100.0 * val / all_total:.1f}%</text>')
    return rc.svg(W, H, "".join(out), "GitHub statistics and top languages")


def card_streak(d):
    H = 100
    inner = W - rc.SHADOW - 36
    items = [("CONTRIBUTIONS \u00b7 1Y", d["total"], "blue", CAL), ("CURRENT STREAK", d["current"], "red", FLAME),
             ("LONGEST \u00b7 1Y", d["longest"], "amber", TROPHY)]
    pitch = inner // len(items)
    out = [rc.frame(W, H, "red")]
    for i, (lab, val, col, spr) in enumerate(items):
        x = 18 + i * pitch + (14 if i else 0)
        if i:
            out.append(_sep(18 + i * pitch, 18, H - 22))
        out.append(f'<g class="{"pulse" if i == 1 else ""}">{rc.sprite(spr, x, 28, 3, col, 0.2 + i * 0.15)}</g>')
        out.append(num(val, x + 40, 18, 5, col, 0.2 + i * 0.15, max_w=pitch - 70)[0])
        out.append(f'<text class="mono mute" x="{x + 40}" y="{H - 24}" font-size="9" letter-spacing="1">{lab}</text>')
    return rc.svg(W, H, "".join(out), "GitHub contribution streak")


MONTHS = ["JAN", "FEB", "MAR", "APR", "MAY", "JUN", "JUL", "AUG", "SEP", "OCT", "NOV", "DEC"]


def card_graph(d):
    H = 182
    cell, pitch = 12, 15
    out = [rc.frame(W, H, "teal")]
    weeks = d["weeks"]
    ncols = len(weeks) if weeks else 53
    x0 = 62
    y0 = 42
    out.append('<text class="mono mute" x="18" y="24" font-size="9.5" letter-spacing="1.5">CONTRIBUTIONS \u00b7 LAST 12 MONTHS</text>')
    # legend, top right
    xr = W - rc.SHADOW - 18
    lx = xr - 28 - 5 * pitch
    out.append(f'<text class="mono mute" x="{lx - 6}" y="23" font-size="8" text-anchor="end">LESS</text>')
    for k in range(5):
        f = "var(--line)" if k == 0 else "var(--teal)"
        out.append(f'<rect x="{lx + k * pitch}" y="14" width="{cell}" height="{cell}" fill="{f}" fill-opacity="{["1", ".3", ".5", ".75", "1"][k]}"/>')
    out.append(f'<text class="mono mute" x="{lx + 5 * pitch + 2}" y="23" font-size="8">MORE</text>')
    for di, lab in ((1, "MON"), (3, "WED"), (5, "FRI")):
        out.append(f'<text class="mono mute" x="18" y="{y0 + di * pitch + 10}" font-size="8">{lab}</text>')
    if weeks:
        peak = max((c for w in weeks for _, c in w), default=0) or 1
        last_month, last_wi = None, -9
        for wi, w in enumerate(weeks):
            m = int(w[0][0][5:7]) - 1
            if m != last_month:
                last_month = m
                if wi - last_wi >= 3 and wi * pitch + 28 < ncols * pitch:
                    out.append(f'<text class="mono mute" x="{x0 + wi * pitch}" y="36" font-size="9">{MONTHS[m]}</text>')
                    last_wi = wi
            for di, (date, c) in enumerate(w):
                lvl = 0 if c == 0 else 1 + min(3, int(4 * (c - 1) / peak)) if peak > 1 else 1
                fill = "var(--line)" if lvl == 0 else "var(--teal)"
                op = ["1", ".3", ".5", ".75", "1"][lvl]
                x, y = x0 + wi * pitch, y0 + di * pitch
                st = f"--d:{wi * 0.025 + di * 0.03:.2f}s;--s:{2.0 + wi * 0.06:.2f}s"
                out.append(f'<rect class="{"cell" if lvl else "cellbg"}" style="{st}" x="{x}" y="{y}" width="{cell}" height="{cell}" fill="{fill}" fill-opacity="{op}"/>')
                if lvl == 4:  # busiest days emit a slow radar ping
                    out.append(f'<rect class="ping" style="--d:{(wi * 7 + di * 3) % 36 / 10:.1f}s" x="{x}" y="{y}" width="{cell}" height="{cell}" fill="none" stroke="var(--teal)" stroke-width="1.5"/>')
                if date == d.get("asof"):  # today: blinking amber outline
                    out.append(f'<rect class="blink" x="{x - 2}" y="{y - 2}" width="{cell + 4}" height="{cell + 4}" fill="none" stroke="var(--amber)" stroke-width="2"/>')
    else:  # snapshot: no calendar offline, so show an empty grid and say why
        for wi in range(ncols):
            for di in range(7):
                out.append(f'<rect x="{x0 + wi * pitch}" y="{y0 + di * pitch}" width="{cell}" height="{cell}" fill="var(--line)" fill-opacity=".6"/>')
        out.append(f'<rect x="{W // 2 - 128}" y="{y0 + 40}" width="252" height="22" fill="var(--card)" stroke="var(--line)" stroke-width="2"/>'
                   f'<text class="mono blink" x="{W // 2 - 2}" y="{y0 + 55}" font-size="9.5" text-anchor="middle" '
                   f'style="fill:var(--ink)">WAITING FOR FIRST WORKFLOW RUN</text>')
    out.append(footer(d).replace("{y}", str(H - 14)))
    return rc.svg(W, H, "".join(out), "GitHub contribution graph")


def render(d):
    rc.write("activity-overview.svg", card_overview(d))
    rc.write("activity-streak.svg", card_streak(d))
    rc.write("activity-graph.svg", card_graph(d))


def main(argv):
    if "--fixture" in argv:
        d = json.load(open(argv[argv.index("--fixture") + 1]))
        d["weeks"] = [[tuple(x) for x in w] for w in d["weeks"]] if d.get("weeks") else None
        d["langs"] = [tuple(x) for x in d["langs"]]
    else:
        token = os.environ.get("GH_TOKEN") or os.environ.get("GITHUB_TOKEN")
        d = SNAPSHOT if ("--snapshot" in argv or not token) else fetch_live(token)
    print("mode:", d["mode"])
    render(d)


if __name__ == "__main__":
    main(sys.argv[1:])
