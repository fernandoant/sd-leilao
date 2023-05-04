import Pyro5.api
import Pyro5.server

from Crypto.Hash import SHA256
from Crypto.Signature import pkcs1_15
from Crypto.PublicKey import RSA

from Produto import Produto
from Leilao import Leilao
from Cliente import Cliente
from Lance import Lance


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
            print(f"Cadastrando usuário {cliente.nome}")

        # Checa se o usuário já está cadastrado
        res = list(filter(lambda x: (x.uri == cliente.uri), self.clientes))
        
        if not res:
            self.clientes.append(cliente)
            return True
        
        return False

    @Pyro5.api.expose
    @Pyro5.api.callback
    def listar_leiloes(self):
        if DEBUG == 1:
            print("Listando leilões cadastrados")
        ret = ""
        for leilao in self.leiloes:
            ret += str(leilao) + '\n'
        return ret

    @Pyro5.api.expose
    @Pyro5.api.oneway
    def criar_leilao(self, criador, infos_leilao, signed_hash):
        if DEBUG == 1:
            print(f"Criando leilão {len(self.leiloes) + 1}")
        if infos_leilao['preco_minimo'] <= 0:
            return

        cliente = list(filter(lambda x: (x.uri == criador.uri), self.clientes))
        if (len(cliente) != 1):
            msg = "Houve um problema ao criar o leilão!"
            self.notificar_clientes(msg, tuple(criador))
            return
        
        cliente = cliente[0]

        if not (self.__verificar_validade(cliente.chave_publica, infos_leilao, signed_hash)):
            msg = "Não foi possível validar a criptografia do conteúdo"
            self.notificar_clientes(msg, tuple(cliente))
            return
        
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

    @Pyro5.api.expose
    @Pyro5.api.oneway
    def dar_lance(self, id_leilao, lance):
        if DEBUG == 1:
            print(f"Lance recebido, leilão {id_leilao}, cliente {lance.cliente.nome}")
        if id_leilao <= 0 or id_leilao > len(self.leiloes):
            return
        
        leilao = self.leiloes[id_leilao - 1]
        leilao.dar_lance(lance)

    def notificar_clientes(self, msg, lista):
        for cliente in lista:
            obj_cliente = Pyro5.api.Proxy(cliente.uri)
            obj_cliente.notificar(msg)
    def __verificar_validade(self, pub_key, content, signed_hash):
        content_hash = SHA256.new(str(content).encode('utf-8'))
        try:
            pkcs1_15.new(RSA.import_key(pub_key)).verify(content_hash, signed_hash)
            print("Assinatura válida.")
            return True
        except:
            print("Assinatura inválida.")
            return False



if __name__ == "__main__":
    servidor = Servidor()
    deamon = Pyro5.server.Daemon()
    ns = Pyro5.api.locate_ns()
    uri = deamon.register(servidor)
    ns.register("servidor", uri)

    deamon.requestLoop()
    print("Aplicação Finalizada")