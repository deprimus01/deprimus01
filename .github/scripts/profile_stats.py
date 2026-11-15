#!/usr/bin/env python3
"""Generate live GitHub profile cards (dark + light SVG) and refresh the recent-repos list.

Runs inside GitHub Actions and uses only the Python standard library.
Every number comes from the GitHub API. Nothing is hard-coded or estimated.
Env: GITHUB_TOKEN (optional, enables contribution counts), PROFILE_USER, ASSETS_DIR, README
"""
import colorsys, json, os, re, sys, urllib.request, urllib.error

USER = os.environ.get("PROFILE_USER", "deprimus01")
TOKEN = os.environ.get("GITHUB_TOKEN") or os.environ.get("GH_TOKEN") or ""
ASSETS = os.environ.get("ASSETS_DIR", "assets")
README = os.environ.get("README", "README.md")

SERIF = "'Iowan Old Style','Palatino Linotype',Palatino,'Book Antiqua',Georgia,serif"
SANS = "'Inter','SF Pro Display','Segoe UI',system-ui,-apple-system,'Helvetica Neue',Arial,sans-serif"
MONO = "'JetBrains Mono','SF Mono',ui-monospace,SFMono-Regular,Menlo,Consolas,monospace"
EM, EML, ICE, MINT, VIO, VIOL, MUTED = "#10b981", "#34d399", "#6ee7b7", "#a7f3d0", "#7c3aed", "#a78bfa", "#8b949e"
RM = "@media (prefers-reduced-motion: reduce){*{animation:none!important}}"

LANG_COLORS = {
    "JavaScript": "#f1e05a", "TypeScript": "#3178c6", "HTML": "#e34c26", "CSS": "#8b5cf6", "Python": "#3572A5",
    "Java": "#b07219", "C++": "#f34b7d", "C": "#9aa0a6", "PHP": "#8892be", "Shell": "#89e051", "Go": "#00ADD8",
    "Kotlin": "#A97BFF", "Dart": "#00B4AB", "EJS": "#a91e50", "SCSS": "#c6538c", "Dockerfile": "#384d54",
}


def request(url, data=None):
    headers = {"Accept": "application/vnd.github+json", "User-Agent": "profile-stats"}
    if TOKEN:
        headers["Authorization"] = f"Bearer {TOKEN}"
    body = json.dumps(data).encode() if data is not None else None
    req = urllib.request.Request(url, data=body, headers=headers)
    with urllib.request.urlopen(req, timeout=30) as r:
        return json.load(r)


def rest(path):
    return request("https://api.github.com" + path)


def fetch():
    user = rest(f"/users/{USER}")
    repos, page = [], 1
    while True:
        chunk = rest(f"/users/{USER}/repos?per_page=100&type=owner&sort=pushed&page={page}")
        repos += chunk
        if len(chunk) < 100:
            break
        page += 1
    own = [r for r in repos if not r["fork"]]
    stars = sum(r["stargazers_count"] for r in own)
    forks = sum(r["forks_count"] for r in own)

    langs = {}
    for r in [r for r in own if not r["archived"]][:80]:
        try:
            for k, v in rest(f"/repos/{USER}/{r['name']}/languages").items():
                langs[k] = langs.get(k, 0) + v
        except Exception:
            pass

    contrib = None
    if TOKEN:
        q = """query($login:String!){user(login:$login){contributionsCollection{
          totalPullRequestContributions contributionCalendar{totalContributions}}}}"""
        try:
            res = request("https://api.github.com/graphql", {"query": q, "variables": {"login": USER}})
            c = res["data"]["user"]["contributionsCollection"]
            contrib = dict(contributions=c["contributionCalendar"]["totalContributions"],
                           prs=c["totalPullRequestContributions"])
        except Exception as e:
            print("graphql skipped:", e)
    return user, own, stars, forks, langs, contrib


def fmt(n):
    return f"{n/1000:.1f}k" if n >= 10000 else f"{n:,}"


def shell(W, H, title, sub, body, label):
    return f"""<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H}" viewBox="0 0 {W} {H}" role="img" aria-label="{label}">
  <defs>
    <linearGradient id="bg" x1="0" y1="0" x2="1" y2="1"><stop offset="0" stop-color="#05080b"/><stop offset=".55" stop-color="#08110f"/><stop offset="1" stop-color="#110a22"/></linearGradient>
    <linearGradient id="edge" x1="0" y1="0" x2="1" y2="1"><stop offset="0" stop-color="#ffffff" stop-opacity=".2"/><stop offset=".5" stop-color="{MINT}" stop-opacity=".2"/><stop offset="1" stop-color="{EM}" stop-opacity=".26"/></linearGradient>
    <linearGradient id="mintline" x1="0" y1="0" x2="1" y2="0"><stop offset="0" stop-color="{MINT}"/><stop offset="1" stop-color="{EML}"/></linearGradient>
    <linearGradient id="num" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="#ffffff"/><stop offset="1" stop-color="#b9cdea"/></linearGradient>
    <linearGradient id="bar" x1="0" y1="0" x2="1" y2="0"><stop offset="0" stop-color="{EML}"/><stop offset="1" stop-color="{VIOL}"/></linearGradient>
    <radialGradient id="glow" cx="1" cy="0" r="1"><stop offset="0" stop-color="{EM}" stop-opacity=".18"/><stop offset="1" stop-color="{EM}" stop-opacity="0"/></radialGradient>
    <clipPath id="c"><rect width="{W}" height="{H}" rx="26"/></clipPath>
  </defs>
  <style>
    .in{{animation:in .8s cubic-bezier(.2,.7,.2,1) backwards}} @keyframes in{{from{{opacity:0;transform:translateY(8px)}}}}
    .grow{{transform-box:fill-box;transform-origin:left;animation:grow 1.2s cubic-bezier(.2,.7,.2,1) backwards}} @keyframes grow{{from{{transform:scaleX(0)}}}}
    {RM}
  </style>
  <g clip-path="url(#c)"><rect width="{W}" height="{H}" fill="url(#bg)"/><rect width="{W}" height="{H}" fill="url(#glow)"/></g>
  <rect x=".75" y=".75" width="{W-1.5}" height="{H-1.5}" rx="25.25" fill="none" stroke="url(#edge)" stroke-width="1.5"/>
  <path d="M36 .75 H{W-36}" stroke="{MINT}" stroke-opacity=".3"/>
  <text x="32" y="56" font-family="{SERIF}" font-size="34" font-weight="700" fill="#f4f6fb">{title}</text>
  <text x="32" y="86" font-family="{SANS}" font-size="20" fill="#a3adbb">{sub}</text>
  {body}
</svg>
"""


def stats_svg(user, stars, forks, contrib):
    items = [("Public repos", user["public_repos"]), ("Stars earned", stars), ("Forks", forks), ("Followers", user["followers"])]
    if contrib:
        items += [("Contributions, 1y", contrib["contributions"]), ("Pull requests", contrib["prs"])]
    W, cols = 640, 3
    rows = (len(items) + cols - 1) // cols
    H = 112 + rows * 92 + 24
    body = ""
    for i, (label, val) in enumerate(items):
        r, c = divmod(i, cols)
        x, y = 32 + c * 200, 150 + r * 92
        body += (f'<g class="in" style="animation-delay:{.1+i*.1:.1f}s"><text x="{x}" y="{y}" font-family="{SERIF}" font-size="44" font-weight="700" fill="url(#num)">{fmt(val)}</text>'
                 f'<text x="{x}" y="{y+28}" font-family="{SANS}" font-size="18" fill="{MUTED}">{label}</text></g>')
    return shell(W, H, "GitHub activity", USER, body, f"GitHub statistics for {USER}")


def langs_svg(langs):
    total = sum(langs.values()) or 1
    top = sorted(langs.items(), key=lambda kv: -kv[1])[:6]
    W = 640
    H = 112 + len(top) * 46 + 18
    body = ""
    for i, (name, v) in enumerate(top):
        pct = v / total * 100
        y = 126 + i * 46
        col = LANG_COLORS.get(name, ICE)
        bw = max(8, 250 * pct / (top[0][1] / total * 100))
        body += (f'<g class="in" style="animation-delay:{.1+i*.08:.2f}s"><circle cx="40" cy="{y+10}" r="7" fill="{col}"/>'
                 f'<text x="60" y="{y+17}" font-family="{SANS}" font-size="22" fill="#e8edf5">{name}</text>'
                 f'<rect x="270" y="{y+2}" width="250" height="16" rx="8" fill="#16211f"/>'
                 f'<rect class="grow" x="270" y="{y+2}" width="{bw:.1f}" height="16" rx="8" fill="url(#bar)" style="animation-delay:{.3+i*.1:.1f}s"/>'
                 f'<text x="{W-32}" y="{y+17}" text-anchor="end" font-family="{MONO}" font-size="18" fill="{MUTED}">{pct:.1f}%</text></g>')
    return shell(W, H, "Top languages", "by code volume", body, f"Top languages for {USER}")


_HEX = re.compile(r"#([0-9a-fA-F]{6}|[0-9a-fA-F]{3})\b")


def _map(m):
    h = m.group(1)
    if len(h) == 3:
        h = "".join(c * 2 for c in h)
    r, g, b = [int(h[i:i + 2], 16) / 255 for i in (0, 2, 4)]
    hh, l, s = colorsys.rgb_to_hls(r, g, b)
    l2 = 0.07 + 0.88 * (1 - l) if (s < 0.55 or l < 0.28 or l > 0.78) else l * 0.6
    r2, g2, b2 = colorsys.hls_to_rgb(hh, l2, s)
    return "#%02x%02x%02x" % (round(r2 * 255), round(g2 * 255), round(b2 * 255))


def write_pair(name, svg):
    os.makedirs(ASSETS, exist_ok=True)
    with open(os.path.join(ASSETS, name + ".svg"), "w", encoding="utf-8") as f:
        f.write(svg)
    with open(os.path.join(ASSETS, name + "-light.svg"), "w", encoding="utf-8") as f:
        f.write(_HEX.sub(_map, svg))
    print("wrote", name)


def update_readme(repos):
    if not os.path.exists(README):
        return
    skip = {USER.lower(), ".github"}
    recent = [r for r in repos if r["name"].lower() not in skip and not r["archived"] and not r.get("private")][:5]
    lines = []
    for r in recent:
        desc = " ".join((r.get("description") or "").split())
        desc = desc.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;").replace("|", "/")
        desc = re.sub(r"([\\`*\[\]_])", r"\\\1", desc)
        lang = f" `{r['language']}`" if r.get("language") else ""
        lines.append(f"- [**{r['name']}**]({r['html_url']}){lang}" + (f": {desc}" if desc else ""))
    if not lines:
        return
    block = "<!-- RECENT:START -->\n" + "\n".join(lines) + "\n<!-- RECENT:END -->"
    txt = open(README, encoding="utf-8").read()
    new = re.sub(r"<!-- RECENT:START -->.*?<!-- RECENT:END -->", lambda m: block, txt, flags=re.S)
    if new != txt:
        open(README, "w", encoding="utf-8").write(new)
        print("README recent repos updated")


def main():
    try:
        user, own, stars, forks, langs, contrib = fetch()
    except urllib.error.HTTPError as e:
        print("GitHub API error:", e)
        sys.exit(1)
    write_pair("stats", stats_svg(user, stars, forks, contrib))
    if langs:
        write_pair("langs", langs_svg(langs))
    update_readme(own)


if __name__ == "__main__":
    main()
