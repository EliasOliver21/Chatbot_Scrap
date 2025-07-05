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
    options.add_argument('--disable-images')
    options.add_argument("user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/99.0.4844.84 Safari/537.36")
    # options.add_argument("--headless")  # Ativa o modo sem interface gráfica
    options.add_argument("--disable-gpu")  # Desativa a aceleração de hardware (necessário em alguns sistemas)
    options.add_argument("--window-size=1920x1080")  # Define o tamanho da janela virtual
    options.add_argument("--no-sandbox")  # Evita erros de permissão em alguns sistemas
    options.add_argument("--disable-dev-shm-usage") 

    driver = webdriver.Chrome(options=options)

    link = "https://sigaa.unb.br/sigaa/public/turmas/listar.jsf"

    # Acessa o Site
    driver.get(link)

    wait = WebDriverWait(driver, 10)

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
    vaga_tppe_lanna = driver.find_element(By.XPATH, '//*[@id="turmasAbertas"]/table/tbody/tr[294]/td[7]')
    # #Verífica a qtde de vagas disponíveis
    vaga_tppe_lanna = 80 - int(vaga_tppe_lanna.text.strip())
    
    #Coleta o elemento desejado na página
    vaga_fse_renato = driver.find_element(By.XPATH, '//*[@id="turmasAbertas"]/table/tbody/tr[160]/td[7]')

    # Pega o valor de vagas ocupadas
    vaga_fse_renato = 80 - int(vaga_fse_renato.text.strip())

     #Coleta o elemento desejado na página
    vaga_bancos_Mauricio = driver.find_element(By.XPATH, '//*[@id="turmasAbertas"]/table/tbody/tr[182]/td[7]')

    vaga_bancos_Mauricio = 80 - int(vaga_bancos_Mauricio.text.strip())

    driver.quit()

     # Retorna uma resposta de acordo com a disponibilidade de vagas nas duas turmas ou somente em comp1
    if (vaga_tppe_lanna > 0 and vaga_comp1_sergio > 0):
        return 'Compiladores 1 e TPPE Disponíveis'
    elif( vaga_comp1_sergio > 0):
        return 'Compiladores 1 Disponível'
    elif( vaga_fse_renato >0):
        return'FSE Disponível'
    elif((vaga_tppe_lanna > 0 and vaga_comp1_sergio > 0) or ( vaga_comp1_sergio > 0)) or ( vaga_fse_renato >0):
        return 'Algumas vagas disponívesis, verifique!!!'
    else:
        return ''
    
def verify_vacancy_2():

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

    time.sleep(3)

    #Localiza elemento da qtde de vagas ocupadas
    vaga_comp1_sergio = driver.find_element(By.XPATH, '//*[@id="turmasAbertas"]/table/tbody/tr[6]/td[7]')

    # Pega o valor de vagas ocupadas
    vaga_comp1_sergio = 100 - int(vaga_comp1_sergio.text.strip())

    # ##Localiza elemento da qtde de vagas ocupadas
    vaga_tppe_lanna = driver.find_element(By.XPATH, '//*[@id="turmasAbertas"]/table/tbody/tr[294]/td[7]')
    # #Verífica a qtde de vagas disponíveis
    vaga_tppe_lanna = 80 - int(vaga_tppe_lanna.text.strip())

    vaga_fse_renato = driver.find_element(By.XPATH, '//*[@id="turmasAbertas"]/table/tbody/tr[160]/td[7]')

    # Pega o valor de vagas ocupadas
    vaga_fse_renato = 80 - int(vaga_fse_renato.text.strip())

     #Coleta o elemento desejado na página
    vaga_bancos_Mauricio = driver.find_element(By.XPATH, '//*[@id="turmasAbertas"]/table/tbody/tr[182]/td[7]')

    vaga_bancos_Mauricio = 80 - int(vaga_bancos_Mauricio.text.strip())

    #Fecha o navegador
    driver.quit()

    resultado = "" \
    f" FGA0003 - COMPILADORES 1 -- Sérgio -- Vagas: {vaga_comp1_sergio}\n\n" \
    f" FGA0242 - TÉCNICAS DE PROGRAMAÇÃO EM PLATAFORMAS EMERGENTES -- Lanna -- Vagas: {vaga_tppe_lanna}\n\n " \
    f" FGA0109 - FUNDAMENTOS DE SISTEMAS EMBARCADOS -- Renato Coral -- Vagas: {vaga_fse_renato}\n\n"\
    f"FGA0137 - SISTEMAS DE BANCO DE DADOS 1 -- Mauricio -- Vagas: {vaga_bancos_Mauricio}\n\n "

    

    return resultado