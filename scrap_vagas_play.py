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
                
                if index + 1 < len(linhas):
                    linha_professor_el = linhas[index + 1]
                    texto_professor = preparar_para_comparacao(linha_professor_el.inner_text())

                    if termo_professor in texto_professor:

                        # print(f"Certo Professor: \n {texto_professor}")
                        # Encontrou a combinação! Extrai os dados da linha da disciplina.
                        celulas = linha_professor_el.locator('td').all()
                        
                        if celulas:
                            vagas_ofertadas_texto = linha_professor_el.locator('td').nth(5).inner_text()
                            
                            vagas_ocupadas = linha_professor_el.locator('td').nth(6).inner_text()
                            
                            #Contagem de vagas

                            vagas_disponiveis = int(vagas_ofertadas_texto.strip()) - int(vagas_ocupadas.strip())

                            if vagas_disponiveis:
                                return f"✅ {nome_disciplina.upper()}: {vagas_disponiveis} vagas disponíveis ({vagas_ocupadas}/{vagas_disponiveis})"
                            else:
                                continue

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
            # print("Navegador iniciado. Acessando o site...")
            page.goto("https://sigaa.unb.br/sigaa/public/turmas/listar.jsf", timeout=60000)

            # --- DADOS DA BUSCA ---
            # Idealmente, isso viria de um arquivo de config ou do seu bot

            disciplinas_a_verificar = converter_turmas('vagas.json')
            resultados_finais = []
            departamento_atual = None

            for busca in disciplinas_a_verificar:
                if busca["departamento"] != departamento_atual:
                    departamento_atual = busca["departamento"]
                    # print(f"Filtrando por departamento: {departamento_atual}...")
                    
                    page.locator('select[name="formTurma:inputNivel"]').select_option(label="GRADUAÇÃO")
                    # O Playwright espera automaticamente o elemento estar pronto
                    page.locator('select[name="formTurma:inputDepto"]').select_option(label=departamento_atual)
                    page.locator('input[name="formTurma:j_id_jsp_1370969402_11"]').click()
                    
                    # Espera a tabela de resultados aparecer após o clique
                    tabela = page.locator('#turmasAbertas')
                    
                    expect(tabela).to_be_visible(timeout=20000)
                    # print("Filtro aplicado. Tabela carregada.")

                # Com a página filtrada, busca a disciplina
                resultado = buscar_vagas_para_disciplina(page, busca["disciplina"], busca["professor"])

                # print(resultado)
                if resultado:
                    resultados_finais.append(resultado)

            if resultados_finais:
                return "\n".join(resultados_finais)
            else:
                return None

        except Exception as e:
            # print(f"Ocorreu um erro geral no scraping: {e}")
            # Tira um screenshot para ajudar a depurar o erro
            page.screenshot(path='erro_playwright.png')
            return f"Erro ao executar o scraping: {e}"
        finally:
            # print("Fechando navegador.")
            browser.close()

# --- Para testar o script diretamente ---
if __name__ == "__main__":
    resultado_geral = verificar_vagas_unb()
    if resultado_geral:
        print("\n--- VAGAS ENCONTRADAS ---")
        print(resultado_geral)
    else:
        print("\nNenhuma vaga encontrada para as disciplinas monitoradas.")