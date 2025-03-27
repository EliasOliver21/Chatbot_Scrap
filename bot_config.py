import telebot
import scrapping_vagas2
import time
import threading


bot = telebot.TeleBot('7665199891:AAFfH_oEGDnCom1f1Grs4QmcUeImF9ORS6g')

@bot.message_handler(['start','help'])
def start(msg:telebot.types.Message):
    ola = "Olá, Mundo!"
    bot.reply_to(msg,ola)

@bot.message_handler(['vagas'])
def start(msg:telebot.types.Message):
    resposta = scrapping_vagas2.verify_vacancy()
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


bot.infinity_polling()


