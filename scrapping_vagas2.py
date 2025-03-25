from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options
from bs4 import BeautifulSoup
from selenium.webdriver.support.ui import Select
import time
from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
import time
import sched
import threading

def verify_vacancy():

    # Abre o navegador
    
    options = Options()
    # options.add_argument('--headless')
    options.add_argument('--disable-images')

    driver = webdriver.Chrome(options=options)

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

    time.sleep(2)

    #Localiza elemento da qtde de vagas ocupadas
    vaga_comp1_sergio = driver.find_element(By.XPATH, '//*[@id="turmasAbertas"]/table/tbody/tr[6]/td[7]')

    # Pega o valor de vagas ocupadas
    vaga_comp1_sergio = 100 - int(vaga_comp1_sergio.text.strip())

    # ##Localiza elemento da qtde de vagas ocupadas
    vaga_tppe_lanna = driver.find_element(By.XPATH, '//*[@id="turmasAbertas"]/table/tbody/tr[292]/td[7]')
    # #Verífica a qtde de vagas disponíveis
    vaga_tppe_lanna = 80 - int(vaga_tppe_lanna.text.strip())

    driver.quit()

     # Retorna uma resposta de acordo com a disponibilidade de vagas nas duas turmas ou somente em comp1
    if (vaga_tppe_lanna > 0 and vaga_comp1_sergio > 0) or vaga_comp1_sergio > 0:
            
        return 'Vagas Disponíveis'
    else:
        return 'Vagas Indisponíveis'
    