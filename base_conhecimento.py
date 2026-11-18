import json
from orientacao import Orientacao

class BaseConhecimento:
    def __init__(self, caminho):
        self.caminho = caminho
        self.orientacoes = []

    def carregar(self):
        try:
            with open(self.caminho, "r", encoding="utf-8") as f:
                dados = json.load(f)
                self.orientacoes = [Orientacao(d) for d in dados]
        except FileNotFoundError:
            print("Erro: Arquivo JSON não encontrado.")
        except json.JSONDecodeError:
            print("Erro: O arquivo JSON está corrompido.")

    def categorias(self):
        return sorted(list(set(o.categoria for o in self.orientacoes)))

    def por_categoria(self, categoria):
        return [o for o in self.orientacoes if o.categoria == categoria]

    def normalizar(self, texto):
        acentos = {"á": "a", "à": "a", "ã": "a", "â": "a", "é": "e", "ê": "e", "í": "i", "ó": "o", "õ": "o", "ô": "o", "ú": "u", "ç": "c"}
        texto = texto.lower().strip()
        for letra, troca in acentos.items():
            texto = texto.replace(letra, troca)
        # Substitui underline e pontuações por espaço
        for sinal in "?!.,;:()_":
            texto = texto.replace(sinal, " ")
        return " " + " ".join(texto.split()) + " "

    def pontuar(self, pergunta, orientacao):
        pontos = 0
        p_norm = self.normalizar(pergunta)
        t_norm = self.normalizar(orientacao.titulo)
        
        for kw in orientacao.palavras_chave:
            if self.normalizar(kw) in p_norm:
                pontos += 3
                
        for palavra in p_norm.split():
            if len(palavra) >= 4 and palavra in t_norm:
                pontos += 1
        return pontos

    def buscar(self, pergunta):
        resultados = []
        for o in self.orientacoes:
            pontos = self.pontuar(pergunta, o)
            if pontos > 0:
                resultados.append((pontos, o))
        # Ordena da maior pontuação para a menor
        resultados.sort(key=lambda x: x[0], reverse=True)
        return resultados
