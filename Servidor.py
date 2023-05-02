import Pyro5.api
import Pyro5.server

from Produto import Produto
from Leilao import Leilao
from Cliente import Cliente

DEBUG = 1

@Pyro5.api.behavior(instance_mode="single")
class Servidor():
    def __init__(self):
        self.clientes = []
        self.leiloes = []

    @Pyro5.api.expose
    @Pyro5.api.callback
    def cadastrar_usuario(self, cliente):
        if DEBUG == 1:
            print(f"Cadastrando usuário {cliente['nome']}")
        cliente = Cliente(cliente['nome'], cliente['chave_publica'], cliente['uri'])
        res = list(filter(lambda x: (x.chave_publica == cliente.chave_publica), self.clientes))
        if not res:
            self.clientes.append(cliente)
            return True
        return False

    @Pyro5.api.expose
    @Pyro5.api.callback
    def listar_leiloes(self):
        if DEBUG == 1:
            print("Listando leilões cadastrados")
        ret = [x.produto.nome for x in self.leiloes]
        return ret
        #return self.leiloes

    @Pyro5.api.expose
    @Pyro5.api.oneway
    def criar_leilao(self, criador, nome, descricao, preco_minimo, duracao):
        if DEBUG == 1:
            print(f"Criando leilão {len(self.leiloes) + 1}")
        if preco_minimo <= 0:
            return
        id_leilao = len(self.leiloes) + 1
        produto = Produto(nome, descricao, preco_minimo)
        leilao = Leilao(id_leilao, criador, produto, duracao, self.notificar_clientes)
        leilao.iniciar_leilao()
        self.leiloes.append(leilao)
        msg = f"Leilão {id_leilao} - novo produto registrado! Vendedor {criador['nome']}, Produto:{nome}, Preço inicial: {preco_minimo}, Duração: {duracao}"
        self.notificar_clientes(msg, self.clientes)

    @Pyro5.api.expose
    @Pyro5.api.oneway
    def dar_lance(self, id_leilao, lance):
        if DEBUG == 1:
            print(f"Lance recebido, leilão {id_leilao}, cliente {lance.cliente.nome}")
      # utilizar chave_publica enviada durante o cadastro para validar o lance
        if id_leilao <= 0 or id_leilao > len(self.leiloes):
            return
        leilao = self.leiloes[id_leilao - 1]
        leilao.dar_lance(lance)

    def notificar_clientes(self, msg, lista):
        for cliente in lista:
            obj_cliente = Pyro5.api.Proxy(cliente.uri)
            obj_cliente.notificar(msg)


if __name__ == "__main__":
    servidor = Servidor()
    deamon = Pyro5.server.Daemon()
    ns = Pyro5.api.locate_ns()
    uri = deamon.register(servidor)
    ns.register("servidor", uri)

    deamon.requestLoop()
    print("Aplicação ativa!!")