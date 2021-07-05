from grafo_pronto import grafo
import random
import queue
from copy import deepcopy
from math import sqrt
import time
import matplotlib.pyplot as plt
import numpy as np
import os
from queue import Queue
from visual import visual

def seleciona_nome_pasta_e_cria_pasta():
        '''Verifica os nome de pasta que já existem, e então escolhe o nome da pasta
         com base no nome da ultima pasta criada'''
        caminho = os.getcwd() + "/Plots/"
        print("caminho_final: ", caminho)
        lista_nome_pastas = os.listdir(caminho)
        nome_pasta_nova = '0'
        if len(lista_nome_pastas) != 0:
            lista_nome_pastas.sort()
            nome_pasta_nova = str(int(lista_nome_pastas[-1]) + 1)

        # Monta caminho com o nome da pasta nova
        caminho_nova_pasta = caminho + "/" + nome_pasta_nova
        # Cria a pasta
        os.mkdir(caminho_nova_pasta)

        # Acessa pasta criada
        os.chdir(caminho_nova_pasta)

def desenha_grafico_fluxo(grafo, lista_lista_fluxos):
	obj = visual()
	for fluxo in lista_lista_fluxos:
		obj.plota_grafico(grafo, fluxo)

	print("Fim do plot de todos os fluxos!")