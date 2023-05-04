class Produto:
    def __init__(self, nome, descricao, preco_minimo):
        self.nome = nome
        self.descricao = descricao
        self.preco_minimo = preco_minimo

    def __str__(self):
        return f"Nome do Produto: {self.nome}, Descrição do Produto: {self.descricao}"