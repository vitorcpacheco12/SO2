import threading
import time
import random
from collections import deque
import matplotlib.pyplot as plt

class BufferBurst:
    def __init__(self, tamanho):
        self.tamanho = tamanho
        self.buffer = deque(maxlen=tamanho)
        self.lock = threading.Lock()
        self.cond_produtor = threading.Condition(self.lock)
        self.cond_consumidor = threading.Condition(self.lock)
        self.ativo = True
        self.historico_ocupacao = []
        self.produtores_parados = 0
        self.itens_produzidos = 0
        self.itens_consumidos = 0
    
    def produzir(self, item):
        with self.lock:
            while len(self.buffer) >= self.tamanho and self.ativo:
                self.produtores_parados += 1
                self.cond_produtor.wait()
                self.produtores_parados -= 1
            
            if not self.ativo:
                return False
            
            self.buffer.append(item)
            self.itens_produzidos += 1
            self.registrar_ocupacao()
            self.cond_consumidor.notify()
            return True
    
    def consumir(self):
        with self.lock:
            while len(self.buffer) == 0 and self.ativo:
                self.cond_consumidor.wait()
            
            if not self.ativo and len(self.buffer) == 0:
                return None
            
            item = self.buffer.popleft()
            self.itens_consumidos += 1
            self.registrar_ocupacao()
            self.cond_produtor.notify()
            return item
    
    def registrar_ocupacao(self):
        ocupacao = len(self.buffer) / self.tamanho * 100
        self.historico_ocupacao.append((time.time(), ocupacao))
    
    def parar(self):
        with self.lock:
            self.ativo = False
            self.cond_produtor.notify_all()
            self.cond_consumidor.notify_all()

class ProdutorBurst(threading.Thread):
    def __init__(self, buffer, id, burst_size, burst_prob=0.3):
        super().__init__()
        self.buffer = buffer
        self.id = id
        self.burst_size = burst_size
        self.burst_prob = burst_prob
        self.ativo = True
        
    def run(self):
        item_id = 0
        while self.ativo:
            # Decide se é um burst
            if random.random() < self.burst_prob:
                # Burst de produção
                for _ in range(self.burst_size):
                    if not self.ativo:
                        break
                    item = f"Burst{self.id}-{item_id}"
                    self.buffer.produzir(item)
                    item_id += 1
                    time.sleep(random.uniform(0.01, 0.05))
            else:
                # Período normal
                item = f"Prod{self.id}-{item_id}"
                self.buffer.produzir(item)
                item_id += 1
                time.sleep(random.uniform(0.3, 0.7))

class ConsumidorVariavel(threading.Thread):
    def __init__(self, buffer, id, taxa_base=0.5):
        super().__init__()
        self.buffer = buffer
        self.id = id
        self.taxa_base = taxa_base
        self.ativo = True
        
    def run(self):
        while self.ativo:
            item = self.buffer.consumir()
            if item:
                # Simula taxa de consumo variável
                tempo = random.expovariate(1/self.taxa_base)
                time.sleep(tempo)

class SimuladorBuffer:
    def __init__(self, tamanho_buffer, num_produtores=3, num_consumidores=2):
        self.buffer = BufferBurst(tamanho_buffer)
        self.produtores = []
        self.consumidores = []
        
        for i in range(num_produtores):
            burst_size = random.randint(3, 8)
            self.produtores.append(ProdutorBurst(self.buffer, i, burst_size))
        
        for i in range(num_consumidores):
            taxa = random.uniform(0.3, 0.8)
            self.consumidores.append(ConsumidorVariavel(self.buffer, i, taxa))
    
    def executar(self, duracao=20):
        print(f"🔄 Iniciando simulação com buffer de {self.buffer.tamanho}")
        print(f"📊 {len(self.produtores)} produtores, {len(self.consumidores)} consumidores")
        
        for p in self.produtores:
            p.start()
        for c in self.consumidores:
            c.start()
        
        time.sleep(duracao)
        
        for p in self.produtores:
            p.ativo = False
        for c in self.consumidores:
            c.ativo = False
        
        self.buffer.parar()
        
        for p in self.produtores:
            p.join()
        for c in self.consumidores:
            c.join()
        
        print("\n📊 Estatísticas finais:")
        print(f"Produzidos: {self.buffer.itens_produzidos}")
        print(f"Consumidos: {self.buffer.itens_consumidos}")
        print(f"Produtores parados: {self.buffer.produtores_parados} vezes")
        print(f"Ocupação máxima: {max(o[1] for o in self.buffer.historico_ocupacao):.1f}%")
        
        return self.buffer.historico_ocupacao
    
    def plotar_ocupacao(self, historico):
        if not historico:
            return
        
        tempos = [h[0] - historico[0][0] for h in historico]
        ocupacoes = [h[1] for h in historico]
        
        plt.figure(figsize=(12, 6))
        plt.plot(tempos, ocupacoes)
        plt.xlabel('Tempo (segundos)')
        plt.ylabel('Ocupação do Buffer (%)')
        plt.title(f'Ocupação do Buffer - Tamanho {self.buffer.tamanho}')
        plt.grid(True)
        plt.ylim(0, 105)
        plt.show()

def executar_experimentos():
    """Executa experimentos com diferentes tamanhos de buffer"""
    resultados = []
    
    for tamanho in [5, 10, 20]:
        print(f"\n{'='*50}")
        print(f"Experimento com buffer de tamanho {tamanho}")
        print('='*50)
        
        simulador = SimuladorBuffer(tamanho, num_produtores=4, num_consumidores=3)
        historico = simulador.executar(duracao=15)
        
        # Registra estatísticas
        ocupacao_media = sum(o[1] for o in historico) / len(historico) if historico else 0
        resultados.append({
            'tamanho': tamanho,
            'producao': simulador.buffer.itens_produzidos,
            'consumo': simulador.buffer.itens_consumidos,
            'ocupacao_media': ocupacao_media,
            'paradas_produtor': simulador.buffer.produtores_parados
        })
        
        # Plota gráfico para o último experimento
        if tamanho == 20:
            simulador.plotar_ocupacao(historico)
    
    print("\n📊 RESUMO DOS EXPERIMENTOS:")
    for r in resultados:
        print(f"Buffer {r['tamanho']}: Produção={r['producao']}, "
              f"Consumo={r['consumo']}, "
              f"Ocupação média={r['ocupacao_media']:.1f}%, "
              f"Paradas={r['paradas_produtor']}")

if __name__ == "__main__":
    executar_experimentos()