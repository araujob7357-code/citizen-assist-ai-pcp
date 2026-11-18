# Citizen Assist AI — Pensamento Computacional (PCP)

**Integrante:** Beatriz da Silva Araújo — RM 570619
**Público e problema:** O assistente atende cidadãos que precisam de informações sobre documentos, saúde e trabalho (RG, CPF, SUS, carteira de trabalho, etc), resolvendo a dificuldade de achar informações oficiais e confiáveis de forma rápida.

**ODS Relacionados:** ODS 16 (Paz, Justiça e Instituições Eficazes) e ODS 3 (Saúde e Bem-Estar).

## 🚀 Como executar
No terminal, rode:
`python main.py`

## 🧮 Regra de pontuação usada
A busca compara a pergunta normalizada (sem acentos e pontuação) com as orientações:
- **+3 pontos** para cada palavra-chave da orientação que aparece na pergunta.
- **+1 ponto** para palavras da pergunta (4+ letras) que aparecem no título.
- **Confiança ALTA:** 6 pontos ou mais.
- **Confiança MÉDIA:** 3 a 5 pontos.
- **Não encontrado:** menos de 3 pontos.

## 🧪 Resultado do teste com usuários
- **Testado com:** 3 pessoas (10 atendimentos no total).
- **Tempo médio:** 15 segundos por dúvida.
- **Acerto:** 80% das dúvidas foram encontradas.
- **Facilidade de uso:** Nota média 4.5 (de 1 a 5).
- **Dúvidas sem solução:** "Como tirar passaporte" (não está na base).
- **Melhoria feita:** Adicionamos a palavra "cns" nas palavras-chave do cartão SUS após um usuário digitar essa sigla e o sistema não achar.

## ⚠️ Limitações
O assistente não substitui os canais oficiais. Ele busca por regras exatas de palavras-chave, o que significa que sinônimos muito distantes (ex: "documento de identidade" em vez de "RG") podem não ser encontrados com confiança alta.

## 📺 Vídeo Técnico
Assista à explicação do código e demonstração no YouTube: [COLE O LINK AQUI]
