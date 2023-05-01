import Pyro5.server
import Pyro5.api
from threading import Thread
from Cliente import Cliente
Pyro5.api.register_class_to_dict(Cliente, lambda x: {"nome": f"{x.nome}", "chave_publica": f"{x.chave_publica}", "uri": f"{x.uri}"})

class Usuario(Cliente):
    def __init__(self, servidor, nome_cliente):
        self.daemon = Pyro5.server.Daemon()
        self.uri = self.daemon.register(self)
        self.thread = Thread(target=self.__loopThread)
        self.thread.daemon = True
        self.nome = nome_cliente
        self.thread.start()
      #gerar chave assicrona
        self.chave_publica = None
        self.servidor = servidor


    def cadastrar(self):
        cliente = Cliente(self.nome, self.chave_publica, self.uri)
        cadastrado = self.servidor.cadastrar_usuario(cliente)
        if cadastrado == True:
            print("Usuario cadastrado com sucesso!!")
        else:
            print("Não foi possivel se cadastrar!!")

    def listar_leiloes(self):
        print(self.servidor.listar_leiloes())

    def criar_leilao(self):
        nome = str(input("Insira nome do produto:"))
        descricao = str(input("Insira descriçao do produto:"))
        preco_minimo = float(input("Insira o lance minimo:"))
        duracao = int(input("Insira a duração do leilao:"))
        cliente = Cliente(self.nome, self.chave_publica, self.uri)
        self.servidor.criar_leilao(cliente, nome, descricao, preco_minimo, duracao)

    def dar_lance(self):
        cliente = Cliente(self.nome, self.chave_publica, self.uri)
        id_leilao = int(input("Insira o id do leilao: "))
        lance = float(input("Insira o valor do lance: "))
        self.servidor.dar_lance(id_leilao, cliente, lance)


    @Pyro5.api.expose
    @Pyro5.api.oneway
    def notificar(self, msg):
        print(msg)

    def __loopThread(self):
        self.daemon.requestLoop()

if __name__ == "__main__":
    ns = Pyro5.api.locate_ns()
    uri = ns.lookup("servidor")
    servidor = Pyro5.api.Proxy(uri)
    usuario = Usuario(servidor, "Jonas")
    usuario.chave_publica = "ola"
    usuario.cadastrar()
    usuario.criar_leilao()
    usuario.thread.join()
