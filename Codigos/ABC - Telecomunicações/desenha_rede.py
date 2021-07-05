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

def desenha_grafico_fluxo(grafo, lista_lista_fluxos):
	obj = visual()
	for fluxo in lista_lista_fluxos:
		obj.plota_grafico(grafo, fluxo)

	print("Fim do plot de todos os fluxos!")