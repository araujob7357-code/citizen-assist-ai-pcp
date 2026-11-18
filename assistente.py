import csv
import json
import time
import os

CAMPOS_CSV = ["data", "origem", "pergunta", "id_orientacao", "encontrou",
              "ajudou", "tentativas", "tempo_segundos", "nota_facilidade"]


class Assistente:
    def __init__(self, nome, base):
        self.nome = nome
        self.base = base
        self.historico = []
        self.tempo_inicio = 0
        self.nota_facilidade = 0
        self.tentativas = 0
        self.arquivo_historico = "data/historico.json"
        self._carregar_historico()

    def _carregar_historico(self):
        os.makedirs("data", exist_ok=True)
        try:
            if os.path.exists(self.arquivo_historico):
                with open(self.arquivo_historico, "r", encoding="utf-8") as f:
                    self.historico = json.load(f)
        except Exception:
            self.historico = []

    def _salvar_historico(self):
        os.makedirs("data", exist_ok=True)
        with open(self.arquivo_historico, "w", encoding="utf-8") as f:
            json.dump(self.historico, f, ensure_ascii=False, indent=2)

    def definir_nota(self, nota):
        self.nota_facilidade = nota
        for h in self.historico:
            if not h.get("nota_facilidade"):
                h["nota_facilidade"] = nota
        self._salvar_historico()

    def registrar(self, origem, pergunta, id_orientacao, encontrou, ajudou):
        tempo_total = round(time.time() - self.tempo_inicio, 1)
        registro = {
            "data": time.strftime("%Y-%m-%d %H:%M:%S"),
            "origem": origem,
            "pergunta": pergunta,
            "id_orientacao": id_orientacao,
            "encontrou": encontrou,
            "ajudou": ajudou,
            "tentativas": max(self.tentativas, 1),
            "tempo_segundos": tempo_total,
            "nota_facilidade": self.nota_facilidade
        }
        self.historico.append(registro)
        self._salvar_historico()
        if ajudou:
            self.tentativas = 0

    def verificar_dados_pessoais(self, texto):
        if "@" in texto or sum(c.isdigit() for c in texto) >= 8:
            return True
        return False

    def perguntar_sn(self):
        while True:
            resp = input("\nEssa orientação respondeu sua dúvida? (s/n): ").strip().lower()
            if resp in ["s", "n"]:
                return resp == "s"
            print("Entrada inválida. Digite 's' para sim ou 'n' para não.")

    def perguntar(self):
        self.tempo_inicio = time.time()
        pergunta = input("\nDigite sua dúvida (ou 0 para voltar): ")

        if pergunta.strip() == "0":
            return

        if not pergunta.strip():
            print("Resposta vazia. Tente novamente.")
            return

        if self.verificar_dados_pessoais(pergunta):
            print("Atenção: não digite CPF, telefone ou e-mail. Reescreva.")
            return

        self.tentativas += 1
        resultados = self.base.buscar(pergunta)

        if not resultados or resultados[0][0] < 3:
            print("Não encontrei uma orientação exata. Tente outras palavras ou navegue pelas categorias (opção 2 do menu).")
            self.registrar("pergunta", pergunta, None, False, False)
            return

        melhor_pontos, melhor_orientacao = resultados[0]
        confianca = "ALTA" if melhor_pontos >= 6 else "MÉDIA"

        print(f"\nConfiança da resposta: {confianca} ({melhor_pontos} pontos)")
        melhor_orientacao.exibir()

        if len(resultados) > 1:
            print("\nAlternativas encontradas:")
            for i, (pts, alt) in enumerate(resultados[1:3], 1):
                alt.exibir_alternativa(i)

        ajudou = self.perguntar_sn()
        self.registrar("pergunta", pergunta, melhor_orientacao.id, True, ajudou)

    def navegar(self):
        while True:
            print("\n--- CATEGORIAS ---")
            cats = self.base.categorias()
            for i, c in enumerate(cats, 1):
                print(f"{i} - {c}")
            print("0 - Voltar")

            esc = input("Escolha uma categoria: ").strip()
            if esc == "0":
                return

            if esc.isdigit() and 1 <= int(esc) <= len(cats):
                cat_escolhida = cats[int(esc) - 1]
                orientacoes = self.base.por_categoria(cat_escolhida)

                while True:
                    print(f"\n--- {cat_escolhida.upper()} ---")
                    for i, o in enumerate(orientacoes, 1):
                        print(f"{i} - {o.titulo}")
                    print("0 - Voltar")

                    esc2 = input("Escolha uma orientação: ").strip()
                    if esc2 == "0":
                        break

                    if esc2.isdigit() and 1 <= int(esc2) <= len(orientacoes):
                        self.tempo_inicio = time.time()
                        o_escolhida = orientacoes[int(esc2) - 1]
                        self.tentativas += 1
                        print("\nConfiança: ALTA (via categoria)")
                        o_escolhida.exibir()
                        ajudou = self.perguntar_sn()
                        self.registrar("categoria", o_escolhida.titulo, o_escolhida.id, True, ajudou)
                        break
                    else:
                        print("Opção inválida. Digite um número da lista.")
            else:
                print("Opção inválida. Digite um número da lista.")

    def mostrar_catalogo(self):
        print("\n" + "=" * 50)
        print("  O QUE VOCÊ PODE PERGUNTAR (exemplos)")
        print("=" * 50)
        for cat in self.base.categorias():
            print(f"\n[{cat.upper()}]")
            for o in self.base.por_categoria(cat):
                if o.exemplos:
                    print(f'  - "{o.exemplos[0]}"')
        print("\nDigite algo parecido na opção 1 do menu.")

    def indicadores(self):
        if not self.historico:
            print("Nenhum atendimento registrado.")
            return

        total = len(self.historico)
        encontrados = sum(1 for h in self.historico if h.get("encontrou"))
        ajudou = sum(1 for h in self.historico if h.get("ajudou"))
        tentativas_totais = sum(h.get("tentativas", 1) for h in self.historico)
        tempo_medio = sum(h.get("tempo_segundos", 0) for h in self.historico) / total

        notas = [h.get("nota_facilidade") for h in self.historico if h.get("nota_facilidade", 0) > 0]
        facilidade_media = sum(notas) / len(notas) if notas else 0

        print("\n--- INDICADORES GERAIS ---")
        print(f"Total de atendimentos registrados: {total}")
        print(f"1. Resposta encontrada: {round((encontrados / total) * 100, 1)}%")
        if encontrados > 0:
            print(f"2. Taxa de acerto (ajudou): {round((ajudou / encontrados) * 100, 1)}%")
        else:
            print("2. Taxa de acerto (ajudou): 0%")
        print(f"3. Tempo médio de resposta: {round(tempo_medio, 1)} segundos")
        print(f"4. Tentativas por atendimento: {round(tentativas_totais / total, 1)}")
        if facilidade_media > 0:
            print(f"5. Facilidade de uso (1 a 5): {round(facilidade_media, 1)}")
        else:
            print("5. Facilidade de uso (1 a 5): ainda não avaliada")

        sem_solucao = [h["pergunta"] for h in self.historico if not h.get("encontrou")]
        print(f"6. Dúvidas sem solução: {len(sem_solucao)}")
        for d in sorted(set(sem_solucao)):
            print(f"   - {d}")

    def exportar_csv(self):
        if not self.historico:
            print("Nenhum atendimento para exportar.")
            return
        os.makedirs("data", exist_ok=True)
        with open("data/atendimentos.csv", "w", newline="", encoding="utf-8") as f:
            writer = csv.DictWriter(f, fieldnames=CAMPOS_CSV, extrasaction="ignore", restval="")
            writer.writeheader()
            writer.writerows(self.historico)
        print("Histórico exportado para data/atendimentos.csv")
