# App de treino

Site estático: `index.html` (template) + `treinos.json` (dados) + `icon.png`.
Para criar ou alterar treinos, edite só o `treinos.json`.

## Publicar no GitHub Pages (uma vez)
1. Crie um repositório público no GitHub (ex.: `treino`).
2. Coloque estes arquivos na raiz do repositório e faça o commit.
3. Em Settings > Pages, escolha "Deploy from a branch", branch `main`, pasta `/ (root)`.
4. Após cerca de 1 minuto o app fica em `https://SEU-USUARIO.github.io/treino/`.

## No iPhone
Abra o endereço no Safari > Compartilhar > Adicionar à Tela de Início.

## Testar no computador
Não abra o index.html direto do disco (o navegador bloqueia a leitura do JSON).
Na pasta, rode `python3 -m http.server 8000` e abra http://localhost:8000.

## Formato do treinos.json
treinos[] > fases[] > exercicios[]. Em cada exercício:
- `videos`: lista de IDs do YouTube. Texto simples = short vertical.
  Use `{"id": "...", "tipo": "video"}` para vídeos horizontais.
- `busca`: termo do link "Buscar no YouTube".
- `timer`: opcional, lista de {label, segundos}.

Fase com `rounds` + `descanso` = circuito com rounds.
Fase com `tabata` = botão de Tabata.
