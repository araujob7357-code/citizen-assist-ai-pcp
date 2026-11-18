class Orientacao:
    def __init__(self, dados):
        self.id = dados.get("id")
        self.categoria = dados.get("categoria")
        self.titulo = dados.get("titulo")
        self.palavras_chave = dados.get("palavras_chave", [])
        self.resposta = dados.get("resposta")
        self.documentos = dados.get("documentos", [])
        self.onde = dados.get("onde")
        self.fonte = dados.get("fonte")
        self.verificado_em = dados.get("verificado_em")
        self.exemplos = dados.get("exemplos", [])

    def exibir(self):
        print(f"\n>> {self.titulo} [{self.categoria}]")
        print(f"Resposta: {self.resposta}")
        if self.documentos:
            print("Documentos necessários:")
            for doc in self.documentos:
                print(f"- {doc}")
        print(f"Onde: {self.onde}")
        print(f"Fonte: {self.fonte} (verificado em {self.verificado_em})")
        print("Aviso: este assistente NÃO é um canal oficial.")

    def exibir_alternativa(self, index):
        print(f"  [{index}] {self.titulo} [{self.categoria}]")
