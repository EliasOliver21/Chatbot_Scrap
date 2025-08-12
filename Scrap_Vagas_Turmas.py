import time
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import Select
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import NoSuchElementException, TimeoutException

def buscar_vagas_para_disciplina(driver, nome_disciplina, nome_professor):
    """
    Busca por uma disciplina e professor, considerando que o nome do professor
    está na linha seguinte à da disciplina.
    """
    try:
        termo_disciplina = nome_disciplina.lower().strip()
        termo_professor = nome_professor.lower().strip()

        # Espera e pega todas as linhas da tabela
        tabela_body = WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.XPATH, '//*[@id="turmasAbertas"]/table/tbody'))
        )
        linhas = tabela_body.find_elements(By.TAG_NAME, 'tr')

        # Usamos enumerate para ter acesso ao índice (a posição) de cada linha
        for index, linha_disciplina in enumerate(linhas):
            texto_disciplina = linha_disciplina.text.lower().strip()

            # 1. Verifica se a linha atual contém o nome da disciplina
            if termo_disciplina in texto_disciplina:

                print(f"Sucesso disciplina: {termo_disciplina}")
                
                # 2. Verifica se existe uma próxima linha para não dar erro no final da tabela
                if index + 1 < len(linhas):
                    # Pega a próxima linha da lista, que deve conter o professor

                    #Verifica até 3 linhas depois de encontrar a disciplina na tabela.
                    for i in range(3):

                        linha_professor = linhas[index + i]
                        texto_professor = linha_professor.text.lower().strip()

                        # 3. Verifica se a próxima linha contém o nome do professor
                        if termo_professor in texto_professor:
                            print(f"Sucesso Professor: {termo_professor}")
                            # SUCESSO! Encontramos a disciplina e o professor correspondente.
                            # Agora, extraímos os dados da LINHA DA DISCIPLINA.
                            
                            celulas = linha_professor.find_elements(By.TAG_NAME, 'td')
                            
                            # Verifica se a linha da disciplina tem colunas suficientes
                            if len(celulas) > 7:
                                vagas_ocupadas = int(celulas[6].text.strip())
                                total_vagas = int(celulas[5].text.strip())
                                vagas_disponiveis = total_vagas - vagas_ocupadas

                                return f"✅ {nome_disciplina.upper()} ({nome_professor}): {vagas_disponiveis} vagas disponíveis ({vagas_ocupadas}/{total_vagas})"
                            else:
                                # Se a linha da disciplina não tem as colunas de vaga, pula para a próxima
                                continue

        # Se o loop terminar sem encontrar a combinação, retorna a mensagem
        return f"❌ {nome_disciplina.upper()} ({nome_professor}): Combinação disciplina/professor não encontrada."

    except TimeoutException:
        return "ℹ️ Nenhuma turma encontrada para o departamento atual."
    except Exception as e:
        return f"🚨 Erro inesperado ao buscar por {nome_disciplina}: {e}"

    except (NoSuchElementException, IndexError) as e:
        return f"⚠️ Erro ao processar a estrutura da tabela para {nome_disciplina}: {e}"
    except Exception as e:
        return f"🚨 Erro inesperado ao buscar por {nome_disciplina}: {e}"


def verificar_vagas_unb():
    """
    Função principal que configura o Selenium, navega no site e busca as vagas
    para uma lista de disciplinas.
    """
    options = Options()
    options.add_argument('--disable-images')
    options.add_argument("user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/99.0.4844.84 Safari/537.36")
    # options.add_argument("--headless")
    options.add_argument("--start-minimized")
    options.add_argument("--disable-gpu")
    options.add_argument("--window-size=1920x1080")
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")
    driver = webdriver.Chrome(options=options)

    try:
        link = "https://sigaa.unb.br/sigaa/public/turmas/listar.jsf"
        driver.get(link)

        # --- Etapa 1: Preenchimento do Formulário ---
        
        # Seleciona Nível "GRADUAÇÃO"
        select_nivel = Select(driver.find_element(By.NAME, 'formTurma:inputNivel'))
        select_nivel.select_by_visible_text("GRADUAÇÃO")

        # Aguarda um instante para o JS da página atualizar, se necessário
        time.sleep(1) 

        # Seleciona Departamento/Campus
        select_depto = Select(driver.find_element(By.NAME, 'formTurma:inputDepto'))
        select_depto.select_by_visible_text("CAMPUS UNB GAMA: FACULDADE DE CIÊNCIAS E TECNOLOGIAS EM ENGENHARIA - BRASÍLIA")
        
        # Clica no botão de busca
        botao_buscar = driver.find_element(By.NAME, 'formTurma:j_id_jsp_1370969402_11')
        botao_buscar.click()

        # --- Etapa 2: Aguardar e buscar os dados ---

        # Espera pelo recebimento dos dados da tabela
        print("Aguardando carregamento da tabela de turmas...")
        WebDriverWait(driver, 20).until(
            EC.visibility_of_element_located((By.ID, 'turmasAbertas'))
        )
        print("Tabela carregada. Buscando disciplinas...")

        # --- LISTA DE DISCIPLINAS PARA VERIFICAR ---
        # Adicione quantas disciplinas quiser nesta lista de tuplas (disciplina, professor)
        disciplinas_a_verificar = [
            ("COMPILADORES 1", "FABIO MACEDO MENDES"),
            ("ESTRUTURAS DE DADOS 2", "MAURICIO"),
        ]

        # --- Etapa 3: Iterar e imprimir resultados ---
        resultados = []
        for disciplina, professor in disciplinas_a_verificar:
            resultado = buscar_vagas_para_disciplina(driver, disciplina, professor)
            print(resultado)
            resultados.append(resultado)
        
        return "\n".join(resultados)

    finally:
        driver.quit()

# Teste do Script
# if __name__ == "__main__":
#     resultados_finais = verificar_vagas_unb()
#     print("\n--- RESUMO FINAL ---")
#     print(resultados_finais)