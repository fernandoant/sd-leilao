from Produto import Produto
from threading import Thread
import time

DEBUG = 1

class Leilao(Thread):
    def __init__(self, id_leilao, criador, produto:Produto, duracao, notificar):
        self.id_leilao = id_leilao
        self.criador = criador
        self.produto = produto
        self.clientes = []
        self.lances = []
        self.lance_atual = produto.preco_minimo
        self.duracao = duracao
        self.tempo_inicio = 0
        self.vencedor = None
        self.notificar = notificar
        self.thread = Thread(target=self._iniciar_leilao)
        self.clientes.append(criador)

    def iniciar_leilao(self):
        if DEBUG == 1:
            print(f"Iniciando o leilão {self.id_leilao}")
        self.thread.start()

    def _iniciar_leilao(self):
        self.tempo_inicio = time.perf_counter()
        tempo_atual = time.perf_counter()
        while(tempo_atual - self.tempo_inicio < self.duracao):
            if len(self.lances) > 0:
                lance = self.lances.pop(0)
                nome_cliente = lance.cliente.nome
                valor_lance = lance.valor
                self.lance_atual = valor_lance
                self.vencedor = nome_cliente
                msg = f"Leilão {self.id_leilao} - Lance recebido! Cliente {nome_cliente}, Produto:{self.produto.nome}, Lance: {valor_lance}"
                self.notificar_clientes(msg, self.clientes)
            tempo_atual = time.perf_counter()
        
        if (self.vencedor is None):
            msg = f"Leilão {self.id_leilao} finalizado! {self.produto} - Nenhum lance foi efetuado para compra do produto!"
        else:
            msg = f"Leilão {self.id_leilao} finalizado! {self.produto}, Preço de Venda: {self.lance_atual}, Vencedor: {self.vencedor}"

        self.notificar_clientes(msg, self.clientes)
        self.duracao = -1
        return True

    def dar_lance(self, lance):
        if self.duracao == -1:
            return False
        elif lance.valor <= self.lance_atual:
            return False

        registrado = list(filter(lambda x: (x.nome == lance.cliente.nome), self.clientes))
        if len(registrado) == 0:
            self.clientes.append(lance.cliente)

        self.lances.append(lance)
        return True

    def notificar_clientes(self, msg, clientes):
        self.notificar(msg, clientes)

    def __str__(self):
        tempo_restante = self.duracao - (time.perf_counter() - self.tempo_inicio)
        return f"Leilão {self.id_leilao}\nCriador: {self.criador.nome}, Produto: {self.produto.nome}, Último lance: {self.lance_atual}, Tempo Restante: {round(tempo_restante)}s"
