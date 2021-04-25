import os
import random
from time import sleep
INF = 123456789


class Tsp:
	def __init__(self, quantidade_cidades):
		self.quantidade_cidades = quantidade_cidades
		self.grafo = []#[(1,1),(2,2),(4,2),(5,2),(5,3),(3,4),(4,5),(5,5),(6,3),(5,6)]

		quantt = int(input(""))

		for i in range(quantt):
			en =  input("")
			indice, x, y = en.split(" ")
			x = int(x)
			y = int(y)

			self.grafo.append((x, y))

		print("tam: ", len(self.grafo))



	def imprime_cordenada_cidade(self, cidade):
		print("Codenadas da cidade ",cidade," : ",self.grafo[cidade])

	def calcula_distancia_entre_cidades(self, cidade_1, cidade_2):
		return ((cidade_2[0] - cidade_1[0]) ** 2 + (cidade_2[1] - cidade_1[1]) ** 2) ** (1/2)

	def gera_caminho(self):
		return random.sample(range(self.quantidade_cidades), self.quantidade_cidades)

	def get_cordenadas(self, pos):
		return self.grafo[pos]

class Bee(Tsp):
	def __init__(self, num_nos, tam_geracao, quant_abelhas_empregadas, limite_tentativas_por_solucao):
		super().__init__(num_nos)

		self.num_nos = num_nos
		self.tam_geracao = tam_geracao
		self.matriz_distancia = []
		self.quant_abelhas_empregadas = quant_abelhas_empregadas
		self.quant_abelhas_observadoras = quant_abelhas_empregadas
		self.limite_tentativas_por_solucao = limite_tentativas_por_solucao

	def inicializa_matriz_distancias(self):
		'''Inicializa a matriz, com os valores das distancias de um i a um ponto j'''
		for i in range(self.num_nos):
			lista_aux = []
			for j in range(self.num_nos):
				lista_aux.append(self.calcula_distancia_entre_cidades(self.get_cordenadas(i), self.get_cordenadas(j)))

			self.matriz_distancia.append(lista_aux)

	def imprime_matriz(self, matriz):
		print("===================================================")
		for linha in matriz:
			print(linha)
		print("===================================================")

	def inicia_geracao(self):
		'''Cria a primeira geração'''
		primeira_geracao = []
		for i in range(self.tam_geracao):
			primeira_geracao.append(self.gera_caminho())

		return primeira_geracao

	def calcula_aptdao_solucao(self, solucao):
		gasto_total_deste_caminho = 0
		# SOMA O TOTAL DO CUSTO DESSE CAMINHO
		for i in range(len(solucao) - 1):
			gasto_total_deste_caminho += self.matriz_distancia[solucao[i]][solucao[i + 1]]

		# ADICIONA O CUSTO DE VOLTAR PARA A CIDADE DE ORIGEM, PARA COMPLETAR O CUSTO TOTAL DESSA SOLUÇÃO
		gasto_total_deste_caminho += self.matriz_distancia[solucao[-1]][solucao[0]]
		return gasto_total_deste_caminho

	def calcula_aptdao_geracao(self, geracao):
		aptdao_geracao = []
		for solucao in geracao:
			aptdao_geracao.append(self.calcula_aptdao_solucao(solucao))
		
		return aptdao_geracao

	def get_melhor_solucao(self, fitness_geracao, geracao):
		menor = INF
		soculacao = []
		tam = len(fitness_geracao)
		for i in range(tam):
			if fitness_geracao[i] < menor:
				menor = fitness_geracao[i]
				soculacao = geracao[i]

		return soculacao, menor

	def inicia_lista_limites(self):
		limites = [0 for i in range(self.tam_geracao)]

		return limites

	def get_dois_numeros_diferentes_randomicos(self, intervalo):
		pos_2 = 0
		pos_1 = random.randint(0, intervalo - 1)
		while pos_1 == pos_2:
			pos_2 = random.randint(0, intervalo - 1)

		return pos_1, pos_2

	def swap(self, solucao, pos1, pos2):
		aux = solucao[pos1]
		solucao[pos1] = solucao[pos2]
		solucao[pos2] = aux

		return solucao

	def aplica_busca_vizinhanca_swap(self, solucao):
		solucao_vizinha = [] + solucao
		pos1, pos2 = self.get_dois_numeros_diferentes_randomicos(len(solucao))

		# print("----------------------------------------")
		# print("antes  > ", solucao_vizinha)
		solucao_vizinha = self.swap(solucao_vizinha, pos1, pos2)
		# print("depois > ", solucao_vizinha)
		# print("----------------------------------------")

		return solucao_vizinha

	def atualiza_solucao(self, solucao_atual, aptdao_solucao_atual, contador_limite_solucao):
		while contador_limite_solucao < self.limite_tentativas_por_solucao:
			# GERA UMA NOVA SOLUÇÃO, NA VIZINHANÇA DA SOLUÇÃO ATUAL
			nova_solucao = self.aplica_busca_vizinhanca_swap(solucao_atual)
			# AVALIA ESSA NOVA SOLUÇÃO GERADA
			aptdao_nova_solucao = self.calcula_aptdao_solucao(nova_solucao)

			if aptdao_nova_solucao < aptdao_solucao_atual:
				# print("****** SOLUÇÃO APRIMORADA! ******")
				solucao_atual = nova_solucao
				aptdao_solucao_atual = aptdao_nova_solucao
				contador_limite_solucao = 0
			else:
				contador_limite_solucao += 1

		return solucao_atual, aptdao_solucao_atual, contador_limite_solucao

	def get_somatorio_fitness(self, fitness_geracao):
		somatorio = 0
		for fit in fitness_geracao:
			somatorio += fit 

		return somatorio

	def gera_valore_probabilistico(self, fitness_geracao, somatorio_fitness):
		# GERA O VALOR PROBABILÍSTO, QUE OBTIDO ATRAVÉS DA SEGUINTE EQUAÇÃO: Pi = fit_i / (sum de i=1 a MP de fit_i)
		Pi = []
		for i in range(len(fitness_geracao)):
			Pi.append(0.9 * (fitness_geracao[i] / somatorio_fitness) + 0.1)

		# print("################################################")
		# print("fitness geração ---------> ", fitness_geracao)
		# print("Valores probabilisticos -> ", Pi)
		# print("################################################")
		return Pi

	def seleciona_solucao_abelha_observadora(self, Pis):
		# print("&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&")
		for i in range(len(Pis)):
			# GERA UM VALOR REAL ENTRE 0 e 1
			prob_escolha = random.random()
			# print(prob_escolha," < ",Pis[i])
			if prob_escolha < Pis[i]:
				return i

		# print("&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&")
		print("GAMBIARRA RECURSIVA")
		return self.seleciona_solucao_abelha_observadora(Pis)

	def get_solucao_com_pior_limite(self, limites):
		pos = 0
		maior = 0
		for i in range(len(limites)):
			if limites[i] > maior:
				maior = limites[i]
				pos = i

		return pos

	# def memorizar_melhor_solucao(self):

	def execute(self, C, aux_l):
		self.inicializa_matriz_distancias()
		# self.imprime_matriz(self.matriz_distancia)
		geracao = self.inicia_geracao()
		# self.imprime_matriz(geracao)
		aptdao_geracao = self.calcula_aptdao_geracao(geracao)
		# self.imprime_matriz(aptdao_geracao)
		melhor_solucao, fit_melhor_solucao = self.get_melhor_solucao(aptdao_geracao, geracao)
		lista_limites = self.inicia_lista_limites()
		
		sol_otima = obj.calcula_aptdao_solucao(aux_l)

		cont = 0
		while cont < C:
			# self.imprime_matriz(aptdao_geracao)

			# INICIA FASE DAS ABELHAS EMPREGADAS
			for i in range(self.quant_abelhas_empregadas):
				# ATUALIZA A SOLUÇÃO, A APTDÃO DA NOVA SOLUÇÃO, E QUANTIDADE DE VEZES PARA ENCONTAR ESSA SOLUÇÃO
				geracao[i], aptdao_geracao[i], lista_limites[i] = self.atualiza_solucao(geracao[i], aptdao_geracao[i], lista_limites[i])
			
			somatorio_fitness = self.get_somatorio_fitness(aptdao_geracao)
			Pis = self.gera_valore_probabilistico(aptdao_geracao, somatorio_fitness)
			# INICIA FASE DAS ABELHAS OBSERVADORAS
			for i in range(self.quant_abelhas_observadoras):
				posicao_escolhida = self.seleciona_solucao_abelha_observadora(Pis)
				geracao[posicao_escolhida], aptdao_geracao[posicao_escolhida], lista_limites[posicao_escolhida] = self.atualiza_solucao(geracao[posicao_escolhida], aptdao_geracao[posicao_escolhida], lista_limites[posicao_escolhida])
				
			A, B = self.get_melhor_solucao(aptdao_geracao, geracao)
			if B < fit_melhor_solucao:
				melhor_solucao, fit_melhor_solucao = A, B


			print("------------------------------------------------------")
			# print("Melhor solução ---------> ", melhor_solucao)
			print("Fitness melhor solução -> ", fit_melhor_solucao)
			print("Solução otima ----------> ", sol_otima)
			print("------------------------------------------------------")
			# INICIA FASE DA ABELHAS EXPLORADORA
			coonntt = 0
			while 1:
				pos_pior_solucao = self.get_solucao_com_pior_limite(lista_limites)
				if lista_limites[pos_pior_solucao] >= self.limite_tentativas_por_solucao:
					geracao[pos_pior_solucao] = self.gera_caminho()
					aptdao_geracao[pos_pior_solucao] = self.calcula_aptdao_solucao(geracao[pos_pior_solucao])
					lista_limites[pos_pior_solucao] = 0
				else:
					break
				
				coonntt += 1
			cont += 1

		# os.system("clear")
		print("------------------------------------------------------")
		# print("Melhor solução ---------> ", melhor_solucao)
		print("Fitness melhor solução -> ", fit_melhor_solucao)
		print("------------------------------------------------------")

		return sol_otima

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



ciclos = 100000
total_abelhas = 100
abelhas_empregadas = int(total_abelhas / 2)
tam_populacao_inicial = int(total_abelhas / 2)
limite_tentativas_por_solucao = 20
quant_cidades = 280

obj = Bee(quant_cidades, tam_populacao_inicial, abelhas_empregadas, limite_tentativas_por_solucao)

aux_l = []
for i in range(280):
	A = input("")
	A = int(A)
	aux_l.append(A - 1)

obj.execute(ciclos, aux_l)

print("Sol. otima -> ", sol_otima)