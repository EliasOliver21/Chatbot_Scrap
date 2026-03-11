from playwright.sync_api import sync_playwright, expect
import json

def preparar_para_comparacao(texto: str) -> str:
    import unicodedata
    if not isinstance(texto, str):
        return ""
    return unicodedata.normalize('NFC', texto).casefold().strip()

def buscar_vagas_para_disciplina(page, nome_disciplina, nome_professor):
    try:
        termo_disciplina = preparar_para_comparacao(nome_disciplina)
        termo_professor = preparar_para_comparacao(nome_professor)

        # Localiza todas as linhas do corpo da tabela
        linhas = page.locator('#turmasAbertas tbody tr').all()

        for index, linha_disciplina_el in enumerate(linhas):
            texto_disciplina = preparar_para_comparacao(linha_disciplina_el.inner_text())

            if termo_disciplina in texto_disciplina:

                # print(f"Certo disciplina: \n {texto_disciplina}")

                for i in range(3):
                
                    if index + i < len(linhas):
                        linha_professor_el = linhas[index + i]
                        texto_professor = preparar_para_comparacao(linha_professor_el.inner_text())

                        if termo_professor in texto_professor:

                            # print(f"Certo Professor: \n {texto_professor}")
                            # Encontrou a combinação! Extrai os dados da linha da disciplina.
                            celulas = linha_professor_el.locator('td').all()
                            
                            if celulas:
                                vagas_ofertadas_texto = linha_professor_el.locator('td').nth(5).inner_text()
                                
                                vagas_ocupadas_texto = linha_professor_el.locator('td').nth(6).inner_text()
                                
                                #Contagem de vagas

                                vagas_ofertadas = int(vagas_ofertadas_texto.strip())

                                vagas_ocupadas = int(vagas_ocupadas_texto.strip())

                                vagas_disponiveis = vagas_ofertadas - vagas_ocupadas
                                
                                # Mostra todas as diciplinas e as vagas disponíveis que passaram pela combinação nome de componente e professor
                                # print(f"{nome_disciplina.upper()} ({nome_professor}): {vagas_disponiveis} vagas disponíveis ({vagas_ocupadas}/{vagas_ofertadas})")

                                if vagas_disponiveis > 0 and vagas_disponiveis < 3:
                                    # print(f"✅ {nome_disciplina.upper()} Professor(a):{termo_professor.upper()}: {vagas_disponiveis} vagas disponíveis ({vagas_ocupadas}/{vagas_ofertadas})")
                                    return f"✅ {nome_disciplina.upper()} Professor(a):{termo_professor.upper()}: {vagas_disponiveis} vagas disponíveis ({vagas_ocupadas}/{vagas_ofertadas})"
                                else:
                                    None
                                    # return f"❌​{nome_disciplina.upper()} Professor(a):{termo_professor.upper()}: {vagas_disponiveis} vagas disponíveis ({vagas_ocupadas}/{vagas_ofertadas})"
                                #     continue

                        # Se não retornou, continua procurando (pode haver outra turma com mesmo nome)
        
        # Se o loop terminar e não encontrar, retorna None
        return None

    except Exception as e:
        return f"Erro ao buscar disciplina '{nome_disciplina}': {e}"
    
def converter_turmas(nome_arquivo):

    try:
        with open(nome_arquivo, 'r', encoding='utf-8') as t:

            dados = json.load(t)
            return dados
        
    except FileNotFoundError:
        return f"Erro: O arquivo '{nome_arquivo}' não foi encontrado."
            

def verificar_vagas_unb():
    """
    Função principal que abre o navegador (headless), aplica os filtros e chama a busca.
    """
    with sync_playwright() as p:
        # Lança o navegador em modo headless. É aqui que a mágica acontece.
        browser = p.chromium.launch(headless=True)
        page = browser.new_page()

        try:
            page.goto("https://sigaa.unb.br/sigaa/public/turmas/listar.jsf", timeout=60000)

            # Turmas no arquivo json
            disciplinas_a_verificar = converter_turmas('vagas.json')
            resultados_finais = []
            departamento_atual = None

            for busca in disciplinas_a_verificar:
                if busca["departamento"] != departamento_atual:
                    departamento_atual = busca["departamento"]
                    
                    page.locator('select[name="formTurma:inputNivel"]').select_option(label="GRADUAÇÃO")
                    # espera o elemento estar pronto
                    page.locator('select[name="formTurma:inputDepto"]').select_option(label=departamento_atual)
                    page.locator('input[name="formTurma:j_id_jsp_1370969402_11"]').click()
                    
                    # Espera a tabela de resultados aparecer após o clique
                    tabela = page.locator('#turmasAbertas')
                    
                    expect(tabela).to_be_visible(timeout=20000)

                # busca a disciplina
                resultado = buscar_vagas_para_disciplina(page, busca["disciplina"], busca["professor"])
                if resultado:
                    resultados_finais.append(resultado)

            if resultados_finais:
                return "\n".join(resultados_finais)
            else:
                return None

        except Exception as e:
            page.screenshot(path='erro_playwright.png')
            return f"Erro ao executar o scraping: {e}"
        finally:
            browser.close()