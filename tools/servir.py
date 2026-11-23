"""Servidor local de prévia que imita o GitHub Pages: /a-pearle serve a-pearle.html e
endereço inexistente devolve 404.html. Uso: python tools/servir.py [porta]"""
import sys
from functools import partial
from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path

DOCS = Path(__file__).resolve().parent.parent / "docs"


class H(SimpleHTTPRequestHandler):
    def send_head(self):
        caminho = self.path.split("?", 1)[0].split("#", 1)[0]
        if caminho != "/" and "." not in caminho.rsplit("/", 1)[-1] and (DOCS / (caminho.lstrip("/") + ".html")).exists():
            self.path = caminho + ".html"
        alvo = DOCS / self.path.split("?", 1)[0].lstrip("/")
        if self.path.split("?", 1)[0] != "/" and not alvo.exists():
            self.send_response(404)
            self.send_header("Content-Type", "text/html; charset=utf-8")
            corpo = (DOCS / "404.html").read_bytes()
            self.send_header("Content-Length", str(len(corpo)))
            self.end_headers()
            self.wfile.write(corpo)
            return None
        return super().send_head()

    def end_headers(self):
        self.send_header("Cache-Control", "no-store")   # prévia sempre com a versão nova
        super().end_headers()


porta = int(sys.argv[1]) if len(sys.argv) > 1 else 8611
ThreadingHTTPServer(("127.0.0.1", porta), partial(H, directory=str(DOCS))).serve_forever()
