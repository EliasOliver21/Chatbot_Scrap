from playwright.sync_api import sync_playwright, Route
import unicodedata
import time
import re
import atexit
from threading import Lock, get_ident
import json

NIVEL_BUSCA = "GRADUAÇÃO"
DEPARTAMENTO_BUSCA = "CAMPUS UNB GAMA: FACULDADE DE CIÊNCIAS E TECNOLOGIAS EM ENGENHARIA - BRASÍLIA"

# --- CONFIGURAÇÃO DE DADOS (Pode vir de um arquivo JSON futuramente) ---
with open("vagas.json", 'r', encoding='utf-8') as turmas:
    DISCIPLINAS_A_VERIFICAR = json.load(turmas)

_SESSOES_POR_THREAD = {}
_SESSOES_LOCK = Lock()
_SCRAPER_LOCK = Lock()

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

def _iniciar_sessao_playwright():
    thread_id = get_ident()
    with _SESSOES_LOCK:
        sessao = _SESSOES_POR_THREAD.get(thread_id)
        if sessao is not None:
            return sessao

        playwright = sync_playwright().start()
        browser = playwright.chromium.launch(headless=True)
        context = browser.new_context()
        page = context.new_page()
        page.route("**/*", abortar_recursos_pesados)

        sessao = {
            "playwright": playwright,
            "browser": browser,
            "context": context,
            "page": page,
        }
        _SESSOES_POR_THREAD[thread_id] = sessao
        return sessao

def _recriar_pagina():
    thread_id = get_ident()
    with _SESSOES_LOCK:
        sessao = _SESSOES_POR_THREAD.get(thread_id)

    if sessao is None:
        return _iniciar_sessao_playwright()

    with _SESSOES_LOCK:
        sessao = _SESSOES_POR_THREAD.get(thread_id)
        if sessao is None:
            return _iniciar_sessao_playwright()

        page = sessao.get("page")
        if page is not None:
            try:
                page.close()
            except Exception:
                pass

        context = sessao["context"]
        nova_pagina = context.new_page()
        nova_pagina.route("**/*", abortar_recursos_pesados)
        sessao["page"] = nova_pagina
        return sessao

def encerrar_sessao_da_thread_atual():
    thread_id = get_ident()
    with _SESSOES_LOCK:
        sessao = _SESSOES_POR_THREAD.pop(thread_id, None)

    if sessao is None:
        return

    page = sessao.get("page")
    context = sessao.get("context")
    browser = sessao.get("browser")
    playwright = sessao.get("playwright")

    if page is not None:
        try:
            page.close()
        except Exception:
            pass
    if context is not None:
        try:
            context.close()
        except Exception:
            pass
    if browser is not None:
        try:
            browser.close()
        except Exception:
            pass
    if playwright is not None:
        try:
            playwright.stop()
        except Exception:
            pass

def encerrar_sessao_playwright():
    with _SESSOES_LOCK:
        sessoes = list(_SESSOES_POR_THREAD.values())
        _SESSOES_POR_THREAD.clear()

    for sessao in sessoes:
        page = sessao.get("page")
        context = sessao.get("context")
        browser = sessao.get("browser")
        playwright = sessao.get("playwright")

        if page is not None:
            try:
                page.close()
            except Exception:
                pass
        if context is not None:
            try:
                context.close()
            except Exception:
                pass
        if browser is not None:
            try:
                browser.close()
            except Exception:
                pass
        if playwright is not None:
            try:
                playwright.stop()
            except Exception:
                pass

atexit.register(encerrar_sessao_playwright)

def acessar_tabela_filtrada(page):
    """Preenche os filtros, clica em buscar e retorna o texto da tabela."""
    for tentativa in range(1, 4):
        try:
            page.goto(
                "https://sigaa.unb.br/sigaa/public/turmas/listar.jsf",
                wait_until="domcontentloaded",
                timeout=45000
            )
        except Exception as e:
            print(f"Tentativa {tentativa}/3: erro no goto ({e}). Recriando página...")
            sessao = _recriar_pagina()
            page = sessao["page"]
            time.sleep(tentativa)
            continue

        botao_cookie = page.get_by_role("button", name="Ciente")
        if botao_cookie.count() > 0:
            botao_cookie.click()

        page.locator('select[name="formTurma:inputNivel"]').wait_for(state="visible", timeout=15000)
        page.locator('select[name="formTurma:inputNivel"]').select_option(label=NIVEL_BUSCA)
        page.locator('select[name="formTurma:inputDepto"]').select_option(label=DEPARTAMENTO_BUSCA)

        try:
            with page.expect_navigation(wait_until="domcontentloaded", timeout=30000):
                page.locator('input[name="formTurma:j_id_jsp_1370969402_11"]').click()
        except Exception as e:
            print(f"Tentativa {tentativa}/3: erro ao clicar em Buscar ({e}).")
            time.sleep(tentativa)
            continue

        if "home.jsf" in page.url:
            print(f"Tentativa {tentativa}/3: redirecionou para home, tentando novamente...")
            time.sleep(tentativa)
            continue

        tabela = page.locator('#turmasAbertas')
        try:
            tabela.wait_for(state="attached", timeout=15000)
            return tabela.inner_text()
        except Exception as e:
            print(f"Tentativa {tentativa}/3: tabela não anexada ({e}).")
            time.sleep(tentativa)

    raise RuntimeError("Não foi possível acessar a tabela de turmas após 3 tentativas.")

def extrair_numeros_da_linha(linha: str):
    numeros = [int(n) for n in re.findall(r'\d+', linha)]
    if len(numeros) < 2:
        return None, None, None

    vagas_totais = numeros[-2]
    vagas_ocupadas = numeros[-1]
    vagas_disponiveis = vagas_totais - vagas_ocupadas
    return vagas_totais, vagas_ocupadas, vagas_disponiveis

def _eh_inicio_disciplina(linha: str) -> bool:
    return bool(re.match(r'^\s*[A-Z]{3}\d{4}\s+-\s+', linha))

def _eh_linha_turma(linha: str) -> bool:
    return bool(re.match(r'^\s*\d{2}\s+20\d{2}\.\d\s+', linha))

def _extrair_professor_da_linha_turma(linha: str) -> str:
    match = re.match(r'^\s*\d{2}\s+20\d{2}\.\d\s+(.+?)\s+\(\d+h\)\s*$', linha)
    if match:
        return match.group(1).strip()
    partes = linha.split()
    if len(partes) >= 3:
        return " ".join(partes[2:]).strip()
    return ""

def _extrair_vagas_da_linha_vagas(linha: str):
    tokens = linha.split()
    if len(tokens) < 2:
        return None, None, None

    if not (tokens[0].isdigit() and tokens[1].isdigit()):
        return None, None, None

    vagas_totais = int(tokens[0])
    vagas_ocupadas = int(tokens[1])
    vagas_disponiveis = vagas_totais - vagas_ocupadas
    return vagas_totais, vagas_ocupadas, vagas_disponiveis

def _extrair_turmas_da_disciplina(linhas: list[str], indice_disciplina: int):
    turmas_disciplina = []
    indice = indice_disciplina + 1

    while indice < len(linhas):
        linha_atual = linhas[indice]

        if _eh_inicio_disciplina(linha_atual):
            break

        if _eh_linha_turma(linha_atual):
            professor = _extrair_professor_da_linha_turma(linha_atual)
            vagas_totais = vagas_ocupadas = vagas_disponiveis = None

            for prox in range(indice + 1, min(indice + 8, len(linhas))):
                if _eh_linha_turma(linhas[prox]) or _eh_inicio_disciplina(linhas[prox]):
                    break

                vt, vo, vd = _extrair_vagas_da_linha_vagas(linhas[prox])
                if vt is not None:
                    vagas_totais, vagas_ocupadas, vagas_disponiveis = vt, vo, vd
                    break

            turmas_disciplina.append({
                "linha_turma": linha_atual,
                "professor": professor,
                "vagas_totais": vagas_totais,
                "vagas_ocupadas": vagas_ocupadas,
                "vagas_disponiveis": vagas_disponiveis,
            })

        indice += 1

    return turmas_disciplina

def extrair_vagas_da_tabela(texto_tabela: str, nome_disciplina: str, nome_professor: str = ""):
    """Busca disciplina/professor no texto da tabela e calcula vagas por turma."""
    termo_disciplina = preparar_texto(nome_disciplina)
    termo_professor = preparar_texto(nome_professor)
    professor_obrigatorio = bool(termo_professor)

    print(f"Verificando vagas para {nome_disciplina} - {nome_professor or 'QUALQUER PROFESSOR'}...")

    linhas = [linha.strip() for linha in texto_tabela.splitlines() if linha.strip()]
    print(f"Verificando {len(linhas)} linhas de texto para {nome_disciplina}...")

    resultados_com_vaga = []
    encontrou_disciplina = False
    encontrou_professor = False
    encontrou_turma_sem_vaga = False

    for index, linha in enumerate(linhas):
        if termo_disciplina not in preparar_texto(linha):
            continue

        encontrou_disciplina = True

        turmas_disciplina = _extrair_turmas_da_disciplina(linhas, index)

        for turma in turmas_disciplina:
            professor_turma = preparar_texto(turma["professor"])

            if professor_obrigatorio and termo_professor not in professor_turma:
                continue

            if professor_obrigatorio:
                encontrou_professor = True

            vagas_totais = turma["vagas_totais"]
            vagas_ocupadas = turma["vagas_ocupadas"]
            vagas_disponiveis = turma["vagas_disponiveis"]

            if vagas_totais is None:
                continue

            if vagas_disponiveis > 0:
                if professor_obrigatorio:
                    resultados_com_vaga.append(
                        f"✅ {nome_disciplina.upper()} ({nome_professor}): {vagas_disponiveis} vagas disponíveis ({vagas_ocupadas}/{vagas_totais})"
                    )
                else:
                    resultados_com_vaga.append(
                        f"✅ {nome_disciplina.upper()}: {vagas_disponiveis} vagas disponíveis ({vagas_ocupadas}/{vagas_totais}) | {turma['linha_turma']}"
                    )
            else:
                encontrou_turma_sem_vaga = True

            if professor_obrigatorio:
                break

    if resultados_com_vaga:
        return "\n".join(resultados_com_vaga)

    if not encontrou_disciplina:
        if professor_obrigatorio:
            return f"⚠️ {nome_disciplina.upper()} ({nome_professor}): disciplina não encontrada na tabela"
        return f"⚠️ {nome_disciplina.upper()}: disciplina não encontrada na tabela"

    if professor_obrigatorio and not encontrou_professor:
        return f"⚠️ {nome_disciplina.upper()} ({nome_professor}): professor não encontrado para a disciplina"

    if professor_obrigatorio:
        return f"❌ {nome_disciplina.upper()} ({nome_professor}): turma encontrada, mas sem vagas disponíveis"
    if encontrou_turma_sem_vaga:
        return f"❌ {nome_disciplina.upper()}: turmas encontradas, mas sem vagas disponíveis"
    return f"⚠️ {nome_disciplina.upper()}: turmas encontradas, mas não foi possível identificar as colunas de vagas"

# --- FUNÇÃO PRINCIPAL DE SCRAPING ---

def verificar_vagas_unb():
    """
    Abre a página, aplica os filtros fixos e busca as disciplinas na tabela.
    """
    print("Iniciando Playwright otimizado...")
    inicio = time.time()
    resultados_encontrados = []

    with _SCRAPER_LOCK:
        try:
            sessao = _iniciar_sessao_playwright()

            print(f"Aplicando filtro de nível: {NIVEL_BUSCA}")
            print(f"Aplicando filtro de departamento: {DEPARTAMENTO_BUSCA}")

            texto_tabela = acessar_tabela_filtrada(sessao["page"])
            print("Tabela carregada. Iniciando busca pelas disciplinas...")

            for busca in DISCIPLINAS_A_VERIFICAR:
                resultado = extrair_vagas_da_tabela(
                    texto_tabela,
                    busca["disciplina"],
                    busca.get("professor", "")
                )
                resultados_encontrados.append(resultado)

        except Exception as e:
            print(f"Erro no scraping: {e}")

        fim = time.time()
        print(f"Tempo total de execução: {fim - inicio:.2f} segundos")

    if resultados_encontrados:
        return "\n\n".join(resultados_encontrados)
    return None

def verificar_vaga_especifica(nome_disciplina: str, nome_professor: str = ""):
    """Busca uma disciplina específica opcionalmente filtrando por professor."""
    inicio = time.time()

    with _SCRAPER_LOCK:
        try:
            sessao = _iniciar_sessao_playwright()
            texto_tabela = acessar_tabela_filtrada(sessao["page"])
            resultado = extrair_vagas_da_tabela(texto_tabela, nome_disciplina, nome_professor)
        except Exception as e:
            return f"❌ Erro ao verificar a disciplina: {e}"

    fim = time.time()
    print(f"Tempo total de execução (busca específica): {fim - inicio:.2f} segundos")
    return resultado

# --- TESTE LOCAL ---
if __name__ == "__main__":
    print("Iniciando teste local de scraping...")
    resultado_final = verificar_vagas_unb()

    if resultado_final:
        print("\n=== RESULTADO DA VERIFICAÇÃO ===")
        print(resultado_final)
    else:
        print("\n=== RESULTADO NEGATIVO ===")
        print("Não foi possível concluir a verificação das disciplinas.")