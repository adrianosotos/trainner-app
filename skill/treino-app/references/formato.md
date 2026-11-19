# Formato do treinos.json e como converter texto de treino

## Índice
1. Estrutura
2. Regras de conversão
3. Exemplo completo de conversão
4. Como achar vídeos

## 1. Estrutura

```
{ "treinos": [ Treino, ... ] }

Treino    { id, nome, descricao?, fases: [Fase, ...] }
Fase      { id, aba, titulo, tempo?, intro?, chips?: [texto], exercicios: [Exercicio],
            rounds?: int, descanso?: segundos,        # circuito em rounds
            tabata?: { rounds, trabalho, descanso } } # intervalado; rounds e tabata não coexistem
Exercicio { id, nome, prescricao, descricao?, busca, videos?: [Video], timer?: [{label, segundos}] }
Video     "ID11CARACTERES"                      # short vertical (padrão)
          { "id": "ID11CARACTERES", "tipo": "video" }   # vídeo horizontal
```

Como o app usa esses campos:
- `aba` é o rótulo curto da aba (uma palavra, até ~11 caracteres, porque são 4 abas no celular). `titulo` é o título da seção.
- `id` do treino vira o endereço (`#id`) e a chave de progresso salvo no aparelho. Trocar o id de um treino existente zera o progresso dele.
- `id` do exercício só precisa ser único dentro da fase. Reaproveite o mesmo id para o mesmo exercício em treinos diferentes.
- Fase com `rounds`: o app mostra Round 1/2/3 e um botão de descanso (`descanso`, em segundos).
- Fase com `tabata`: o app mostra "Iniciar Tabata". Os exercícios da fase se alternam a cada round de trabalho, na ordem da lista.
- `timer` cria o botão de cronômetro do exercício. Um item por etapa (ex.: lado direito e lado esquerdo = dois itens).
- `busca` alimenta o link "Nenhum serviu? Buscar no YouTube". Use termos que funcionam bem no YouTube, geralmente em inglês para exercícios de kettlebell e musculação, e em português para alongamentos genéricos.

## 2. Regras de conversão

- **Uma fase por bloco do treino** (aquecimento, força, cardio, resfriamento...). Mais de 5 fases deixam as abas apertadas; agrupe se for o caso.
- **`prescricao`** é o que o aluno precisa ler de relance: "10 por lado", "30 s de cada lado", "3 x 12", "contínuo". Séries, repetições e tempos vão aqui, nunca na descrição.
- **`descricao`** explica o movimento em 1 ou 2 frases, no imperativo. Se o texto original traz a descrição, preserve o sentido e o vocabulário.
- **Rounds**: "3 rounds, 1 min de pausa só no fim de cada round" → `rounds: 3, descanso: 60`, e a prescrição de cada exercício vira só a repetição de um round.
- **Tabata / HIIT**: "8 rounds de 20 s de esforço e 10 s de descanso" → `tabata: {rounds: 8, trabalho: 20, descanso: 10}`.
- **Lados**: "30 s de cada lado" → `timer` com duas etapas de 30 s, rotuladas com o lado.
- **Tempo total ou sustentado** ("5 minutos", "1 minuto cravado") → `timer` com uma etapa. Se o exercício é só de repetições, não crie timer.
- **Não invente**: não acrescente exercícios, séries ou cargas que o texto não traz. Se faltar algo essencial (ex.: nenhuma prescrição), pergunte.
- **Chips** resumem as regras da fase em frases curtas: "3 rounds", "Sem descanso", "20 s on / 10 s off".

## 3. Exemplo completo

Texto do usuário:

> Treino B (30 min). Aquecimento: 5 min de bike. Circuito, 4 rounds, descanso de 90 s entre rounds: goblet squat 12, flexão 15, remada com kettlebell 10 por lado.

Resultado (trecho):

```json
{
  "id": "treino-b",
  "nome": "Treino B",
  "descricao": "Circuito de 30 minutos",
  "fases": [
    {
      "id": "p1", "aba": "Aquecimento", "titulo": "Aquecimento", "tempo": "5 min",
      "intro": "Eleve a frequência cardíaca aos poucos.",
      "chips": ["5 min"],
      "exercicios": [
        { "id": "bike", "nome": "Bike", "prescricao": "5 min em ritmo leve",
          "descricao": "Pedale em ritmo leve, aumentando a cadência no fim.",
          "busca": "aquecimento bike ritmo leve",
          "timer": [{ "label": "Bike", "segundos": 300 }], "videos": [] }
      ]
    },
    {
      "id": "p2", "aba": "Circuito", "titulo": "Circuito de força", "tempo": "25 min",
      "intro": "Faça os três exercícios em sequência e descanse só no fim do round.",
      "chips": ["4 rounds", "90 s de pausa entre rounds"],
      "rounds": 4, "descanso": 90,
      "exercicios": [
        { "id": "goblet", "nome": "Goblet squat", "prescricao": "12 repetições",
          "descricao": "Agache fundo segurando o kettlebell junto ao peito.",
          "busca": "kettlebell goblet squat", "videos": ["PkCljShXeGQ"] },
        { "id": "flexao", "nome": "Flexão", "prescricao": "15 repetições",
          "descricao": "Mantenha o corpo alinhado e desça até o peito quase tocar o chão.",
          "busca": "how to push up form", "videos": [] },
        { "id": "remada", "nome": "Remada com kettlebell", "prescricao": "10 por lado",
          "descricao": "Apoie uma mão, mantenha o tronco firme e puxe o kettlebell em direção ao quadril.",
          "busca": "kettlebell single arm row", "videos": [] }
      ]
    }
  ]
}
```

(Os `videos: []` ficam vazios até a etapa de busca; a skill preenche.)

## 4. Como achar vídeos

A busca da web do Claude não devolve links de vídeo para consultas comuns, mas devolve para consultas que começam com o domínio. O padrão que funciona:

- `youtube.com/shorts <exercício em inglês> form`
- `youtube.com/shorts <exercício> how to`
- variações: `technique`, `tutorial`, `common mistakes` quando os primeiros resultados forem fracos.

Se a ferramenta de busca tiver um modo "estendido" ou mais completo, prefira-o: o modo padrão frequentemente devolve só artigos.

**Extrair o ID** (11 caracteres) do endereço:
- `youtube.com/shorts/ID` → short
- `youtube.com/watch?v=ID` ou `m.youtube.com/watch?v=ID` → vídeo (`tipo: "video"`), a menos que o título/descrição digam que é short
- `youtu.be/ID` → vídeo
- Ignore parâmetros depois do ID (`?cbrd=1`, `&pp=...`).

**Escolher** com base no título e na descrição que aparecem no resultado:
- Prefira shorts (até ~1 min) que mostrem a execução do exercício exato, de um instrutor ou canal de treino.
- Evite: variações diferentes do exercício pedido (ex.: "squat com salto" para "goblet squat"), vídeos de máquinas quando o exercício é livre, tutoriais longos, anúncios de programa de treino.
- Prefira vídeos recentes quando houver empate.
- Varie os 3 vídeos (ângulos/instrutores diferentes) em vez de três do mesmo canal.
- Se o melhor que existe é um substituto próximo (outro exercício parecido), use-o e registre isso no relatório final.

Nunca escreva um ID de memória nem invente um: só use IDs que apareceram em um resultado de busca ou que o usuário forneceu.
