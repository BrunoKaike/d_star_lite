import os
import sys
import math
from memory_profiler import profile
import time

import grade

class DStarLite:
    def __init__(self, origem, destino, tipo_heuristica, num_linhas, num_colunas):
        self.origem, self.destino = origem, destino
        self.tipo_heuristica = tipo_heuristica

        self.ambiente = grade.Grade(num_linhas, num_colunas, origem[0], origem[1], destino[0], destino[1])
        self.ambiente.imprimir_grade()
        self.movimentos_possiveis = self.ambiente.movimentos  # Conjunto de movimentos possíveis
        self.obstaculos = self.ambiente.obstaculos  # Posição dos obstáculos
        self.num_linhas = self.ambiente.num_linhas
        self.num_colunas = self.ambiente.num_colunas

        self.g, self.rhs, self.U = {}, {}, {}
        self.km = 0

        for i in range(1, self.ambiente.num_linhas - 1):
            for j in range(1, self.ambiente.num_colunas - 1):
                self.rhs[(i, j)] = float("inf")
                self.g[(i, j)] = float("inf")

        self.rhs[self.destino] = 0.0
        self.U[self.destino] = self.calcular_chave(self.destino)
        self.visitados = set()
        self.contador = 0

    def executar(self):
        start_time = time.time()
        self.calcular_caminho()
        caminho = self.extrair_caminho()
        end_time = time.time()
        elapsed_time = end_time - start_time
        print(f"Tempo de execução: {elapsed_time} segundos")

        print("Caminho encontrado:")
        for ponto in caminho:
            print(ponto)
        self.aguardar_entrada()

    def aguardar_entrada(self):
        x, y = map(int, input("Digite os valores de x e y separados por um espaço do novo OBSTACULO: ").split())
        if x < 0 or x > self.num_linhas - 1 or y < 0 or y > self.num_colunas - 1:
            print("Escolha uma área válida!")
        else:
            x, y = int(x), int(y)
            print("Transformando posição(", x, ",", y,") em OBSTÁCULO")

            s_atual = self.origem
            s_ultimo = self.origem
            i = 0
            caminho = [self.origem]
            start_time = time.time()
            while s_atual != self.destino:
                s_lista = {}

                for s in self.obter_vizinhos(s_atual):
                    s_lista[s] = self.g[s] + self.calcular_custo(s_atual, s)
                s_atual = min(s_lista, key=s_lista.get)
                caminho.append(s_atual)

                if i < 1:
                    self.km += self.calcular_heuristica(s_ultimo, s_atual)
                    s_ultimo = s_atual
                    if (x, y) not in self.obstaculos:
                        self.obstaculos.add((x, y))
                        self.g[(x, y)] = float("inf")
                        self.rhs[(x, y)] = float("inf")
                    else:
                        self.obstaculos.remove((x, y))
                        self.atualizar_vertice((x, y))
                    for s in self.obter_vizinhos((x, y)):
                        self.atualizar_vertice(s)
                    i += 1

                    self.contador += 1
                    self.visitados = set()
                    self.calcular_caminho()
                    
            end_time = time.time()
            elapsed_time = end_time - start_time
            print(f"Tempo de execução: {elapsed_time} segundos")
            print("Novo caminho após alteração no grafo:", caminho)
            self.aguardar_entrada()

    #@profile
    def calcular_caminho(self):
        start_time = time.time()
        try:
            while True:
                s, v = self.obter_chave_menor()
                if v >= self.calcular_chave(self.origem) and \
                        self.rhs[self.origem] == self.g[self.origem]:
                    break

                k_antigo = v
                self.U.pop(s)
                self.visitados.add(s)

                if k_antigo < self.calcular_chave(s):
                    self.U[s] = self.calcular_chave(s)
                elif self.g[s] > self.rhs[s]:
                    self.g[s] = self.rhs[s]
                    for x in self.obter_vizinhos(s):
                        self.atualizar_vertice(x)
                else:
                    self.g[s] = float("inf")
                    self.atualizar_vertice(s)
                    for x in self.obter_vizinhos(s):
                        self.atualizar_vertice(x)
        except ValueError:
            end_time = time.time()
            elapsed_time = end_time - start_time
            print(f"Tempo de execução: {elapsed_time} segundos")
            print("Não existe caminho para o destino.")
            sys.exit()

    def atualizar_vertice(self, s):
        if s != self.destino:
            self.rhs[s] = float("inf")
            for x in self.obter_vizinhos(s):
                self.rhs[s] = min(self.rhs[s], self.g[x] + self.calcular_custo(s, x))
        if s in self.U:
            self.U.pop(s)

        if self.g[s] != self.rhs[s]:
            self.U[s] = self.calcular_chave(s)

    def calcular_chave(self, s):
        return [min(self.g[s], self.rhs[s]) + self.calcular_heuristica(self.origem, s) + self.km,
                min(self.g[s], self.rhs[s])]

    def obter_chave_menor(self):
        s = min(self.U, key=self.U.get)
        return s, self.U[s]

    def calcular_heuristica(self, s_origem, s_destino):
        tipo_heuristica = self.tipo_heuristica

        if tipo_heuristica == "manhattan":
            return abs(s_destino[0] - s_origem[0]) + abs(s_destino[1] - s_origem[1])
        else:
            return math.hypot(s_destino[0] - s_origem[0], s_destino[1] - s_origem[1])

    def calcular_custo(self, s_origem, s_destino):
        if self.ha_colisao(s_origem, s_destino):
            return float("inf")

        return math.hypot(s_destino[0] - s_origem[0], s_destino[1] - s_origem[1])

    def ha_colisao(self, s_origem, s_destino):
        if s_origem in self.obstaculos or s_destino in self.obstaculos:
            return True

        if s_origem[0] != s_destino[0] and s_origem[1] != s_destino[1]:
            if s_destino[0] - s_origem[0] == s_origem[1] - s_destino[1]:
                s1 = (min(s_origem[0], s_destino[0]), min(s_origem[1], s_destino[1]))
                s2 = (max(s_origem[0], s_destino[0]), max(s_origem[1], s_destino[1]))
            else:
                s1 = (min(s_origem[0], s_destino[0]), max(s_origem[1], s_destino[1]))
                s2 = (max(s_origem[0], s_destino[0]), min(s_origem[1], s_destino[1]))

            if s1 in self.obstaculos or s2 in self.obstaculos:
                return True

        return False

    def obter_vizinhos(self, s):
        vizinhos = set()
        for u in self.movimentos_possiveis:
            s_proximo = tuple([s[i] + u[i] for i in range(2)])
            if s_proximo not in self.obstaculos:
                vizinhos.add(s_proximo)

        return vizinhos

    #@profile
    def extrair_caminho(self):
        caminho = [self.origem]
        s = self.origem

        for k in range(1000):
            g_lista = {}
            for x in self.obter_vizinhos(s):
                if not self.ha_colisao(s, x):
                    g_lista[x] = self.g[x]
            s = min(g_lista, key=g_lista.get)
            caminho.append(s)
            if s == self.destino:
                break

        return list(caminho)


def main():
    origem = (1, 1)
    destino = (8, 8)
    num_linhas = int(input("Informe o número de linhas: "))
    num_colunas = int(input("Informe o número de colunas: "))
    origem = tuple(map(int, input("Digite os valores de x e y para a origem separados por um espaço: ").split()))
    destino = tuple(map(int, input("Digite os valores de x e y para o destino separados por um espaço: ").split()))

    dstar_lite = DStarLite(origem, destino, "euclidean", num_linhas, num_colunas)
    dstar_lite.executar()


if __name__ == '__main__':
    main()
