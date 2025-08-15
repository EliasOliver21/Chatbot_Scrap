import telebot
import scrap_vagas_turmas
import time
import threading

bot = telebot.TeleBot('7665199891:AAFfH_oEGDnCom1f1Grs4QmcUeImF9ORS6g')

bot.set_webhook()

@bot.message_handler(['start','help'])
def start(msg:telebot.types.Message):
    ola = "Digite algum comando:\n\n" \
    "/start: Comandos.\n\n" \
    "/vagas: Apresenta a quantidade de vagas disponíveis das disciplinas já adicionadas no script.\n\n" \
    "/vagas_temp: Realiza uma consulta constante a cada 50 segundo e caso alguma das disciplinas possua vaga, retorna qual disciplina está disponível e se for várias retorna 'Múltiplas disciplinas disponíveis'.\n\n" \
    "/parar_vagas: Para a verificação temporizada das vagas\n\n" \
    "/vaga: Busca por uma vaga específica, a partir do nome da diciplina e do professor. Digite o comando da seguinte forma: ""/vaga Nome da disciplina - Nome do professor""\n"

    bot.reply_to(msg,ola)

@bot.message_handler(['vagas'])
def start(msg:telebot.types.Message):
    resposta = scrap_vagas_turmas.verificar_vagas_unb()
    bot.reply_to(msg,resposta)

executando = False

def verificacao(msg):
    global executando
    while executando:
        try:
            resultado = scrap_vagas_turmas.verificar_vagas_unb() # Chama a função do outro script
            if resultado:
                print(resultado)
                bot.send_message(msg.chat.id, f"🔍 Resultado da verificação:\n {resultado}")
        except Exception as e:
            bot.send_message(msg.chat.id, f"❌ Ocorreu um erro: {str(e)}")
            continue
        
        time.sleep(50)  # Aguarda 50 segundos antes da próxima verificação

@bot.message_handler(commands=['vagas_temp'])
def start(msg: telebot.types.Message):
    global executando
    if not executando:
        executando = True
        bot.reply_to(msg, "⏳ A verificação foi iniciada! O bot verificará as vagas a cada 50 segundos.")
        thread = threading.Thread(target=verificacao, args=(msg,))
        thread.daemon = True  # Permite encerrar a thread quando o programa terminar
        thread.start()

@bot.message_handler(commands=['parar_vagas'])
def stop(msg: telebot.types.Message):
    global executando
    executando = False
    bot.reply_to(msg, "⏹ A verificação de vagas foi interrompida.")

@bot.message_handler(['vaga'])
def handle_text_messages(message):

    try:
        user_input = message.text.replace('/vaga','').strip()
        disciplina, professor = user_input.split("-")
        resultado = scrap_vagas_turmas.verificar_vaga(disciplina, professor)
        bot.send_message(message.chat.id, f"{resultado}")

    except Exception as e:
        bot.send_message(message.chat.id, f"Formato Inválido.\n\n Execute o comando com o seguinte formato:\n\n  Exemplo: `/vaga Compiladores 1 - Sergio `\n\n Não esqueça dos acentos!!!")


bot.infinity_polling()