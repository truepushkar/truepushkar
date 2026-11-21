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


def card_overview(d):
    """Stats row + top languages in one compact card (replaces activity-stats + activity-langs)."""
    H = 182
    out = [rc.frame(W, H, "blue")]
    items = [("STARS", d["stars"], "blue"), ("REPOS", d["repos"], "red"), ("COMMITS", d["commits"], "amber"),
             ("PRS \u00b7 1Y", d["prs"], "teal")]
    pitch = (W - rc.SHADOW - 36) // len(items)
    for i, (lab, val, col) in enumerate(items):
        x = 18 + i * pitch
        out.append(numc(val, x, 16, col, 0.2 + i * 0.1, pitch - 6))
        out.append(f'<text class="mono mute" x="{x}" y="50" font-size="8" letter-spacing=".8">{lab}</text>')
    out.append(f'<line class="march" x1="18" y1="63" x2="{W - rc.SHADOW - 18}" y2="63" stroke="var(--line)" stroke-width="2" stroke-dasharray="4 4"/>')

    langs = d["langs"][:7]
    total = sum(v for _, v in langs) or 1
    all_total = d.get("lang_total") or total  # percentage of ALL counted bytes/repos, not just the top 7
    top = max(v for _, v in langs) if langs else 1
    out.append('<text class="mono mute" x="18" y="80" font-size="8.5" letter-spacing="1.5">TOP LANGUAGES</text>')
    palette = ["blue", "red", "amber", "teal"]
    SEGS, COLW = 36, (W - rc.SHADOW - 36) // 2
    for i, (name, val) in enumerate(langs):
        r, c = divmod(i, 2)
        x0, y = 18 + c * COLW, 90 + r * 16
        col = palette[i % 4]
        filled = max(1, round(SEGS * val / top))
        out.append(f'<text class="mono" x="{x0}" y="{y + 8}" font-size="9.5">{rc.esc(name)}</text>')
        for sgi in range(SEGS):
            on = sgi < filled
            fill = f"var(--{col})" if on else "var(--line)"
            cls = f'class="pop" style="--d:{0.2 + i * 0.08 + sgi * 0.02:.2f}s"' if on else ""
            out.append(f'<rect {cls} x="{x0 + 68 + sgi * 6}" y="{y}" width="5" height="9" fill="{fill}"/>')
        out.append(f'<text class="mono mute" x="{x0 + COLW - 12}" y="{y + 8}" font-size="9.5" text-anchor="end">{100.0 * val / all_total:.1f}%</text>')

    if d["mode"] == "snapshot":
        tag = f'SNAPSHOT {d["asof"]} \u00b7 UPDATES AFTER FIRST WORKFLOW RUN'
    else:
        who = f'{LOGIN.upper()}' + "".join(f' + {o.upper()}' for o in ORGS)
        tag = f'UPDATED {d["asof"]} \u00b7 {who}'
    out.append(f'<text class="mono mute" x="18" y="{H - 14}" font-size="8" letter-spacing=".4">{rc.esc(tag)}</text>')
    return rc.svg(W, H, "".join(out), "GitHub statistics and top languages")


FLAME = ["00010000", "00110000", "01110100", "01111100", "11111110", "11111110", "01111100", "00111000"]


def card_streak(d):
    H = 112
    items = [("CONTRIBUTIONS \u00b7 1Y", d["total"], "blue"), ("CURRENT STREAK", d["current"], "red"),
             ("LONGEST \u00b7 1Y", d["longest"], "amber")]
    out = [rc.frame(W, H, "red")]
    pitch = (W - rc.SHADOW - 36) // len(items)
    for i, (lab, val, col) in enumerate(items):
        x = 18 + i * pitch
        svg_num, h = num(val, x, 18, 4, col, 0.2 + i * 0.15)
        out.append(svg_num)
        out.append(f'<text class="mono mute" x="{x}" y="68" font-size="9" letter-spacing="1">{lab}</text>')
    out.append(f'<g class="pulse">{rc.sprite(FLAME, 18 + pitch + 108, 52, 3, "red", 0.8)}</g>')
    out.append(footer(d).replace("{y}", str(H - 14)))
    return rc.svg(W, H, "".join(out), "GitHub contribution streak")


MONTHS = ["JAN", "FEB", "MAR", "APR", "MAY", "JUN", "JUL", "AUG", "SEP", "OCT", "NOV", "DEC"]


def card_graph(d):
    H = 170
    cell, pitch = 12, 14
    out = [rc.frame(W, H, "teal")]
    weeks = d["weeks"]
    ncols = len(weeks) if weeks else 53
    x0 = (W - rc.SHADOW - (ncols * pitch - 1)) // 2
    y0 = 40
    out.append('<text class="mono mute" x="18" y="22" font-size="9.5" letter-spacing="1.5">CONTRIBUTIONS \u00b7 LAST 12 MONTHS</text>')
    if weeks:
        peak = max((c for w in weeks for _, c in w), default=0) or 1
        last_month, last_wi = None, -9
        for wi, w in enumerate(weeks):
            m = int(w[0][0][5:7]) - 1
            if m != last_month:
                last_month = m
                if wi - last_wi >= 3 and wi * pitch + 24 < ncols * pitch:  # skip crowded labels
                    out.append(f'<text class="mono mute" x="{x0 + wi * pitch}" y="34" font-size="9">{MONTHS[m]}</text>')
                    last_wi = wi
            for di, (date, c) in enumerate(w):
                lvl = 0 if c == 0 else 1 + min(3, int(4 * (c - 1) / peak)) if peak > 1 else 1
                fill = "var(--line)" if lvl == 0 else "var(--teal)"
                op = ["1", ".3", ".5", ".75", "1"][lvl]
                out.append(f'<rect class="sweep" style="--d:{1.0 + wi * 0.09:.2f}s" x="{x0 + wi * pitch}" y="{y0 + di * pitch}" '
                           f'width="{cell}" height="{cell}" fill="{fill}" fill-opacity="{op}"/>')
        # legend
        lx = W - rc.SHADOW - 14 - 5 * pitch - 70
        out.append(f'<text class="mono mute" x="{lx}" y="{H - 14}" font-size="8" text-anchor="end">LESS</text>')
        for k in range(5):
            f = "var(--line)" if k == 0 else "var(--teal)"
            out.append(f'<rect x="{lx + 8 + k * pitch}" y="{H - 21}" width="{cell}" height="{cell}" fill="{f}" fill-opacity="{["1", ".3", ".5", ".75", "1"][k]}"/>')
        out.append(f'<text class="mono mute" x="{lx + 8 + 5 * pitch + 4}" y="{H - 14}" font-size="8">MORE</text>')
    else:  # snapshot: no calendar offline, so show an empty grid and say why
        for wi in range(ncols):
            for di in range(7):
                out.append(f'<rect x="{x0 + wi * pitch}" y="{y0 + di * pitch}" width="{cell}" height="{cell}" fill="var(--line)" fill-opacity=".6"/>')
        out.append(f'<rect x="{W // 2 - 128}" y="{y0 + 14}" width="252" height="22" fill="var(--card)" stroke="var(--line)" stroke-width="2"/>'
                   f'<text class="mono blink" x="{W // 2 - 2}" y="{y0 + 29}" font-size="9.5" text-anchor="middle" '
                   f'style="fill:var(--ink)">WAITING FOR FIRST WORKFLOW RUN</text>')
    out.append(footer(d).replace("{y}", str(H - 14)) if d["mode"] != "live" else "")
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
