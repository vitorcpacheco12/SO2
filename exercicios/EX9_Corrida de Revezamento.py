import threading
import time
import random
from typing import List

class BarreiraRevezamento:
    def __init__(self, num_threads):
        self.num_threads = num_threads
        self.contador = 0
        self.lock = threading.Lock()
        self.cond = threading.Condition(self.lock)
        self.geracao = 0
        
    def esperar(self):
        with self.lock:
            minha_geracao = self.geracao
            self.contador += 1
            
            if self.contador == self.num_threads:
                self.contador = 0
                self.geracao += 1
                self.cond.notify_all()
            else:
                while self.geracao == minha_geracao:
                    self.cond.wait()

class EquipeRevezamento(threading.Thread):
    def __init__(self, id, barreira, num_voltas=5):
        super().__init__()
        self.id = id
        self.barreira = barreira
        self.num_voltas = num_voltas
        self.voltas_completadas = 0
        self.tempo_inicio = None
        self.tempos_volta = []
        self.ativo = True
    
    def _correr_volta(self):
        """Simula correr uma volta"""
        tempo_volta = random.uniform(0.5, 1.5)
        time.sleep(tempo_volta)
        return tempo_volta
    
    def run(self):
        while self.ativo and self.voltas_completadas < self.num_voltas:
            # Cada thread (membro da equipe) corre uma volta
            tempo = self._correr_volta()
            self.voltas_completadas += 1
            self.tempos_volta.append(tempo)
            
            print(f"🏃 Equipe {self.id} - Membro completou volta {self.voltas_completadas} em {tempo:.2f}s")
            
            # Aguarda os outros membros da equipe
            self.barreira.esperar()
            
            # Atualiza estatísticas
            if self.voltas_completadas == self.num_voltas:
                print(f"🏁 Equipe {self.id} completou a prova!")

class CorridaRevezamento:
    def __init__(self, num_equipes=4, membros_por_equipe=3, num_voltas=5):
        self.num_equipes = num_equipes
        self.membros_por_equipe = membros_por_equipe
        self.num_voltas = num_voltas
        self.equipes = []
        
        for i in range(num_equipes):
            barreira = BarreiraRevezamento(membros_por_equipe)
            for j in range(membros_por_equipe):
                equipe = EquipeRevezamento(
                    id=i,
                    barreira=barreira,
                    num_voltas=num_voltas
                )
                self.equipes.append(equipe)
    
    def executar(self):
        print(f"🚀 INÍCIO DA CORRIDA DE REVEZAMENTO")
        print(f"📊 {self.num_equipes} equipes, {self.membros_por_equipe} membros cada")
        print(f"🏁 {self.num_voltas} voltas por membro\n")
        
        inicio = time.time()
        
        # Inicia todas as threads
        for equipe in self.equipes:
            equipe.start()
        
        # Aguarda todas terminarem
        for equipe in self.equipes:
            equipe.join()
        
        fim = time.time()
        
        # Estatísticas por equipe
        print("\n📊 RESULTADOS FINAIS:")
        for i in range(self.num_equipes):
            equipes_grupo = self.equipes[i*self.membros_por_equipe:(i+1)*self.membros_por_equipe]
            total_voltas = sum(e.voltas_completadas for e in equipes_grupo)
            tempo_total = sum(e.tempos_volta for e in equipes_grupo for t in e.tempos_volta)
            print(f"Equipe {i}: {total_voltas} voltas completadas, Tempo total: {tempo_total:.2f}s")
        
        print(f"\n⏱️ Duração total: {fim - inicio:.2f}s")
        
        # Calcula voltas por minuto
        voltas_por_minuto = (self.num_equipes * self.num_voltas) / ((fim - inicio) / 60)
        print(f"📈 Desempenho: {voltas_por_minuto:.2f} voltas/minuto")

def experimentar_tamanhos_equipe():
    """Experimenta diferentes tamanhos de equipe"""
    print("=== EXPERIMENTO: DIFERENTES TAMANHOS DE EQUIPE ===\n")
    
    tamanhos = [2, 3, 4, 6]
    resultados = []
    
    for tamanho in tamanhos:
        print(f"\n📋 Teste com {tamanho} membros por equipe")
        print("-" * 40)
        
        corrida = CorridaRevezamento(
            num_equipes=3,
            membros_por_equipe=tamanho,
            num_voltas=3
        )
        
        inicio = time.time()
        corrida.executar()
        fim = time.time()
        
        resultados.append({
            'membros': tamanho,
            'tempo': fim - inicio,
            'voltas_por_minuto': (3 * 3) / ((fim - inicio) / 60)
        })
    
    print("\n📊 COMPARAÇÃO:")
    for r in resultados:
        print(f"{r['membros']} membros: Tempo={r['tempo']:.2f}s, "
              f"Voltas/minuto={r['voltas_por_minuto']:.2f}")

if __name__ == "__main__":
    experimentar_tamanhos_equipe()