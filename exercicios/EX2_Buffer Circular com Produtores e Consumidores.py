import threading
import time
import random
import queue
from collections import deque
import statistics

class BufferCircular:
    def __init__(self, tamanho):
        self.tamanho = tamanho
        self.buffer = deque(maxlen=tamanho)
        self.lock = threading.Lock()
        self.cond_produtor = threading.Condition(self.lock)
        self.cond_consumidor = threading.Condition(self.lock)
        self.items_produzidos = 0
        self.items_consumidos = 0
        self.tempos_espera = []
        self.ativo = True
        
    def produzir(self, item, produtor_id):
        with self.lock:
            while len(self.buffer) >= self.tamanho and self.ativo:
                self.cond_produtor.wait()
            
            if not self.ativo:
                return False
                
            inicio_espera = time.time()
            self.buffer.append(item)
            self.items_produzidos += 1
            self.tempos_espera.append(time.time() - inicio_espera)
            self.cond_consumidor.notify()
            return True
    
    def consumir(self, consumidor_id):
        with self.lock:
            while len(self.buffer) == 0 and self.ativo:
                self.cond_consumidor.wait()
            
            if not self.ativo and len(self.buffer) == 0:
                return None
                
            item = self.buffer.popleft()
            self.items_consumidos += 1
            self.cond_produtor.notify()
            return item
    
    def parar(self):
        with self.lock:
            self.ativo = False
            self.cond_produtor.notify_all()
            self.cond_consumidor.notify_all()

class Produtor(threading.Thread):
    def __init__(self, buffer, id, tempo_medio=0.5):
        super().__init__()
        self.buffer = buffer
        self.id = id
        self.tempo_medio = tempo_medio
        
    def run(self):
        for i in range(100):
            if not self.buffer.ativo:
                break
            item = f"P{self.id}-{i}"
            self.buffer.produzir(item, self.id)
            print(f"Produtor {self.id} produziu: {item}")
            time.sleep(random.expovariate(1/self.tempo_medio))

class Consumidor(threading.Thread):
    def __init__(self, buffer, id, tempo_medio=0.5):
        super().__init__()
        self.buffer = buffer
        self.id = id
        self.tempo_medio = tempo_medio
        
    def run(self):
        while self.buffer.ativo or len(self.buffer.buffer) > 0:
            item = self.buffer.consumir(self.id)
            if item:
                print(f"Consumidor {self.id} consumiu: {item}")
            time.sleep(random.expovariate(1/self.tempo_medio))

def experimento(tamanho_buffer, num_produtores=3, num_consumidores=3):
    print(f"\n=== Experimento com buffer de tamanho {tamanho_buffer} ===")
    buffer = BufferCircular(tamanho_buffer)
    
    produtores = [Produtor(buffer, i) for i in range(num_produtores)]
    consumidores = [Consumidor(buffer, i) for i in range(num_consumidores)]
    
    inicio = time.time()
    
    for p in produtores:
        p.start()
    for c in consumidores:
        c.start()
    
    for p in produtores:
        p.join()
    
    buffer.parar()
    
    for c in consumidores:
        c.join()
    
    fim = time.time()
    
    # Estatísticas
    throughput = buffer.items_consumidos / (fim - inicio)
    tempo_medio_espera = statistics.mean(buffer.tempos_espera) if buffer.tempos_espera else 0
    
    print(f"Throughput: {throughput:.2f} itens/segundo")
    print(f"Tempo médio de espera: {tempo_medio_espera:.3f} segundos")
    print(f"Total produzido: {buffer.items_produzidos}")
    print(f"Total consumido: {buffer.items_consumidos}")
    
    return {
        'tamanho': tamanho_buffer,
        'throughput': throughput,
        'tempo_medio': tempo_medio_espera
    }

if __name__ == "__main__":
    resultados = []
    for tamanho in [5, 10, 20, 50]:
        resultados.append(experimento(tamanho))
    
    print("\n=== RESUMO DOS EXPERIMENTOS ===")
    for r in resultados:
        print(f"Buffer {r['tamanho']}: Throughput={r['throughput']:.2f}, Tempo médio={r['tempo_medio']:.3f}s")