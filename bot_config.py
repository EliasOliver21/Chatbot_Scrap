import telebot
import new_scrap_vagas_play as scrap_vagas_play
import time
import threading

with open('token.txt', encoding='utf-8') as token_file:
    bot = telebot.TeleBot(token_file.read().strip())

bot.remove_webhook()

def filtrar_apenas_vagas_disponiveis(resultado: str) -> str:
    if not resultado:
        return ""

    linhas_com_vaga = [linha for linha in resultado.splitlines() if linha.strip().startswith("✅")]
    return "\n".join(linhas_com_vaga)

@bot.message_handler(['start','help'])
def start(msg:telebot.types.Message):
    ola = "Digite algum comando:\n\n" \
    "/start: Comandos.\n\n" \
    "/vagas: Apresenta a quantidade de vagas disponíveis das disciplinas já adicionadas no script.\n\n" \
    "/vagas_temp: Realiza uma consulta constante a cada 180 segundos e caso alguma das disciplinas possua vaga, retorna o status.\n\n" \
    "/parar_vagas: Para a verificação temporizada das vagas\n\n" \
    "/vaga: Busca por uma vaga específica. Formato: /vaga Nome da disciplina - Nome do professor\n" \
    "(o professor é opcional; sem ele retorna turmas da disciplina com vagas)."

    bot.reply_to(msg,ola)

@bot.message_handler(['vagas'])
def start(msg:telebot.types.Message):
    resposta = scrap_vagas_play.verificar_vagas_unb()
    vagas_disponiveis = filtrar_apenas_vagas_disponiveis(resposta)
    if vagas_disponiveis:
        bot.reply_to(msg, f"🔔 Vagas disponíveis:\n{vagas_disponiveis}")
    else:
        bot.reply_to(msg, "Nenhuma vaga disponível no momento.")

@bot.message_handler(commands=['vaga'])
def vaga_especifica(msg: telebot.types.Message):
    texto = msg.text.replace('/vaga', '', 1).strip()

    if not texto:
        bot.reply_to(msg, "Use: /vaga Nome da disciplina - Nome do professor (professor opcional)")
        return

    if ' - ' in texto:
        disciplina, professor = texto.split(' - ', 1)
        disciplina = disciplina.strip()
        professor = professor.strip()
    else:
        disciplina = texto
        professor = ""

    if not disciplina:
        bot.reply_to(msg, "Informe pelo menos o nome da disciplina.")
        return

    resultado = scrap_vagas_play.verificar_vaga_especifica(disciplina, professor)
    bot.reply_to(msg, resultado or "Não foi possível verificar a disciplina informada.")

executando = False

def verificacao(msg):
    global executando
    try:
        while executando:
            try:
                resultado = scrap_vagas_play.verificar_vagas_unb() # Chama a função do outro script
                vagas_disponiveis = filtrar_apenas_vagas_disponiveis(resultado)

                if vagas_disponiveis:
                    bot.send_message(msg.chat.id, f"🔔 Vagas disponíveis:\n{vagas_disponiveis}")
            except Exception as e:
                bot.send_message(msg.chat.id, f"❌ Ocorreu um erro: {str(e)}")
                continue

            time.sleep(180)
    finally:
        scrap_vagas_play.encerrar_sessao_da_thread_atual()

@bot.message_handler(commands=['vagas_temp'])
def start(msg: telebot.types.Message):
    global executando
    if not executando:
        executando = True
        bot.reply_to(msg, "⏳ A verificação foi iniciada! O bot verificará as vagas a cada 180 segundos.")
        thread = threading.Thread(target=verificacao, args=(msg,))
        thread.daemon = True  # Permite encerrar a thread quando o programa terminar
        thread.start()
    else:
        bot.reply_to(msg, "ℹ️ A verificação já está em execução.")

@bot.message_handler(commands=['parar_vagas'])
def stop(msg: telebot.types.Message):
    global executando
    executando = False
    bot.reply_to(msg, "⏹ A verificação de vagas foi interrompida.")

if __name__ == "__main__":
    bot.infinity_polling(skip_pending=True, timeout=60, long_polling_timeout=60)