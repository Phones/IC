import os
import time
import random
from time import sleep
from grafo_pronto import grafo
from helpers import *

G = grafo('pdh.txt')
random.seed(None)
class cromossomo:
    demanda_caminho = None
    fluxo_aresta = None
    custo = None
    soma_tam_caminhos= None

    def __gera_cromossomo(self):
        candidato = [0 for i in range(len(G.demandas))]
        while True:
            tam = len(G.demandas)
            for i in range(tam):
                candidato[i] = random.randint(0,len(G.caminhos[i])-1)
            a=[0.0 for i in range(len(G.arestas))]
            for i in range(tam):
                tam1 = len(G.caminhos[i][candidato[i]])
                for e in range(tam1):
                    if G.caminhos[i][candidato[i]][e] == 1:
                        a[e] += G.demandas[i].routing_value
            deu = True
            for e in range(len(G.arestas)):
                if a[e] > G.array_max_cap[e]:
                    deu = False
                    break
            if deu:
                self.demanda_caminho= [[] for i in range(tam)]
                for i in range(tam):
                    caminho = []+G.caminhos[i][candidato[i]]
                    tam1 = len(caminho)
                    for j in range(tam1):
                        if caminho[j] == 1:
                            self.demanda_caminho[i].append(j)
                self.fluxo_aresta = a
                break

    def __calcula_custo(self):
        tam = len(G.arestas)
        self.custo = 0.0
        for e in range(len(G.arestas)):
            self.custo+=G.arestas[e].pre_installed_capacity_cost
            if self.fluxo_aresta == 0 or self.fluxo_aresta[e]<=G.arestas[e].pre_installed_capacity:
                continue
            val = 100000000000.0
            for k in range(len(G.arestas[e].module_list)):
                if G.arestas[e].module_list[k].capacidade+G.arestas[e].pre_installed_capacity >= self.fluxo_aresta[e]:
                    val = min(val,G.arestas[e].module_list[k].cost)
            self.custo += val

    def __calcula_custo_dif(self,fluxo_aresta):
        tam = len(G.arestas)
        custo = 0.0
        for e in range(len(G.arestas)):
            custo+=G.arestas[e].pre_installed_capacity_cost
            if fluxo_aresta[e] == 0 or fluxo_aresta[e]<=G.arestas[e].pre_installed_capacity:
                continue
            val = 100000000000.0
            for k in range(len(G.arestas[e].module_list)):
                if G.arestas[e].module_list[k].capacidade +G.arestas[e].pre_installed_capacity >= fluxo_aresta[e]:
                    val = min(val, G.arestas[e].module_list[k].cost)
            custo += val
        return custo

    def __calcula_soma_tamanho_caminhos(self):
        tam = len(self.demanda_caminho)
        self.soma_tam_caminhos=0
        for i in range(tam):
            self.soma_tam_caminhos+=len(self.demanda_caminho[i])

    def __imprime_cromossomo(self):
        print('-------------')
        for d in range(len(self.demanda_caminho)):
            for e in range(len(self.demanda_caminho[d])):
                print(self.demanda_caminho[d][e],end=' ')
            print()
        print('-------------')

    def busca_local(self, pos, lista_limites):
        continua = 1
        while continua:
            tt = len(self.demanda_caminho)
            demanda_idx = 0
            continua = 0

            while demanda_idx < len(self.demanda_caminho):
                demanda_caminho = [] + self.demanda_caminho
                fluxo_aresta = [] + self.fluxo_aresta
                custo = 0.0
                soma_tam_caminho = 0
                conjunto_caminho = [] + G.caminhos[demanda_idx]

                for e in demanda_caminho[demanda_idx]:#remove fluxo do caminho atual
                    fluxo_aresta[e] -= G.demandas[demanda_idx].routing_value

                ref_fluxo_aresta = [] + fluxo_aresta

                for cmh in conjunto_caminho:#para cada caminho do conjunto de caminhos
                    cmh_formatado = []
                    for i in range(len(cmh)):
                        if cmh[i] == 1:
                            cmh_formatado.append(i)

                    demanda_caminho[demanda_idx] = [] + cmh_formatado

                    for e in cmh_formatado:
                        fluxo_aresta[e] += G.demandas[demanda_idx].routing_value

                    custo = self.__calcula_custo_dif(fluxo_aresta)
                    for c in demanda_caminho:
                        soma_tam_caminho += len(c)

                    if (custo < self.custo and soma_tam_caminho <= self.soma_tam_caminhos) or (custo<=self.custo and soma_tam_caminho<self.soma_tam_caminhos):
                    #if custo < self.custo:
                        self.demanda_caminho = [] + demanda_caminho
                        self.fluxo_aresta = [] + fluxo_aresta
                        self.custo = custo
                        self.soma_tam_caminhos = soma_tam_caminho
                        continua = 1
                    fluxo_aresta = [] + ref_fluxo_aresta
                demanda_idx+=1


        return demanda_caminho, fluxo_aresta, custo

    def __lt__(self,other):
        return (self.custo < other.custo and self.soma_tam_caminhos <= other.soma_tam_caminhos) or (self.custo <= other.custo and self.soma_tam_caminhos < other.soma_tam_caminhos)

    def __eq__(self, other):
        return (self.custo == other.custo and self.soma_tam_caminhos == other.soma_tam_caminhos)

    def eh_aceitavel(self,demanda_caminho):
        fluxo_aresta = [ 0.0 for i in range(len(self.fluxo_aresta))]
        for cmh in range(len(demanda_caminho)):
            for e in demanda_caminho[cmh]:
                fluxo_aresta[e] += G.demandas[cmh].routing_value
        for e in range(len(fluxo_aresta)):
            if fluxo_aresta[e] > G.array_max_cap[e]+G.arestas[e].pre_installed_capacity:
                return None
        return fluxo_aresta

    def __add__(self, other):
        while True:
            filho1 = []
            filho2 = []
            sz = len(self.demanda_caminho)
            p1 = random.randint(1,int(sz/2))
            p2 = random.randint(int(sz/2+1),sz-2)
            ord = []
            for i in range(len(self.demanda_caminho)):
                if i<=p1 or i>p2:
                    ord.append(0)
                elif i<=p2:
                    ord.append(1)

            for c in range(len(self.demanda_caminho)):
                if ord[c] == 1:
                    filho1.append(self.demanda_caminho[c])
                    filho2.append(other.demanda_caminho[c])
                else:
                    filho2.append(self.demanda_caminho[c])
                    filho1.append(other.demanda_caminho[c])
            prole = []
            f1 = self.eh_aceitavel(filho1)
            f2 = self.eh_aceitavel(filho2)
            if f1 != None:
                prole.append(cromossomo(tipo='receber',demanda_caminho=filho1,fluxo_aresta=f1))
            if f2 != None:
                prole.append(cromossomo(tipo='receber',demanda_caminho=filho2,fluxo_aresta=f2))
            return prole

    def mutacao(self):
        return cromossomo()


    def __init__(self,tipo='gerar',demanda_caminho=None,fluxo_aresta=None,item=None):
        if tipo == 'gerar':
            self.__gera_cromossomo()
        if tipo == 'receber':
            self.demanda_caminho = demanda_caminho
            self.fluxo_aresta = fluxo_aresta
        if tipo == 'atribuir':
            self.demanda_caminho = item.demanda_caminho
            self.fluxo_aresta = item.fluxo_aresta
            self.custo = item.custo
            self.soma_tam_caminhos = item.soma_tam_caminhos
            return

        self.__calcula_custo()
        self.__calcula_soma_tamanho_caminhos()

class ABC:
    def __init__(self, nome_instancia=''):
        self.ciclos = 10
        self.total_abelhas = 100
        self.quantidade_abelhas_empregadas = int(self.total_abelhas / 2)
        self.tamanho_populacao = int(self.total_abelhas / 2)
        self.limite_tentativas_por_solucao = 20
        self.quantidade_abelhas_observadoras = self.quantidade_abelhas_empregadas
        self.quantidade_abelhas_exploradoras = self.quantidade_abelhas_empregadas
        self.populacao, self.ranks = [], []
        self.melhor_solucao_global = None
        self.lista_limites = [0 for i in range(self.tamanho_populacao)]
        self.melhores_solucoes = None

    def monta_vetor_ranks(self):
        self.ranks = [ 1 for i in range(len(self.populacao))]
        vis = [0 for i in range(len(self.populacao))]
        r = 1
        while True:
            qt = [0 for i in range(len(self.populacao))]
            for x in range(len(self.populacao)):
                if vis[x] == 1:
                    continue
                for y in range(len(self.populacao)):
                    if vis[y] == 1:
                        continue
                    if self.populacao[x] < self.populacao[y]:
                        qt[y] +=1
            para = True
            for i in range(len(self.populacao)):
                if qt[i] == 0 and vis[i]==0:
                    self.ranks[i] = r
                    vis[i]=1
                    para = False
            if para == True:
                break
            r += 1
        self.frente = []
        for i in range(len(self.populacao)):
            if self.ranks[i] == 1:
                self.frente.append(cromossomo(tipo='atribuir',item=self.populacao[i]))


    def gera_populacao_inicial(self):
        print('gerando populacao')
        for i in range(self.tamanho_populacao):
            self.populacao.append(cromossomo())

        print('Populacao gerada')

    def imprime_populacao(self):
        for i in range(len(self.populacao)):
            po = self.populacao[i]
            print("Custo: ", po.custo)
            print("Ranks: ", self.ranks[i])
            print("soma_tam_caminhos: ", po.soma_tam_caminhos)

    def imprime_custo_e_soma_caminho_solucao(self):
        linha()
        for i in range(len(self.melhores_solucoes)):
            print("SOLUÇÃO, Custo: ", self.melhores_solucoes[i].custo)
            print("SOLUÇÃO, soma_tam_caminhos: ", self.melhores_solucoes[i].soma_tam_caminhos)
        linha()


    def imprime_apenas_um_cromosso(self, cromo, pos):
        print("Custo: ", cromo.custo)
        print("Ranks: ", self.ranks[pos])
        print("soma_tam_caminhos: ", cromo.soma_tam_caminhos) 

    def get_frente_pareto_geracao_atual(self):
        lista_posicao_frente_geracao = []
        for i in range(len(self.ranks)):
            if self.ranks[i] == 1:
                ''' Adiciona a posição dos ranks que possuem valor 1, 
                esses são a frente de pareto da geração atual. '''
                lista_posicao_frente_geracao.append(self.populacao[i])

        return lista_posicao_frente_geracao

    def get_maior_rank(self):
        return max(self.ranks)

    def calcula_somatorio_fitness(self):
        return sum(self.ranks)

    def calcula_pis(self, somatorio_ranks):
        pis = []
        menor_rank = 1
        maior_rank = self.get_maior_rank()

        # Monta o vetor com todas as probabilidades
        for i in range(len(self.populacao)):
            ''' Para evitar a indefinição matematica, de divisão por 0. Onde o menor_rank, e o maior_rank ficam iguais
            sendo por exemplo, ambos igual a 1.'''
            if menor_rank == maior_rank:
                pis.append(1)
                continue

            pis.append( ((self.ranks[i] - menor_rank) / (maior_rank - menor_rank)) )

        return pis

    def fase_abelha_empregadas(self):
        '''Executa a fase das abelhas empregadas, aplicando uma busca local em cada fonte de elemento.'''
        for i in range(self.quantidade_abelhas_empregadas):
             
            self.populacao[i].demanda_caminho, self.populacao[i].fluxo_aresta,self.populacao[i].custo = self.populacao[i].busca_local(i, self.lista_limites)

    def fase_abelha_observadoras(self, pis):
        for i in range(self.quantidade_abelhas_observadoras):
            # Probabilidade
            pi, prob = pis[i], random.random()
            if prob < pi:
                #print(" !DENTRO DO IF! ")
                # Faz a escolha desse fonte de alimento, e envia uma abelha observadora dela
                self.populacao[i].demanda_caminho, self.populacao[i].fluxo_aresta, self.populacao[i].custo= self.populacao[i].busca_local(i, self.lista_limites)

    def verifica_existe(self, obj, lista):
        '''Verifica se um objeto, já existe em uma determinada lista de obj, da classe cromossomo.'''
        for obj_lista in lista:
            if obj == obj_lista:
                return True

        return False

    def fase_abelha_exploradoras(self):
        for i in range(self.quantidade_abelhas_exploradoras):
            '''Caso essa fonte de alimento tenha se esgotado, envia uma abelha exploradora,
            onde ela substitui essa fonte, por uma fonte de alimento aletoria'''
            if self.lista_limites[i] == self.limite_tentativas_por_solucao:
                self.populacao[i] = cromossomo()

    def armazena_melhores_solucao(self, frente_pareto_solucao_atual):
        '''Caso a lista de melhores soluções esteja vazia, significa que está na primeira iteração,
        logo a primeira frente de pareto gerada, são as melhores soluções.'''
        if len(self.melhores_solucoes) == 0:
            # Evita a inserção de objs repetidos
            for obj_frente in frente_pareto_solucao_atual:
                if self.verifica_existe(obj_frente, self.melhores_solucoes):
                    self.melhores_solucoes.append(obj_frente)
            return

        for sol in frente_pareto_solucao_atual:
            '''Verifica, se a solução domina alguma das soluções que estão como melhores soluções até então,
            caso isso ocorra, remove as soluções que são dominadas, e então insere essa nova solução a lista
             de melhores soluções.'''
            
            # Evita inserção de objetos repetidos
            if self.verifica_existe(sol, self.melhores_solucoes):
                continue

            dominada = False
            lista_aux = []
            for m_sol in self.melhores_solucoes:
                if not sol < m_sol:
                    # Não domina uma das melhores soluções
                    lista_aux.append(m_sol)
                elif m_sol < sol:
                    # Domina a sol
                    dominada = True
                    break

            if not dominada:
                lista_aux.append(sol)
                ''' Substitui a lista de melhores soluções, por um nova lista, 
                que contenha a nova solução que foi adicionada.'''
                self.melhores_solucoes = [] + lista_aux



    def execute_abc(self):
        time_ini = time.time()
        self.gera_populacao_inicial()
        self.monta_vetor_ranks()
        self.imprime_populacao()
        # Cada cromossomo já possui o seu fitness embutido, logo não é necessario fazer a etapa de fitness da geração
        self.monta_vetor_ranks()
        self.melhores_solucoes = self.get_frente_pareto_geracao_atual()
        cont = 0
        while cont < self.ciclos:
            print(f"------------------ cilco -> {cont} ------------------")
            print("FASE DAS ABELHAS EMPREGADAS")
            self.fase_abelha_empregadas()
            # Monta o vetor de propabilidades
            print("FASE DAS ABELHAS CALCULA VETOR DE PIS")
            lista_pis = self.calcula_pis(self.calcula_somatorio_fitness())
            print("FASE DAS ABELHAS OBERSADORAS")
            self.fase_abelha_observadoras(lista_pis)
            self.monta_vetor_ranks()
            print("vetor ranks: ", self.ranks)
            frente_pareto_atual = self.get_frente_pareto_geracao_atual()
            self.armazena_melhores_solucao(frente_pareto_atual)
            print("FASE DAS ABELHAS EXPLORADORAS")
            self.fase_abelha_exploradoras()
            print("-------------------------------------------------")
            cont += 1

        print(" !FIM DA EXECUÇÃO!\nMELHORES SOLUÇÕES ENCONTRADAS: ")
        self.imprime_custo_e_soma_caminho_solucao()

'''
--------------------------------- PARAMETROS DO ABC ---------------------------------

SN -> Total de abelhas na população, sendo que, metade delas conehcem a fonte de alimento,
e a outra metade fará escolha de acordo com a qualidade da fonte. Logo, metade são abelhas
campeiras, e a outra metade são abelhas observadoras.

tamanho da população inicial -> SN/2

Cada solução xi é um vetor D-dimensional, sendo D o número de variáveis de projeto do problema

C -> Quantidade de ciclos que algoritmo vai repetir

MP -> Tamanho da população

Número de abelhas empregadas é igual ao número de soluções na população
-> total_abelhas = SN
-> tam_populacao_inicial = SN/2
-> limite_tentativas_por_solucao = Quantas vezes uma abelha tanta melhorar a solução até abandonar ela
-> 
'''

obj = ABC("pdh.txt")
obj.execute_abc()