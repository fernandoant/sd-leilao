import Pyro5.server
import Pyro5.api
from threading import Thread
from Cliente import Cliente

class Usuario(Cliente):
    def __init__(self, servidor, nome_cliente):
        self.daemon = Pyro5.server.Daemon()
        self.uri = self.daemon.register(self)
     #   self.thread = Thread(target=self.receber_notificacao)
     #   self.thread.daemon = True
        self.nome = nome_cliente
      #gerar chave assicrona
        self.chave_publica = None
        self.servidor = servidor


    def cadastrar(self):
        self.servidor.cadastrar_usuario(Cliente(self))


    def listar_leiloes(self):
        self.servidor.listar_leiloes(Cliente(self))

    def criar_leilao(self):
        nome = str(input("Insira nome do produto:"))
        descricao = str(input("Insira descriçao do produto:"))
        preco_minimo = float(input("Insira o lance minimo:"))
        duracao = int(input("Insira a duração do leilao:"))
        self.servidor.criar_leilao(Cliente(self), nome, descricao, preco_minimo, duracao)

    def dar_lance(self):
        id_leilao = int(input("Insira o id do leilao: "))
        lance = float(input("Insira o valor do lance: "))
        self.servidor.dar_lance(id_leilao, Cliente(self), lance)


    @Pyro5.api.expose
    @Pyro5.api.oneway
    def notificar(self, msg):
        print(msg)


