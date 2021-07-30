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
G = grafo('pdh.txt')
fluxo_aresta = [258,115,364,0,197,0,0,266,99,0,0,278,138,237,252,237,268,215,124,0,105,0,95,0,0,0,115,212,263,160,384,0,247,100]
visual(G,fluxo_aresta)
