from playwright.sync_api import sync_playwright, Route
import unicodedata
import time

NIVEL_BUSCA = "GRADUAÇÃO"
DEPARTAMENTO_BUSCA = "CAMPUS UNB GAMA: FACULDADE DE CIÊNCIAS E TECNOLOGIAS EM ENGENHARIA - BRASÍLIA"

# --- CONFIGURAÇÃO DE DADOS (Pode vir de um arquivo JSON futuramente) ---
DISCIPLINAS_A_VERIFICAR = [
    {
        "disciplina": "COMPILADORES 1",
        "professor": "SÉRGIO",
        "departamento": "CAMPUS UNB GAMA: FACULDADE DE CIÊNCIAS E TECNOLOGIAS EM ENGENHARIA - BRASÍLIA"
    },
    {
        "disciplina": "ESTRUTURAS DE DADOS 2",
        "professor": "MAURICIO",
        "departamento": "CAMPUS UNB GAMA: FACULDADE DE CIÊNCIAS E TECNOLOGIAS EM ENGENHARIA - BRASÍLIA"
    }
]

# --- FUNÇÕES AUXILIARES ---

def preparar_texto(texto: str) -> str:
    """Normaliza o texto para evitar problemas com acentos e maiúsculas."""
    if not isinstance(texto, str):
        return ""
    return unicodedata.normalize('NFC', texto).casefold().strip()

def abortar_recursos_pesados(route: Route):
    """
    Esta é a mágica da eficiência! Bloqueia o download de tudo que não for essencial.
    """
    recursos_bloqueados = ["image", "stylesheet", "font", "media"]
    if route.request.resource_type in recursos_bloqueados:
        route.abort()
    else:
        route.continue_()

def acessar_tabela_filtrada(page):
    """Preenche os filtros, clica em buscar e retorna o texto da tabela."""
    page.goto("https://sigaa.unb.br/sigaa/public/turmas/listar.jsf", wait_until="load")

    botao_cookie = page.get_by_role("button", name="Ciente")
    if botao_cookie.count() > 0:
        botao_cookie.click()

    page.locator('select[name="formTurma:inputNivel"]').wait_for(state="visible", timeout=15000)
    page.locator('select[name="formTurma:inputNivel"]').select_option(label=NIVEL_BUSCA)
    page.locator('select[name="formTurma:inputDepto"]').select_option(label=DEPARTAMENTO_BUSCA)

    with page.expect_navigation(wait_until="domcontentloaded", timeout=30000):
        page.locator('input[name="formTurma:j_id_jsp_1370969402_11"]').click()

    if "home.jsf" in page.url:

        acessar_tabela_filtrada(page) # Tenta novamente se redirecionado para a home

    tabela = page.locator('#turmasAbertas')
    tabela.wait_for(state="attached", timeout=15000)
    return tabela.inner_text()

def extrair_vagas_da_tabela(page, nome_disciplina, nome_professor):
    """Lógica de varredura da tabela, já otimizada com as correções anteriores."""
    termo_disciplina = preparar_texto(nome_disciplina)
    termo_professor = preparar_texto(nome_professor)

    # Pega todas as linhas
    linhas = page.locator('#turmasAbertas tbody tr').all()

    print(f"Verificando {len(linhas)} linhas para {nome_disciplina} - {nome_professor}...")

    for index, linha_disciplina_el in enumerate(linhas):
        texto_disciplina = preparar_texto(linha_disciplina_el.inner_text())

        if termo_disciplina in texto_disciplina:
            if index + 1 < len(linhas):
                linha_professor_el = linhas[index + 1]
                texto_professor = preparar_texto(linha_professor_el.inner_text())

                if termo_professor in texto_professor:
                    # Verifica a quantidade de colunas por segurança
                    if linha_disciplina_el.locator('td').count() > 7:
                        vagas_ocupadas = int(linha_disciplina_el.locator('td').nth(6).inner_text().strip())
                        total_vagas = int(linha_disciplina_el.locator('td').nth(7).inner_text().strip())
                        vagas_disponiveis = total_vagas - vagas_ocupadas

                        if vagas_disponiveis > 0:
                            return f"✅ {nome_disciplina.upper()} ({nome_professor}): {vagas_disponiveis} vagas disponíveis ({vagas_ocupadas}/{total_vagas})"
    return None

# --- FUNÇÃO PRINCIPAL DE SCRAPING ---

def verificar_vagas_unb():
    """
    Abre a página, aplica os filtros fixos e tenta retornar as informações da tabela.
    """
    print("Iniciando Playwright otimizado...")
    inicio = time.time()

    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)  # Modo visível para depuração
        context = browser.new_context()
        page = context.new_page()

        # page.route("**/*", abortar_recursos_pesados)

        try:
            print(f"Aplicando filtro de nível: {NIVEL_BUSCA}")
            print(f"Aplicando filtro de departamento: {DEPARTAMENTO_BUSCA}")

            texto_tabela = acessar_tabela_filtrada(page)
            print("Tabela carregada com sucesso.")
            return texto_tabela

        except Exception as e:
            print(f"Erro no scraping: {e}")
        finally:
            browser.close()
            fim = time.time()
            print(f"Tempo total de execução: {fim - inicio:.2f} segundos")

    return None

# --- TESTE LOCAL ---
if __name__ == "__main__":
    print("Iniciando teste local de scraping...")
    resultado_final = verificar_vagas_unb()
    
    if resultado_final:
        print("\n=== INFORMAÇÕES DA TABELA ===")
        print(resultado_final)
    else:
        print("\n=== RESULTADO NEGATIVO ===")
        print("Não foi possível acessar a tabela das turmas.")