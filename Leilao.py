from Produto import Produto
import time
class Leilao:
    def __init__(self, id, criador, produto:Produto, duracao, notificar):
        self.id = id
        self.criador = criador
        self.produto = produto
        self.list_Cliente = []
        self.list_lance = []
        self.lance_atual = produto.preco_minimo
        self.duracao = duracao
        self.vencedor = None
        self.notificar = notificar

    def comecar_leilao(self):
        tempo_inicio = time.perf_counter()
        tempo_atual = time.perf_counter()
        while(tempo_atual - tempo_inicio < self.duracao):
            if len(self.list_lance > 0):
                cliente, lance = self.list_lance.pop(0).items()
                self.lance_atual = lance
                self.vencedor = cliente
                msg = f"Leilão {id} - Lance recebido! Cliente {cliente.nome},Produto:{self.produto}, Lance: {lance}"
                self.notificar_clientes(msg)
            tempo_atual = time.perf_counter()
        msg = f"Leilão {self.id} finalizado! Produto vendido: {self.produto}, Preço de Venda: {self.lance_atual}, Vencedor: {self.vencedor}"
        self.notificar_clientes(msg)
        return True

    def dar_lance(self, cliente, lance):
        if lance <= self.lance_atual:
            return False
        buscarCliente = filter(lambda x: (x.id == cliente.id), self.listCliente)
        if buscarCliente is None:
            self.listCliente.append(cliente)
        self.listLance.append({cliente: lance})

    def listar_lance_atual(self):
        return self.lance_atual

    def notificar_clientes(self, msg):
        self.notificar(msg, self.list_Cliente)


