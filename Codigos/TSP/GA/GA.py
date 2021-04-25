import os
import random
from time import sleep
from copy import deepcopy
import matplotlib.pyplot as plt
from pylab import plot, show
import time



grafo = []

class cidades:
	def __init__(self):
		self.grafo = [(1,1),(2,2),(4,2),(5,2),(5,3),(3,4),(4,5),(5,5),(6,3),(5,6)]
	@staticmethod
	def imprime_cordenada_cidade(cidade):
		print("Codenadas da cidade ",cidade," : ",self.grafo[cidade])

	@staticmethod
	def calcula_distancia_entre_cidades(cidade_1, cidade_2):
		return ((cidade_2[0] - cidade_1[0]) ** 2 + (cidade_2[1] - cidade_1[1]) ** 2) ** (1/2)

	@staticmethod
	def get_cordenadas(pos):
		# grafo = [(1,1),(2,2),(4,2),(5,2),(5,3),(3,4),(4,5),(5,5),(6,3),(5,6)]
		# grafo = [(1,3),
		# 		(4,2),
		# 		(-1,-1),
		# 		(0,0),
		# 		(1,2),
		# 		(2,3),
		# 		(2,2),
		# 		(10,10),
		# 		(1,4),
		# 		(5,1),
		# 		(2,5),
		# 		(6,10),
		# 		(14,23),
		# 		(67,12)]
		
		return grafo[pos]


class GA:
	def __init__(self, quantidade_cidades):
		self.populacao = []
		self.quantidade_cidades = quantidade_cidades
		self.resultados_individuos = []

	def imprime_populacao(self):
		cont = 0
		print("--------------- POPULAÇÃO -------------------")
		for individuo in self.populacao:
			print(cont, " -> ", individuo)
			cont += 1
		print("---------------------------------------------")

	def gera_caminho(self):
		return random.sample(range(self.quantidade_cidades), self.quantidade_cidades)
		
	def inicia_populacao(self):
		for i in range(self.quantidade_cidades):
			self.populacao.append(self.gera_caminho())
			print("cont: ", i)
		# self.imprime_populacao()

	def fitness_individuo(self, individuo):
		gasto_total_deste_caminho = 0
		for i in range(len(individuo) - 1):
			gasto_total_deste_caminho += cidades.calcula_distancia_entre_cidades(cidades.get_cordenadas(individuo[i]) , cidades.get_cordenadas(individuo[i + 1]))

		gasto_total_deste_caminho += cidades.calcula_distancia_entre_cidades(cidades.get_cordenadas(individuo[-1]), cidades.get_cordenadas(individuo[0]))
		return gasto_total_deste_caminho

	def fitness_geracao(self):
		fitness_geracao_atual = []
		for i in range(len(self.populacao)):
			print("cont: ", i)
			individuo = self.populacao[i]
			fitness_geracao_atual.append((self.fitness_individuo(individuo), i))

		
		return fitness_geracao_atual

	def gera_descendente(self, pai_1, pai_2):
		filho = []
		tam = len(pai_1)
		ini_intervalo = random.randint(0, tam - 1)
		fim_intervalo = random.randint(ini_intervalo, tam - 1)

		# print("ini -> ", ini_intervalo, " fim -> ", fim_intervalo)
		if ini_intervalo == fim_intervalo:
			filho.append(pai_1[ini_intervalo])
		else:
			for i in range(ini_intervalo, fim_intervalo):
				# print(pai_1[i])
				filho.append(pai_1[i])

		for gene in pai_2:
			if not gene in filho:
				filho.append(gene)

		return filho


	def get_dois_numeros_randomicos(self):
		pos_1 = 0
		pos_2 = 0
		while pos_1 == pos_2:
			pos_1 = random.randint(0, len(self.populacao) - 1)
			pos_2 = random.randint(pos_1, len(self.populacao) - 1)

		return pos_1, pos_2


	def escolhe_pai(self):
		pai = 0

		aux_1, aux_2 = self.get_dois_numeros_randomicos()
		pai = aux_1 if self.resultados_individuos[aux_1][0] < self.resultados_individuos[aux_2][0] else aux_2
		print("-----------------------------------------------")
		print("PAI QUE FOi ESCOLHIDO: ", pai, " APITIDÃO: ", self.resultados_individuos[pai][0])

		return pai

	def gera_nova_populacao(self, fitness_populacao):
		filho_1 = self.gera_descendente(self.populacao[self.escolhe_pai()], self.populacao[self.escolhe_pai()])
		filho_2 = self.gera_descendente(self.populacao[self.escolhe_pai()], self.populacao[self.escolhe_pai()])
		print("-----------------------------------------------")

		self.populacao[fitness_populacao[-2][1]] = filho_1
		self.populacao[fitness_populacao[-1][1]] = filho_2

		self.resultados_individuos[fitness_populacao[-2][1]] = (self.fitness_individuo(filho_1), fitness_populacao[-2][1])
		self.resultados_individuos[fitness_populacao[-1][1]] = (self.fitness_individuo(filho_2), fitness_populacao[-1][1])


	def mutacao(self, individuo):
		pos_1 = 0
		pos_2 = 0
		while pos_1 == pos_2:
			pos_1 = random.randint(0, len(individuo) - 1)
			pos_2 = random.randint(pos_1, len(individuo) - 1)

		# print("------------- MUTAÇÃO ---------------")
		# print("POSIÇÕES TROCADAS ", pos_1, pos_2)
		# print("ANTES:  ", individuo)

		aux = individuo[pos_1]
		individuo[pos_1] = individuo[pos_2]
		individuo[pos_2] = aux

		# print("DEPOIS: ", individuo)
		# print("-------------------------------------")
		return individuo

	def mutacao_populacao(self):
		pos_1 = 0
		pos_2 = 0
		while pos_1 == pos_2:
			pos_1 = random.randint(0, len(self.populacao) - 1)
			pos_2 = random.randint(pos_1, len(self.populacao) - 1)

		print("INTERVALO DA MUTAÇÃO	 NA POPULAÇÃO:", pos_1, pos_2)
		for i in range(pos_1, pos_2):
			self.populacao[i] = self.mutacao(self.populacao[i])
			self.resultados_individuos[i] = (self.fitness_individuo(self.populacao[i]), self.resultados_individuos[i][1])

	def exec_GA(self):
		vetor_result_aux = []
		self.inicia_populacao()
		self.resultados_individuos = self.fitness_geracao()
		i = 0
		k = [i]
		inii = time.time()
		while i < 500000:

			lista_aux_resultados  = []
			lista_aux_resultados = deepcopy(self.resultados_individuos)
			# # print(lista_aux_resultados)
			lista_aux_resultados.sort()

			# print("---------- RESULTADO INDIVIDUOS -------------")
			# for resultado in self.resultados_individuos:
			# 	print(resultado)
			# print("---------------------------------------------")

			self.gera_nova_populacao(lista_aux_resultados)
			# print("NOVA POPULAÇÃO: ")
			# self.imprime_populacao()
			#self.mutacao_populacao()
			# print("POPULAÇÃO APÓS A MUTAÇÃO: ")
			# self.imprime_populacao()
			os.system("cls")
			# print("###################################################################################")
			print("Geração: ", i)
			print("RESULTADO DO MELHOR CAMINHO DESSA POPULAÇÃO -> ", lista_aux_resultados[0][0])
			vetor_result_aux.append(lista_aux_resultados[0][0])
			# print("###################################################################################")
			# sleep(5)
			i += 1
			k.append(i)
		print("time.time() inicial: ", inii)
		print("time.time() final: ", time.time())
		print("TEMPO GASTO: ", time.time() - inii)
		plt.figure(0)
		plt.plot(vetor_result_aux, color="red")

		plt.savefig('grafico1.png')





quantt = int(input(""))

for i in range(quantt):
	en =  input("")
	print("a:: ",en)
	indice, x, y = en.split(" ")
	x = int(x)
	y = int(y)

	grafo.append((x, y))

print("Tamanho da variavel grafo: ", len(grafo))

sleep(5)

numero_cidades = len(grafo)

obj = GA(numero_cidades)
obj.exec_GA()