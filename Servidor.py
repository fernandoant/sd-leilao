from Cliente import Cliente
import threading
from Produto import Produto
from Leilao import Leilao
import Pyro5.api


@Pyro5.behavior(instance_mode="single")
class Servidor():
    def __init__(self):
        self.clientes = []
        self.leiloes = []

    def cadastrar_usuario(self, cliente):
        buscarCliente = filter(lambda x: (x.chave_publica == cliente.chave_publica), self.clientes)
        if buscarCliente is None:
            self.clientes.append(cliente)

    def listar_leiloes(self):
        map(lambda x: print(x), self.leiloes)

    def criar_leilao(self, criador, nome, descricao, preco_minimo, duracao):
        if preco_minimo <= 0:
            return
        id = len(self.leiloes) + 1
        produto = Produto(nome, descricao, preco_minimo)
        leilao = Leilao(id, criador, produto, duracao, self.notificar_clientes)
        leilao.iniciar_leilao()
        self.leiloes.append(leilao)
        msg = f"Leilão {id} - novo produto registrado! Vendedor {criador.nome},Produto:{nome}, Preço inicial: {preco_minimo} , Duração: {duracao}"
        self.notificar_clientes(msg, self.clientes)
    def dar_lance(self, id_leilao, cliente, lance):
      # utilizar chave_publica enviada durante o cadastro para validar o lance
        if id_leilao <= 0 or id_leilao > len(self.leiloes):
            return
        leilao = self.leiloes[id_leilao - 1]
        leilao.dar_lance(cliente, lance)

    def notificar_clientes(self, msg, lista):
        for cliente in lista:
            obj_cliente = Pyro5.api.Proxy(cliente.uri)
            obj_cliente.notificar(msg)
