import threading
import random
import time
from typing import List

class Conta:
    def __init__(self, id, saldo_inicial=1000):
        self.id = id
        self.saldo = saldo_inicial
        self.lock = threading.Lock()
    
    def transferir(self, destino, valor):
        if self.id < destino.id:
            self.lock.acquire()
            destino.lock.acquire()
        else:
            destino.lock.acquire()
            self.lock.acquire()
        
        try:
            if self.saldo >= valor:
                self.saldo -= valor
                destino.saldo += valor
                return True
            return False
        finally:
            self.lock.release()
            destino.lock.release()

class SistemaBancario:
    def __init__(self, num_contas=5, saldo_inicial=1000):
        self.contas = [Conta(i, saldo_inicial) for i in range(num_contas)]
        self.saldo_total_inicial = num_contas * saldo_inicial
        self.lock_global = threading.Lock()
        self.sem_trava = False
    
    def transferir_seguro(self, origem_idx, destino_idx, valor):
        """Transferência com trava adequada"""
        return self.contas[origem_idx].transferir(self.contas[destino_idx], valor)
    
    def transferir_inseguro(self, origem_idx, destino_idx, valor):
        """Transferência sem trava (para demonstração de condição de corrida)"""
        if self.contas[origem_idx].saldo >= valor:
            # Simula atraso para aumentar chance de condição de corrida
            time.sleep(random.uniform(0.001, 0.005))
            self.contas[origem_idx].saldo -= valor
            time.sleep(random.uniform(0.001, 0.005))
            self.contas[destino_idx].saldo += valor
            return True
        return False
    
    def verificar_soma_global(self):
        soma = sum(conta.saldo for conta in self.contas)
        return soma == self.saldo_total_inicial
    
    def executar_threads(self, num_threads=10, num_transferencias=100, seguro=True):
        threads = []
        
        def worker():
            for _ in range(num_transferencias):
                origem = random.randint(0, len(self.contas) - 1)
                destino = random.randint(0, len(self.contas) - 1)
                while destino == origem:
                    destino = random.randint(0, len(self.contas) - 1)
                
                valor = random.randint(1, 100)
                
                if seguro:
                    self.transferir_seguro(origem, destino, valor)
                else:
                    self.transferir_inseguro(origem, destino, valor)
        
        for i in range(num_threads):
            t = threading.Thread(target=worker)
            threads.append(t)
            t.start()
        
        for t in threads:
            t.join()
    
    def demonstrar_corrida(self):
        print("=== DEMONSTRAÇÃO DE CONDIÇÃO DE CORRIDA ===")
        print(f"Saldo total inicial: {self.saldo_total_inicial}")
        
        # Execução segura
        sistema_seguro = SistemaBancario(num_contas=5, saldo_inicial=1000)
        sistema_seguro.executar_threads(num_threads=5, num_transferencias=100, seguro=True)
        print(f"Execução com trava - Soma total: {sum(c.saldo for c in sistema_seguro.contas)}")
        print(f"Verificação: {'✓' if sistema_seguro.verificar_soma_global() else '✗'}")
        
        # Execução insegura
        sistema_inseguro = SistemaBancario(num_contas=5, saldo_inicial=1000)
        sistema_inseguro.executar_threads(num_threads=5, num_transferencias=100, seguro=False)
        print(f"Execução sem trava - Soma total: {sum(c.saldo for c in sistema_inseguro.contas)}")
        print(f"Verificação: {'✓' if sistema_inseguro.verificar_soma_global() else '✗'}")

if __name__ == "__main__":
    banco = SistemaBancario()
    banco.demonstrar_corrida()