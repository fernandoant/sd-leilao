from threading import Thread
from Crypto.Hash import SHA256
from Crypto.PublicKey import RSA
from Crypto import Random
from Crypto.Signature import pkcs1_15
import Pyro5.server
import Pyro5.api
import base64

from Cliente import Cliente
from Lance import Lance

def _cliente_to_dict(cliente):
    return {
        "__class__": "Cliente",
        "nome": f"{cliente.nome}",
        "chave_publica": base64.b64encode(cliente.chave_publica).decode(),
        "uri": f"{cliente.uri}",
    }

def _lance_to_dict(lance):
    cliente = _cliente_to_dict(lance.cliente)
    return {
        "__class__": "Lance",
        "cliente": cliente,
        "valor_lance" : lance.valor,
    }

Pyro5.api.register_class_to_dict(Cliente, _cliente_to_dict)
Pyro5.api.register_class_to_dict(Lance, _lance_to_dict)


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
        self.chave_privada = pkcs1_15.new(self.par_chaves)
        self.chave_publica = self.par_chaves.publickey().export_key()
        self.servidor = servidor


    def cadastrar(self):
        cliente = self.__get_cliente()
        cadastrado = self.servidor.cadastrar_usuario(cliente)
        if cadastrado is True:
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
            "uri_criador": str(self.uri),
            "nome": nome,
            "descricao": descricao,
            "preco_minimo": preco_minimo,
            "duracao": duracao,
        }

        leilao_assinado = self._assinar(leilao)

        self.servidor.criar_leilao(self.__get_cliente(), leilao, leilao_assinado)

    def dar_lance(self):
        id_leilao = int(input("Insira o id do leilao: "))
        valor_lance = float(input("Insira o valor do lance: "))
        
        lance = {
            "cliente": {
                "nome": self.nome,
                "chave_publica": base64.b64encode(self.chave_publica).decode(),
                "uri": str(self.uri)
            },
            "valor_lance": valor_lance
        }

        lance_assinado = self._assinar(lance)

        self.servidor.dar_lance(id_leilao, lance, lance_assinado)

    @Pyro5.api.expose
    @Pyro5.api.oneway
    def notificar(self, msg):
        print(msg)

    def __loopThread(self):
        self.daemon.requestLoop()

    def __get_cliente(self):
        return Cliente(self.nome, self.chave_publica, self.uri)
    
    def _assinar(self, conteudo):
        hash_conteudo = SHA256.new(str(conteudo).encode('utf-8'))
        conteudo_assinado = self.chave_privada.sign(hash_conteudo)
        conteudo_assinado = base64.b64encode(conteudo_assinado).decode()
        return conteudo_assinado

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
    usuario.cadastrar()

    while True:
        op = menu()
        if op is None:
            continue

        if op == 1:
            usuario.listar_leiloes()
        elif op == 2:
            usuario.criar_leilao()
        elif op == 3:
            usuario.dar_lance()
        elif op == 0:
            usuario.daemon.close()
            break

    usuario.thread.join()
