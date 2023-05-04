import Pyro5.api
import Pyro5.server
import base64

from Crypto.Hash import SHA256
from Crypto.Signature import pkcs1_15
from Crypto.PublicKey import RSA

from threading import Thread

from Produto import Produto
from Leilao import Leilao
from Cliente import Cliente
from Lance import Lance

DEBUG = 0

def __dict_to_cliente(_, dict_cliente):
    nome = dict_cliente.get("nome")
    chave = dict_cliente.get("chave_publica")
    uri = dict_cliente.get("uri")
    return Cliente(nome, chave, uri)

def __dict_to_lance(_, dict_lance):
    cliente = __dict_to_cliente("Cliente", dict_lance.get("cliente"))
    valor = dict_lance.get("valor_lance")
    return Lance(cliente, valor)

Pyro5.api.register_dict_to_class("Cliente", __dict_to_cliente)
Pyro5.api.register_dict_to_class("Lance", __dict_to_lance)

@Pyro5.api.behavior(instance_mode="single")
class Servidor():
    def __init__(self):
        self.clientes = []
        self.leiloes = []

    @Pyro5.api.expose
    #@Pyro5.api.callback
    def cadastrar_usuario(self, cliente):
        if DEBUG == 1:
            print()
            print(f"Cadastrando usuário {cliente.nome}")

        # Checa se o usuário já está cadastrado
        res = list(filter(lambda x: (x.uri == cliente.uri), self.clientes))

        if not res:
            self.clientes.append(cliente)
            return True
        
        return False

    @Pyro5.api.expose
    #@Pyro5.api.callback
    def listar_leiloes(self):
        if DEBUG == 1:
            print("\nListando leilões cadastrados")
        
        if len(self.leiloes) == 0:
            return "Não há leilões ativos no momento"
        
        ret = ""
        for leilao in self.leiloes:
            if leilao.duracao != -1:
                ret += str(leilao) + '\n'

        return ret

    @Pyro5.api.expose
    #@Pyro5.api.callback
    def criar_leilao(self, criador, infos_leilao, leilao_assinado):
        if DEBUG == 1:
            print(f"\nCriando leilão {len(self.leiloes) + 1}")
        if infos_leilao['preco_minimo'] <= 0:
            return False

        cliente = list(filter(lambda x: (x.uri == criador.uri), self.clientes))
        if (len(cliente) != 1):
            return False
        
        cliente = cliente[0]
        leilao_assinado = base64.b64decode(leilao_assinado)

        if not (self.__verificar_validade(cliente.chave_publica, infos_leilao, leilao_assinado)):
            return False
        
        nome = infos_leilao['nome']
        descricao = infos_leilao['descricao']
        preco_minimo = infos_leilao['preco_minimo']
        duracao = infos_leilao['duracao']
        
        # Cria um leilão
        id_leilao = len(self.leiloes) + 1
        produto = Produto(nome, descricao, preco_minimo)
        leilao = Leilao(id_leilao, criador, produto, duracao, self.notificar_clientes)

        # Inicia a thread (Contador) do leilão e o adiciona na lista de leilões
        leilao.iniciar_leilao()
        self.leiloes.append(leilao)

        msg = f"Leilão {id_leilao} - novo produto registrado! Vendedor {criador.nome}, Produto:{nome}, Preço inicial: {preco_minimo}, Duração: {duracao}"
        self.notificar_clientes(msg, self.clientes)
        return True

    @Pyro5.api.expose
    #@Pyro5.api.callback
    def dar_lance(self, id_leilao, dict_lance, lance_assinado):
        nome = dict_lance['cliente']['nome']
        chave_pub = dict_lance['cliente']['chave_publica']
        uri_cliente = dict_lance['cliente']['uri']
        cliente = Cliente(nome, chave_pub, uri_cliente)
        lance = Lance(cliente, dict_lance['valor_lance'])

        if DEBUG == 1:
            print(f"\nLance recebido, leilão {id_leilao}, cliente {lance.cliente.nome}")
        if id_leilao <= 0 or id_leilao > len(self.leiloes):
            return False
        
        cliente = list(filter(lambda x: (x.uri == lance.cliente.uri), self.clientes))
        if (len(cliente) != 1):
            return False
        
        cliente = cliente[0]
        lance_assinado = base64.b64decode(lance_assinado)

        if not (self.__verificar_validade(cliente.chave_publica, dict_lance, lance_assinado)):
            return False
        
        leilao = self.leiloes[id_leilao - 1]
        return leilao.dar_lance(lance)

    def notificar_clientes(self, msg, lista):
        for cliente in lista:
            obj_cliente = Pyro5.api.Proxy(cliente.uri)
            obj_cliente.notificar(msg)

    def __verificar_validade(self, chave_publica, conteudo, hash_assinado):
        chave_publica = base64.b64decode(chave_publica).decode()
        hash_conteudo = SHA256.new(str(conteudo).encode('utf-8'))
        assinatura = pkcs1_15.new(RSA.import_key(chave_publica))

        try:
            assinatura.verify(hash_conteudo, hash_assinado)
            print()
            print("Assinatura válida.")
            return True
        except (ValueError, TypeError):
            print()
            print("Assinatura inválida")
            return False

def menu():
    while True:
        print("Digite 0 para encerrar o servidor!")
        option = input("> ")

        if not option.isdigit() or int(option) != 0:
            print("Opção inválida, tente novamente!") 
        else:
            deamon.close()
            return

if __name__ == "__main__":
    servidor = Servidor()
    deamon = Pyro5.server.Daemon()
    ns = Pyro5.api.locate_ns()
    uri = deamon.register(servidor)
    ns.register("servidor", uri)
    thread = Thread(target=deamon.requestLoop)
    thread.start()

    print("Servidor iniciado...")
    menu()
    thread.join()