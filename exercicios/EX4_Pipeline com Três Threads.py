import threading
import time
import random
from queue import Queue, Empty

class FilaLimitada:
    def __init__(self, tamanho_max):
        self.fila = Queue(maxsize=tamanho_max)
        self.ativo = True
    
    def colocar(self, item):
        """Coloca item com backpressure"""
        while self.ativo:
            try:
                self.fila.put(item, timeout=0.1)
                return True
            except:
                if not self.ativo:
                    return False
        return False
    
    def retirar(self, timeout=None):
        """Retira item com timeout"""
        try:
            return self.fila.get(timeout=timeout)
        except Empty:
            return None
    
    def fechar(self):
        self.ativo = False

class Captura(threading.Thread):
    def __init__(self, fila, num_itens=20):
        super().__init__()
        self.fila = fila
        self.num_itens = num_itens
        
    def run(self):
        for i in range(self.num_itens):
            if not self.fila.ativo:
                break
            item = f"Dado_{i}"
            print(f"📥 Capturou: {item}")
            self.fila.colocar(item)
            time.sleep(random.uniform(0.1, 0.3))
        # Poison pill
        self.fila.colocar(None)
        print("📥 Captura finalizada")

class Processamento(threading.Thread):
    def __init__(self, fila_entrada, fila_saida):
        super().__init__()
        self.fila_entrada = fila_entrada
        self.fila_saida = fila_saida
        
    def run(self):
        while self.fila_entrada.ativo:
            item = self.fila_entrada.retirar(timeout=0.1)
            if item is None:
                # Poison pill
                self.fila_saida.colocar(None)
                break
            if item is not None:
                processado = f"Processado({item})"
                print(f"⚙️ Processou: {processado}")
                self.fila_saida.colocar(processado)
                time.sleep(random.uniform(0.2, 0.5))
        print("⚙️ Processamento finalizado")

class Gravacao(threading.Thread):
    def __init__(self, fila):
        super().__init__()
        self.fila = fila
        self.itens_gravados = []
        
    def run(self):
        while self.fila.ativo:
            item = self.fila.retirar(timeout=0.1)
            if item is None:
                break
            if item is not None:
                self.itens_gravados.append(item)
                print(f"💾 Gravou: {item}")
                time.sleep(random.uniform(0.3, 0.6))
        print("💾 Gravação finalizada")

class Pipeline:
    def __init__(self, tamanho_fila=5, num_itens=20):
        self.fila_captura_processamento = FilaLimitada(tamanho_fila)
        self.fila_processamento_gravacao = FilaLimitada(tamanho_fila)
        self.captura = Captura(self.fila_captura_processamento, num_itens)
        self.processamento = Processamento(
            self.fila_captura_processamento,
            self.fila_processamento_gravacao
        )
        self.gravacao = Gravacao(self.fila_processamento_gravacao)
    
    def executar(self):
        print("🚀 Iniciando Pipeline...")
        
        self.captura.start()
        self.processamento.start()
        self.gravacao.start()
        
        self.captura.join()
        self.processamento.join()
        self.gravacao.join()
        
        print("✅ Pipeline finalizado com sucesso")
        print(f"📊 Total de itens gravados: {len(self.gravacao.itens_gravados)}")
        return self.gravacao.itens_gravados

if __name__ == "__main__":
    pipeline = Pipeline(tamanho_fila=3, num_itens=15)
    pipeline.executar()