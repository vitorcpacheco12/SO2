import threading
import time
import random
from collections import defaultdict

class Recurso:
    def __init__(self, id):
        self.id = id
        self.lock = threading.Lock()
        self.proprietario = None
    
    def adquirir(self, thread_id, tempo_maximo=None):
        """Adquire o recurso com timeout opcional"""
        inicio = time.time()
        while True:
            if self.lock.acquire(timeout=0.1 if tempo_maximo else None):
                self.proprietario = thread_id
                return True
            
            if tempo_maximo and (time.time() - inicio) > tempo_maximo:
                return False
    
    def liberar(self):
        self.proprietario = None
        self.lock.release()

class ThreadDeadlock(threading.Thread):
    def __init__(self, id, recursos, ordem=None):
        super().__init__()
        self.id = id
        self.recursos = recursos
        self.ordem = ordem
        self.progresso = 0
        self.ativo = True
        self.acordado = time.time()
    
    def _adquirir_recursos_ordem_aleatoria(self):
        """Adquire recursos em ordem aleatória (pode causar deadlock)"""
        for recurso in self.recursos:
            if not self.ativo:
                return False
            if not recurso.adquirir(self.id, tempo_maximo=2.0):
                # Libera recursos já adquiridos
                for r in self.recursos:
                    if r.proprietario == self.id:
                        r.liberar()
                return False
        return True
    
    def _adquirir_recursos_ordem_global(self):
        """Adquire recursos em ordem global (evita deadlock)"""
        # Ordena recursos por ID
        recursos_ordenados = sorted(self.recursos, key=lambda r: r.id)
        for recurso in recursos_ordenados:
            if not self.ativo:
                return False
            if not recurso.adquirir(self.id):
                for r in recursos_ordenados:
                    if r.proprietario == self.id:
                        r.liberar()
                return False
        return True
    
    def run(self):
        while self.ativo:
            self.acordado = time.time()
            
            # Simula trabalho
            if self.ordem == "global":
                sucesso = self._adquirir_recursos_ordem_global()
            else:
                sucesso = self._adquirir_recursos_ordem_aleatoria()
            
            if sucesso:
                self.progresso += 1
                # Simula uso dos recursos
                time.sleep(random.uniform(0.1, 0.3))
                # Libera recursos
                for recurso in self.recursos:
                    if recurso.proprietario == self.id:
                        recurso.liberar()
            else:
                # Falha ao adquirir recursos
                time.sleep(0.1)
    
    def parar(self):
        self.ativo = False

class Watchdog(threading.Thread):
    def __init__(self, threads, timeout=3.0):
        super().__init__()
        self.threads = threads
        self.timeout = timeout
        self.ativo = True
    
    def run(self):
        while self.ativo:
            time.sleep(1)  # Verifica a cada segundo
            
            agora = time.time()
            for thread in self.threads:
                if thread.ativo and (agora - thread.acordado) > self.timeout:
                    print(f"⚠️ ALERTA: Thread {thread.id} pode estar bloqueada!")
                    print(f"   Último progresso: {thread.acordado:.2f}s")
                    print(f"   Progresso total: {thread.progresso}")
                    
                    # Relatório de recursos
                    for recurso in thread.recursos:
                        if recurso.lock.locked():
                            print(f"   Recurso {recurso.id}: bloqueado por {recurso.proprietario}")

class SimuladorDeadlock:
    def __init__(self, num_threads=5, num_recursos=5, ordem="aleatoria"):
        self.num_threads = num_threads
        self.num_recursos = num_recursos
        self.ordem = ordem
        self.recursos = [Recurso(i) for i in range(num_recursos)]
        self.threads = []
        
        # Cria threads com recursos aleatórios
        for i in range(num_threads):
            # Cada thread precisa de 2-3 recursos
            num_necessarios = random.randint(2, 3)
            recursos_thread = random.sample(self.recursos, num_necessarios)
            
            thread = ThreadDeadlock(
                id=i,
                recursos=recursos_thread,
                ordem=ordem
            )
            self.threads.append(thread)
    
    def executar(self, duracao=15):
        print(f"🔄 SIMULADOR DE DEADLOCK")
        print(f"📊 Método: {'Ordem Global' if self.ordem == 'global' else 'Ordem Aleatória'}")
        print(f"🧵 {self.num_threads} threads, {self.num_recursos} recursos\n")
        
        # Inicia threads
        for thread in self.threads:
            thread.start()
        
        # Inicia watchdog
        watchdog = Watchdog(self.threads, timeout=3.0)
        watchdog.start()
        
        # Monitora progresso
        inicio = time.time()
        try:
            while time.time() - inicio < duracao:
                time.sleep(1)
                
                # Mostra progresso periodicamente
                if int(time.time() - inicio) % 5 == 0:
                    progressos = [t.progresso for t in self.threads]
                    print(f"📈 Progresso: {progressos}")
        
        except KeyboardInterrupt:
            print("\n🛑 Interrompido pelo usuário")
        
        finally:
            # Finaliza tudo
            for thread in self.threads:
                thread.parar()
            watchdog.ativo = False
            
            for thread in self.threads:
                thread.join(timeout=1.0)
            watchdog.join(timeout=1.0)
            
            print("\n📊 RESULTADO:")
            for thread in self.threads:
                status = "✅" if thread.progresso > 0 else "❌"
                print(f"Thread {thread.id}: {status} {thread.progresso} progressos")

def comparar_comportamentos():
    """Compara comportamento com e sem ordem global"""
    print("="*60)
    print("COMPARAÇÃO: ORDEM ALEATÓRIA VS ORDEM GLOBAL")
    print("="*60)
    
    print("\n🔴 EXPERIMENTO 1: Ordem Aleatória (pode causar deadlock)")
    print("-"*50)
    sim1 = SimuladorDeadlock(num_threads=5, num_recursos=5, ordem="aleatoria")
    sim1.executar(duracao=10)
    
    print("\n" + "="*60 + "\n")
    
    print("🟢 EXPERIMENTO 2: Ordem Global (evita deadlock)")
    print("-"*50)
    sim2 = SimuladorDeadlock(num_threads=5, num_recursos=5, ordem="global")
    sim2.executar(duracao=10)

if __name__ == "__main__":
    comparar_comportamentos()