"""The middle monitor's picture: a dark code editor showing a real file from this repo, laid out in HTML
and captured with headless Chrome at 1600 x 900 (the panel's 16:9). It only has to read as "an IDE" at
the size the hero shows it (owner, 2026-11-25); the code is real all the same. No product's look or logo.

  python3 tools/studio/ide.py        ->  tools/studio/renders/ide.png
"""
import html, os, re, subprocess

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.dirname(os.path.dirname(HERE))
SRC = "src/app/_components/FoldingScreen.tsx"
FIRST, COUNT = 48, 24
OUT = os.path.join(HERE, "renders", "ide.png")
CHROME = "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome"

KEYWORDS = r"\b(const|let|var|return|if|else|function|export|default|import|from|new|type|for|of|while|await|async|null|true|false|undefined)\b"
TOKENS = [
    ("cm", r"//[^\n]*"),
    ("st", r"`[^`]*`|\"[^\"\n]*\"|'[^'\n]*'"),
    ("tg", r"</?[A-Za-z][\w.]*"),
    ("kw", KEYWORDS),
    ("nu", r"\b\d+(?:\.\d+)?\b"),
    ("fn", r"\b[a-zA-Z_]\w*(?=\()"),
    ("ty", r"\b[A-Z]\w*\b"),
]
RX = re.compile("|".join(f"(?P<{k}>{p})" for k, p in TOKENS))


def highlight(line):
    out, i = [], 0
    for m in RX.finditer(line):
        out.append(html.escape(line[i:m.start()]))
        out.append(f'<span class="{m.lastgroup}">{html.escape(m.group())}</span>')
        i = m.end()
    out.append(html.escape(line[i:]))
    return "".join(out) or "&nbsp;"


def main():
    lines = open(os.path.join(REPO, SRC)).read().split("\n")
    shown = lines[FIRST - 1:FIRST - 1 + COUNT]
    code = "\n".join(f'<div class="ln"><i>{FIRST + k}</i><b>{highlight(l)}</b></div>' for k, l in enumerate(shown))
    mini = "".join(f'<div style="width:{min(len(l.rstrip()), 90) * 0.9}px;margin-left:{(len(l) - len(l.lstrip())) * 0.9}px"></div>'
                   for l in lines[:120])
    tree = [("src", 0, "d"), ("app", 1, "d"), ("_components", 2, "d"), ("FoldingScreen.tsx", 3, "a"), ("StudioScene.tsx", 3, "f"),
            ("Phone.tsx", 3, "f"), ("StickyTop.tsx", 3, "f"), ("blog", 2, "d"), ("work", 2, "d"), ("layout.tsx", 2, "f"),
            ("page.tsx", 2, "f"), ("site.css", 2, "f"), ("content.ts", 1, "f"), ("tools", 0, "d"), ("gold-screen", 1, "d"),
            ("studio", 1, "d"), ("public", 0, "d"), ("package.json", 0, "f"), ("PRODUCT.md", 0, "f")]
    tree_html = "".join(f'<div class="t {k}" style="padding-left:{14 + d * 14}px">{n}</div>' for n, d, k in tree)
    term = ["<span class='pr'>~/code/new-portfolio</span> <span class='br'>test/hero</span>", "$ npm run dev", "",
            "&gt; next dev", "", "   ▲ Next.js 16.2.3", "   - Local:        http://localhost:3000", "",
            " <span class='ok'>✓</span> Ready", " <span class='ok'>✓</span> Compiled /", "$ <span class='cur'>&nbsp;</span>"]
    page = f"""<!doctype html><html><head><meta charset="utf-8"><style>
* {{ box-sizing: border-box; margin: 0; }}
body {{ width: 1600px; height: 900px; background: #1d1e23; color: #b9c0cb; font: 13px/1 -apple-system, system-ui, sans-serif;
  display: grid; grid-template: 30px 1fr 22px / 46px 250px 1fr; overflow: hidden; }}
.top {{ grid-column: 1 / 4; background: #17181c; border-bottom: 1px solid #0e0f12; display: flex; align-items: center; gap: 8px; padding-left: 14px; }}
.top i {{ width: 12px; height: 12px; border-radius: 50%; background: #3a3c44; }}
.top span {{ margin: 0 auto; color: #7d8390; font-size: 12px; transform: translateX(-30px); }}
.act {{ background: #17181c; display: flex; flex-direction: column; align-items: center; gap: 22px; padding-top: 16px; }}
.act i {{ width: 22px; height: 22px; border: 2px solid #565b66; border-radius: 5px; }}
.act i:first-child {{ border-color: #c9ced8; }}
.side {{ background: #1a1b20; border-right: 1px solid #111216; padding-top: 12px; }}
.side h6 {{ font: 600 11px/1 sans-serif; letter-spacing: .08em; color: #7d8390; padding: 0 14px 12px; }}
.t {{ height: 24px; line-height: 24px; color: #a8afbb; white-space: nowrap; }}
.t.d::before {{ content: "▾ "; color: #6c7280; }}
.t.f::before, .t.a::before {{ content: "◆ "; color: #4f8ccf; font-size: 9px; }}
.t.a {{ background: #2b2e37; color: #e4e7ec; }}
.main {{ display: grid; grid-template-rows: 34px 24px 1fr 236px; min-width: 0; min-height: 0; overflow: hidden; }}
.tabs {{ display: flex; background: #17181c; }}
.tabs div {{ padding: 0 18px; line-height: 34px; color: #7d8390; border-right: 1px solid #111216; }}
.tabs .on {{ background: #1d1e23; color: #e4e7ec; box-shadow: inset 0 2px 0 #8f7bf0; }}
.crumb {{ color: #7d8390; padding-left: 18px; line-height: 24px; font-size: 12px; }}
.ed {{ position: relative; font: 15px/22px Menlo, monospace; padding-top: 4px; overflow: hidden; }}
.ln {{ display: flex; white-space: pre; }}
.ln i {{ font-style: normal; width: 64px; text-align: right; padding-right: 22px; color: #4c515c; flex: none; }}
.ln b {{ font-weight: 400; color: #c3c9d3; }}
.cm {{ color: #687080; font-style: italic; }} .st {{ color: #9ecb7f; }} .tg {{ color: #e57b84; }} .kw {{ color: #c68ce3; }}
.nu {{ color: #dca06a; }} .fn {{ color: #6fb3f0; }} .ty {{ color: #e7c47c; }}
.mini {{ position: absolute; right: 14px; top: 6px; width: 90px; display: flex; flex-direction: column; gap: 2px; opacity: .55; }}
.mini div {{ height: 2px; background: #8b93a1; border-radius: 1px; }}
.panel {{ border-top: 1px solid #111216; background: #1a1b20; padding: 10px 18px; }}
.panel nav {{ display: flex; gap: 22px; font-size: 11px; letter-spacing: .06em; color: #7d8390; margin-bottom: 14px; }}
.panel nav b {{ color: #e4e7ec; font-weight: 500; border-bottom: 1px solid #e4e7ec; padding-bottom: 4px; }}
.term {{ font: 14px/19px Menlo, monospace; color: #c3c9d3; white-space: pre; }}
.pr {{ color: #6fb3f0; }} .br {{ color: #c68ce3; }} .ok {{ color: #7fd08a; }} .cur {{ background: #c3c9d3; }}
.bar {{ grid-column: 1 / 4; background: #5b4bc4; color: #eceaff; font-size: 12px; display: flex; gap: 22px; align-items: center; padding: 0 12px; }}
.bar span:last-child {{ margin-left: auto; }}
</style></head><body>
<div class="top"><i></i><i></i><i></i><span>FoldingScreen.tsx — new-portfolio</span></div>
<div class="act"><i></i><i></i><i></i><i></i><i></i></div>
<div class="side"><h6>EXPLORER</h6>{tree_html}</div>
<div class="main">
  <div class="tabs"><div>page.tsx</div><div class="on">FoldingScreen.tsx</div><div>site.css</div><div>scene.py</div></div>
  <div class="crumb">src › app › _components › FoldingScreen.tsx</div>
  <div class="ed">{code}<div class="mini">{mini}</div></div>
  <div class="panel"><nav><b>TERMINAL</b><span>PROBLEMS</span><span>OUTPUT</span></nav><div class="term">{"<br>".join(term)}</div></div>
</div>
<div class="bar"><span>⎇ test/hero</span><span>✓ 0 problems</span><span>Ln {FIRST + 12}, Col 18</span><span>TypeScript JSX</span></div>
</body></html>"""
    page_path = os.path.join(HERE, "renders", "ide.html")
    os.makedirs(os.path.dirname(page_path), exist_ok=True)
    open(page_path, "w").write(page)
    prof = os.path.join(HERE, "renders", ".chrome-ide")
    subprocess.run([CHROME, "--headless=new", "--disable-gpu", "--hide-scrollbars", f"--user-data-dir={prof}",
                    "--force-device-scale-factor=1", "--window-size=1600,900", f"--screenshot={OUT}", "file://" + page_path],
                   check=True, capture_output=True)
    print("SAVED", OUT)


if __name__ == "__main__":
    main()
