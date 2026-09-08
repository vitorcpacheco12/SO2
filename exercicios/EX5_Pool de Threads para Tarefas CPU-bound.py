import threading
import queue
import time
import math
from typing import Callable, Any

class ThreadPool:
    def __init__(self, num_threads):
        self.num_threads = num_threads
        self.fila_tarefas = queue.Queue()
        self.threads = []
        self.ativo = True
        self.resultados = []
        self.lock_resultados = threading.Lock()
        
        for i in range(num_threads):
            t = threading.Thread(target=self._worker, name=f"Worker-{i}")
            t.start()
            self.threads.append(t)
    
    def _worker(self):
        while self.ativo:
            try:
                tarefa = self.fila_tarefas.get(timeout=0.1)
                if tarefa is None:  # Poison pill
                    break
                
                func, args, callback = tarefa
                resultado = func(*args)
                
                with self.lock_resultados:
                    self.resultados.append((callback, resultado))
                    
                self.fila_tarefas.task_done()
            except queue.Empty:
                continue
    
    def submit(self, func, args=(), callback=None):
        """Submete uma tarefa para execução"""
        if not self.ativo:
            raise RuntimeError("Pool está finalizado")
        self.fila_tarefas.put((func, args, callback))
    
    def shutdown(self):
        """Finaliza o pool de threads"""
        self.ativo = False
        # Envia poison pills para todas as threads
        for _ in range(self.num_threads):
            self.fila_tarefas.put(None)
        
        for t in self.threads:
            t.join()
    
    def get_resultados(self):
        """Retorna todos os resultados processados"""
        return self.resultados

# Funções de exemplo para CPU-bound
def eh_primo(n):
    """Testa se um número é primo (CPU-bound)"""
    if n < 2:
        return False
    for i in range(2, int(math.sqrt(n)) + 1):
        if n % i == 0:
            return False
    return True

def fibonacci(n):
    """Calcula Fibonacci iterativamente (CPU-bound)"""
    if n <= 1:
        return n
    a, b = 0, 1
    for _ in range(2, n + 1):
        a, b = b, a + b
    return b

class SistemaProcessamento:
    def __init__(self, num_threads):
        self.pool = ThreadPool(num_threads)
        self.contador_tarefas = 0
    
    def processar_entrada(self, linha):
        """Processa entrada do usuário"""
        partes = linha.strip().split()
        if not partes:
            return
        
        comando = partes[0].lower()
        
        if comando == "primo":
            if len(partes) > 1:
                try:
                    n = int(partes[1])
                    self.pool.submit(eh_primo, (n,), self._callback_primo)
                    self.contador_tarefas += 1
                except ValueError:
                    print("❌ Número inválido")
        
        elif comando == "fib":
            if len(partes) > 1:
                try:
                    n = int(partes[1])
                    self.pool.submit(fibonacci, (n,), self._callback_fib)
                    self.contador_tarefas += 1
                except ValueError:
                    print("❌ Número inválido")
        
        elif comando == "status":
            print(f"📊 Tarefas enviadas: {self.contador_tarefas}")
            print(f"📊 Resultados coletados: {len(self.pool.get_resultados())}")
        
        elif comando == "sair":
            return False
        
        else:
            print("Comandos: primo <n> | fib <n> | status | sair")
        
        return True
    
    def _callback_primo(self, resultado):
        """Callback para resultados de teste de primalidade"""
        print(f"🔢 Primo: {resultado}")
    
    def _callback_fib(self, resultado):
        """Callback para resultados de Fibonacci"""
        print(f"🔢 Fibonacci: {resultado}")
    
    def executar(self):
        """Executa o sistema interativo"""
        print("🧵 Sistema de Processamento de Tarefas")
        print("Comandos: primo <n> | fib <n> | status | sair")
        
        try:
            while True:
                linha = input(">>> ")
                if not self.processar_entrada(linha):
                    break
        except EOFError:
            pass
        finally:
            print("🛑 Finalizando pool...")
            self.pool.shutdown()
            print("✅ Pool finalizado")

if __name__ == "__main__":
    sistema = SistemaProcessamento(num_threads=4)
    sistema.executar()