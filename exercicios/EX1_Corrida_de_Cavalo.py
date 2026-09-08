import threading
import random
import time
from collections import defaultdict

class CorridaCavalos:
    def __init__(self, distancia_total=100):
        self.distancia_total = distancia_total
        self.cavalos = {}
        self.posicoes = {}
        self.vencedor = None
        self.lock_placar = threading.Lock()
        self.lock_vencedor = threading.Lock()
        self.barreira_largada = threading.Barrier(2)  # Será ajustado dinamicamente
        
    def adicionar_cavalo(self, nome):
        self.cavalos[nome] = threading.Thread(target=self._correr, args=(nome,))
        self.posicoes[nome] = 0
        
    def _correr(self, nome):
        # Aguarda a largada sincronizada
        self.barreira_largada.wait()
        
        while self.posicoes[nome] < self.distancia_total:
            # Avança em passos aleatórios (1-5)
            passo = random.randint(1, 5)
            with self.lock_placar:
                self.posicoes[nome] = min(self.posicoes[nome] + passo, self.distancia_total)
                print(f"{nome}: {self.posicoes[nome]}/{self.distancia_total}")
            
            # Verifica se é o vencedor
            if self.posicoes[nome] >= self.distancia_total:
                with self.lock_vencedor:
                    if self.vencedor is None:
                        self.vencedor = nome
                        print(f"\n🏆 {nome} VENCEU A CORRIDA! 🏆")
                break
            
            time.sleep(random.uniform(0.1, 0.5))
    
    def iniciar_corrida(self, aposta):
        # Cria barreira com número de cavalos + 1 (para a thread principal)
        self.barreira_largada = threading.Barrier(len(self.cavalos) + 1)
        
        # Inicia todas as threads
        for thread in self.cavalos.values():
            thread.start()
        
        # Sincroniza a largada
        print("🏁 PREPARAR...")
        time.sleep(1)
        print("🏁 APONTAR...")
        time.sleep(1)
        print("🏁 JÁ!")
        self.barreira_largada.wait()
        
        # Aguarda todas as threads terminarem
        for thread in self.cavalos.values():
            thread.join()
        
        print(f"\n📊 RESULTADO FINAL:")
        print(f"Vencedor: {self.vencedor}")
        print(f"Sua aposta: {aposta}")
        if aposta == self.vencedor:
            print("🎉 VOCÊ GANHOU! Parabéns!")
        else:
            print("😞 Você perdeu. Tente novamente!")

# Exemplo de uso
if __name__ == "__main__":
    corrida = CorridaCavalos(distancia_total=50)
    corrida.adicionar_cavalo("Relâmpago")
    corrida.adicionar_cavalo("Trovão")
    corrida.adicionar_cavalo("Flecha")
    corrida.adicionar_cavalo("Vento")
    
    aposta = input("Aposte em um cavalo (Relâmpago/Trovão/Flecha/Vento): ")
    corrida.iniciar_corrida(aposta)