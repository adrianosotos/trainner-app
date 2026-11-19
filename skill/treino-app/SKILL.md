---
name: treino-app
description: Monta e publica treinos no app de treino pessoal (site no GitHub Pages que o usuário abre no iPhone). Converte o treino que o usuário escreve em texto para o treinos.json, procura vídeos demonstrativos de cada exercício no YouTube, valida tudo e faz o commit e o push. Use sempre que o usuário colar ou descrever um treino, pedir para adicionar, criar, atualizar ou ajustar um treino, trocar um exercício ou um vídeo, mencionar "app de treino", "meu treino", "ficha de treino" ou "publicar o treino", mesmo que não peça explicitamente para publicar.
compatibility: Requer git com acesso ao repositório do app (push configurado), Python 3 e a ferramenta de busca na web. Pensada para o Claude Code.
---

# Treino App

O app é um site estático: `index.html` (template, não muda) lê o `treinos.json` (dados). Esta skill transforma um treino descrito em texto em uma entrada nova do `treinos.json`, anexa vídeos de demonstração e publica no GitHub Pages. O usuário não edita JSON; ele escreve o treino do jeito que pensa nele.

Leia `references/formato.md` antes de escrever o JSON: ele traz a estrutura, as regras de conversão (rounds, tabata, lados, timers) e o método para achar vídeos.

## Fluxo

### 1. Localizar o repositório
- Se o diretório atual tem `treinos.json` e `index.html`, ele é o repositório.
- Senão, leia `~/.claude/treino-app.json` (campo `repo`, caminho do clone). Se não existir, pergunte ao usuário o caminho do clone ou a URL do repositório (e clone), e salve o caminho nesse arquivo para as próximas vezes.
- Se o repositório estiver vazio ou novo (sem `index.html`), copie `assets/index.html` e `assets/icon.png` para a raiz e crie `treinos.json` com `{"treinos": []}`. Em um repositório novo, lembre o usuário uma vez de ativar o Pages em Settings > Pages (branch `main`, pasta raiz) e de que o repositório precisa ser público no plano gratuito.
- Rode `git pull --rebase` antes de editar, para não divergir de alterações anteriores.

### 2. Entender o pedido
Decida se é um treino novo, uma alteração em um treino existente, ou só troca de vídeo/exercício. Leia o `treinos.json` atual para saber o que já existe. Se o `id` que você escolheria já existe, pergunte se é para substituir (o progresso salvo no aparelho é por id, então trocar o conteúdo mantém o progresso e trocar o id zera).

Se o texto do usuário não traz o essencial (quais exercícios, ou quantas séries/repetições/tempo de cada um), pergunte em uma única mensagem. Não complete com exercícios ou números inventados: o treino é a rotina física de uma pessoa, e uma carga ou volume errado é pior que uma pergunta.

### 3. Converter em JSON
Siga `references/formato.md`. Pontos que mais importam:
- `prescricao` curta e legível de relance; séries e tempos ficam nela.
- Fases com `rounds`/`descanso` para circuitos e `tabata` para intervalados.
- `timer` só onde o exercício tem tempo definido (alongamentos, lados alternados, esforço por tempo).
- Reaproveite ids, descrições e vídeos de exercícios que já existem em outro treino do `treinos.json` (mesmo exercício = mesmos dados). Isso mantém consistência e economiza buscas.

### 4. Procurar vídeos
Para cada exercício sem vídeos, busque até 3 demonstrações curtas seguindo o método da seção 4 de `references/formato.md` (consultas começando por `youtube.com/shorts ...`, modo de busca mais completo quando existir). Escolha pelo título e pela descrição, extraia o ID e use somente IDs que apareceram nos resultados. Se não achar nada bom, deixe `videos: []`: o app mostra o link de busca no lugar, e isso é melhor que um vídeo errado.

### 5. Validar
```bash
python3 <pasta-da-skill>/scripts/validar.py treinos.json --online --corrigir
```
Sem `--online` ele confere só a estrutura. Com `--online` ele confirma no YouTube que cada vídeo existe e pode ser incorporado, e `--corrigir` remove os que não passam. Se removeu vídeos de algum exercício, busque substitutos e rode de novo. Se a rede falhar, o script avisa "não consegui verificar" e não remove nada; nesse caso diga isso ao usuário.

### 6. Conferir antes de publicar
Mostre ao usuário um resumo curto do que vai subir: nome do treino, fases, exercícios com prescrição, e quantos vídeos cada um ganhou. Se alguma interpretação foi uma escolha sua (ex.: "10 por lado" virou timer ou não), diga qual. Publique sem esperar resposta quando o usuário já tiver pedido para publicar e não houver dúvida relevante; se houve alguma suposição que muda o treino, espere a confirmação.

### 7. Publicar
```bash
git add treinos.json   # e index.html/icon.png apenas se foram criados agora
git commit -m "Treino: <nome do treino>"
git pull --rebase && git push
```
Faça commit só dos arquivos do app. O repositório é público, então nunca inclua dados pessoais (nomes, saúde, localização) nos treinos nem nas mensagens de commit.

O Pages leva cerca de 1 minuto para atualizar. Derive o endereço do `git remote get-url origin`: `https://<usuario>.github.io/<repositorio>/`. Informe o endereço e que o iPhone pode precisar de um refresh (puxar a página para baixo no Safari) para ver a versão nova.

### 8. Relatório final
Responda de forma curta com: o que foi publicado, o endereço, e uma lista honesta do que ficou aquém:
- exercícios sem vídeo;
- vídeos que são substitutos próximos e não o exercício exato;
- vídeos que não consegui verificar online;
- o que não deu para testar (você não vê o app rodando no celular).

Não afirme que os vídeos têm determinada duração, popularidade ou qualidade de execução: você só viu título e descrição.

## Alterações pequenas
Para trocar um vídeo, uma prescrição ou o nome de um exercício, edite só esse trecho do JSON, valide, faça commit e push. Não reescreva o arquivo inteiro.
