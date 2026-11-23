# Nota e avaliações do Google atualizadas sozinhas: passo a passo

Todo dia às 06:17 (Brasília), uma rotina no GitHub consulta a ficha da Pearle no Google pela API
oficial, pega só a nota e o número de avaliações e, se mudou, gera e publica o site de novo.

Custo esperado: R$ 0. Uma consulta por dia são ~30 por mês, e a faixa usada tem 1.000 grátis
(depois, US$ 20 por 1.000). O Google exige cartão no faturamento mesmo assim.

Leva uns 10 minutos. A chave **não** deve ser colada no chat nem em arquivo do projeto: ela vai
direto do Google Cloud para o segredo do GitHub.

## 1. Google Cloud: projeto, faturamento e API

1. Abra **https://console.cloud.google.com** com a sua conta Google.
2. No seletor de projeto (topo da tela), clique em **Novo projeto**. Nome: `site-pearle`. **Criar**.
3. Menu ☰ → **Faturamento** → vincule uma conta de faturamento (cartão).
4. Menu ☰ → **APIs e serviços** → **Biblioteca** → procure **Places API (New)** → **Ativar**.
   (Atenção: é a "(New)", não a "Places API" antiga.)

## 2. Criar a chave, só para essa API

1. Menu ☰ → **APIs e serviços** → **Credenciais** → **+ Criar credenciais** → **Chave de API**.
2. Na chave criada, clique em **Editar chave de API**:
   - **Nome:** `site-pearle-github`
   - **Restrições de aplicativo:** Nenhuma (a rotina roda em servidores do GitHub, sem IP fixo)
   - **Restrições de API:** **Restringir chave** → marque só **Places API (New)** → **Salvar**
3. Copie a chave (botão **Mostrar chave** → copiar). Não cole em nenhum outro lugar além do passo 3.

**Recomendado (trava de segurança):** Menu ☰ → **Faturamento** → **Orçamentos e alertas** →
crie um orçamento de R$ 5 com alerta por e-mail. Se algo sair do esperado, você é avisado.

## 3. GitHub: guardar a chave como segredo

1. Abra **https://github.com/borzanr/estetica-pearle-site/settings/secrets/actions**
2. **New repository secret**
   - **Name:** `PLACES_API_KEY`
   - **Secret:** cole a chave
   - **Add secret**

## 4. GitHub: permitir que a rotina publique

1. Abra **https://github.com/borzanr/estetica-pearle-site/settings/actions**
2. Em **Workflow permissions**, marque **Read and write permissions** → **Save**.

## 5. Testar na hora

1. Abra **https://github.com/borzanr/estetica-pearle-site/actions**
2. À esquerda, **Avaliações do Google** → **Run workflow** → **Run workflow**.
3. Em ~1 minuto deve ficar verde. Clique na execução → **atualizar** → **Consultar o Google**:
   deve aparecer `Google: nota 5.0 com NN avaliações`.

Se ficar vermelho, a mensagem do passo mostra o motivo (sem a chave) — me mande o texto.

## Depois

- Nada a fazer no dia a dia. Quando chegar avaliação nova, o site mostra no dia seguinte.
- Para parar: em **Actions → Avaliações do Google → ⋯ → Disable workflow**.
- Para trocar a chave: repita o passo 2 e atualize o segredo no passo 3.
