## relatorio.md 

Relatório - Laboratório 01 de Sistemas Operacionais 2
Aluno: Vitor Cunha Pacheco
Disciplina: Sistemas Operacionais 2
Data: 08/09/2026

Sumário
Exercício 1 - Corrida de Cavalos

Exercício 2 - Buffer Circular

Exercício 3 - Transferências entre Contas

Exercício 4 - Pipeline

Exercício 5 - Pool de Threads

Exercício 6 - Processamento Paralelo

Exercício 7 - Jantar dos Filósofos

Exercício 8 - Buffer com Bursts

Exercício 9 - Corrida de Revezamento

Exercício 10 - Watchdog

Conclusão

Exercício 1 - Corrida de Cavalos
Descrição
Implementação de uma corrida onde cada cavalo é uma thread que avança em passos aleatórios até cruzar a linha de chegada. O usuário faz uma aposta antes da largada, e o sistema anuncia o vencedor e verifica se a aposta foi correta.

Solução Proposta
Estrutura:
Classe CorridaCavalos gerencia a corrida

Cada cavalo é uma thread

Barreira para largada sincronizada

Locks para exclusão mútua no placar e no vencedor

Mecanismos de Sincronização:
threading.Barrier para largada simultânea

threading.Lock para proteger acesso ao placar

Lock separado para definir o vencedor (evita condições de corrida)

Tratamento de Empates:
O primeiro cavalo a cruzar a linha de chegada define o vencedor

Lock garante atomicidade na verificação e atualização

Código Principal:

    class CorridaCavalos:

    def __init__(self, distancia_total=100):
        self.distancia_total = distancia_total
        self.cavalos = {}
        self.posicoes = {}
        self.vencedor = None
        self.lock_placar = threading.Lock()
        self.lock_vencedor = threading.Lock()
        self.barreira_largada = None
    
    def adicionar_cavalo(self, nome):
        self.cavalos[nome] = threading.Thread(target=self._correr, args=(nome,))
        self.posicoes[nome] = 0
    
    def _correr(self, nome):
        self.barreira_largada.wait()  # Largada sincronizada
        
        while self.posicoes[nome] < self.distancia_total:
            passo = random.randint(1, 5)  # Passo aleatório
            with self.lock_placar:
                self.posicoes[nome] = min(self.posicoes[nome] + passo, self.distancia_total)
            
            if self.posicoes[nome] >= self.distancia_total:
                with self.lock_vencedor:
                    if self.vencedor is None:
                        self.vencedor = nome
                break
            
            time.sleep(random.uniform(0.1, 0.5))

  Exercício 2 - Buffer Circular
Descrição
Implementação de um buffer circular de tamanho N acessado por múltiplos produtores e consumidores, utilizando mecanismos de sincronização para garantir exclusão mútua e ausência de espera ativa.

Solução Proposta
Estrutura:
Classe BufferCircular gerencia o buffer e a sincronização

Produtores geram itens com tempos aleatórios

Consumidores retiram itens do buffer

Coleta de estatísticas de throughput e tempo médio de espera

Mecanismos de Sincronização:
threading.Condition para controle de produtores e consumidores

Lock único protege o buffer

Variáveis de condição para produtor (buffer cheio) e consumidor (buffer vazio)

Código Principal:

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
    
    def produzir(self, item):
        with self.lock:
            while len(self.buffer) >= self.tamanho and self.ativo:
                self.cond_produtor.wait()  # Espera sem busy-wait
            
            if not self.ativo:
                return False
            
            inicio_espera = time.time()
            self.buffer.append(item)
            self.items_produzidos += 1
            self.tempos_espera.append(time.time() - inicio_espera)
            self.cond_consumidor.notify()  # Notifica consumidor
            return True
    
    def consumir(self):
        with self.lock:
            while len(self.buffer) == 0 and self.ativo:
                self.cond_consumidor.wait()  # Espera sem busy-wait
            
            if not self.ativo and len(self.buffer) == 0:
                return None
            
            item = self.buffer.popleft()
            self.items_consumidos += 1
            self.cond_produtor.notify()  # Notifica produtor
            return item

Exercício 3 - Transferências entre Contas
Descrição
Simulação de M contas e T threads realizando transferências aleatórias entre contas, protegendo os saldos com travas adequadas e comprovando a invariância da soma global.

Solução Proposta
Estrutura:
Classe Conta representa uma conta bancária com seu lock

Classe SistemaBancario gerencia as contas e transferências

Transferências seguras e inseguras para comparação

Verificação da soma global com asserções

Mecanismos de Sincronização:
Um mutex por conta (lock por recurso)

Ordenação por ID para evitar deadlock

Versão sem locks para demonstrar condições de corrida

Código Principal:

    class Conta:
    def __init__(self, id, saldo_inicial=1000):
        self.id = id
        self.saldo = saldo_inicial
        self.lock = threading.Lock()
    
    def transferir(self, destino, valor):
        # Evita deadlock com ordenação por ID
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
    
    def transferir_inseguro(self, origem_idx, destino_idx, valor):
        # Simula condição de corrida
        if self.contas[origem_idx].saldo >= valor:
            time.sleep(random.uniform(0.001, 0.005))  # Janela de condição de corrida
            self.contas[origem_idx].saldo -= valor
            time.sleep(random.uniform(0.001, 0.005))
            self.contas[destino_idx].saldo += valor
            return True
        return False

Exercício 4 - Pipeline
Descrição
Construção de uma linha de processamento com três threads: captura, processamento e gravação, conectadas por duas filas limitadas com protocolo de encerramento limpo.

Solução Proposta
Estrutura:
Classe FilaLimitada implementa fila com backpressure

Três threads: Captura, Processamento, Gravação

Duas filas limitadas conectando os estágios

Protocolo poison pill para encerramento

Mecanismos de Sincronização:
queue.Queue(maxsize=N) com bloqueio natural

Poison pill (None) para sinalizar fim

Timeout para evitar deadlock no encerramento

Código Principal:

    class FilaLimitada:
    def __init__(self, tamanho_max):
        self.fila = Queue(maxsize=tamanho_max)
        self.ativo = True
    
    def colocar(self, item):
        while self.ativo:
            try:
                self.fila.put(item, timeout=0.1)
                return True
            except:
                if not self.ativo:
                    return False
        return False
    
    def retirar(self, timeout=None):
        try:
            return self.fila.get(timeout=timeout)
        except Empty:
            return None

    class Captura(threading.Thread):
    def __init__(self, fila, num_itens=20):
        super().__init__()
        self.fila = fila
        self.num_itens = num_itens
    
    def run(self):
        for i in range(self.num_itens):
            self.fila.colocar(f"Dado_{i}")
            time.sleep(random.uniform(0.1, 0.3))
        self.fila.colocar(None)  # Poison pill

    class Processamento(threading.Thread):
    def run(self):
        while True:
            item = self.fila_entrada.retirar(timeout=0.1)
            if item is None:  # Detecta poison pill
                self.fila_saida.colocar(None)  # Propaga
                break
            if item is not None:
                processado = f"Processado({item})"
                self.fila_saida.colocar(processado)

  Exercício 5 - Pool de Threads
Descrição
Implementação de um pool fixo de N threads que processa uma fila concorrente de tarefas CPU-bound, com interface interativa e finalização apropriada.

Solução Proposta
Estrutura:
Classe ThreadPool gerencia pool de threads e fila de tarefas

Tarefas CPU-bound: teste de primalidade e Fibonacci

Interface interativa via entrada padrão

Finalização com poison pills

Mecanismos de Sincronização:
queue.Queue thread-safe para fila de tarefas

Lock para proteger resultados coletados

Poison pills para finalização do pool

Código Principal:

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
    
    def shutdown(self):
        self.ativo = False
        # Envia poison pills para todas as threads
        for _ in range(self.num_threads):
            self.fila_tarefas.put(None)
        for t in self.threads:
            t.join()

    # Funções CPU-bound
    def eh_primo(n):
    if n < 2:
        return False
    for i in range(2, int(math.sqrt(n)) + 1):
        if n % i == 0:
            return False
    return True

    def fibonacci(n):
    if n <= 1:
        return n
    a, b = 0, 1
    for _ in range(2, n + 1):
        a, b = b, a + b
    return b

  Exercício 6 - Processamento Paralelo
Descrição
Leitura de um arquivo grande de inteiros calculando soma total e histograma de frequências usando P threads em paralelo, com medição de speedup.

Solução Proposta
Estrutura:
Classe ProcessadorArquivo gerencia leitura e processamento

Particionamento do arquivo em blocos

Map local em cada thread

Reduce na thread principal

Medição de speedup para diferentes P

Código Principal:

    class ProcessadorArquivo:
    def __init__(self, arquivo, num_threads=4):
        self.arquivo = arquivo
        self.num_threads = num_threads
        self.lock = threading.Lock()
    
    def ler_arquivo_em_blocos(self):
        with open(self.arquivo, 'r') as f:
            numeros = [int(line.strip()) for line in f if line.strip()]
        
        tamanho_bloco = math.ceil(len(numeros) / self.num_threads)
        blocos = []
        for i in range(0, len(numeros), tamanho_bloco):
            blocos.append(numeros[i:i + tamanho_bloco])
        return blocos
    
    def processar_bloco(self, bloco):
        soma = sum(bloco)
        histograma = defaultdict(int)
        for n in bloco:
            histograma[n] += 1
        return soma, dict(histograma)
    
    def processar_paralelo(self):
        blocos = self.ler_arquivo_em_blocos()
        threads = []
        resultados_parciais = []
        
        def worker(bloco):
            soma, hist = self.processar_bloco(bloco)
            with self.lock:
                resultados_parciais.append((soma, hist))
        
        inicio = time.time()
        for bloco in blocos:
            t = threading.Thread(target=worker, args=(bloco,))
            threads.append(t)
            t.start()
        for t in threads:
            t.join()
        
        # Reduce
        soma_total = sum(s[0] for s in resultados_parciais)
        histograma_total = defaultdict(int)
        for _, hist in resultados_parciais:
            for n, count in hist.items():
                histograma_total[n] += count
        
        return {
            'soma_total': soma_total,
            'histograma': dict(histograma_total),
            'tempo': time.time() - inicio
        }

  Exercício 7 - Jantar dos Filósofos
Descrição
Implementação do problema dos filósofos com duas soluções para evitar deadlock: ordem global de aquisição e semáforo limitante.

Soluções Propostas
Estrutura:
Classe Filosofo representa cada filósofo

Garfos representados por mutex

Dois métodos: ordem global e semáforo

Coleta de métricas por filósofo

Solução A: Ordem Global de Aquisição

    def _pegar_garfos_ordem(self):
    if self.id % 2 == 0:
        self.garfo_esquerdo.acquire()
        self.garfo_direito.acquire()
    else:
        self.garfo_direito.acquire()
        self.garfo_esquerdo.acquire()
        
 Solução B: Semáforo Limitante

    def _pegar_garfos_semaforo(self):
    with self.semaforo_global:  # Permite apenas 4 filósofos
        self.garfo_esquerdo.acquire()
        self.garfo_direito.acquire()

Exercício 8 - Buffer com Bursts
Descrição
Extensão do exercício 2 simulando rajadas de produção (bursts) e períodos de ociosidade, com backpressure para controle de fluxo.

Solução Proposta
Estrutura:
Classe BufferBurst estende buffer com histórico de ocupação

Produtores com capacidade de gerar bursts

Consumidores com taxas variáveis

Monitoramento contínuo da ocupação

Código Principal:

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
    
    def produzir(self, item):
        with self.lock:
            while len(self.buffer) >= self.tamanho and self.ativo:
                self.produtores_parados += 1  # Contabiliza backpressure
                self.cond_produtor.wait()
                self.produtores_parados -= 1
            
            if not self.ativo:
                return False
            
            self.buffer.append(item)
            ocupacao = len(self.buffer) / self.tamanho * 100
            self.historico_ocupacao.append((time.time(), ocupacao))
            self.cond_consumidor.notify()
            return True

    class ProdutorBurst(threading.Thread):
    def __init__(self, buffer, id, burst_size, burst_prob=0.3):
        super().__init__()
        self.buffer = buffer
        self.id = id
        self.burst_size = burst_size
        self.burst_prob = burst_prob
        self.ativo = True
    
    def run(self):
        while self.ativo:
            if random.random() < self.burst_prob:
                # Rajada de produção (burst)
                for _ in range(self.burst_size):
                    if not self.ativo:
                        break
                    self.buffer.produzir(f"Burst{self.id}-{item_id}")
                    time.sleep(random.uniform(0.01, 0.05))
            else:
                # Produção normal
                self.buffer.produzir(f"Prod{self.id}-{item_id}")
                time.sleep(random.uniform(0.3, 0.7))

  Exercício 9 - Corrida de Revezamento
Descrição
Modelagem de uma corrida de revezamento onde K threads representam uma equipe e todas precisam alcançar uma barreira para liberar a próxima "perna" da prova.

Solução Proposta
Estrutura:
Classe BarreiraRevezamento implementa barreira reutilizável

Classe EquipeRevezamento representa membros da equipe

Múltiplas equipes competindo simultaneamente

Registro de voltas completadas por minuto

Código Principal:

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
                self.cond.notify_all()  # Libera todos
            else:
                while self.geracao == minha_geracao:
                    self.cond.wait()  # Aguarda os outros

    class EquipeRevezamento(threading.Thread):
    def __init__(self, id, barreira, num_voltas=5):
        super().__init__()
        self.id = id
        self.barreira = barreira
        self.num_voltas = num_voltas
        self.voltas_completadas = 0
        self.tempos_volta = []
    
    def run(self):
        while self.ativo and self.voltas_completadas < self.num_voltas:
            # Cada membro corre uma "perna"
            tempo_volta = random.uniform(0.5, 1.5)
            time.sleep(tempo_volta)
            self.voltas_completadas += 1
            self.tempos_volta.append(tempo_volta)
            self.barreira.esperar()  # Aguarda os outros membros

   Exercício 10 - Watchdog
Descrição
Implementação de um watchdog que detecta ausência de progresso e identifica threads bloqueadas, com correção usando ordem total de travamento.

Solução Proposta
Estrutura:
Classe Recurso representa recursos com lock e proprietário

Classe ThreadDeadlock threads que adquirem recursos

Classe Watchdog monitora threads bloqueadas

Dois modos: aleatório (causa deadlock) e ordenado (previne)

Código Principal:

    class Recurso:
    def __init__(self, id):
        self.id = id
        self.lock = threading.Lock()
        self.proprietario = None
    
    def adquirir(self, thread_id, tempo_maximo=None):
        inicio = time.time()
        while True:
            if self.lock.acquire(timeout=0.1 if tempo_maximo else None):
                self.proprietario = thread_id
                return True
            if tempo_maximo and (time.time() - inicio) > tempo_maximo:
                return False

    class Watchdog(threading.Thread):
    def __init__(self, threads, timeout=3.0):
        super().__init__()
        self.threads = threads
        self.timeout = timeout
        self.ativo = True
    
    def run(self):
        while self.ativo:
            time.sleep(1)
            agora = time.time()
            for thread in self.threads:
                if thread.ativo and (agora - thread.acordado) > self.timeout:
                    print(f"⚠️ ALERTA: Thread {thread.id} pode estar bloqueada!")
                    for recurso in thread.recursos:
                        if recurso.lock.locked():
                            print(f"   Recurso {recurso.id}: bloqueado por {recurso.proprietario}")
                    print(f"   Progresso total: {thread.progresso}")

 Conclusão
Resumo dos Aprendizados
Este laboratório proporcionou uma compreensão profunda dos conceitos fundamentais de sistemas operacionais relacionados à concorrência:

Sincronização: Uso de locks, semáforos e variáveis de condição

Padrões de Design: Produtor-consumidor, pipeline, pool de threads

Problemas Comuns: Condições de corrida, deadlock, starvation

Métricas: Importância de medir desempenho e coletar estatísticas

Monitoramento: Watchdogs para detecção de problemas

Desafios Superados
Deadlock em transferências: Resolvido com ordenação por ID

Backpressure em buffers: Implementado com variáveis de condição

Starvation no jantar: Mitigado com fairness nos métodos

Condições de corrida: Identificadas e corrigidas com locks

Aplicações Práticas
Sistemas bancários (transferências)

Processamento de dados (pipeline)

Servidores web (pool de threads)

Sistemas embarcados (watchdogs)

Próximos Passos
Implementar versões com multiprocessing

Testar com cargas maiores

Adicionar mais métricas de desempenho

Explorar outras estratégias de sincronização

