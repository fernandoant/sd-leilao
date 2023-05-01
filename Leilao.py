from Produto import Produto
import time
from threading import Thread
class Leilao(Thread):
    def __init__(self, id, criador, produto:Produto, duracao, notificar):
        self.id = id
        self.criador = criador
        self.produto = produto
        self.list_Cliente = []
        self.list_lance = []
        self.lance_atual = produto.preco_minimo
        self.duracao = duracao
        self.tempo_inicio = 0
        self.vencedor = None
        self.notificar = notificar
        self.thread = Thread(target=self._iniciar_leilao)
        self.list_Cliente.append(criador)

    def iniciar_leilao(self):
        self.thread.start()
    def _iniciar_leilao(self):
        self.tempo_inicio = time.perf_counter()
        tempo_atual = time.perf_counter()
        while(tempo_atual - self.tempo_inicio < self.duracao):
            if len(self.list_lance) > 0:
                cliente, lance = self.list_lance.pop(0).items()
                self.lance_atual = lance
                self.vencedor = cliente
                msg = f"Leilão {id} - Lance recebido! Cliente {cliente.nome},Produto:{self.produto}, Lance: {lance}"
                self.notificar_clientes(msg, self.list_Cliente)
            tempo_atual = time.perf_counter()
        msg = f"Leilão {self.id} finalizado! Produto vendido: {self.produto}, Preço de Venda: {self.lance_atual}, Vencedor: {self.vencedor}"
        self.notificar_clientes(msg, self.list_Cliente)
        self.duracao = -1
        return True

    def dar_lance(self, cliente, lance):
        if self.duracao == -1:
            msg = "Não foi possivel realizar o lance! Leilão finalizado!"
            self.notificar_clientes(msg, (cliente,))
        if lance <= self.lance_atual:
            return False
        buscarCliente = filter(lambda x: (x.id == cliente.id), self.list_Cliente)
        if buscarCliente is None:
            self.list_Cliente.append(cliente)
        self.list_lance.append({cliente: lance})

    def listar_lance_atual(self):
        return self.lance_atual

    def notificar_clientes(self, msg, clientes):
        self.notificar(msg, clientes)

    def __str__(self):
        tempo_restante = time.perf_counter() - self.tempo_inicio
        print(f"Leilão {self.id}")
        print(f"Criador: {self.criador.nome}, Produto: {self.produto.nome}")
        print(f"Último lance: {self.lance_atual}, Tempo Restante: {tempo_restante}")

