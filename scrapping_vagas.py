from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome import options
from bs4 import BeautifulSoup
from selenium.webdriver.support.ui import Select
import time

from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By

# Abre o navegador
driver = webdriver.Chrome()

link = "https://sigaa.unb.br/sigaa/public/turmas/listar.jsf"

# Acessa o Site
driver.get(link)

# Localiza o elemento <select> pelo nome e cria uma instância da classe Select
nivel_select = Select(driver.find_element(By.NAME, 'formTurma:inputNivel'))

# Seleciona a opção pelo valor visível
nivel_select.select_by_visible_text("GRADUAÇÃO")  # "G" para Graduação

#Seleciona o Campus
nivel_select = Select(driver.find_element(By.NAME, 'formTurma:inputDepto'))

#Seleciona o Campus
nivel_select.select_by_visible_text("CAMPUS UNB GAMA: FACULDADE DE CIÊNCIAS E TECNOLOGIAS EM ENGENHARIA - BRASÍLIA")  # "G" para Graduação

#Clica no botão de busca
nivel_select = driver.find_element(By.NAME, 'formTurma:j_id_jsp_1370969402_11')

nivel_select.click()

time.sleep(15)

# Agora vamos pegar o código fonte da página e usar o BeautifulSoup para buscar a tabela
soup = BeautifulSoup(driver.page_source, "html.parser")

# Tenta encontrar o corpo da tabela onde estão os dados das turmas
# turmas = []


# turmas = soup.find_all('span', class_='tituloDisciplina')

# for turma in turmas:
#     print(turma)
# # Verifica se o corpo da tabela foi encontrado

agrupadores = soup.find_all('tr', class_='agrupador')  # Linhas com a turma
linhas_par = soup.find_all('tr', class_='linhaPar')   # Linhas com os dados das turmas (pares)
linhas_impar = soup.find_all('tr', class_='linhaImpar')  # Linhas com os dados das turmas (ímpares)

# Vamos agrupar as turmas e verificar as vagas
for agrupador in agrupadores:
    # Encontrar o nome da turma dentro de 'agrupador'
    nome_turma_element = agrupador.find('a', title=True)
    if nome_turma_element:
        nome_turma = nome_turma_element.text.strip()

        # Filtra apenas as turmas que você deseja (como exemplo)
        if nome_turma in ['FGA0242 - TÉCNICAS DE PROGRAMAÇÃO EM PLATAFORMAS EMERGENTES', 'FGA0124 - PROJETO DE ALGORITMOS']:
            print(f"Encontrada a turma: {nome_turma}")

            # Verifica se a turma tem dados nas linhas 'linhaPar' ou 'linhaImpar'
            turma_encontrada = False
            for linha in linhas_par + linhas_impar:
                if nome_turma in linha.text:
                    turma_encontrada = True
                    colunas = linha.find_all('td')

                    if len(colunas) >= 8:  # Verifica se a linha possui a quantidade esperada de colunas
                        vagas_ofertadas = int(colunas[5].text.strip())  # Vagas ofertadas (coluna 6)
                        vagas_ocupadas = int(colunas[6].text.strip())  # Vagas ocupadas (coluna 7)

                        print(f"Vagas ofertadas: {vagas_ofertadas}")
                        print(f"Vagas ocupadas: {vagas_ocupadas}")

                        # Verifica se a turma tem vagas disponíveis
                        vagas_disponiveis = vagas_ofertadas - vagas_ocupadas
                        if vagas_disponiveis > 0:
                            print(f"A turma {nome_turma} tem {vagas_disponiveis} vagas disponíveis!")
                        else:
                            print(f"A turma {nome_turma} não possui vagas disponíveis.")
                    else:
                        print(f"Não foi possível obter informações de vagas para a turma: {nome_turma}")

            if not turma_encontrada:
                print(f"Não encontrou dados da turma {nome_turma} nas linhas.")
            print("-" * 50)

# Fecha o navegador
driver.quit()