import threading
import time
import random
from collections import defaultdict

class Filosofo(threading.Thread):
    def __init__(self, id, garfo_esquerdo, garfo_direito, metodo="ordem"):
        super().__init__()
        self.id = id
        self.garfo_esquerdo = garfo_esquerdo
        self.garfo_direito = garfo_direito
        self.metodo = metodo
        self.refeicoes = 0
        self.tempo_espera_total = 0
        self.tempo_espera_maximo = 0
        self.ativo = True
        
        # Para método de semáforo
        self.semaforo_global = None
    
    def _pensar(self):
        time.sleep(random.uniform(0.1, 0.3))
    
    def _comer(self):
        tempo = random.uniform(0.2, 0.5)
        time.sleep(tempo)
        self.refeicoes += 1
    
    def _pegar_garfos_ordem(self):
        """Método a: Ordem global de aquisição"""
        inicio_espera = time.time()
        
        # Adquire na ordem para evitar deadlock
        if self.id % 2 == 0:
            self.garfo_esquerdo.acquire()
            self.garfo_direito.acquire()
        else:
            self.garfo_direito.acquire()
            self.garfo_esquerdo.acquire()
        
        tempo_espera = time.time() - inicio_espera
        self.tempo_espera_total += tempo_espera
        self.tempo_espera_maximo = max(self.tempo_espera_maximo, tempo_espera)
    
    def _pegar_garfos_semaforo(self):
        """Método b: Semáforo limitando a 4 filósofos"""
        inicio_espera = time.time()
        
        with self.semaforo_global:
            self.garfo_esquerdo.acquire()
            self.garfo_direito.acquire()
        
        tempo_espera = time.time() - inicio_espera
        self.tempo_espera_total += tempo_espera
        self.tempo_espera_maximo = max(self.tempo_espera_maximo, tempo_espera)
    
    def run(self):
        while self.ativo and self.refeicoes < 10:
            self._pensar()
            
            if self.metodo == "ordem":
                self._pegar_garfos_ordem()
            else:
                self._pegar_garfos_semaforo()
            
            self._comer()
            self.garfo_esquerdo.release()
            self.garfo_direito.release()

class JantarFilosofos:
    def __init__(self, num_filosofos=5, metodo="ordem"):
        self.num_filosofos = num_filosofos
        self.metodo = metodo
        self.garfos = [threading.Lock() for _ in range(num_filosofos)]
        
        if metodo == "semaforo":
            self.semaforo_global = threading.Semaphore(num_filosofos - 1)
        
        self.filosofos = []
        for i in range(num_filosofos):
            f = Filosofo(
                i,
                self.garfos[i],
                self.garfos[(i + 1) % num_filosofos],
                metodo
            )
            if metodo == "semaforo":
                f.semaforo_global = self.semaforo_global
            self.filosofos.append(f)
    
    def executar(self, duracao=10):
        print(f"🧠 Jantar dos Filósofos - Método: {self.metodo}")
        print("Iniciando...")
        
        for f in self.filosofos:
            f.start()
        
        time.sleep(duracao)
        
        for f in self.filosofos:
            f.ativo = False
        
        for f in self.filosofos:
            f.join()
        
        print("\n📊 Estatísticas:")
        print(f"Método: {self.metodo}")
        for f in self.filosofos:
            media_espera = f.tempo_espera_total / f.refeicoes if f.refeicoes > 0 else 0
            print(f"Filósofo {f.id}: {f.refeicoes} refeições, Espera média={media_espera:.3f}s, "
                  f"Espera máxima={f.tempo_espera_maximo:.3f}s")

def comparar_metodos():
    """Compara os dois métodos de solução"""
    print("=== COMPARAÇÃO DOS MÉTODOS ===\n")
    
    print("1. Método: Ordem Global de Aquisição")
    jantar1 = JantarFilosofos(5, "ordem")
    jantar1.executar(8)
    
    print("\n" + "="*50 + "\n")
    
    print("2. Método: Semáforo (4 filósofos simultâneos)")
    jantar2 = JantarFilosofos(5, "semaforo")
    jantar2.executar(8)

if __name__ == "__main__":
    comparar_metodos()