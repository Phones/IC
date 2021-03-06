import os
import time
import random
from time import sleep
from grafo_pronto import grafo
from helpers import *
from desenha_rede import *
from copy import deepcopy
# from pasta_maluca.GA_BRABO_BAO import GA

G = grafo('pdh.txt')
random.seed(None)
class cromossomo:
    demanda_caminho = None
    fluxo_aresta = None
    custo = None
    soma_tam_caminhos= None
    tempo_solucao = None

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


    def troca_caminhos(self, obj_cromossomo, demanda_idx):
        demanda_caminho = [] + obj_cromossomo.demanda_caminho
        fluxo_aresta = [] + obj_cromossomo.fluxo_aresta
        custo = 0.0
        soma_tam_caminho = 0
        conjunto_caminho = [] + G.caminhos[demanda_idx]

        for e in demanda_caminho[demanda_idx]:#remove fluxo do caminho atual
            fluxo_aresta[e] -= G.demandas[demanda_idx].routing_value

        ref_fluxo_aresta = [] + fluxo_aresta

        '''Para cada caminho, dentro dos caminhos, e verifica quais arestas est??o sendo utilizadas,
        Coloca a aresta que est?? utilizada na lista de caminho formatado'''
        for cmh in conjunto_caminho: # para cada caminho do conjunto de caminhos
            cmh_formatado = []
            for i in range(len(cmh)):
                if cmh[i] == 1:
                    cmh_formatado.append(i)

            # Troca o caminho da variavel auxiliar
            demanda_caminho[demanda_idx] = [] + cmh_formatado

            # Soma o fluxo do novo caminho, no fluxo_aresta
            for e in cmh_formatado:
                fluxo_aresta[e] += G.demandas[demanda_idx].routing_value

            # Calcula o custo
            custo = self.__calcula_custo_dif(fluxo_aresta)
            # Calcula a soma dos tamanhos dos caminhos
            for c in demanda_caminho:
                soma_tam_caminho += len(c)

            # Verifica de melhorou, atraves da dominancia de pareto
            if (custo < obj_cromossomo.custo and soma_tam_caminho <= obj_cromossomo.soma_tam_caminhos) or (custo<=obj_cromossomo.custo and soma_tam_caminho<obj_cromossomo.soma_tam_caminhos):
            #if custo < self.custo:
                obj_cromossomo.demanda_caminho = [] + demanda_caminho
                obj_cromossomo.fluxo_aresta = [] + fluxo_aresta
                obj_cromossomo.custo = custo
                obj_cromossomo.soma_tam_caminhos = soma_tam_caminho
                continua = 1
            fluxo_aresta = [] + ref_fluxo_aresta

        return obj_cromossomo


    def busca_local(self,  pos, lista_limites, tempo_):
        lista_numeros_random = [i for i in range(len(self.demanda_caminho))]
        random.shuffle(lista_numeros_random)
        print("LISTAAAAAAAAAAAAAAAAA: ", lista_numeros_random)
        
        continua = 1
        while continua:
            continua = 0
            for demanda_idx in lista_numeros_random:
                obj_auxiliar = self.troca_caminhos(cromossomo(tipo="receber",
                    demanda_caminho=self.demanda_caminho,
                    fluxo_aresta=self.fluxo_aresta,custo=self.custo,
                    soma_tam_caminhos=self.soma_tam_caminhos), demanda_idx)

                if (obj_auxiliar.custo < self.custo and obj_auxiliar.soma_tam_caminhos <= self.soma_tam_caminhos) or (obj_auxiliar.custo <= self.custo and obj_auxiliar.soma_tam_caminhos < self.soma_tam_caminhos):
                    self.demanda_caminho = [] + obj_auxiliar.demanda_caminho
                    self.fluxo_aresta = [] + obj_auxiliar.fluxo_aresta
                    self.custo = obj_auxiliar.custo
                    self.soma_tam_caminhos = obj_auxiliar.soma_tam_caminhos
                    continua = 1


        return self.demanda_caminho, self.fluxo_aresta, self.custo, (time.time() - tempo_)

    def __lt__(self,other):
        return (self.custo < other.custo and self.soma_tam_caminhos <= other.soma_tam_caminhos) or (self.custo <= other.custo and self.soma_tam_caminhos < other.soma_tam_caminhos)

    def __eq__(self, other):
        return (self.custo == other.custo and self.soma_tam_caminhos == other.soma_tam_caminhos)

    def eh_aceitavel(self,demanda_caminho):
        fluxo_aresta = [0.0 for i in range(len(self.fluxo_aresta))]
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
                if i <= p1 or i > p2:
                    ord.append(0)
                elif i<= p2:
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


    def __init__(self,tipo='gerar',demanda_caminho=None,fluxo_aresta=None,custo=0,soma_tam_caminhos=0,item=None):
        if tipo == 'gerar':
            self.__gera_cromossomo()
            self.__calcula_custo()
            self.__calcula_soma_tamanho_caminhos()
            #self.busca_local()
            return

        if tipo == 'receber':
            self.demanda_caminho = demanda_caminho
            self.fluxo_aresta = fluxo_aresta
            self.__calcula_custo()
            self.__calcula_soma_tamanho_caminhos()
            #self.__busca_local()
            return

        if tipo == 'atribuir':
            self.demanda_caminho = item.demanda_caminho
            self.fluxo_aresta = item.fluxo_aresta
            self.custo = item.custo
            self.soma_tam_caminhos = item.soma_tam_caminhos
            return
            
        if tipo == 'colocar':
            self.demanda_caminho = demanda_caminho
            self.fluxo_aresta = fluxo_aresta
            self.custo = custo
            self.soma_tam_caminhos = soma_tam_caminhos
            return

class ABC:
    def __init__(self, nome_instancia='', tempo_max_execucao=0,quant_abelhas=100):
        self.ciclos = 0
        self.todos_fluxos = []
        self.total_abelhas = quant_abelhas
        self.tempo_max_execucao = tempo_max_execucao
        self.quantidade_abelhas_empregadas = int(self.total_abelhas / 2)
        self.tamanho_populacao = int(self.total_abelhas / 2)
        self.limite_tentativas_por_solucao = 20
        self.quantidade_abelhas_observadoras = self.quantidade_abelhas_empregadas
        self.quantidade_abelhas_exploradoras = self.quantidade_abelhas_empregadas
        self.populacao, self.ranks = [], []
        self.melhor_solucao_global = None
        self.lista_limites = [0 for i in range(self.tamanho_populacao)]
        self.melhores_solucoes = None
        self.tempo_inicio = time.time()

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
            print("SOLU????O, Custo: ", self.melhores_solucoes[i].custo)
            print("SOLU????O, soma_tam_caminhos: ", self.melhores_solucoes[i].soma_tam_caminhos)
        linha()


    def imprime_apenas_um_cromosso(self, cromo, pos):
        print("Custo: ", cromo.custo)
        print("Ranks: ", self.ranks[pos])
        print("soma_tam_caminhos: ", cromo.soma_tam_caminhos) 

    def get_frente_pareto_geracao_atual(self):
        lista_posicao_frente_geracao = []
        for i in range(len(self.ranks)):
            if self.ranks[i] == 1:
                ''' Adiciona a posi????o dos ranks que possuem valor 1, 
                esses s??o a frente de pareto da gera????o atual. '''
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
            ''' Para evitar a indefini????o matematica, de divis??o por 0. Onde o menor_rank, e o maior_rank ficam iguais
            sendo por exemplo, ambos igual a 1.'''
            if menor_rank == maior_rank:
                pis.append(1)
                continue

            pis.append( ((self.ranks[i] - menor_rank) / (maior_rank - menor_rank)) )

        return pis

    def fase_abelha_empregadas(self):
        '''Executa a fase das abelhas empregadas, aplicando uma busca local em cada fonte de elemento.'''
        for i in range(self.quantidade_abelhas_empregadas):
             
            self.populacao[i].demanda_caminho, self.populacao[i].fluxo_aresta, self.populacao[i].custo, self.populacao[i].tempo_solucao = self.populacao[i].busca_local(i, self.lista_limites, self.tempo_inicio)

    def fase_abelha_observadoras(self, pis):
        for i in range(self.quantidade_abelhas_observadoras):
            # Probabilidade
            pi, prob = pis[i], random.random()
            if prob < pi:
                #print(" !DENTRO DO IF! ")
                # Faz a escolha desse fonte de alimento, e envia uma abelha observadora dela
                self.populacao[i].demanda_caminho, self.populacao[i].fluxo_aresta, self.populacao[i].custo, self.populacao[i].tempo_solucao = self.populacao[i].busca_local(i, self.lista_limites, self.tempo_inicio)

    def verifica_existe(self, obj, lista):
        '''Verifica se um objeto, j?? existe em uma determinada lista de obj, da classe cromossomo.'''
        for obj_lista in lista:
            if obj == obj_lista:
                return True

        return False

    def fase_abelha_exploradoras(self):
        for i in range(self.quantidade_abelhas_exploradoras):
            '''Caso essa fonte de alimento tenha se esgotado, envia uma abelha exploradora,
            onde ela substitui essa fonte, por uma fonte de alimento aletoria'''
            #if self.lista_limites[i] == self.limite_tentativas_por_solucao:
            self.populacao[i] = cromossomo()

    def armazena_melhores_solucao(self, frente_pareto_solucao_atual):
        '''Caso a lista de melhores solu????es esteja vazia, significa que est?? na primeira itera????o,
        logo a primeira frente de pareto gerada, s??o as melhores solu????es.'''
        if len(self.melhores_solucoes) == 0:
            # Evita a inser????o de objs repetidos
            for obj_frente in frente_pareto_solucao_atual:
                if self.verifica_existe(obj_frente, self.melhores_solucoes):
                    self.melhores_solucoes.append(obj_frente)
            return

        for sol in frente_pareto_solucao_atual:
            '''Verifica, se a solu????o domina alguma das solu????es que est??o como melhores solu????es at?? ent??o,
            caso isso ocorra, remove as solu????es que s??o dominadas, e ent??o insere essa nova solu????o a lista
             de melhores solu????es.'''
            
            # Evita inser????o de objetos repetidos
            if self.verifica_existe(sol, self.melhores_solucoes):
                continue

            dominada = False
            lista_aux = []
            for m_sol in self.melhores_solucoes:
                if not sol < m_sol:
                    # N??o domina uma das melhores solu????es
                    lista_aux.append(m_sol)
                elif m_sol < sol:
                    # Domina a sol
                    dominada = True
                    break

            if not dominada:
                lista_aux.append(sol)
                ''' Substitui a lista de melhores solu????es, por um nova lista, 
                que contenha a nova solu????o que foi adicionada.'''
                self.melhores_solucoes = [] + lista_aux


    def salva_fluxos(self):
        aux = ''
        arq = open("fluxos.txt", "w")
        for m_sol in self.melhores_solucoes:
            aux += str(m_sol.custo) + "\n"
            aux += str(m_sol.soma_tam_caminhos) + "\n"
            aux += str(m_sol.fluxo_aresta) + "\n"
            aux += str(m_sol.tempo_solucao) + "\n"
            self.todos_fluxos.append(m_sol.fluxo_aresta)

        arq.write(aux)
        arq.close()

    def get_fluxos(self):
        return self.todos_fluxos

    def salva_parametros_usados(self):
        string = ''
        string += 'ciclos: ' + str(self.ciclos) + '\n'
        string += 'total_abelhas: ' + str(self.total_abelhas) + '\n'
        string += 'tempo_max_execucao: ' + str(self.tempo_max_execucao) + '\n'
        string += 'quantidade_abelhas_empregadas: ' + str(self.quantidade_abelhas_empregadas) + '\n'
        string += 'tamanho_populacao: ' + str(self.tamanho_populacao) + '\n'
        string += 'limite_tentativas_por_solucao: ' + str(self.limite_tentativas_por_solucao) + '\n'
        string += 'quantidade_abelhas_observadoras: ' + str(self.quantidade_abelhas_observadoras) + '\n'
        string += 'quantidade_abelhas_exploradoras: ' + str(self.quantidade_abelhas_exploradoras) + '\n'

        arq = open('parametros_utilizados.txt', 'w')
        arq.write(string)
        arq.close()

    def salva_custos_e_soma_caminho_ordenado(self):
        string = ''
        lista_aux = []
        for i in range(len(self.melhores_solucoes)):
            lista_aux.append([self.melhores_solucoes[i].custo, self.melhores_solucoes[i].soma_tam_caminhos, i, self.melhores_solucoes[i].tempo_solucao])

        lista_aux.sort()
        for pos in lista_aux:
            string += "SOLU????O " + str(pos[2]) + ", Custo: " + str(pos[0]) + '\n'
            string += "SOLU????O " + str(pos[2]) + ", soma_tam_caminhos: " + str(pos[1]) + '\n'
            string += "SOLU????O " + str(pos[2]) + ", tempo: " + str(pos[3]) + '\n'

        arq = open('custos_e_soma_caminho.txt', 'w')
        arq.write(string)
        arq.close()

    def gambiarra_suprema_sinistra_verifica_chegou14(self):
        for sol in self.melhores_solucoes:
            aux___ = str(sol.custo)
            if aux___[0] == '1' and aux___[1] == '4':
                return True

        return False

    def plot_frente_de_pareto(self,geracao):
        grande_frente_pareto = self.melhores_solucoes
        custo_frente = np.array([grande_frente_pareto[i].custo for i in range(len(grande_frente_pareto))])
        soma_tam_caminhos_frente = np.array([grande_frente_pareto[i].soma_tam_caminhos for i in range(len(grande_frente_pareto))])
        custo = np.array([self.populacao[i].custo for i in range(len(self.populacao))])
        soma_tam_caminhos = np.array([self.populacao[i].soma_tam_caminhos for i in range(len(self.populacao))])
        plt.scatter(soma_tam_caminhos,custo,c=np.array(['blue' for i in range(len(self.populacao))]),label='Outras solu????es')
        plt.scatter(soma_tam_caminhos_frente, custo_frente, c=np.array(['red' for i in range(len(grande_frente_pareto))]),label='Frente de pareto')
        plt.xlabel('Soma dos Hops')
        plt.ylabel('Custo')
        plt.title('ABC - Gera????o '+geracao)
        plt.legend()
        print(os.getcwd())
        caminho = 'Gera????o('+str(geracao)+').png'
        plt.savefig(caminho)
        plt.close()

    def execute_abc(self):
        time_ini = time.time()
        self.gera_populacao_inicial()
        self.monta_vetor_ranks()
        self.imprime_populacao()
        # Cada cromossomo j?? possui o seu fitness embutido, logo n??o ?? necessario fazer a etapa de fitness da gera????o
        self.monta_vetor_ranks()
        self.melhores_solucoes = self.get_frente_pareto_geracao_atual()
        conttttt = 0
        self.tempo_inicio = time.time()
        while (time.time() - self.tempo_inicio) < self.tempo_max_execucao:
            print(f"------------------ ciclo -> {self.ciclos} ------------------")
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

            if (time.time() - self.tempo_inicio) >= self.tempo_max_execucao:
                self.ciclos += 1
                break

            print("FASE DAS ABELHAS EXPLORADORAS")
            self.fase_abelha_exploradoras()
            print("-------------------------------------------------")
            self.ciclos += 1

            # if self.gambiarra_suprema_sinistra_verifica_chegou14():
            #     print("Inicio: ", self.tempo_inicio)
            #     print("Final: ", time.time() - self.tempo_inicio)
            #     break
            conttttt += 1
        print(" !FIM DA EXECU????O!\nMELHORES SOLU????ES ENCONTRADAS: ")
        self.imprime_custo_e_soma_caminho_solucao()
        return conttttt
'''
--------------------------------- PARAMETROS DO ABC ---------------------------------

SN -> Total de abelhas na popula????o, sendo que, metade delas conehcem a fonte de alimento,
e a outra metade far?? escolha de acordo com a qualidade da fonte. Logo, metade s??o abelhas
campeiras, e a outra metade s??o abelhas observadoras.

tamanho da popula????o inicial -> SN/2

Cada solu????o xi ?? um vetor D-dimensional, sendo D o n??mero de vari??veis de projeto do problema

C -> Quantidade de ciclos que algoritmo vai repetir

MP -> Tamanho da popula????o

N??mero de abelhas empregadas ?? igual ao n??mero de solu????es na popula????o
-> total_abelhas = SN
-> tam_populacao_inicial = SN/2
-> limite_tentativas_por_solucao = Quantas vezes uma abelha tanta melhorar a solu????o at?? abandonar ela
-> 
'''
# Teste feitos com limita????o de execu????o de no maximo 1h(3600s)
quant_tempo_duracao = 3600

total_abelhas = 2000

obj = ABC("pdh.txt", tempo_max_execucao=quant_tempo_duracao,quant_abelhas=total_abelhas)
conttttt = obj.execute_abc()
print("Quantidade de ciclos executados: ", obj.ciclos)

name = 's'
while name != 'n' and name != 's':
    name = input("Plotar o gr??fico?(s/n)").lower()
    print(name)


if name == 's':
    # Cria a pasta que ir?? armazenar os plots
    seleciona_nome_pasta_e_cria_pasta()
    #
    obj.plot_frente_de_pareto(str(conttttt))
    # Salva os fluxos no arquivo de texto, e preenche lista de fluxos
    obj.salva_fluxos()
    # Salva os parametro utilizados
    obj.salva_parametros_usados()
    # Salva os custos e soma caminhos das solu????es
    obj.salva_custos_e_soma_caminho_ordenado()
    # Desenha o grafico de todos os fluxos das solu????es encontradas
    desenha_grafico_fluxo(G, obj.get_fluxos())


# print("Enviando popula????o para o GA!")
# obj_GA = GA(populacao=obj.self.populacao)
#
# obj_GA.Executa()