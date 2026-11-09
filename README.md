<h1 align="center">Pushkar Singh</h1>

<p align="center">
  <b>Backend &amp; Web Developer</b><br>
  <sub>Python · Flask · Jinja — building software that is simple, useful, and actually gets used.</sub>
</p>

<p align="center">
  <a href="https://github.com/truepushkar"><img src="https://img.shields.io/badge/GitHub-truepushkar-0b1026?style=for-the-badge&logo=github&logoColor=a78bfa&labelColor=0b1026" alt="GitHub" /></a>
  <a href="https://discord.com/users/1141179236309287082"><img src="https://img.shields.io/badge/Discord-pushkarop-0b1026?style=for-the-badge&logo=discord&logoColor=a78bfa&labelColor=0b1026" alt="Discord: pushkarop" /></a>
  <a href="https://x.com/TruePushkar"><img src="https://img.shields.io/badge/X-TruePushkar-0b1026?style=for-the-badge&logo=x&logoColor=a78bfa&labelColor=0b1026" alt="X" /></a>
  <a href="https://www.youtube.com/@truepushkar"><img src="https://img.shields.io/badge/YouTube-truepushkar-0b1026?style=for-the-badge&logo=youtube&logoColor=a78bfa&labelColor=0b1026" alt="YouTube" /></a>
  <a href="mailto:truepushkar@gmail.com"><img src="https://img.shields.io/badge/Email-truepushkar@gmail.com-0b1026?style=for-the-badge&logo=gmail&logoColor=a78bfa&labelColor=0b1026" alt="Email" /></a>
</p>

<p align="center">
  <img src="https://komarev.com/ghpvc/?username=truepushkar&label=Profile%20views&color=a78bfa&style=flat-square" alt="Profile views" />
  <a href="https://github.com/truepushkar?tab=followers"><img src="https://img.shields.io/github/followers/truepushkar?label=Followers&style=flat-square&color=a78bfa&labelColor=0b1026" alt="Followers" /></a>
  <img src="https://img.shields.io/badge/Open%20to-collaboration-a78bfa?style=flat-square&labelColor=0b1026" alt="Open to collaboration" />
</p>

## About

I build web applications around problems that are easy to see but often unnecessarily complicated to solve — attendance systems that replace paper registers, lightweight tools that don't demand an account before they're useful.

My primary stack is **Python + Flask**, with hand-written Jinja templates and whichever database fits the problem. I care more about solving the right problem than collecting technologies.

Lately that has meant a lot of AI plumbing: OpenAI- and Anthropic-compatible gateways that let any harness talk to a provider it wasn't written for, and small Cloudflare Workers that do one thing well and cost nothing to run.

```yaml
focus:      Backend & Web Development
stack:      Python · Flask · Jinja
also:       TypeScript · React · Cloudflare Workers · Docker · PHP · Java
building:   Small, sharp, composable tools
org:        @nullstacks — open-source AI tools and utilities
studying:   B.Tech Computer Science, KIIT (2025 – present)
since:      2022
```

## Selected work

| Project | What it does | ★ | Live |
|---|---|:-:|---|
| **[Stow](https://github.com/truepushkar/stow)** | Paste text, get a short link. Optional expiry, optional password, no account. Read protection enforced server-side, so the link alone opens nothing. Flask API + React client. | 4 | [demo](https://stowpaste.vercel.app/) |
| **[biometric-attendance](https://github.com/truepushkar/biometric-attendance)** | Face-recognition attendance for colleges, built for the Smart India Hackathon. Marks students present from an image and gives admins per-student analytics. | 9 | — |
| **[PaperSnap](https://github.com/nullstacks/papersnap)** | 23-tool PDF suite that runs entirely in the browser — no server, no uploads, no accounts. React 19 + strict TypeScript. | 2 | [demo](https://papersnap.nullstacks.workers.dev) |
| **[SourcebookLM](https://github.com/truepushkar/SourcebookLM)** | AI notebook that eats PDFs, DOCX, URLs and YouTube transcripts, then turns them into mind maps, reports, flashcards, quizzes and slide decks. | 4 | [demo](https://sourcebook-lm.vercel.app) |
| **[humanize-text](https://github.com/truepushkar/humanize-text)** | Text humanization pipeline with the reasoning left in the open: two LLM rewrites, then two translation hops through different NMT engines. Zero backend. | 4 | [demo](https://truepushkar.github.io/humanize-text/) |
| **[llm-proxy](https://github.com/truepushkar/llm-proxy)** | Self-hosted OpenAI-compatible reverse proxy — chat, models, images, embeddings and TTS behind one API. Streaming SSE, rate limits, budgets, admin dashboard. | 2 | — |
| **[Heardlist](https://github.com/nullstacks/heardlist)** | Free public proxy-list API on Cloudflare Workers. Hourly-refreshed, de-duplicated, filterable by protocol, country and latency. No API key. | 2 | [demo](https://heardlist.nullstacks.workers.dev/) |
| **[MailAPI](https://github.com/nullstacks/mailapi)** | Your Gmail as a REST API — Google OAuth, per-user keys, multi-account, disposable `+tag` aliases. One key reaches every linked mailbox. | 2 | [demo](https://mailapi.nullstacks.workers.dev/) |
| **[R2-storage](https://github.com/truepushkar/R2-storage)** | Production-ready file storage as a single Cloudflare Worker on R2. Streaming uploads, range requests, auto-expiry, login + dashboard. | 1 | [demo](https://cdn.nullstacks.workers.dev/) |
| **[GlazeStudio](https://github.com/truepushkar/GlazeStudio)** | CleanShot X–style screenshot beautifier with social post import, in a glass UI with light and dark mode. Entire editor is client-side. | 1 | [demo](https://glazestudio.vercel.app/) |
| **[CampusHub](https://github.com/truepushkar/CampusHub)** | One dashboard for the six portals every campus somehow ends up with: events, notices, complaints, timetables, club spaces. | 3 | [demo](https://campus-hub-eta-eight.vercel.app) |
| **Portfolio** | The site version of all of this. | 0 | [demo](https://portfolio-liart-phi-41.vercel.app) |

### AI gateways

A family of tiny Workers that re-expose a third-party model provider behind **both** OpenAI and Anthropic endpoints, so any client works unchanged:

**[kilo-gateway](https://github.com/nullstacks/kilo-gateway)** · **[qoder2api](https://github.com/nullstacks/qoder2api)** · **[cline2api](https://github.com/nullstacks/cline2api)** · **[opencode-gateway](https://github.com/nullstacks/opencode-gateway)** · **[mai-image](https://github.com/nullstacks/mai-image)**

## The numbers

| | |
|---|---|
| **Public repositories** | 84 across four identities — 78 original, 6 forks |
| **Stars earned** | 68 |
| **Live deployments** | 10, checked and responding |
| **Shipping since** | 2022 **(March 2022 — first public repo was a Minecraft server site)** |
| **Busiest year** | 2026 — 29 repositories |

Everything above is counted from the GitHub API, not from memory.

## Technology

<p align="center">
  <img src="https://skillicons.dev/icons?i=python,flask,mongodb,mysql,html,css,js,ts,react,tailwind,docker,cloudflare,git,githubactions,vercel,java,php,powershell&theme=dark" alt="Python, Flask, MongoDB, MySQL, HTML, CSS, JavaScript, TypeScript, React, Tailwind, Docker, Cloudflare, Git, GitHub Actions, Vercel, Java, PHP, PowerShell" />
</p>

| Area | Technologies |
|---|---|
| **Languages** | Python, JavaScript, TypeScript, PHP, Java, HTML/CSS, PowerShell, SQL |
| **Backend** | Flask, FastAPI, aiohttp, Jinja |
| **Serverless** | Cloudflare Workers, Workers KV, R2, Cron Triggers, wrangler |
| **Frontend** | React 19, Vite 6, Tailwind CSS v4, React Router 7, vanilla JS |
| **Data** | MongoDB, MySQL, SQLite, Workers KV |
| **AI / ML** | Gemini, OpenAI-compatible APIs, `face_recognition`, gateway design |
| **Documents** | pdf-lib, pdfjs-dist, mammoth, jszip, xlsx, html2canvas |
| **Browser** | Manifest V3 extensions, IndexedDB, canvas / WebM export |
| **Ops** | Docker, GHCR, Coolify, Vercel, GitHub Actions, Cloudflare Pages |
| **Protocols** | SSE streaming, OAuth 2.0 device flow, Google OAuth, range requests |

## Now

- Second-year **B.Tech Computer Science** student at **KIIT, Bhubaneswar**.
- Building out **[@nullstacks](https://github.com/nullstacks)** — open-source AI tools and utilities that are small, sharp and composable.
- Interested in **compatibility layers**: the unglamorous code that makes two systems agree on a protocol.
- Open to collaboration, freelance work and interesting problems. Discord is the fastest way to reach me.

## Activity

<p align="center">
  <img src="https://github-stats-extended.vercel.app/api?username=truepushkar&show_icons=true&rank_icon=github&hide_border=true&bg_color=0b1026&title_color=a78bfa&text_color=c7d2fe&icon_color=a78bfa&border_radius=12" height="165" alt="GitHub statistics" />
  <img src="https://github-stats-extended.vercel.app/api/top-langs/?username=truepushkar&layout=compact&langs_count=8&hide_border=true&bg_color=0b1026&title_color=a78bfa&text_color=c7d2fe&border_radius=12" height="165" alt="Top languages" />
</p>

<p align="center">
  <img src="https://github-readme-streak-stats-eight.vercel.app/?user=truepushkar&hide_border=true&background=0b1026&stroke=2d1b69&ring=a78bfa&fire=a78bfa&currStreakLabel=a78bfa&sideLabels=c7d2fe&currStreakNum=ede9fe&sideNums=ede9fe&dates=64748b&border_radius=12" alt="GitHub contribution streak" />
</p>

<p align="center">
  <img src="https://raw.githubusercontent.com/truepushkar/truepushkar/output/snake.svg" alt="GitHub contribution graph" />
</p>

## Contact

| | |
|---|---|
| **Discord** | [`pushkarop`](https://discord.com/users/1141179236309287082) — fastest reply |
| **Email** | [truepushkar@gmail.com](mailto:truepushkar@gmail.com) |
| **X** | [@TruePushkar](https://x.com/TruePushkar) |

---

<p align="center">
  <sub><i>"What we know is a drop, what we don't know is an ocean."</i></sub>
</p>
