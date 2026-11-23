# Pearle Estética Avançada by Eliana Abreu

Site estático (HTML/CSS/JS) da clínica Pearle, no Jardim Ester, São Paulo. Prévia em
https://esteticapearle.borzanti.com (GitHub Pages, pasta `docs/`, sem indexação).

## Estrutura

- `src/pages/*.html`: uma página por arquivo, com cabeçalho `---` (slug, title, description, preload).
- `src/assets/`: CSS, JS e imagens (fotos do Instagram @estetica.pearle, recortadas e otimizadas).
- `tools/build.py`: monta cabeçalho, menu, rodapé, dados para o Google, sitemap e robots em cada página.
  Telefone, endereço e redes ficam no dicionário `SITE`: mudou, muda em um lugar só.
- `docs/`: saída gerada (não editar à mão).

## Comandos

```
python tools/build.py                   # prévia em docs/ (noindex, faixa de prévia)
python tools/build.py --env production  # versão final em site-publicar/
python tools/servir.py 8611             # prévia local em http://localhost:8611 (imita o GitHub Pages)
```
