"""Atualiza a nota e o número de avaliações da Pearle no Google (src/dados.json).

Usa a API oficial do Google (Places API New), pedindo só `rating` e `userRatingCount`
(faixa Enterprise: 1.000 consultas grátis; uma por dia fica bem abaixo disso).

Uso:
  PLACES_API_KEY=... python tools/atualizar_google.py      # consulta o Google
  python tools/atualizar_google.py --simular resposta.json  # testa com uma resposta salva

A chave vem só da variável de ambiente PLACES_API_KEY (segredo do GitHub); nunca é impressa.
Sai com código 0 e um aviso se a chave não existir (rotina ainda não configurada).
"""
from __future__ import annotations

import argparse
import json
import os
import sys
import urllib.error
import urllib.request
from datetime import date
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
DADOS = ROOT / "src" / "dados.json"
BUSCA = "PEARLE ESTETICA BY ELIANA ABREU, R. Pantaleão Brás, 93, Jardim Ester, São Paulo"
NOME_ESPERADO = "PEARLE"          # confere que o lugar encontrado é mesmo a Pearle


def aviso(msg: str) -> None:
    # Formato que o GitHub Actions mostra como aviso amarelo no resumo da rotina.
    print(f"::warning::{msg}" if os.environ.get("GITHUB_ACTIONS") else f"AVISO: {msg}")


def chamar(url: str, chave: str, campos: str, corpo: dict | None = None) -> dict:
    req = urllib.request.Request(
        url,
        data=json.dumps(corpo).encode() if corpo is not None else None,
        method="POST" if corpo is not None else "GET",
        headers={"X-Goog-Api-Key": chave, "X-Goog-FieldMask": campos, "Content-Type": "application/json"},
    )
    try:
        with urllib.request.urlopen(req, timeout=30) as r:
            return json.load(r)
    except urllib.error.HTTPError as e:
        # Mostra o erro do Google (sem a chave) para dar para entender o problema.
        detalhe = e.read().decode("utf-8", "replace")[:500]
        raise SystemExit(f"Google respondeu {e.code}: {detalhe}")


def descobrir_place_id(chave: str) -> str:
    """Busca o identificador da ficha uma única vez (só o id: faixa mais barata da busca)."""
    r = chamar("https://places.googleapis.com/v1/places:searchText", chave,
               "places.id,places.displayName", {"textQuery": BUSCA, "languageCode": "pt-BR"})
    for p in r.get("places", []):
        if NOME_ESPERADO in p.get("displayName", {}).get("text", "").upper():
            return p["id"]
    raise SystemExit("Não achei a ficha da Pearle na busca do Google.")


def ler_dados() -> dict:
    return json.loads(DADOS.read_text(encoding="utf-8")) if DADOS.exists() else {}


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--simular", help="arquivo JSON com uma resposta da Place Details, para testes")
    args = ap.parse_args()

    dados = ler_dados()
    novo_id = False
    if args.simular:
        resp = json.loads(Path(args.simular).read_text(encoding="utf-8"))
    else:
        chave = os.environ.get("PLACES_API_KEY", "").strip()
        if not chave:
            aviso("PLACES_API_KEY não configurada: números do Google não atualizados.")
            return
        pid = dados.get("place_id")
        if not pid:   # descobre uma vez e guarda, para as próximas execuções não buscarem de novo
            pid = dados["place_id"] = descobrir_place_id(chave)
            novo_id = True
        resp = chamar(f"https://places.googleapis.com/v1/places/{pid}", chave,
                      "displayName,rating,userRatingCount")

    nome = resp.get("displayName", {}).get("text", "")
    nota, total = resp.get("rating"), resp.get("userRatingCount")
    if NOME_ESPERADO not in nome.upper() or not isinstance(nota, (int, float)) or not isinstance(total, int):
        raise SystemExit(f"Resposta inesperada do Google (nome={nome!r}, nota={nota!r}, total={total!r}).")
    if not (1 <= nota <= 5 and 0 < total < 100000):
        raise SystemExit(f"Valores fora do esperado: nota={nota}, total={total}.")

    novo = {"nota": round(float(nota), 1), "avaliacoes": total}
    mudou = any(dados.get(k) != v for k, v in novo.items())
    mes = date.today().strftime("%Y-%m")
    # Grava quando os números mudam, ou uma vez por mês (mantém a rotina ativa no GitHub,
    # que desliga rotinas de repositórios sem nenhum commit por 60 dias).
    if mudou or novo_id or dados.get("verificado_em") != mes:
        if mudou:
            dados["atualizado_em"] = date.today().isoformat()
        dados.update(novo)
        dados["verificado_em"] = mes
        DADOS.write_text(json.dumps(dados, ensure_ascii=False, indent=2) + "\n", encoding="utf-8", newline="\n")
    print(f"Google: nota {novo['nota']} com {novo['avaliacoes']} avaliações"
          + (" (mudou)" if mudou else " (sem mudança)"))


if __name__ == "__main__":
    sys.exit(main())
