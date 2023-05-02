from threading import Thread
from Cliente import Cliente
from Lance import Lance

import Pyro5.server
import Pyro5.api
Pyro5.api.register_class_to_dict(Cliente, lambda x: {"nome": f"{x.nome}", "chave_publica": f"{x.chave_publica}", "uri": f"{x.uri}"})
#Pyro5.api.register_class_to_dict(Lance, lambda x: {"nome": f"{x.nome}", "chave_publica": f"{x.chave_publica}", "uri": f"{x.uri}"})
 
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
        cadastrado = self.servidor.cadastrar_usuario(self.__get_cliente())
        if cadastrado == True:
            print("Usuario cadastrado com sucesso!!\n")
        else:
            print("Não foi possivel se cadastrar!!\n")

    def listar_leiloes(self):
        print(self.servidor.listar_leiloes())

    def criar_leilao(self):
        nome = str(input("Insira nome do produto: "))
        descricao = str(input("Insira descriçao do produto: "))
        preco_minimo = float(input("Insira o lance minimo: "))
        duracao = int(input("Insira a duração do leilao: "))
        self.servidor.criar_leilao(self.__get_cliente(), nome, descricao, preco_minimo, duracao)

    def dar_lance(self):
        id_leilao = int(input("Insira o id do leilao: "))
        valor_lance = float(input("Insira o valor do lance: "))
        lance = Lance(self.__get_cliente, valor_lance)
        self.servidor.dar_lance(id_leilao, lance)


    @Pyro5.api.expose
    @Pyro5.api.oneway
    def notificar(self, msg):
        print(msg)

    def __loopThread(self):
        self.daemon.requestLoop()

    def __get_cliente(self):
        return Cliente(self.nome, self.chave_publica, self.uri)

def menu():
    print("O que deseja fazer?")
    print("1) Listar leilões ativos")
    print("2) Criar leilão")
    print("3) Dar lance em um leilão ativo")
    print("0) Sair")
    op = input("> ")
    if not op.isdigit() or int(op) < 0 or int(op) > 4:
        print("Opção inválida, tente novamente!")
        return None
    return int(op)

if __name__ == "__main__":
    ns = Pyro5.api.locate_ns()
    uri = ns.lookup("servidor")
    servidor = Pyro5.api.Proxy(uri)

    nome_cliente = str(input("Digite seu nome: "))
    usuario = Usuario(servidor, nome_cliente)
    usuario.chave_publica = nome_cliente
    usuario.cadastrar()

    while True:
        op = menu()
        if op == None:
            continue

        if op == 1:
            usuario.listar_leiloes()
        elif op == 2:
            usuario.criar_leilao()
        elif op == 3:
            usuario.dar_lance()
        elif op == 0:
            break

    usuario.thread.join()
