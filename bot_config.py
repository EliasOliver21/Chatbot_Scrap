import telebot
import Scrap_Vagas_Turmas
import time
import threading


bot = telebot.TeleBot('7665199891:AAFfH_oEGDnCom1f1Grs4QmcUeImF9ORS6g')

bot.set_webhook()

@bot.message_handler(['start','help'])
def start(msg:telebot.types.Message):
    ola = "Digite algum comando:\n" \
    "/start: Comandos.\n" \
    "/vagas: Apresenta a quantidade de vagas disponíveis das disciplinas já adicionadas.\n" \
    "/vagas_temp: Realiza uma consulta constante a cada 50 segundo e caso alguma das disciplinas possua vaga, retorna qual disciplina está disponível e se for várias retorna 'Múltiplas disciplinas disponíveis'."
    bot.reply_to(msg,ola)

@bot.message_handler(['vagas'])
def start(msg:telebot.types.Message):
    resposta = scrapping_vagas2.verify_vacancy_2()
    bot.reply_to(msg,resposta)

executando = False

def verificacao(msg):
    global executando
    while executando:
        try:
            resultado = scrapping_vagas2.verify_vacancy()  # Chama a função do outro script
            if resultado == "Vagas Disponíveis":
                bot.send_message(msg.chat.id, f"🔍 Resultado da verificação: {resultado}")
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

bot.infinity_polling()