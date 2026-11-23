"""Gera o site estático da Pearle Estética Avançada by Eliana Abreu.

Uso:
  python tools/build.py                   # prévia em docs/ (noindex, faixa de prévia)
  python tools/build.py --env production  # versão final em site-publicar/

Só biblioteca padrão. Conteúdo:
  src/pages/*.html   uma página por arquivo, com cabeçalho "---" (slug, title, description...)
  src/assets/        CSS, JS e imagens (copiados para <saida>/assets)
Chaves no texto: {{phone}}, {{wa:mensagem}}, {{icon:nome}}, {{link:slug}}, {{depoimentos}},
{{cta:título|texto|mensagem}}, {{endereco}}, {{horario}}, {{year}} e qualquer chave de SITE.
"""
from __future__ import annotations

import argparse
import hashlib
import html
import json
import re
import shutil
from datetime import date
from pathlib import Path
from urllib.parse import quote

ROOT = Path(__file__).resolve().parent.parent
SRC = ROOT / "src"
OUT_PREVIEW = ROOT / "docs"
OUT_PROD = ROOT / "site-publicar"
esc = html.escape

SITE = {
    "name": "Pearle Estética Avançada by Eliana Abreu",
    "short": "Pearle",
    "phone_e164": "5511978552981",
    "phone": "(11) 97855-2981",
    "street": "R. Pantaleão Brás, 93",
    "district": "Jardim Ester",
    "city": "São Paulo",
    "state": "SP",
    "zip": "05372-080",
    "lat": -23.5828177,
    "lng": -46.7626555,
    "instagram": "https://www.instagram.com/estetica.pearle/",
    "instagram_handle": "@estetica.pearle",
    "tiktok": "https://www.tiktok.com/@estetica.pearle",
    "google_reviews": "https://www.google.com/maps/place/?q=place_id:0x94ce55c6d02dd891:0x3e83868478eccdca",
    "rating": "5,0",
    "reviews": "51",
    "prod_url": "https://esteticapearle.borzanti.com",   # trocar pelo domínio oficial quando houver
    "preview_url": "https://esteticapearle.borzanti.com",
}

WA_DEFAULT = "Olá, Eliana! Vi o site da Pearle e gostaria de agendar uma avaliação."

# (slug, rótulo, submenu)
NAV = [
    ("", "Início", None),
    ("a-pearle", "A Pearle", None),
    ("#", "Tratamentos", [
        ("tratamentos-faciais", "Tratamentos faciais"),
        ("tratamentos-corporais", "Tratamentos corporais"),
        ("depilacao-a-laser", "Depilação a laser"),
        ("harmonizacao-facial", "Harmonização e injetáveis"),
    ]),
    ("massagens", "Massagens", None),
    ("contato", "Contato", None),
]

ICONS = {
    "wa": '<svg viewBox="0 0 24 24" fill="currentColor" aria-hidden="true"><path d="M12 2a10 10 0 0 0-8.6 15.1L2 22l5-1.3A10 10 0 1 0 12 2Zm0 18.2a8.2 8.2 0 0 1-4.2-1.2l-.3-.2-3 .8.8-2.9-.2-.3A8.2 8.2 0 1 1 12 20.2Zm4.5-6.1c-.2-.1-1.5-.7-1.7-.8-.2-.1-.4-.1-.6.1l-.8 1c-.1.2-.3.2-.5.1a6.7 6.7 0 0 1-3.3-2.9c-.3-.4.3-.4.8-1.4.1-.2 0-.3 0-.5l-.8-1.8c-.2-.5-.4-.4-.6-.4h-.5a1 1 0 0 0-.7.3 3 3 0 0 0-.9 2.2 5.2 5.2 0 0 0 1.1 2.7 11.8 11.8 0 0 0 4.5 4c1.7.7 2.4.8 3.2.6.5-.1 1.5-.6 1.7-1.2.2-.6.2-1.1.2-1.2-.1-.1-.3-.2-.5-.3Z"/></svg>',
    "menu": '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.6" aria-hidden="true"><path d="M4 7h16M4 12h16M4 17h16"/></svg>',
    "seta": '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"><path d="M5 12h14M13 6l6 6-6 6"/></svg>',
    "baixo": '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"><path d="m6 9 6 6 6-6"/></svg>',
    "check": '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.2" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"><path d="M20 6 9 17l-5-5"/></svg>',
    "rosto": '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5" aria-hidden="true"><circle cx="12" cy="12" r="8"/><path d="M9 10h.01M15 10h.01M9 15c1.7 1.3 4.3 1.3 6 0"/></svg>',
    "corpo": '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5" aria-hidden="true"><path d="M8 3c0 4-2 5-2 9s2 6 2 9M16 3c0 4 2 5 2 9s-2 6-2 9M9 12h6"/></svg>',
    "laser": '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5" aria-hidden="true"><path d="M12 3v4M12 17v4M3 12h4M17 12h4M6 6l2.5 2.5M15.5 15.5 18 18M6 18l2.5-2.5M15.5 8.5 18 6"/><circle cx="12" cy="12" r="2.5"/></svg>',
    "coracao": '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5" aria-hidden="true"><path d="M12 21s-7-4.4-7-10a4 4 0 0 1 7-2.6A4 4 0 0 1 19 11c0 5.6-7 10-7 10Z"/></svg>',
    "brilho": '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5" aria-hidden="true"><path d="M12 3l1.8 5.2L19 10l-5.2 1.8L12 17l-1.8-5.2L5 10l5.2-1.8Z"/><path d="M19 16l.7 1.8 1.8.7-1.8.7L19 21l-.7-1.8-1.8-.7 1.8-.7Z"/></svg>',
    "local": '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.6" aria-hidden="true"><path d="M12 21s-7-6.2-7-11.5a7 7 0 0 1 14 0C19 14.8 12 21 12 21Z"/><circle cx="12" cy="9.5" r="2.5"/></svg>',
    "fone": '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.6" aria-hidden="true"><path d="M5 4h4l2 5-2.5 1.5a11 11 0 0 0 5 5L15 13l5 2v4a2 2 0 0 1-2 2A16 16 0 0 1 3 6a2 2 0 0 1 2-2Z"/></svg>',
    "relogio": '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.6" aria-hidden="true"><circle cx="12" cy="12" r="9"/><path d="M12 7v5l3 2"/></svg>',
}

DEPOIMENTOS = [
    ("A Eliana é muito atenciosa, entende de verdade o que nos incomoda e propõe um tratamento personalizado.", "Sheila · cliente de tratamento facial"),
    ("Sou cliente da Eliana há anos e já fiz diversos procedimentos com ela, todos com resultados excelentes.", "Danielle · cliente há anos"),
    ("A Pearle leva muito a sério a execução de todos os procedimentos, sempre atentos e atualizados.", "Su · avaliação no Google"),
]


def wa(text: str) -> str:
    return f"https://wa.me/{SITE['phone_e164']}?text={quote(text)}"


def read(p: Path) -> str:
    return p.read_text(encoding="utf-8")


def write(p: Path, s: str) -> None:
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(s, encoding="utf-8", newline="\n")


def front_matter(text: str) -> tuple[dict, str]:
    m = re.match(r"^---\s*\n(.*?)\n---\s*\n", text, re.S)
    if not m:
        return {}, text
    meta = {}
    for line in m.group(1).splitlines():
        if ":" in line:
            k, v = line.split(":", 1)
            meta[k.strip()] = v.strip()
    return meta, text[m.end():]


class Build:
    def __init__(self, env: str):
        self.prod = env == "production"
        self.out = OUT_PROD if self.prod else OUT_PREVIEW
        self.base = SITE["prod_url"]
        self.ver = ""

    def href(self, slug: str) -> str:
        return "/" if slug == "" else f"/{slug}"

    # ---- blocos reutilizáveis -------------------------------------------------
    def depoimentos(self) -> str:
        figs = "".join(f'<figure class="depo"><blockquote>“{esc(t)}”</blockquote><figcaption>{esc(q)}</figcaption></figure>'
                       for t, q in DEPOIMENTOS)
        return f"""<section id="depoimentos">
  <div class="wrap">
    <div class="depo-topo">
      <div><span class="selo">Quem já é cliente</span><h2>O carinho de quem <em>volta sempre</em></h2></div>
      <div class="nota-google"><strong>{SITE['rating']}</strong><div><span class="estrelas">★★★★★</span><br><span data-count="{SITE['reviews']}">{SITE['reviews']}</span> avaliações no Google</div></div>
    </div>
    <div class="depos">{figs}</div>
    <p class="nota"><a href="{esc(SITE['google_reviews'])}" target="_blank" rel="noopener">Ler todas as avaliações no Google</a></p>
  </div>
</section>"""

    def cta(self, arg: str) -> str:
        titulo, texto, msg = (arg.split("|") + ["", "", ""])[:3]
        return f"""<section class="cta-faixa">
  <div class="wrap">
    <div><h2>{titulo}</h2><p>{texto}</p></div>
    <a class="btn btn-claro" href="{esc(wa(msg or WA_DEFAULT))}" target="_blank" rel="noopener">{ICONS['wa']}Agendar pelo WhatsApp</a>
  </div>
</section>"""

    def endereco(self) -> str:
        s = SITE
        return f"{s['street']} · {s['district']}<br>{s['city']}, {s['state']} · CEP {s['zip']}"

    def horario(self) -> str:
        return ('<table class="horario"><tr><td>Segunda a quinta</td><td>9h às 19h</td></tr>'
                '<tr><td>Sexta</td><td>9h às 17h</td></tr><tr><td>Sábado e domingo</td><td>Fechado</td></tr></table>')

    def fill(self, body: str) -> str:
        def rep(m: re.Match) -> str:
            key, _, arg = m.group(1).partition(":")
            if key == "wa":
                return esc(wa(arg or WA_DEFAULT))
            if key == "icon":
                return ICONS[arg]
            if key == "link":
                return self.href(arg)
            if key == "depoimentos":
                return self.depoimentos()
            if key == "cta":
                return self.cta(arg)
            if key == "endereco":
                return self.endereco()
            if key == "horario":
                return self.horario()
            if key == "year":
                return str(date.today().year)
            return esc(str(SITE[key]))
        return re.sub(r"\{\{([a-z0-9_]+(?::[^}]*)?)\}\}", rep, body)

    # ---- moldura da página ----------------------------------------------------
    def jsonld(self) -> str:
        s = SITE
        data = {
            "@context": "https://schema.org",
            "@type": "BeautySalon",
            "@id": self.base + "/#pearle",
            "name": s["name"],
            "url": self.base + "/",
            "image": self.base + "/assets/img/eliana-heroi.webp",
            "description": "Estética facial e corporal, massagens terapêuticas, drenagem linfática e depilação a laser no Jardim Ester, São Paulo.",
            "telephone": "+" + s["phone_e164"],
            "address": {"@type": "PostalAddress", "streetAddress": s["street"], "addressLocality": s["city"],
                        "addressRegion": s["state"], "postalCode": s["zip"], "addressCountry": "BR"},
            "geo": {"@type": "GeoCoordinates", "latitude": s["lat"], "longitude": s["lng"]},
            "openingHoursSpecification": [
                {"@type": "OpeningHoursSpecification", "dayOfWeek": ["Monday", "Tuesday", "Wednesday", "Thursday"], "opens": "09:00", "closes": "19:00"},
                {"@type": "OpeningHoursSpecification", "dayOfWeek": "Friday", "opens": "09:00", "closes": "17:00"},
            ],
            "founder": {"@type": "Person", "name": "Eliana Abreu", "jobTitle": "Esteticista"},
            "sameAs": [s["instagram"], s["tiktok"]],
        }
        return json.dumps(data, ensure_ascii=False)

    def header(self, slug: str, grupo: str) -> str:
        itens = []
        for s, label, sub in NAV:
            if sub:
                ativo = " ativo" if slug in [x for x, _ in sub] else ""
                links = "".join(f'<a href="{self.href(x)}"{" aria-current=\"page\"" if x == slug else ""}>{y}</a>' for x, y in sub)
                itens.append(f'<div class="sub{ativo}"><button class="sub-btn" type="button" aria-expanded="false">{label}{ICONS["baixo"]}</button>'
                             f'<div class="sub-menu">{links}</div></div>')
            else:
                cur = ' aria-current="page"' if s == slug else ""
                itens.append(f'<a href="{self.href(s)}"{cur}>{label}</a>')
        itens.append(f'<a class="btn btn-prim" href="{esc(wa(WA_DEFAULT))}" target="_blank" rel="noopener">Agendar</a>')
        faixa = "" if self.prod else '<div class="faixa-previa">Prévia do novo site da Pearle, para aprovação.</div>'
        return f"""{faixa}<header class="topo">
  <div class="wrap">
    <a class="marca" href="/" aria-label="Pearle Estética Avançada, início"><small>Estética ✦ Avançada</small><b>PEARLE</b><small>by Eliana Abreu</small></a>
    <button class="abre-menu" aria-label="Abrir menu" aria-expanded="false" aria-controls="menu">{ICONS['menu']}</button>
    <nav class="menu" id="menu" aria-label="Principal">{"".join(itens)}</nav>
  </div>
</header>"""

    def footer(self) -> str:
        s = SITE
        trat = "".join(f'<li><a href="{self.href(x)}">{y}</a></li>' for x, y in NAV[2][2])
        return f"""<footer class="rodape">
  <div class="wrap">
    <div>
      <a class="marca" href="/"><small>Estética ✦ Avançada</small><b>PEARLE</b><small>by Eliana Abreu</small></a>
      <p>Estética com propósito e técnica. Cuidado personalizado da sua autoestima.</p>
    </div>
    <div><h4>Tratamentos</h4><ul>{trat}<li><a href="/massagens">Massagens terapêuticas</a></li></ul></div>
    <div><h4>Contato</h4><ul>
      <li><a href="{esc(wa(WA_DEFAULT))}" target="_blank" rel="noopener">WhatsApp {s['phone']}</a></li>
      <li>{s['street']} · {s['district']}</li>
      <li>Seg a qui 9h–19h · Sex 9h–17h</li>
    </ul></div>
    <div><h4>Redes</h4><ul>
      <li><a href="{esc(s['instagram'])}" target="_blank" rel="noopener">Instagram {s['instagram_handle']}</a></li>
      <li><a href="{esc(s['tiktok'])}" target="_blank" rel="noopener">TikTok {s['instagram_handle']}</a></li>
    </ul></div>
    <p class="copy">© {date.today().year} {s['name']}. [CNPJ a confirmar]</p>
  </div>
</footer>
<a class="zap" href="{esc(wa(WA_DEFAULT))}" target="_blank" rel="noopener" aria-label="Falar no WhatsApp">{ICONS['wa']}</a>"""

    def page(self, meta: dict, body: str) -> str:
        slug = meta.get("slug", "")
        url = self.base + ("/" if slug in ("", "404") else self.href(slug))
        title, desc = meta["title"], meta["description"]
        robots = "" if self.prod and slug != "404" else '<meta name="robots" content="noindex, nofollow">\n'
        pre = meta.get("preload", "")
        pre = f'<link rel="preload" as="image" href="{pre}" fetchpriority="high">\n' if pre else ""
        return f"""<!doctype html>
<html lang="pt-BR">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1, viewport-fit=cover">
<script>if(location.search.indexOf('semanim')<0)requestAnimationFrame(function(){{document.documentElement.classList.add('anim')}})</script>
<title>{esc(title)}</title>
<meta name="description" content="{esc(desc)}">
{robots}<link rel="canonical" href="{url}">
<meta property="og:type" content="website">
<meta property="og:locale" content="pt_BR">
<meta property="og:site_name" content="{SITE['name']}">
<meta property="og:title" content="{esc(title)}">
<meta property="og:description" content="{esc(desc)}">
<meta property="og:url" content="{url}">
<meta property="og:image" content="{self.base}/assets/img/eliana-heroi.webp">
<meta name="theme-color" content="#7a1838">
<link rel="icon" href="/assets/img/favicon.svg" type="image/svg+xml">
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=Cormorant+Garamond:ital,wght@0,500;0,600;1,500&family=Jost:wght@400;500&display=swap">
{pre}<link rel="stylesheet" href="/assets/css/site.css?v={self.ver}">
<script type="application/ld+json">{self.jsonld()}</script>
</head>
<body class="pg-{slug or 'inicio'}">
<a class="pular" href="#conteudo">Pular para o conteúdo</a>
{self.header(slug, meta.get("grupo", ""))}
<main id="conteudo">
{self.fill(body)}
</main>
{self.footer()}
<script src="/assets/js/site.js?v={self.ver}" defer></script>
</body>
</html>
"""

    def run(self) -> None:
        out = self.out
        if out.exists():
            for p in out.iterdir():
                if p.name in ("CNAME", ".nojekyll", ".git"):
                    continue
                shutil.rmtree(p) if p.is_dir() else p.unlink()
        out.mkdir(exist_ok=True)
        shutil.copytree(SRC / "assets", out / "assets")
        h = hashlib.md5()
        for p in sorted((SRC / "assets").glob("*/*.*")):
            if p.suffix in (".css", ".js"):
                h.update(p.read_bytes())
        self.ver = h.hexdigest()[:8]
        urls = []
        for f in sorted((SRC / "pages").glob("*.html")):
            meta, body = front_matter(read(f))
            slug = meta.get("slug", "")
            write(out / ("index.html" if slug == "" else f"{slug}.html"), self.page(meta, body))
            if slug != "404":
                urls.append(self.base + self.href(slug))
        write(out / "sitemap.xml", '<?xml version="1.0" encoding="UTF-8"?>\n<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n'
              + "".join(f"  <url><loc>{u}</loc></url>\n" for u in urls) + "</urlset>\n")
        if self.prod:
            write(out / "robots.txt", f"User-agent: *\nAllow: /\nSitemap: {self.base}/sitemap.xml\n")
        else:
            write(out / "robots.txt", "# PRÉVIA: bloqueia indexação.\nUser-agent: *\nDisallow: /\n")
            write(out / "CNAME", SITE["preview_url"].split("//")[1] + "\n")
            write(out / ".nojekyll", "")
        print(f"{len(urls)} páginas em {out} ({'produção' if self.prod else 'prévia'})")


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--env", choices=["preview", "production"], default="preview")
    Build(ap.parse_args().env).run()
