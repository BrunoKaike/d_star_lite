import random

class Grade:
    def __init__(self, num_linhas, num_colunas, x_o, y_o, x_d, y_d):
        self.num_linhas = int(num_linhas)  # Tamanho do plano de fundo
        self.num_colunas = int(num_colunas)
        self.movimentos = [(-1, 0), (-1, 1), (0, 1), (1, 1),
                           (1, 0), (1, -1), (0, -1), (-1, -1)]
        self.obstaculos = self.mapa_obstaculos(x_o, y_o, x_d, y_d)

    def atualizar_obstaculos(self, obstaculos):
        self.obstaculos = obstaculos

    def mapa_obstaculos(self, x_o, y_o, x_d, y_d):

        percentual_obstaculos = float(input("Digite a porcentagem de obstáculos desejada: "))
        linhas = self.num_linhas
        colunas = self.num_colunas
        obstaculos = set()

        for i in range(linhas):
            obstaculos.add((i, 0))
            obstaculos.add((i, colunas - 1))

        for i in range(colunas):
            obstaculos.add((0, i))
            obstaculos.add((linhas - 1, i))

        total_celulas = linhas * colunas
        num_obstaculos = int((percentual_obstaculos / 100) * total_celulas)

        for _ in range(num_obstaculos):
            obstaculo = (random.randint(1, linhas - 2), random.randint(1, colunas - 2))
            while obstaculo == (x_o, y_o) or obstaculo == (x_d, y_d):
                obstaculo = (random.randint(1, linhas - 2), random.randint(1, colunas - 2))
            obstaculos.add(obstaculo)

        return obstaculos
    
    def imprimir_grade(self):
        for i in range(self.num_linhas):
            for j in range(self.num_colunas):
                if (i, j) in self.obstaculos:
                    print("#", end=" ")
                else:
                    print(".", end=" ")
            print()
