from threading import Thread
from Cliente import Cliente
from Lance import Lance

from Crypto.Hash import SHA256
from Crypto.PublicKey import RSA
from Crypto import Random

import Pyro5.server
import Pyro5.api

def __cliente_to_dict(cliente):
    return {
        "__class__": "Cliente",
        "nome": f"{cliente.nome}",
        "chave_publica": f"{cliente.chave_publica}",
        "uri": f"{cliente.uri}",
    }

def __lance_to_dict(lance):
    cliente = __cliente_to_dict(lance.cliente)
    return {
        "__class__": "Lance",
        "cliente": cliente,
        "valor_lance" : lance.valor,
    }

Pyro5.api.register_class_to_dict(Cliente, __cliente_to_dict)
Pyro5.api.register_class_to_dict(Lance, __lance_to_dict)

 
class Usuario(Cliente):

    def __init__(self, servidor, nome_cliente):
        random_seed = Random.new().read

        self.daemon = Pyro5.server.Daemon()
        self.uri = self.daemon.register(self)
        self.thread = Thread(target=self.__loopThread)
        self.thread.daemon = True
        self.nome = nome_cliente
        self.thread.start()
        self.par_chaves = RSA.generate(1024, random_seed)
        self.chave_publica = self.par_chaves.publickey()
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

        leilao = {
            "uri_criador": self.uri,
            "nome": nome,
            "descricao": descricao,
            "preco_minimo": preco_minimo,
            "duracao": duracao,
        }

        value_hash = SHA256.new(str(leilao).encode('utf-8')).digest()
        signed_value = self.par_chaves.sign(value_hash, '')

        self.servidor.criar_leilao(self.__get_cliente(), leilao, signed_value)

    def dar_lance(self):
        id_leilao = int(input("Insira o id do leilao: "))
        valor_lance = float(input("Insira o valor do lance: "))
        lance = Lance(self.__get_cliente(), valor_lance)
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
