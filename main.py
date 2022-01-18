import telebot, time
from time import sleep, time
from iqoptionapi.stable_api import IQ_Option
from datetime import datetime
from telebot import types, util
from github import Github
from datetime import datetime, timedelta
from colorama import init
import pytz, threading
from bs4 import BeautifulSoup
import requests

#api_bot = "2118641728:AAG5uHqiYHEh3WRYc-gOtHSLOvAmGY4sh7U"
api_bot="5060827840:AAHoiNIuNlr8q3eHvhL2ADZSC6OvV_RY9II"
bot = telebot.TeleBot(api_bot, threaded=True, num_threads=10)
g = Github(login_or_token="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",timeout=5*60)
repo = g.get_user().get_repo('autoIQ')
all_files = []
contents = repo.get_contents("")
content = str(contents)

def noticias(par, horario_):
    headers = requests.utils.default_headers()
    headers.update({'User-Agent': 'Mozilla/5.0 (Windows NT 6.1; Win64; x64; rv:79.0) Gecko/20100101 Firefox/79.0'})
    data = requests.get('http://br.investing.com/economic-calendar/', headers=headers)
    resultados = []
    if data.status_code == requests.codes.ok:
        info = BeautifulSoup(data.text, 'html.parser')
        blocos = ((info.find('table', {'id': 'economicCalendarData'})).find('tbody')).findAll('tr', {'class': 'js-event-item'})
        for blocos2 in blocos:
            impacto = str((blocos2.find('td', {'class': 'sentiment'})).get('data-img_key')).replace('bull', '')
            horario = str(blocos2.get('data-event-datetime')).replace('/', '-')
            moeda = (blocos2.find('td', {'class': 'left flagCur noWrap'})).text.strip()
            resultados.append({'par': moeda, 'horario': horario, 'impacto': impacto})
    for info in resultados:
        if str(par).upper()==str(info['par']).upper() and (horario_==info['horario'][11:16]) and int(info['impacto'])>=2:
            return True
        elif str(par).upper()==str(info['par']).upper() and ((horario_==info['horario'][11:16])) and int(info['impacto'])==1:
            return 'Notícia'
            #print('PARIDADE: ', info['par'],'\n HORARIO: ', info['horario'], '\n IMPACTO: ', info['impacto'], '\n--------\n')
        else:
            return False

login_dict = {}
class login:
    def __init__(self, email):
        self.email = email
        self.senha = None

config_mhi = {}
class mhi_config:
    def __init__(self, conta):
        self.conta = conta
        self.operacao = None
        self.tipo_mhi = None
        self.time_frame = None
        self.par = None
        self.valor_entrada = None
        self.martingale = None
        self.stop_loss = None
        self.stop_gain = None

config_lista_sinais = {}
class lista_sinais_config:
    def __init__(self, conta):
        self.conta = conta
        self.operacao = None
        self.valor_entrada = None
        self.martingale = None
        self.stop_loss = None
        self.stop_gain = None

config_term = {}
class termometro_config:
    def __init__(self, par):
        self.par = par
        self.timeframe = None

config_tend = {}
class tendencia_config:
    def __init__(self, conta):
        self.conta = conta
        self.operacao = None
        self.time_frame = None
        self.par = None
        self.valor_entrada = None
        self.martingale = None
        self.stop_loss = None
        self.stop_gain = None
        
        
config_catalogador = {}
class catalogador_config:
    def __init__(self, time_frame):
        self.time_frame = time_frame
        self.dias = None
        self.porcentagem = None
        self.martingale = None

global ligado
global ligado_sinais

def cliente_permitido(id):
    valores = []
    arq_dados = 'cliente_permitido.txt'
    try:
        file = open(arq_dados, 'r').read()
    except:
        print("Nenhum cliente regitrado.")

    for index, dados in enumerate(file.split('\n')):
        if len(dados) > 0 and dados != '':
            dados_ = dados.split(',')
            if dados_[0] == id:
                valores.append({
                    'id_telegram': dados_[0],
                    'estado': dados_[1],
                    'plano': dados_[2],
                    'mes_espiracao': dados_[3]
                })

    return valores

def nao_exist(id):
    result = False
    file = open("{}.txt".format(id), 'r')
    for dado in file:
        if dado.strip() != '':
            result = True
    file.close()
    return result

@bot.message_handler(commands=['start'])
def send_welcome(message):
    id_user = message.from_user.id
    dados_cli = cliente_permitido(str(id_user))
    if len(dados_cli) > 0:
        for data in dados_cli:
            id_telegram = int(data['id_telegram'])
            estado = int(data['estado'])
            plano = str(data['plano'])
            mes_espiracao = int(data['mes_espiracao'])

    try:
        
        if id_telegram==id_user and estado==0:
            bot.send_message(message.chat.id, "Olá tudo bem "+message.from_user.first_name +
                        " " + message.from_user.last_name + "?" +
                        "\nSeja bem vindo(a) ao ROBÔ ALPHA este é o seu ID: " +str(message.chat.id) +
                        "\nContacte @Zcreations1 para obter acesso ao bot! ")
        
        elif id_telegram==id_user and plano!='super_admin' and plano!='admin':

            markup = types.ReplyKeyboardMarkup(resize_keyboard=True, row_width=10)
            itembtng = types.KeyboardButton('🤖Listar Bots')
            markup.row(itembtng)
            bot.send_message(message.chat.id, "Olá tudo bem " +str(message.from_user.first_name)+
            '\nBem vindo de volta ao ROBÔ ALPHA',reply_markup=markup)
            try:
                git_file ='lista_catalogada_{}.txt'.format(message.chat.id)
                git_login ='login_{}.txt'.format(message.chat.id)
                if git_file in content:
                    pass
                else:
                    repo.create_file(git_file, "committing files", '') 

                if git_login in content:
                    pass
                else:
                    repo.create_file(git_file, "committing files", '')  
            except:
                pass      
        elif id_telegram == id_user and estado == 1 and plano == 'super_admin':
           
            try:
                git_file ='lista_catalogada_{}.txt'.format(message.chat.id)
                git_login ='login_{}.txt'.format(message.chat.id)
                if git_file in content:
                    pass
                else:
                    repo.create_file(git_file, "committing files", '') 
                     
                if git_login in content:
                    pass
                else:
                    repo.create_file(git_file, "committing files", '')  
            except:
                pass     

            markup = types.ReplyKeyboardMarkup(resize_keyboard=True, row_width=10)
            itembtna = types.KeyboardButton('✅Add usuário')
            itembtnb = types.KeyboardButton('⛔Excluir usuário')
            itembtnc = types.KeyboardButton('📖Listar usuários')
            itembtnd = types.KeyboardButton('📨Alterar Pacote')
            itembtne = types.KeyboardButton('📅Alterar data de expiração')
            itembtnf = types.KeyboardButton('🚫Restringir usuário')
            itembtng = types.KeyboardButton('🤖Listar Bots')
            markup.row(itembtna, itembtnb)
            markup.row(itembtnc, itembtnd)
            markup.row(itembtne)
            markup.row(itembtnf, itembtng)
            bot.send_message(message.chat.id,"Bem-vindo de volta Super-Admin " +str(message.from_user.first_name),reply_markup=markup)

        elif id_telegram == id_user and estado == 1 and plano == 'admin':
           
            try:
                git_file ='lista_catalogada_{}.txt'.format(message.chat.id)
                git_login ='login_{}.txt'.format(message.chat.id)
                if git_file in content:
                    pass
                else:
                    repo.create_file(git_file, "committing files", '') 
                     
                if git_login in content:
                    pass
                else:
                    repo.create_file(git_file, "committing files", '')  
            except:
                pass     
            
            markup = types.ReplyKeyboardMarkup(resize_keyboard=True, row_width=10)
            itembtna = types.KeyboardButton('🛂Prestar Suporte')
            itembtnb = types.KeyboardButton('📚Dados do Usuário')
            itembtnc = types.KeyboardButton('👥Usuários Ativos')
            itembtnd = types.KeyboardButton('📨Pacotes disponíveis')
            itembtne = types.KeyboardButton('🔐Verificação de Usuário')
            itembtng = types.KeyboardButton('🤖Listar Bots')
            markup.row(itembtna, itembtnb)
            markup.row(itembtnc, itembtnd)
            markup.row(itembtne)
            markup.row(itembtng)
            bot.send_message(message.chat.id,"Bem-vindo de volta Admin "+str(message.from_user.first_name),reply_markup=markup)

    except:
        bot.send_message(message.chat.id, "Olá tudo bem "+str(message.from_user.first_name)+
                        " " + message.from_user.last_name + "?" +
                        "\nSeja bem vindo(a) ao ROBÔ ALPHA este é o seu ID: " +str(message.chat.id) +
                        "\nContacte @Zcreations1 para obter acesso ao bot! ")

@bot.message_handler(func=lambda message: message.text == '🤖Listar Bots')
def listar_bots(message):
    id_user = message.from_user.id
    dados_cli = cliente_permitido(str(id_user))
    if len(dados_cli) > 0:
        for data in dados_cli:
            id_telegram = int(data['id_telegram'])
            estado = int(data['estado'])
            plano = str(data['plano'])
            mes_espiracao = int(data['mes_espiracao'])

    if (id_telegram == id_user) and (estado == 1) and plano == "Grátis":
        markup = types.ReplyKeyboardMarkup(resize_keyboard=True, row_width=10)
        itembtna = types.KeyboardButton('Bot de Lista de Sinais')
        markup.row(itembtna)
        bot.send_message(message.chat.id,"Bot disponível para o plano grátis",reply_markup=markup)
    elif (id_telegram == id_user) and (estado == 1) and plano == "Bronze":

        markup = types.ReplyKeyboardMarkup(resize_keyboard=True, row_width=10)
        itembtna = types.KeyboardButton('Lista de Sinais')
        itembtnb = types.KeyboardButton('MHI')
        markup.row(itembtnb)
        markup.row(itembtna)
        bot.send_message(message.chat.id,"Bots disponíveis para o plano bronze",reply_markup=markup)
    elif (id_telegram == id_user) and (estado == 1) and plano == "Prata":

        markup = types.ReplyKeyboardMarkup(resize_keyboard=True, row_width=10)
        itembtna = types.KeyboardButton('Lista de Sinais')
        itembtnb = types.KeyboardButton('MHI')
        itembtnc = types.KeyboardButton('Catalogador')
        itembtnd = types.KeyboardButton('Estratégia Chinesa')
        markup.row(itembtnb, itembtnc)
        markup.row(itembtna, itembtnd)
        bot.send_message(message.chat.id,"Bots disponíveis para o plano prata",reply_markup=markup)
    elif (id_telegram == id_user) and (estado == 1) and plano == "Ouro":

        markup = types.ReplyKeyboardMarkup(resize_keyboard=True, row_width=10)
        itembtna = types.KeyboardButton('Lista de Sinais')
        itembtnb = types.KeyboardButton('MHI')
        itembtnc = types.KeyboardButton('Catalogador')
        itembtnd = types.KeyboardButton('Estratégia Chinesa')
        itembtne = types.KeyboardButton('Tendência')
        itembtng = types.KeyboardButton('Estratégia Berman')
        itembtnf = types.KeyboardButton('Sinais ao Vivo')
        itembtnh = types.KeyboardButton('Scalper')
        markup.row(itembtnf)
        markup.row(itembtnb,itembtne,itembtnh)
        markup.row(itembtnc,itembtna)
        markup.row(itembtnd, itembtng)
        bot.send_message(message.chat.id,"Bots disponíveis para o plano ouro",reply_markup=markup)

    elif (id_telegram == id_user) and (estado == 1) and plano == "Disponível":

        markup = types.ReplyKeyboardMarkup(resize_keyboard=True, row_width=10)
        itembtna = types.KeyboardButton('Lista de Sinais')
        itembtnb = types.KeyboardButton('MHI')
        itembtnc = types.KeyboardButton('Catalogador')
        itembtnf = types.KeyboardButton('Sinais ao Vivo')
        markup.row(itembtnf)
        markup.row(itembtnb, itembtnc)
        markup.row(itembtna)
        bot.send_message(message.chat.id,"Bots disponíveis até ao momento",reply_markup=markup)

    elif (id_telegram == id_user) and (plano == "Grátis" or plano == "Bronze" or plano == "Prata" or plano == "Ouro") and estado != 1:
        bot.send_message(message.chat.id,"Por Algum motivo você já não tem acesso ao Bot." +
            "\nContacte o suporte para lhe prestar ajuda: --> @Zcreations1")

    elif ((id_telegram == id_user) and (estado == 1) and plano == "admin") or ((id_telegram == id_user) 
        and (estado == 1) and plano == "super_admin"):

        markup = types.ReplyKeyboardMarkup(resize_keyboard=True, row_width=10)
        itembtna = types.KeyboardButton('Lista de Sinais')
        itembtnb = types.KeyboardButton('MHI')
        itembtnc = types.KeyboardButton('Catalogador')
        itembtnd = types.KeyboardButton('Estratégia Chinesa')
        itembtne = types.KeyboardButton('Tendência')
        itembtng = types.KeyboardButton('Estratégia Berman')
        itembtnf = types.KeyboardButton('Sinais ao Vivo')
        itembtni = types.KeyboardButton('Scalper')
        itembtnh = types.KeyboardButton('🔙VOLTAR')
        markup.row(itembtnf)
        markup.row(itembtnb,itembtne,itembtni)
        markup.row(itembtnc,itembtna)
        markup.row(itembtnd, itembtng)
        markup.row(itembtnh)
        bot.send_message(message.chat.id,"====Bots Disponíveis====",reply_markup=markup)

@bot.message_handler(func=lambda message: message.text == 'Lista de Sinais')
def bot_lista_sinais(message):
    git_file ='{}.txt'.format(message.chat.id)
    if git_file in content:
        pass
    else:
        repo.create_file(git_file, "committing files", '')
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True, row_width=10)
    itembtng = types.KeyboardButton('🔐Fazer Login')
    itembtna = types.KeyboardButton('✅Ligar bot de sinais')
    itembtnb = types.KeyboardButton('🔴Desligar bot de sinais')
    itembtnc = types.KeyboardButton('📖Adicionar Sinais')
    itembtnd = types.KeyboardButton('⚙Configurar Bot de Sinais')
    itembtne = types.KeyboardButton('🆘Ajuda')
    itembtnf = types.KeyboardButton('🤖Listar Bots')
    markup.row(itembtnc)
    markup.row(itembtnd)
    markup.row(itembtng)
    markup.row(itembtna, itembtnb)
    markup.row(itembtne, itembtnf)
    bot.send_message(message.chat.id,"Bot de lista de sinais",reply_markup=markup)

    @bot.message_handler(func=lambda message: message.text == '✅Ligar bot de sinais')
    def ligar_lista(message):
        global ligado_sinais
        ligado_sinais = True
        bot.send_message(message.chat.id, "✅Bot de Lista de sinais✅")
        chat_id = message.chat.id
        dados_config_lista_sinais = config_lista_sinais[chat_id]
        dados_config_login = login_dict[chat_id]
        id_user = message.from_user.id
        dados_cli = cliente_permitido(str(id_user))
        if len(dados_cli) > 0:
            for data in dados_cli:
                id_telegram = int(data['id_telegram'])
                estado = int(data['estado'])
                plano = str(data['plano'])
                mes_espiracao = int(data['mes_espiracao'])
        def stop(lucro, gain, loss):
            if lucro <= float('-' + str(abs(loss))):
                bot.send_message(message.chat.id, '🔴Stop Loss batido!')
                return
            if lucro >= float(abs(gain)):
                bot.send_message(message.chat.id, '✅Stop Gain Batido!')
                return

        def Martingale(valor, payout):
            lucro_esperado = valor * payout
            perca = float(valor)

            while True:
                if round(valor * payout, 2) > round(abs(perca) + lucro_esperado, 2):
                    return round(valor, 2)
                    break
                valor += 0.01

        def Payout(par):
            API.subscribe_strike_list(par, 1)
            while True:
                d = API.get_digital_current_profit(par, 1)
                if d != False:
                    d = round(int(d) / 100, 2)
                    break

            API.unsubscribe_strike_list(par, 1)

            return d

        try:
                
            if (dados_config_login.email == None) or (dados_config_login.senha== None):

                    bot.send_message(message.chat.id,'🚨Erro verifique os dados de Login e tente novamente🚨')

            else:
                usuario = dados_config_login.email  # input("Digite o usuário da IQ Option: ")
                senha = dados_config_login.senha  #getpass.getpass(f"Digite a senha da IQ Option: ")
                API = IQ_Option(usuario, senha)
                print(API.connect())
        except:
                bot.send_message(message.chat.id, '🚨ERRO DE LOGIN🚨\n'
                                                  +'Verifique os seu dados de login da IQ option\n')

        if API.check_connect():
            bot.send_message(message.chat.id, '✅Conectado com sucesso!✅')
        else:
            bot.send_message(message.chat.id, '🚨Erro ao se conectar🚨')
            return

        try:
            conta = int(dados_config_lista_sinais.conta)  
            if int(conta) == 1:
                API.change_balance('PRACTICE')
            elif int(conta) == 2:
                API.change_balance('REAL')  # PRACTICE / REAL
            else:
                bot.send_message(message.chat.id,"❌Erro ao escolher o tipo de conta❌")
        except:
            bot.send_message(message.chat.id, "❌Erro, tente novamente❌")
            return

        while True:
            try:
                operacao = int(dados_config_lista_sinais.operacao)  
                if operacao > 0 and operacao < 3: break
            except:
                bot.send_message(message.chat.id,'❌Opção de escolha entre digital e binária errada❌')
                break

        def get_sinal():
            sinais=[]
            arq_sinais = "{}.txt".format(id_user)
            try:
                file = open(arq_sinais, 'r').read()
            except:
                print("Todos os sinais já foram analisados.")
                return
            for index,sinal in enumerate(file.split('\n')):
                if len(sinal) > 0 and sinal != '':
                    sinal_ = sinal.split(',')
                    #formato da lista: TIMESTAMP,PARIDADE,call,1
                    utcmoment_naive = datetime.utcnow()
                    utcmoment = utcmoment_naive.replace(tzinfo=pytz.utc)
                    timezones = ['America/Sao_Paulo']
                    for tz in timezones:
                        localDatetime = utcmoment.astimezone(pytz.timezone(tz))
                    
                    f=localDatetime.strftime('%H:%M')
                    if str(sinal_[0]) == str(localDatetime.strftime('%H:%M')) and (noticias(par[3:6], f)!=True or noticias(par[0:3], f)!=True):
                            sinais.append({'timestamp': sinal_[0],
                                            'par': sinal_[1],
                                            'dir': sinal_[2],
                                            'timeframe': sinal_[3]})
                            open(arq_sinais, 'w').write(file.replace(sinal, ''))
            return sinais

        valor_entrada = float(dados_config_lista_sinais.valor_entrada)
        valor_entrada_b = float(valor_entrada)

        martingale = int(dados_config_lista_sinais.martingale)
        martingale += 1

        stop_loss = float(dados_config_lista_sinais.stop_loss)
        stop_gain = float(dados_config_lista_sinais.stop_gain)

        lucro = 0
        bot.send_message(
            message.chat.id, "✅Aguarde os resultados das suas operações✅\n" +
                            "⏳⏳⏳⏳⏳⏳⏳⏳⏳⏳⏳⏳⏳⏳")
        ops=0
        try:

            while ligado_sinais:
                sinais = get_sinal()

                if len(sinais) > 0:
                    for data in sinais:
                        valor_entrada = valor_entrada_b
                        par=str(data['par']).upper()
                        dir=str(data['dir']).lower()
                        time_frame=int(data['timeframe'])
                        payout = Payout(par)    

                        valor_entrada = valor_entrada_b
                        for i in range(martingale):
                        
                            status,id = API.buy_digital_spot(par, valor_entrada, dir, time_frame) if operacao == 1 else API.buy(valor_entrada, par, dir, time_frame)
                            bot.send_message(message.chat.id,"✅Uma operações em andamento✅\n" +
                                                                "Paridade: "+str(par)+
                                                                "\nDireção: "+str(dir)+
                                                                "\nTime Frame: "+str(time_frame)+
                                                                "\nPayout: "+str(payout*100))
                            if status:
                                while True:
                                    try:
                                        status,valor = API.check_win_digital_v2(id) if operacao == 1 else API.check_win_v3(id)
                                    except:
                                        status = True
                                        valor = 0
                                    
                                    if status:
                                        valor = valor if valor > 0 else float('-' + str(abs(valor_entrada)))
                                        lucro += round(valor, 2)
                                        
                                        msg = '''
                                💹Resultado da operação💹\n

                                RESULTADO:''' + ('✅WIN' if valor > 0 else '🚨LOSS') + '''
                                LUCRO: 💲''' + str(round(valor, 2)) + '''\n
                                ''' + (str(i)+ ' ♻GALE' if i > 0 else '') + '''\n'''
                                        bot.send_message(message.chat.id,str(msg))
                                    
                                        valor_entrada = Martingale(valor_entrada, payout)
                                        if lucro <= float('-' +str(abs(stop_loss))):
                                            bot.send_message(message.chat.id,'🔴Stop Loss batido!')
                                            return
                                            break
                                        if lucro >= float(abs(stop_gain)):
                                            bot.send_message(message.chat.id,'✅Stop Gain Batido!')
                                            return
                                            break
                                        if valor > 0 : break
                                        break
                                if valor > 0 : break
                            else:
                                bot.send_message(message.chat.id,'🚨ERRO AO REALIZAR OPERAÇÃO\n' +
                                'O activo selecionado não se encontra aberto.')
                                break
                print(ops+1, 'Operações abertas |', datetime.now().strftime('%H:%M:%S'), end='\r')
        except Exception as e:
                        print("O Bot encontrou o erro abaixo:\n",e)

    try:
        @bot.message_handler(func=lambda message: message.text == '🔴Desligar bot de sinais')
        def desligar_lista(message):
            global ligado_sinais
            ligado_sinais = False
            bot.send_message(message.chat.id,"🔴Bot de Lista de sinais desligado!🔴")
            return
    except:
        pass

@bot.message_handler(func=lambda message: message.text == 'MHI')
def bot_mhi(message):
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True, row_width=10)
    itembtnf = types.KeyboardButton('🔐Fazer Login')
    itembtna = types.KeyboardButton('✅Ligar MHI')
    itembtnb = types.KeyboardButton('🔴Desligar MHI')
    itembtnc = types.KeyboardButton('⚙Configurar Bot de MHI')
    itembtnd = types.KeyboardButton('🆘Ajuda')
    itembtne = types.KeyboardButton('🤖Listar Bots')
    markup.row(itembtnc)
    markup.row(itembtnf)
    markup.row(itembtna, itembtnb)
    markup.row(itembtnd, itembtne)
    bot.send_message(message.chat.id, "Bot de MHI", reply_markup=markup)
    
    @bot.message_handler(func=lambda message: message.text == '✅Ligar MHI')
    def ligar(message):
        global ligado
        ligado = True
        bot.send_message(message.chat.id, "✅Bot de MHI ligado✅")
        chat_id = message.chat.id
        dados_config_mhi = config_mhi[chat_id]
        dados_config_login = login_dict[chat_id]
        id_user = message.from_user.id
        dados_cli = cliente_permitido(str(id_user))
        if len(dados_cli) > 0:
            for data in dados_cli:
                id_telegram = int(data['id_telegram'])
                estado = int(data['estado'])
                plano = str(data['plano'])
                mes_espiracao = int(data['mes_espiracao'])
        
        def Martingale(valor, payout):
            lucro_esperado = valor * payout
            perca = float(valor)

            while True:
                if round(valor * payout, 2) > round(
                        abs(perca) + lucro_esperado, 2):
                    return round(valor, 2)
                    break
                valor += 0.01

        def Payout(par):
            API.subscribe_strike_list(par, 1)
            while True:
                d = API.get_digital_current_profit(par, 1)
                if d != False:
                    d = round(int(d) / 100, 2)
                    break
            API.unsubscribe_strike_list(par, 1)

            return d

        try:
                
            if (dados_config_login.email == None) or (dados_config_login.senha== None):

                    bot.send_message(message.chat.id,'🚨Erro verifique os dados de Login e tente novamente🚨')

            else:
                usuario = dados_config_login.email  # input("Digite o usuário da IQ Option: ")
                senha = dados_config_login.senha  #getpass.getpass(f"Digite a senha da IQ Option: ")
                API = IQ_Option(usuario, senha)
                print(API.connect())
        except:
                bot.send_message(message.chat.id, '🚨ERRO DE LOGIN🚨\n'
                                                  +'Verifique os seu dados de login da IQ option\n')

        if API.check_connect():
            bot.send_message(message.chat.id, '✅Conectado com sucesso!✅')
        else:
            bot.send_message(message.chat.id, '🚨Erro ao se conectar🚨')
            return

        try:

            conta = int(
                dados_config_mhi.conta
            )  #int(input('\nEscolha em qual conta Operar:\n 1 - Treinamento\n 2 - REAL\n:: '))

            if int(conta) == 1:
                API.change_balance('PRACTICE')
            elif int(conta) == 2:
                API.change_balance('REAL')  # PRACTICE / REAL
            else:
                bot.send_message(message.chat.id,
                                 "❌Erro ao escolher o tipo de conta❌")
        except:
            bot.send_message(message.chat.id, "❌Erro, tente novamente❌")
            return

        while True:
            try:
                operacao = int(dados_config_mhi.operacao)

                if operacao > 0 and operacao < 3: break
            except:
                bot.send_message(
                    message.chat.id,
                    '❌Opção de escolha entre digital e binária errada❌')
                break

        while True:
            try:
                tipo_mhi = int(
                    dados_config_mhi.tipo_mhi
                )  #int(input('Deseja operar a favor da\n  1 - Minoria\n  2 - Maioria\n  :: '))

                if tipo_mhi > 0 and tipo_mhi < 3: break
            except:
                bot.send_message(message.chat.id, '❌Tipo de HMI incorreto❌')
                break

        while True:
            try:
                time_frame = int(dados_config_mhi.time_frame)
                break
            except:
                bot.send_message(message.chat.id, '❌Time frame incorreto❌')
                break

        par = str(dados_config_mhi.par).upper()
        valor_entrada = float(dados_config_mhi.valor_entrada)
        valor_entrada_b = float(valor_entrada)

        martingale = int(dados_config_mhi.martingale)
        martingale += 1

        stop_loss = float(dados_config_mhi.stop_loss)
        stop_gain = float(dados_config_mhi.stop_gain)

        lucro = 0
        payout = Payout(par)
        bot.send_message(
            message.chat.id, "✅Aguarde os resultados das suas operações✅\n" +
                             "⏳⏳⏳⏳⏳⏳⏳⏳⏳⏳⏳⏳⏳⏳")
        
        while ligado:
            minutos = float(((datetime.now()).strftime('%M.%S'))[1:])
            entrar = True if (minutos >= 4.58 and minutos <= 5) or minutos >= 9.58 else False

            if entrar:
                dir = False
                velas = API.get_candles(par, (time_frame*60), 3, time())

                velas[0] = 'g' if velas[0]['open'] < velas[0][ 'close'] else 'r' if velas[0]['open'] > velas[0]['close'] else 'd'
                velas[1] = 'g' if velas[1]['open'] < velas[1]['close'] else 'r' if velas[1]['open'] > velas[1]['close'] else 'd'
                velas[2] = 'g' if velas[2]['open'] < velas[2]['close'] else 'r' if velas[2]['open'] > velas[2]['close'] else 'd'

                cores = velas[0] + ' ' + velas[1] + ' ' + velas[2]

                if cores.count('g') > cores.count('r') and cores.count('d') == 0:
                    dir = ('put' if tipo_mhi == 1 else 'call')
                if cores.count('r') > cores.count('g') and cores.count('d') == 0:
                    dir = ('call' if tipo_mhi == 1 else 'put')

                f=datetime.now().strftime('%H:%M')
                if dir and (noticias(par[3:6], f)!=True or noticias(par[0:3], f)!=True):

                    bot.send_message(message.chat.id, '✅Uma operação em andamento✅' +
                        '\nTempo de análise: ' + str(minutos) + '⏰' +
                        '\nCor da entrada: ' +
                        str('💹' if dir == 'call' else '🚨') + '\nDireção: ' +
                        str('Compra' if dir == 'call' else 'Venda'))

                    valor_entrada = valor_entrada_b
                    for i in range(martingale):
                        
                        status, id = API.buy_digital_spot(
                        par, valor_entrada, dir,time_frame) if operacao == 1 else API.buy(valor_entrada, par, dir, time_frame)

                        if status:
                            while True:
                                try:
                                    status, valor = API.check_win_digital_v2(
                                        id
                                    ) if operacao == 1 else API.check_win_v3(
                                        id)
                                except:
                                    status = True
                                    valor = 0

                                if status:
                                    valor = valor if valor > 0 else float('-' + str(abs(valor_entrada)))
                                    lucro += round(valor, 2)

                                    msg = '''
                            💹Resultado da operação💹\n

                            RESULTADO:''' + ('✅WIN' if valor > 0 else '🚨LOSS') + '''
                            LUCRO: 💲''' + str(round(valor, 2)) + '''\n
                            ''' + (str(i)+ ' ♻GALE' if i > 0 else '') + '''\n'''
                                    bot.send_message(message.chat.id,msg)

                                    valor_entrada = Martingale(valor_entrada, payout)

                                    if lucro <= float('-' +str(abs(stop_loss))):
                                        bot.send_message(message.chat.id,'🔴Stop Loss batido!')
                                        return
                                        break
                                    if lucro >= float(abs(stop_gain)):
                                        bot.send_message(message.chat.id,'✅Stop Gain Batido!')
                                        return
                                        break

                                    if valor > 0: break

                                    break

                            if valor > 0: break

                        else:
                            bot.send_message(message.chat.id,'🚨ERRO AO REALIZAR OPERAÇÃO\n' +
                                'O activo selecionado não se encontra aberto.')
                            break
                            return

    try:
        @bot.message_handler(func=lambda message: message.text == '🔴Desligar MHI')
        def desligar(message):
            global ligado
            ligado = False
            bot.send_message(message.chat.id,"🔴Bot de MHI desligado!🔴")
            return
    except:
        pass
        
@bot.message_handler(func=lambda message: message.text == '🆘Ajuda')
def ajuda(message):
    bot.send_message(message.chat.id,"Olá " + message.from_user.first_name + " caso tenhas algum\n" +
        "problema com o bot, contacte o suporte--> @Zcreations1")

@bot.message_handler(func=lambda message: message.text == 'Estratégia Chinesa')
def bot_estrategia_chinesa(message):
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True, row_width=10)
    itembtnf = types.KeyboardButton('🔐Fazer Login')
    itembtna = types.KeyboardButton('✅Ligar método chinês')
    itembtnb = types.KeyboardButton('🔴Desligar método chinês')
    itembtnc = types.KeyboardButton('⚙Configurar método chinês')
    itembtnd = types.KeyboardButton('🆘Ajuda')
    itembtne = types.KeyboardButton('🤖Listar Bots')
    markup.row(itembtnc)
    markup.row(itembtnf)
    markup.row(itembtna, itembtnb)
    markup.row(itembtnd, itembtne)
    bot.send_message(message.chat.id,"Bot de Estratégia Chinesa",reply_markup=markup)

@bot.message_handler(func=lambda message: message.text == 'Tendência')
def bot_tendencia(message):
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True, row_width=10)
    itembtnf = types.KeyboardButton('🔐Fazer Login')
    itembtna = types.KeyboardButton('✅Ligar Tendência')
    itembtnb = types.KeyboardButton('🔴Desligar Tendência')
    itembtnc = types.KeyboardButton('⚙Configurar Tendência')
    itembtnd = types.KeyboardButton('🆘Ajuda')
    itembtne = types.KeyboardButton('🤖Listar Bots')
    markup.row(itembtnc)
    markup.row(itembtnf)
    markup.row(itembtna,itembtnb)
    markup.row(itembtnd, itembtne)
    bot.send_message(message.chat.id, "Bot de Tendência de sinais", reply_markup=markup)

    @bot.message_handler(func=lambda message: message.text == '✅Ligar Tendência')
    def ligar_tendencia_sinal(message):
        global ligado
        ligado = True
        chat_id = message.chat.id
        dados_config_tend = config_tend[chat_id]
        dados_config_login = login_dict[chat_id]
        id_user = message.from_user.id
        dados_cli = cliente_permitido(str(id_user))
        if len(dados_cli) > 0:
            for data in dados_cli:
                id_telegram = int(data['id_telegram'])
                estado = int(data['estado'])
                plano = str(data['plano'])
                mes_espiracao = int(data['mes_espiracao'])
        
        def Martingale(valor, payout):
            lucro_esperado = valor * payout
            perca = float(valor)

            while True:
                if round(valor * payout, 2) > round(
                        abs(perca) + lucro_esperado, 2):
                    return round(valor, 2)
                    break
                valor += 0.01

        def Payout(par):
            API.subscribe_strike_list(par, 1)
            while True:
                d = API.get_digital_current_profit(par, 1)
                if d != False:
                    d = round(int(d) / 100, 2)
                    break
            API.unsubscribe_strike_list(par, 1)

            return d

        try:
                
            if (dados_config_login.email == None) or (dados_config_login.senha== None):

                    bot.send_message(message.chat.id,'🚨Erro verifique os dados de Login e tente novamente🚨')

            else:
                usuario = dados_config_login.email  # input("Digite o usuário da IQ Option: ")
                senha = dados_config_login.senha  #getpass.getpass(f"Digite a senha da IQ Option: ")
                API = IQ_Option(usuario, senha)
                print(API.connect())
        except:
                bot.send_message(message.chat.id, '🚨ERRO DE LOGIN🚨\n'
                                                  +'Verifique os seu dados de login da IQ option\n')

        if API.check_connect():
            bot.send_message(message.chat.id, '✅Conectado com sucesso!✅')
        else:
            bot.send_message(message.chat.id, '🚨Erro ao se conectar🚨')
            return

        try:

            conta = int(
                dados_config_tend.conta
            )  #int(input('\nEscolha em qual conta Operar:\n 1 - Treinamento\n 2 - REAL\n:: '))

            if int(conta) == 1:
                API.change_balance('PRACTICE')
            elif int(conta) == 2:
                API.change_balance('REAL')  # PRACTICE / REAL
            else:
                bot.send_message(message.chat.id,
                                 "❌Erro ao escolher o tipo de conta❌")
        except:
            bot.send_message(message.chat.id, "❌Erro, tente novamente❌")
            return

        while True:
            try:
                operacao = int(dados_config_tend.operacao)

                if operacao > 0 and operacao < 3: break
            except:
                bot.send_message(
                    message.chat.id,
                    '❌Opção de escolha entre digital e binária errada❌')
                break

        while True:
            try:
                timeframe = int(dados_config_tend.time_frame)
                break
            except:
                bot.send_message(message.chat.id, '❌Time frame incorreto❌')
                break

        par = str(dados_config_tend.par).upper()
        valor_entrada = float(dados_config_tend.valor_entrada)
        valor_entrada_b = float(valor_entrada)

        martingale = int(dados_config_tend.martingale)
        martingale += 1

        stop_loss = float(dados_config_tend.stop_loss)
        stop_gain = float(dados_config_tend.stop_gain)
        banca_inicial = API.get_balance()
        lucro = 0
        payout = Payout(par)
        bot.send_message(message.chat.id, "✅Aguarde os resultados das suas operações✅\n" +
                             "⏳⏳⏳⏳⏳⏳⏳⏳⏳⏳⏳⏳⏳⏳")
        timestamp_ = int(round(datetime.now().timestamp()))
        g=datetime.fromtimestamp(timestamp_).strftime('%H:%M')
        if (int(g.split(':')[1]) % int(timeframe))==0:

            while ligado:
                minutos = float(((datetime.now()).strftime('%M.%S'))[1:])
                entrar = True if (minutos >= 4.45 and minutos <= 5) or minutos >= 9.45 else False

                velas = API.get_candles(par.upper(), (int(timeframe) * 60), 20,  time())
                ultimo = round(velas[0]['close'], 3)
                primeiro = round(velas[-1]['close'], 3)

                diferenca = abs( round( ( (ultimo - primeiro)/primeiro ) * 100, 3) )
                if ultimo < primeiro and diferenca > 0.01:
                    dir = "call"
                elif ultimo > primeiro and diferenca > 0.01:
                    dir = "put"
               
                tendencia = "💹CALL" if ultimo < primeiro and diferenca > 0.01 else "🛑PUT" if ultimo > primeiro and diferenca > 0.01 else 'INDECISÃO' 
                utcmoment_naive = datetime.utcnow()
                utcmoment = utcmoment_naive.replace(tzinfo=pytz.utc)
                timezones = ['America/Sao_Paulo']
                for tz in timezones:
                    localDatetime = utcmoment.astimezone(pytz.timezone(tz))
                    
                f=localDatetime.strftime('%H:%M')
                e = noticias(par[3:6], f)
                n = noticias(par[0:3], f)
                if entrar:

                    if (e!=True or n!=True):
                        bot.send_message(message.chat.id,'❇====BOT DE TEDÊNCIA DE SINAL====❇'+
                            '\nParidade: '+str(par)+
                            '\n⏰: M'+str(timeframe)+
                            '\nPayout: '+str(int(Payout(par)*100))+'%'
                            '\nTendência da Próxima vela: '+str(tendencia))
                        valor_entrada = valor_entrada_b
                        for i in range(martingale):
                            
                            status, id = API.buy_digital_spot(par, valor_entrada, dir,timeframe) if operacao == 1 else API.buy(valor_entrada, par, dir, timeframe)

                            if status:
                                while True:
                                    try:
                                        status, valor = API.check_win_digital_v2(id) if operacao == 1 else API.check_win_v3(id)
                                    except:
                                        status = True
                                        valor = 0

                                    if status:
                                        valor = valor if valor > 0 else float('-' + str(abs(valor_entrada)))
                                        lucro += round(valor, 2)

                                        msg = '''
                                💹Resultado da operação💹\n

                                RESULTADO:''' + ('✅WIN' if valor > 0 else '🚨LOSS') + '''
                                LUCRO: 💲''' + str(round(valor, 2)) + '''\n
                                ''' + (str(i)+ ' ♻GALE' if i > 0 else '') + '''\n'''
                                        bot.send_message(message.chat.id,msg)

                                        valor_entrada = Martingale(valor_entrada, payout)

                                        if lucro <= float('-' +str(abs(stop_loss))):
                                            bot.send_message(message.chat.id,'🚨Stop Loss batido!🚨\n'+
                                                                            'Lucro obtido: -'+str(lucro)+
                                                                            '\nBanca inicial: '+str(banca_inicial)+
                                                                            '\nBanca atual: '+str(API.get_balance()))
                                            return
                                            break
                                        if lucro >= float(abs(stop_gain)):
                                            bot.send_message(message.chat.id,'✅Stop Gain Batido!✅\n'+
                                                                            'Lucro obtido: -'+str(lucro)+
                                                                            '\nBanca inicial: '+str(banca_inicial)+
                                                                            '\nBanca atual: '+str(API.get_balance()))
                                            return
                                            break

                                        if valor > 0: break

                                        break

                                if valor > 0: break

                            else:
                                bot.send_message(message.chat.id,'🚨ERRO AO REALIZAR OPERAÇÃO\n' +
                                    'O activo selecionado não se encontra aberto.')
                                break
                                return

                    else:
                        bot.send_message(message.chat.id,'❇====HORÁRIO DE NOTÍCIA====❇'+
                            '\nParidade: '+str(par)+
                            '\n⏰: M'+str(timeframe)+
                            '\nTendência da Próxima vela: '+str(tendencia)+
                            '\n🚨Cuidado não opere, o impacto da notícia é maior que 1🚨'
                            )

    try:
        @bot.message_handler(func=lambda message: message.text == '🔴Desligar Tendência')
        def desligar(message):
            global ligado
            ligado = False
            bot.send_message(message.chat.id,"🔴Bot de Tendência desligado!🔴")
            return
    except:
        pass

@bot.message_handler(func=lambda message: message.text == 'Estratégia Berman')
def bot_estrategia_berman(message):
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True, row_width=10)
    itembtnf = types.KeyboardButton('🔐Fazer Login')
    itembtna = types.KeyboardButton('✅Ligar EB')
    itembtnb = types.KeyboardButton('🔴Desligar EB')
    itembtnc = types.KeyboardButton('⚙Configurar EB')
    itembtnd = types.KeyboardButton('🆘Ajuda')
    itembtne = types.KeyboardButton('🤖Listar Bots')
    markup.row(itembtnc)
    markup.row(itembtnf)
    markup.row(itembtna, itembtnb)
    markup.row(itembtnd, itembtne)
    bot.send_message(message.chat.id,"Bot de Estratégia Berman",reply_markup=markup)

@bot.message_handler(func=lambda message: message.text == 'Catalogador')
def bot_catalogador(message):
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True, row_width=10)
    itembtnf = types.KeyboardButton('🔐Fazer Login')
    itembtna = types.KeyboardButton('✅Ligar Catalogador')
    itembtnc = types.KeyboardButton('⚙Configurar Catalogador')
    itembtnd = types.KeyboardButton('🆘Ajuda')
    itembtne = types.KeyboardButton('🤖Listar Bots')
    markup.row(itembtnc)
    markup.row(itembtnf)
    markup.row(itembtna)
    markup.row(itembtnd, itembtne)
    bot.send_message(message.chat.id,"Catalogação de Sinais",reply_markup=markup)

    @bot.message_handler(func=lambda message: message.text == '✅Ligar Catalogador')
    def ligar_catalogador(message):
        chat_id = message.chat.id
        dados_config_cat = config_catalogador[chat_id]
        dados_config_login = login_dict[chat_id]
        init(autoreset=True)
        try:
                
            if (dados_config_login.email == None) or (dados_config_login.senha== None):

                    bot.send_message(message.chat.id,'🚨Erro verifique os dados de Login e tente novamente🚨')

            else:
                usuario = dados_config_login.email  # input("Digite o usuário da IQ Option: ")
                senha = dados_config_login.senha  #getpass.getpass(f"Digite a senha da IQ Option: ")
                API = IQ_Option(usuario, senha)
                print(API.connect())
        except:
                bot.send_message(message.chat.id, '🚨ERRO DE LOGIN🚨\n'
                                                  +'Verifique os seu dados de login da IQ option\n')

        if API.check_connect():
            bot.send_message(message.chat.id, '✅Conectado com sucesso!✅')
        else:
            bot.send_message(message.chat.id, '🚨Erro ao se conectar🚨')
            return

        def cataloga(par, dias, prct_call, prct_put, timeframe):
            data = []
            datas_testadas = []
            time_ = time()
            sair = False
            while sair == False:
                velas = API.get_candles(par, (timeframe * 60), 3000, time_)
                velas.reverse()
                
                for x in velas:	
                    if datetime.fromtimestamp(x['from']).strftime('%Y-%m-%d') not in datas_testadas: 
                        datas_testadas.append(datetime.fromtimestamp(x['from']).strftime('%Y-%m-%d'))
                        
                    if len(datas_testadas) <= dias:
                        x.update({'cor': 'verde' if x['open'] < x['close'] else 'vermelha' if x['open'] > x['close'] else 'doji'})
                        data.append(x)
                    else:
                        sair = True
                        break
                        
                time_ = int(velas[-1]['from'] - 1)

            analise = {}
            for velas in data:
                horario = datetime.fromtimestamp(velas['from']).strftime('%H:%M')
                if horario not in analise : analise.update({horario: {'verde': 0, 'vermelha': 0, 'doji': 0, '%': 0, 'dir': ''}})	
                analise[horario][velas['cor']] += 1
                
                try:
                    analise[horario]['%'] = round(100 * (analise[horario]['verde'] / (analise[horario]['verde'] + analise[horario]['vermelha'] + analise[horario]['doji'])))
                except:
                    pass
            
            for horario in analise:
                if analise[horario]['%'] > 50 : analise[horario]['dir'] = 'CALL'
                if analise[horario]['%'] < 50 : analise[horario]['%'],analise[horario]['dir'] = 100 - analise[horario]['%'],'PUT '
            
            return analise

        timeframe = int(dados_config_cat.time_frame)

        dias = int(dados_config_cat.dias)

        porcentagem = int(dados_config_cat.porcentagem)

        martingale = dados_config_cat.martingale

        prct_call = abs(porcentagem)
        prct_put = abs(100 - porcentagem)
        P = API.get_all_open_time()
        bot.send_message(message.chat.id,'Catalogando, por favor aguarde...')
        catalogacao = {}
        for par in P['digital']:
            if P['digital'][par]['open'] == True:
                catalogacao.update({par: cataloga(par, dias, prct_call, prct_put, timeframe)})	

                for par in catalogacao:
                    for horario in sorted(catalogacao[par]):
                        if martingale.strip() != '':					
                        
                            mg_time = horario
                            soma = {'verde': catalogacao[par][horario]['verde'], 'vermelha': catalogacao[par][horario]['vermelha'], 'doji': catalogacao[par][horario]['doji']}
                            
                            for i in range(int(martingale)):

                                catalogacao[par][horario].update({'mg'+str(i+1): {'verde': 0, 'vermelha': 0, 'doji': 0, '%': 0} })

                                mg_time = str(datetime.strptime((datetime.now()).strftime('%Y-%m-%d ') + str(mg_time), '%Y-%m-%d %H:%M') + timedelta(minutes=timeframe))[11:-3]
                                
                                if mg_time in catalogacao[par]:
                                    catalogacao[par][horario]['mg'+str(i+1)]['verde'] += catalogacao[par][mg_time]['verde'] + soma['verde']
                                    catalogacao[par][horario]['mg'+str(i+1)]['vermelha'] += catalogacao[par][mg_time]['vermelha'] + soma['vermelha']
                                    catalogacao[par][horario]['mg'+str(i+1)]['doji'] += catalogacao[par][mg_time]['doji'] + soma['doji']
                                    
                                    catalogacao[par][horario]['mg'+str(i+1)]['%'] = round(100 * (catalogacao[par][horario]['mg'+str(i+1)]['verde' if catalogacao[par][horario]['dir'] == 'CALL' else 'vermelha'] / (catalogacao[par][horario]['mg'+str(i+1)]['verde'] + catalogacao[par][horario]['mg'+str(i+1)]['vermelha'] + catalogacao[par][horario]['mg'+str(i+1)]['doji']) ) )
                                    
                                    soma['verde'] += catalogacao[par][mg_time]['verde']
                                    soma['vermelha'] += catalogacao[par][mg_time]['vermelha']
                                    soma['doji'] += catalogacao[par][mg_time]['doji']
                                else:						
                                    catalogacao[par][horario]['mg'+str(i+1)]['%'] = 'N/A'
                
        for par in catalogacao:
            for horario in sorted(catalogacao[par]):
                ok = False		
                
                if catalogacao[par][horario]['%'] >= porcentagem:
                    ok = True
                else:
                    for i in range(int(martingale)):
                        if catalogacao[par][horario]['mg'+str(i+1)]['%'] >= porcentagem:
                            ok = True
                            break
                
                if ok == True:
                
                    msg = par+' - '+horario+' - '+('🔴' if catalogacao[par][horario]['dir'] == 'PUT ' else '✅') + catalogacao[par][horario]['dir'] + ' - ' + str(catalogacao[par][horario]['%']) + '%'
                    
                    if martingale.strip() != '':
                        for i in range(int(martingale)):
                            if str(catalogacao[par][horario]['mg'+str(i+1)]['%']) != 'N/A':
                                msg += ' | MG ' + str(i+1) + ' - ' + str(catalogacao[par][horario]['mg'+str(i+1)]['%']) + '%'
                            else:
                                msg += ' | MG ' + str(i+1) + ' - N/A' 
                                
                    open('lista_catalogada_{}.txt'.format(message.chat.id), 'a').write(horario + ',' + par + ',' + catalogacao[par][horario]['dir'].strip() + '\n')

                    hora_cat = horario.split(':')
                    hora_atual=datetime.now().strftime('%H:%M').split(':')
                    f=datetime.now().strftime('%H:%M')
                    if (int(hora_cat[0])==int(hora_atual[0])) or (int(hora_cat[0])>int(hora_atual[0])) and (noticias(par[3:6], f)!=True or noticias(par[0:3], f)!=True):
                        rs = horario + ',' + par + ',' + catalogacao[par][horario]['dir'].strip()
                        bot.send_message(message.chat.id,rs)

@bot.message_handler(func=lambda message: message.text == 'Sinais ao Vivo')
def bot_indicadores_tecnicos(message):
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True, row_width=10)
    itembtnf = types.KeyboardButton('🔐Fazer Login')
    itembtna = types.KeyboardButton('✅Ligar Sinais')
    itembtnb = types.KeyboardButton('🔴Desligar Sinais')
    itembtnc = types.KeyboardButton('⚙Configurar Sinais ao Vivo')
    itembtnd = types.KeyboardButton('🆘Ajuda')
    itembtne = types.KeyboardButton('🤖Listar Bots')
    markup.row(itembtnc)
    markup.row(itembtnf)
    markup.row(itembtna, itembtnb)
    markup.row(itembtnd, itembtne)
    bot.send_message(message.chat.id,"🌡Tedência por Termómetro🌡", reply_markup=markup)

    @bot.message_handler(func=lambda message: message.text == '✅Ligar Sinais')
    def ligar_termometro(message):
        global ligado
        ligado = True
        chat_id = message.chat.id
        dados_config_login = login_dict[chat_id]
        dados_config_term = config_term[chat_id]

        try:       
            try:
                    
                if (dados_config_login.email == None) or (dados_config_login.senha== None) or (dados_config_login.email == '') or (dados_config_login.senha== ''):

                        bot.send_message(message.chat.id,'🚨Erro verifique os dados de Login e tente novamente🚨')

                else:
                    usuario = dados_config_login.email  # input("Digite o usuário da IQ Option: ")
                    senha = dados_config_login.senha  #getpass.getpass(f"Digite a senha da IQ Option: ")
                    API = IQ_Option(usuario, senha)
                    print(API.connect())
            except:
                    bot.send_message(message.chat.id, '🚨ERRO DE LOGIN🚨\n'
                                                    +'Verifique os seu dados de login da IQ option\n')
                
            if API.check_connect():
                bot.send_message(message.chat.id, '✅Conectado com sucesso!✅')
            else:
                bot.send_message(message.chat.id, '🚨Erro ao se conectar🚨')
                return

            def bin_payout(par, timeframe):
                par = par.upper()
                tb = API.get_all_profit()
                API.subscribe_strike_list(par, timeframe)
                tentativas = 0
                while True:
                    d = API.get_digital_current_profit(par, timeframe)
                    if d != False:
                        d = int(d)
                        break                
                API.unsubscribe_strike_list(par, timeframe)
                
                payout = {'binario': 0, 'digital': d}
                vl = int(100 * tb[par]['binary'])
                
                return vl

            def Payout(par):
                API.subscribe_strike_list(par, 1)
                while True:
                    d = API.get_digital_current_profit(par, 1)
                    if d != False:
                        d = round(int(d) / 100, 2)
                        break
                API.unsubscribe_strike_list(par, 1)

                return (d*100)

            par = str(dados_config_term.par).upper() # trader[1] # paridade
            timec = int(dados_config_term.timeframe)#int(trader[2]) # time candle 1 5 15 min
            oscdif = 30
            para_automaticamente = 0
            while ligado:
                # Info Oscillators
                oscHold = 0 
                oscShell = 0
                oscBuy = 0
                # Info Moving Averages
                mavHold = 0 
                mavShell = 0
                mavBuy = 0
                #
                sumHold = 0 
                sumShell = 0
                sumBuy = 0
                try:
                    indicators = API.get_technical_indicators(par)
                except:
                    bot.send_message(message.chat.id,'🚨Upsi, sua paridade não é elegível para ser usada neste Bot.🚨')
                    break

                for data in indicators:   
                    if int(data['candle_size'])==int(timec*60):
                        if data['group'] == 'OSCILLATORS':
                            oscHold = oscHold + str(data).count('hold')
                            oscShell = oscShell + str(data).count('sell')
                            oscBuy = oscBuy + str(data).count('buy')                    
                        if data['group'] == 'MOVING AVERAGES':
                            mavHold = mavHold + str(data).count('hold')
                            mavShell = mavShell + str(data).count('sell')
                            mavBuy = mavBuy + str(data).count('buy')    
                        if data['group'] == 'SUMMARY':
                            sumHold = sumHold + str(data).count('hold')
                            sumShell = sumShell + str(data).count('sell')
                            sumBuy = sumBuy + str(data).count('buy')   
                timestamp_ = int(round(datetime.now().timestamp()))
                f=datetime.fromtimestamp(timestamp_).strftime('%H:%M')
                if noticias(par[3:6], f)==True or noticias(par[0:3], f)==True:
                    pass     
                elif noticias(par[3:6], f)=='Notícia' or noticias(par[0:3], f)=='Notícia':         
                    if oscdif != mavBuy:
                        oscdif = mavBuy
                        para_automaticamente=para_automaticamente+1
                        #if para_automaticamente==10: break
                        if (int(f.split(':')[1]) % int(timec))==0:

                            if ((int(mavBuy)+int(oscBuy)+int(sumBuy)) > (int(mavShell)+int(oscShell)+int(sumShell))) and  ((int(mavBuy)+int(oscBuy)+int(sumBuy)) > (int(mavHold)+int(oscHold)+int(sumHold))):
                                #if msgid > 0: bot.delete_message(session.chat.id, msgid) ⏰%Y-%m-%d
                                message = bot.send_message(message.chat.id, 
                                '✅## Tendência do Sinal ##✅\n\n'+
                                '[DATA: '+str(datetime.now().strftime('%Y-%m-%d'))+']'+
                                '\n===========================\n'+
                                '⏰'+str(f)+
                                '\n✅CALL'+
                                '\n## PAR: '+str(par).upper()+' | EXP: M'+str(timec)+'##\n\n'+
                                '🚨Horario de notícia cuidado🚨\n'+
                                'IMPACTO: 1'+
                                '\nPara mais informações consute:\n'+
                                'http://br.investing.com/economic-calendar/')
                
                            elif ((int(mavShell)+int(oscShell)+int(sumShell)) > (int(mavBuy)+int(oscBuy)+int(sumBuy))) and  ((int(mavShell)+int(oscShell)+int(sumShell)) > (int(mavHold)+int(oscHold)+int(sumHold))):
                                #if msgid > 0: bot.delete_message(session.chat.id, msgid) ⏰%Y-%m-%d
                                message = bot.send_message(message.chat.id, 
                                '✅## Tendência do Sinal ##✅\n\n'+
                                '[DATA: '+str(datetime.now().strftime('%Y-%m-%d'))+']'+
                                '\n===========================\n'+
                                '⏰'+str(f)+
                                '\n🔴PUT'+
                                '\n## PAR: '+str(par).upper()+' | EXP: M'+str(timec)+'##\n\n'+
                                '🚨Horario de notícia cuidado🚨\n'+
                                'IMPACTO: 1'+
                                '\nPara mais informações consute:\n'+
                                'http://br.investing.com/economic-calendar/')
                            elif ((int(mavHold)+int(oscHold)+int(sumHold))>(int(mavBuy)+int(oscBuy)+int(sumBuy))) and ((int(mavHold)+int(oscHold)+int(sumHold))>(int(mavShell)+int(oscShell)+int(sumShell))):
                                #if msgid > 0: bot.delete_message(session.chat.id, msgid) ⏰%Y-%m-%d
                                message = bot.send_message(message.chat.id, 
                                '✅## Tendência do Sinal ##✅\n\n'+
                                '[DATA: '+str(datetime.now().strftime('%Y-%m-%d'))+']'+
                                '\n===========================\n'+
                                '⏰'+str(f)+
                                '\n🚨INDECISÃO--> NÃO ENTRAR'+
                                '\n## PAR: '+str(par).upper()+' | EXP: M'+str(timec)+'##\n\n'+
                                '🚨Horario de notícia cuidado🚨\n'+
                                'IMPACTO: 1'+
                                '\nPara mais informações consute:\n'+
                                'http://br.investing.com/economic-calendar/')

                else:
                    if oscdif != mavBuy:
                        oscdif = mavBuy
                        para_automaticamente=para_automaticamente+1
                        #if para_automaticamente==10: break
                        if (int(f.split(':')[1]) % int(timec))==0:

                            if ((int(mavBuy)+int(oscBuy)+int(sumBuy)) > (int(mavShell)+int(oscShell)+int(sumShell))) and  ((int(mavBuy)+int(oscBuy)+int(sumBuy)) > (int(mavHold)+int(oscHold)+int(sumHold))):
                                #if msgid > 0: bot.delete_message(session.chat.id, msgid) ⏰%Y-%m-%d
                                message = bot.send_message(message.chat.id, 
                                '✅## Tendência do Sinal ##✅\n\n'+
                                '[DATA: '+str(datetime.now().strftime('%Y-%m-%d'))+']'+
                                '\n===========================\n'+
                                '⏰'+str(f)+
                                '\n✅CALL'+
                                '\n## PAR: '+str(par).upper()+' | EXP: M'+str(timec)+'##\n\n')
                
                            elif ((int(mavShell)+int(oscShell)+int(sumShell)) > (int(mavBuy)+int(oscBuy)+int(sumBuy))) and  ((int(mavShell)+int(oscShell)+int(sumShell)) > (int(mavHold)+int(oscHold)+int(sumHold))):
                                #if msgid > 0: bot.delete_message(session.chat.id, msgid) ⏰%Y-%m-%d
                                message = bot.send_message(message.chat.id, 
                                '✅## Tendência do Sinal ##✅\n\n'+
                                '[DATA: '+str(datetime.now().strftime('%Y-%m-%d'))+']'+
                                '\n===========================\n'+
                                '⏰'+str(f)+
                                '\n🔴PUT'+
                                '\n## PAR: '+str(par).upper()+' | EXP: M'+str(timec)+'##\n\n')
                            elif ((int(mavHold)+int(oscHold)+int(sumHold))>(int(mavBuy)+int(oscBuy)+int(sumBuy))) and ((int(mavHold)+int(oscHold)+int(sumHold))>(int(mavShell)+int(oscShell)+int(sumShell))):
                                #if msgid > 0: bot.delete_message(session.chat.id, msgid) ⏰%Y-%m-%d
                                message = bot.send_message(message.chat.id, 
                                '✅## Tendência do Sinal ##✅\n\n'+
                                '[DATA: '+str(datetime.now().strftime('%Y-%m-%d'))+']'+
                                '\n===========================\n'+
                                '⏰'+str(f)+
                                '\n🚨INDECISÃO--> NÃO ENTRAR'+
                                '\n## PAR: '+str(par).upper()+' | EXP: M'+str(timec)+'##\n\n')

        except:
            bot.send_message(message.chat.id,'🚨Upsi, verifique sua configuração.🚨\n'
                                             'Obs.: OTC não é elegível para este Bot')
    
    try:
        @bot.message_handler(func=lambda message: message.text == '🔴Desligar Sinais')
        def desligar_terM(message):
            global ligado
            ligado = False
            bot.send_message(message.chat.id,"🔴Sinais ao Vivo desligado!🔴")
            return
    except:
        pass
                    
@bot.message_handler(func=lambda message: message.text == 'Scalper')
def bot_scalper(message):
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True, row_width=10)
    itembtnf = types.KeyboardButton('🔐Fazer Login')
    itembtna = types.KeyboardButton('✅Ligar Scalper')
    itembtnb = types.KeyboardButton('🔴Desligar Scalper')
    itembtnc = types.KeyboardButton('⚙Configurar Scalper')
    itembtnd = types.KeyboardButton('🆘Ajuda')
    itembtne = types.KeyboardButton('🤖Listar Bots')
    markup.row(itembtnc)
    markup.row(itembtnf)
    markup.row(itembtna, itembtnb)
    markup.row(itembtnd, itembtne)
    bot.send_message(message.chat.id, "Bot de Scalper", reply_markup=markup)

@bot.message_handler(func=lambda message: message.text == '🔙VOLTAR')
def voltar(message):
    id_user = message.from_user.id
    dados_cli = cliente_permitido(str(id_user))
    if len(dados_cli) > 0:
        for data in dados_cli:
            id_telegram = int(data['id_telegram'])
            estado = int(data['estado'])
            plano = str(data['plano'])
            mes_espiracao = int(data['mes_espiracao'])
    if estado == 1 and plano == "admin":
        markup = types.ReplyKeyboardMarkup(resize_keyboard=True, row_width=10)
        itembtna = types.KeyboardButton('🛂Prestar Suporte')
        itembtnb = types.KeyboardButton('📚Dados do Usuário')
        itembtnc = types.KeyboardButton('👥Usuários Ativos')
        itembtnd = types.KeyboardButton('📨Pacotes disponíveis')
        itembtne = types.KeyboardButton('🔐Verificação de Usuário')
        itembtng = types.KeyboardButton('🤖Listar Bots')
        markup.row(itembtna, itembtnb)
        markup.row(itembtnc, itembtnd)
        markup.row(itembtne)
        markup.row(itembtng)
        bot.send_message(message.chat.id,"=======ROBÔ ALPHA=======",reply_markup=markup)

    elif estado == 1 and plano == "super_admin":

            markup = types.ReplyKeyboardMarkup(resize_keyboard=True, row_width=10)
            itembtna = types.KeyboardButton('✅Add usuário')
            itembtnb = types.KeyboardButton('⛔Excluir usuário')
            itembtnc = types.KeyboardButton('📖Listar usuários')
            itembtnd = types.KeyboardButton('📨Alterar Pacote')
            itembtne = types.KeyboardButton('📅Alterar data de expiração')
            itembtnf = types.KeyboardButton('🚫Restringir usuário')
            itembtng = types.KeyboardButton('🤖Listar Bots')
            markup.row(itembtna, itembtnb)
            markup.row(itembtnc, itembtnd)
            markup.row(itembtne)
            markup.row(itembtnf, itembtng)
            bot.send_message(message.chat.id,"=======ROBÔ ALPHA=======",reply_markup=markup)

@bot.message_handler(func=lambda message: message.text == '🔐Fazer Login')
def fazer_login(message):
    msg = bot.reply_to(message,
                       "🔐Entrar na iq Option🔐\n" + "Digite seu Email:")
    bot.register_next_step_handler(msg, process_email_step)

def process_email_step(message):
    try:
        chat_id = message.chat.id
        email = message.text
        if (email == None) or (email == ''):
            msg = bot.reply_to(message,
                               '❌O campo e-mail não pode estar vazio❌')
            bot.register_next_step_handler(msg, process_email_step)
            return
        dados = login(email)
        login_dict[chat_id] = dados
        msg = bot.reply_to(message, '🔑Digite sua Senha🔑')
        bot.register_next_step_handler(msg, process_senha_step)
    except Exception as e:
        bot.reply_to(message,
                     '❌Upsi, ocorreu um erro, tente novamente /start❌')

def process_senha_step(message):
    try:
        chat_id = message.chat.id
        senha = message.text
        if (senha == None) or (senha == ''):
            msg = bot.reply_to(message, '❌O campo senha não pode estar vazio❌')
            bot.register_next_step_handler(msg, process_senha_step)
            return
        dados = login_dict[chat_id]
        dados.senha = senha
        try:
            chat_id = message.chat.id
            dados = login_dict[chat_id]
            id_user = message.from_user.id
            dados_cli = cliente_permitido(str(id_user))
            if len(dados_cli) > 0:
                for data in dados_cli:
                    id_telegram = int(data['id_telegram'])
                    estado = int(data['estado'])

            if estado == 1 and id_telegram==chat_id:

                bot.send_message(message.chat.id, "✅Dados salvos com sucesso✅")

            elif estado != 1 or id_telegram==chat_id:
                dados.email = None
                dados.senha = None
        except:
            bot.reply_to(message, 'Email/Senha não foram salvos! \nOpção inválida tente novamente')
    except:
        bot.reply_to(message, '❌Upsi, houve um erro, tente novamente➡ /start')

@bot.message_handler(func=lambda message: message.text == '📖Adicionar Sinais')
def add_lista(message):
        msg=bot.reply_to(message, "✅Digite sua lista de sinais✅"
                                         +"\nPara tal tenha em conta o seguinte formato:\n"+
                                         "07:25,EURUSD-OTC,call,5 ou 07:25,EURUSD,put,1")
        bot.register_next_step_handler(msg, process_add_lista_step)

def process_add_lista_step(message):
        try:
            lista = message.text
            if lista != '':
                git_file ='{}.txt'.format(message.chat.id)
                if git_file in content:
                    repo.update_file(git_file, "committing files", lista)
                else:
                    repo.create_file(git_file, "committing files", lista)
            else:
                bot.reply_to(message, 'Envie pelo menos um sinal')
            bot_lista_sinais(message)
        except Exception as e:
            bot.reply_to(message, '❌Upsi, houve um erro, tente novamente➡ /start')

@bot.message_handler(func=lambda message: message.text == '⚙Configurar Sinais ao Vivo')
def Configurar_Termometro(message):
        msg=bot.reply_to(message,"✅Dgite a Paridade a analisar✅"
                                 +"\nObs: O termómetro funciona apenas em mercado normal")
        bot.register_next_step_handler(msg, process_add_par_term)

def process_add_par_term(message):
        try:
            chat_id = message.chat.id
            par = message.text
            if par.isdigit() or par == '':
                msg = bot.reply_to(message,'❌Opção inválida, escolha por Ex.: EURUSD')
                bot.register_next_step_handler(msg, process_add_par_term)
                return
            dados = termometro_config(par)
            config_term[chat_id] = dados
            msg = bot.reply_to(message, 'Defina o Time Frame')
            bot.register_next_step_handler(msg, process_add_time_term)
        except Exception as e:
            bot.reply_to(message, '❌Upsi, houve um erro, tente novamente➡ /start')

def process_add_time_term(message):
    
    chat_id = message.chat.id
    time_frame = message.text
    if (not time_frame.isdigit()):
            msg = bot.reply_to(message,'❌Opção inválida, escolha: \n1 para M1, 5 para M5 ou 15 para M15:')
            bot.register_next_step_handler(msg, process_add_time_term)
            return
    dados = config_term[chat_id]
    dados.timeframe = time_frame
    bot.send_message(message.chat.id, 'Dados salvos com sucesso\n'+
                '\nParidade: '+dados.par+
                '\nTime Frame: '+dados.timeframe+
                '\n\nCaso queiras retificar clique em ⚙Configurar Termómetro')
        
@bot.message_handler(func=lambda message: message.text == '⚙Configurar Bot de MHI')
def config_do_mhi(message):
        msg = bot.reply_to(
            message,"Escolha em qual conta Operar:\n 1 - Treinamento\n 2 - REAL:")
        bot.register_next_step_handler(msg, process_conta_step)

def process_conta_step(message):
        try:
            chat_id = message.chat.id
            conta = message.text
            if (not conta.isdigit()):
                msg = bot.reply_to(
                    message,
                    '❌Opção inválida, escolha: \n1 para conta de Treinamento \n2 para Real'
                )
                bot.register_next_step_handler(msg, process_conta_step)
                return
            dados = mhi_config(conta)
            config_mhi[chat_id] = dados
            msg = bot.reply_to(message,'Desejas operar na\n  1 - Digital\n  2 - Binaria:')
            bot.register_next_step_handler(msg, process_operacao_step)
        except Exception as e:
            bot.reply_to(message,
                        '❌Upsi, ocorreu um erro, tente novamente /start❌')

def process_operacao_step(message):
        try:
            chat_id = message.chat.id
            operacao = message.text
            if (not operacao.isdigit()):
                msg = bot.reply_to(
                    message,
                    '❌Opção inválida, escolha: \n1 para Digital \n2 para Binaria:')
                bot.register_next_step_handler(msg, process_operacao_step)
                return
            dados = config_mhi[chat_id]
            dados.operacao = operacao
            msg = bot.reply_to(
                message,
                'Desejas operar a favor da\n  1 - Minoria\n  2 - Maioria:')
            bot.register_next_step_handler(msg, process_tipo_mhi_step)
        except Exception as e:
            bot.reply_to(message, '❌Upsi, houve um erro, tente novamente➡ /start')

def process_tipo_mhi_step(message):
        try:
            chat_id = message.chat.id
            tipo_mhi = message.text
            if (not tipo_mhi.isdigit()):
                msg = bot.reply_to(
                    message,
                    '❌Opção inválida, escolha: \n1 para Minoria \n2 para Maioria:')
                bot.register_next_step_handler(msg, process_tipo_mhi_step)
                return
            dados = config_mhi[chat_id]
            dados.tipo_mhi = tipo_mhi
            msg = bot.reply_to(
                message, 'Selecione o Time Frame\n' +
                'Obs.: o Bot opera apenas em M1, M5 e M15\n' +
                'Digite 1 para M1, 5 para M5 e 15 para M15')
            bot.register_next_step_handler(msg, process_time_frame_step)
        except Exception as e:
            bot.reply_to(message, '❌Upsi, houve um erro, tente novamente➡ /start')

def process_time_frame_step(message):
        try:
            chat_id = message.chat.id
            time_frame = message.text
            if (not time_frame.isdigit()):
                msg = bot.reply_to(
                    message,
                    '❌Opção inválida, escolha: \n1 para M1, 5 para M5 ou 15 para M15:'
                )
                bot.register_next_step_handler(msg, process_time_frame_step)
                return
            dados = config_mhi[chat_id]
            dados.time_frame = time_frame
            msg = bot.reply_to(
                message, 'Digite a paradidade por onde operar\n' +
                'Lembre-se de selecionar apenas paridades abertas\n' +
                'Ex.: EURUSD ou então EURUSD-OTC para mercado OTC:')
            bot.register_next_step_handler(msg, process_par_step)
        except Exception as e:
            bot.reply_to(message, '❌Upsi, houve um erro, tente novamente➡ /start')

def process_par_step(message):
        try:
            chat_id = message.chat.id
            par = message.text
            if par.isdigit() or par == '':
                msg = bot.reply_to(message,'❌Opção inválida, escolha por Ex.: EURUSD')
                bot.register_next_step_handler(msg, process_par_step)
                return
            dados = config_mhi[chat_id]
            dados.par = par
            msg = bot.reply_to(message, 'Digite o valor de entrada')
            bot.register_next_step_handler(msg, process_valor_entrada_step)
        except Exception as e:
            bot.reply_to(message, '❌Upsi, houve um erro, tente novamente➡ /start')

def process_valor_entrada_step(message):
        try:
            chat_id = message.chat.id
            valor_entrada = message.text
            if float(valor_entrada) < 1:
                msg = bot.reply_to(message,
                                '❌O valor de entrada não pode ser menor que 1')
                bot.register_next_step_handler(msg, process_valor_entrada_step)
                return
            dados = config_mhi[chat_id]
            dados.valor_entrada = valor_entrada
            msg = bot.reply_to(
                message, 'Indique a quantidade de Martingale\n' +
                'Coloque 0 caso não queiras utilizá-lo\n' +
                'Aconcelho indicar no máximo 2 níveis de Martingale')
            bot.register_next_step_handler(msg, process_martingale_step)
        except Exception as e:
            bot.reply_to(message, '❌Upsi, houve um erro, tente novamente➡ /start')

def process_martingale_step(message):
        try:
            chat_id = message.chat.id
            martingale = message.text
            if (not martingale.isdigit()):
                msg = bot.reply_to(
                    message, '❌Opção inválida, digite apenas número inteiros')
                bot.register_next_step_handler(msg, process_martingale_step)
                return
            dados = config_mhi[chat_id]
            dados.martingale = martingale
            msg = bot.reply_to(message, 'Digite o valor do stop Loss')
            bot.register_next_step_handler(msg, process_stop_loss_step)
        except Exception as e:
            bot.reply_to(message, '❌Upsi, houve um erro, tente novamente➡ /start')

def process_stop_loss_step(message):
        try:
            chat_id = message.chat.id
            stop_loss = message.text
            if float(stop_loss) < 1:
                msg = bot.reply_to(
                    message,
                    '❌Opção inválida, digite apenas números e maior ou igual a 1')
                bot.register_next_step_handler(msg, process_stop_loss_step)
                return
            dados = config_mhi[chat_id]
            dados.stop_loss = stop_loss
            msg = bot.reply_to(message, 'Digite o valor do Stop Gain')
            bot.register_next_step_handler(msg, process_stop_gain_step)
        except Exception as e:
            bot.reply_to(message, '❌Upsi, houve um erro, tente novamente➡ /start')

def process_stop_gain_step(message):
        try:
            chat_id = message.chat.id
            stop_gain = message.text
            if float(stop_gain) < 1:
                msg = bot.reply_to(message, '❌Opção inválida, digite apenas número e maior que 0')
                bot.register_next_step_handler(msg, process_stop_gain_step)
                return
            dados = config_mhi[chat_id]
            dados.stop_gain = stop_gain
            markup = types.ReplyKeyboardMarkup(resize_keyboard=True, row_width=10)
            markup.add('✅Guardar', 'Alterar')
            msg = bot.reply_to(message,'✅Desejas guardar os dados?✅',reply_markup=markup)
            bot.register_next_step_handler(msg, process_guardar_mhi_step)
        except Exception as e:
            bot.reply_to(message, '❌Upsi, houve um erro, tente novamente➡ /start')

def process_guardar_mhi_step(message):
        try:
            chat_id = message.chat.id
            salvar = message.text
            dados = config_mhi[chat_id]
            if salvar == u'✅Guardar':

                bot.send_message(message.chat.id, '✅Dados inseridos com sucesso✅' +
                    '\nTipo de Conta: '+('Real' if int(dados.conta)==2 else 'Treinamento')
                    +'\nOperar na: '+('Digital' if int(dados.operacao)==1 else 'Binária') 
                    +'\nTipo de MHI: '+('Minoria' if int(dados.tipo_mhi)==1 else 'Maioria')
                    +'\nTime Frame: M' + str(dados.time_frame) 
                    +'\nParidade: '+str(dados.par)
                    +'\nValor de entrada: '+str(dados.valor_entrada) 
                    +'\nNível de Martingale: '+str(dados.martingale) 
                    +'\nStop Loss: '+str(dados.stop_loss)
                    +'\nStop Gain: '+str(dados.stop_gain))

                bot_mhi(message)

            elif salvar == u'Alterar':
                msg = 'Escolha em qual conta Operar:\n 1 - Treinamento\n 2 - REAL:'
                bot.register_next_step_handler(msg, process_conta_step)
            else:
                dados.conta = None
                dados.operacao = None
                dados.tipo_mhi = None
                dados.time_frame == None
                dados.par = None
                dados.valor_entrada = None
                dados.martingale = None
                dados.stop_loss == None
                dados.stop_gain = None
                bot_mhi(message)
        except Exception as e:
            bot.reply_to(message, '❌Upsi, houve um erro, tente novamente➡ /start')

@bot.message_handler(func=lambda message: message.text == '⚙Configurar Bot de Sinais')
def config_da_lista_de_sinais(message):
        msg = bot.reply_to(message,"Escolha em qual conta Operar:\n 1 - Treinamento\n 2 - REAL:")
        bot.register_next_step_handler(msg, process_conta_sinais_step)

def process_conta_sinais_step(message):
        try:
            chat_id = message.chat.id
            conta = message.text
            if (not conta.isdigit()):
                msg = bot.reply_to(message,'❌Opção inválida, escolha: \n1 para conta de Treinamento \n2 para Real')
                bot.register_next_step_handler(msg, process_conta_sinais_step)
                return
            dados = lista_sinais_config(conta)
            config_lista_sinais[chat_id] = dados
            msg = bot.reply_to(message,'Desejas operar na\n  1 - Digital\n  2 - Binaria:')
            bot.register_next_step_handler(msg, process_operacao_sinais_step)
        except Exception as e:
            bot.reply_to(message,
                        '❌Upsi, ocorreu um erro, tente novamente /start❌')

def process_operacao_sinais_step(message):
        try:
            chat_id = message.chat.id
            operacao = message.text
            if (not operacao.isdigit()):
                msg = bot.reply_to(message,'❌Opção inválida, escolha: \n1 para Digital \n2 para Binaria:')
                bot.register_next_step_handler(msg, process_operacao_sinais_step)
                return
            dados = config_lista_sinais[chat_id]
            dados.operacao = operacao
            msg = bot.reply_to(message,'Digite o valor de entrada')
            bot.register_next_step_handler(msg, process_valor_entrada_sinais_step)
        except Exception as e:
            bot.reply_to(message, '❌Upsi, houve um erro, tente novamente➡ /start')

def process_valor_entrada_sinais_step(message):
        try:
            chat_id = message.chat.id
            valor_entrada = message.text
            if float(valor_entrada) < 1:
                msg = bot.reply_to(message,'❌O valor de entrada não pode ser menor que 1')
                bot.register_next_step_handler(msg, process_valor_entrada_sinais_step)
                return
            dados = config_lista_sinais[chat_id]
            dados.valor_entrada = valor_entrada
            msg = bot.reply_to(message, 'Indique a quantidade de Martingale\n' +
                'Coloque 0 caso não queiras utilizá-lo\n' +
                'Aconcelho indicar no máximo 2 níveis de Martingale')
            bot.register_next_step_handler(msg, process_martingale_sinais_step)
        except Exception as e:
            bot.reply_to(message, '❌Upsi, houve um erro, tente novamente➡ /start')

def process_martingale_sinais_step(message):
        try:
            chat_id = message.chat.id
            martingale = message.text
            if (not martingale.isdigit()):
                msg = bot.reply_to(message, '❌Opção inválida, digite apenas número inteiros')
                bot.register_next_step_handler(msg, process_martingale_sinais_step)
                return
            dados = config_lista_sinais[chat_id]
            dados.martingale = martingale
            msg = bot.reply_to(message, 'Digite o valor do stop Loss')
            bot.register_next_step_handler(msg, process_stop_loss_sinais_step)
        except Exception as e:
            bot.reply_to(message, '❌Upsi, houve um erro, tente novamente➡ /start')

def process_stop_loss_sinais_step(message):
        try:
            chat_id = message.chat.id
            stop_loss = message.text
            if float(stop_loss) < 1:
                msg = bot.reply_to(message,'❌Opção inválida, digite apenas números e maior ou igual a 1')
                bot.register_next_step_handler(msg, process_stop_loss_sinais_step)
                return
            dados = config_lista_sinais[chat_id]
            dados.stop_loss = stop_loss
            msg = bot.reply_to(message, 'Digite o valor do Stop Gain')
            bot.register_next_step_handler(msg, process_stop_gain_sinais_step)
        except Exception as e:
            bot.reply_to(message, '❌Upsi, houve um erro, tente novamente➡ /start')

def process_stop_gain_sinais_step(message):
        try:
            chat_id = message.chat.id
            stop_gain = message.text
            if float(stop_gain) < 1:
                msg = bot.reply_to(message,'❌Opção inválida, digite apenas número e maior que 0')
                bot.register_next_step_handler(msg, process_stop_gain_sinais_step)
                return
            dados = config_lista_sinais[chat_id]
            dados.stop_gain = stop_gain
            markup = types.ReplyKeyboardMarkup(resize_keyboard=True, row_width=10)
            markup.add('✅Guardar', 'Alterar')
            msg = bot.reply_to(message,'✅Desejas guardar os dados?✅',reply_markup=markup)
            bot.register_next_step_handler(msg, process_guardar_sinais_step)
        except Exception as e:
            bot.reply_to(message, '❌Upsi, houve um erro, tente novamente➡ /start')

def process_guardar_sinais_step(message):
        try:
            chat_id = message.chat.id
            salvar = message.text
            dados = config_lista_sinais[chat_id]
            if salvar == u'✅Guardar':

                bot.send_message(message.chat.id, '✅Dados inseridos com sucesso✅' +
                    '\nTipo de Conta: '+('Real' if int(dados.conta)==2 else 'Treinamento')
                    +'\nOperar na: '+('Digital' if int(dados.operacao)==1 else 'Binária')
                    +'\nValor de entrada: '+str(dados.valor_entrada) + 
                    '\nNível de Martingale:' +str(dados.martingale) + '\nStop Loss: '+
                    str(dados.stop_loss) + '\nStop Gain: '+ str(dados.stop_gain))

                bot_lista_sinais(message)

            elif salvar == u'Alterar':
                msg='Escolha em qual conta Operar:\n 1 - Treinamento\n 2 - REAL:'
                bot.register_next_step_handler(msg, process_conta_sinais_step)
            else:
                dados.conta = None
                dados.operacao = None
                dados.valor_entrada = None
                dados.martingale = None
                dados.stop_loss == None
                dados.stop_gain = None
                bot_lista_sinais(message)
        except Exception as e:
            bot.reply_to(message, '❌Upsi, houve um erro, tente novamente➡ /start')

@bot.message_handler(func=lambda message: message.text == '⚙Configurar Catalogador')
def config_do_catalogador(message):
        msg = bot.reply_to(message,"Indique o Time Frame a analizar:")
        bot.register_next_step_handler(msg, process_time_frame_cat_step)

def process_time_frame_cat_step(message):
        try:
            chat_id = message.chat.id
            time_frame = message.text
            if (not time_frame.isdigit()):
                msg = bot.reply_to(message,'❌Opção inválida, digite apenas número:')
                bot.register_next_step_handler(msg, process_time_frame_cat_step)
                return
            dados = catalogador_config(time_frame)
            config_catalogador[chat_id] = dados
            msg = bot.reply_to(message, 'Quantos dias pretendes analizar?')
            bot.register_next_step_handler(msg, process_dias_cat_step)
        except Exception as e:
            bot.reply_to(message, '❌Upsi, houve um erro, tente novamente➡ /start')

def process_dias_cat_step(message):
        try:
            chat_id = message.chat.id
            dias = message.text
            if (not dias.isdigit()):
                msg = bot.reply_to(message,'❌Opção inválida digite apenas números')
                bot.register_next_step_handler(msg, process_dias_cat_step)
                return
            dados = config_catalogador[chat_id]
            dados.dias = dias
            msg = bot.reply_to(message,'Qual a percentagem mínima?')
            bot.register_next_step_handler(msg, process_percent_cat_step)
        except Exception as e:
            bot.reply_to(message, '❌Upsi, houve um erro, tente novamente➡ /start')

def process_percent_cat_step(message):
        try:
            chat_id = message.chat.id
            porcentagem = message.text
            if (not porcentagem.isdigit()):
                msg = bot.reply_to(message,'❌Opção inválida, digite apenas número!')
                bot.register_next_step_handler(msg, process_percent_cat_step)
                return
            dados = config_catalogador[chat_id]
            dados.porcentagem = porcentagem
            msg = bot.reply_to(message,'Digite a quantidade de Martingale:')
            bot.register_next_step_handler(msg, process_martingale_cat_step)
        except Exception as e:
            bot.reply_to(message, '❌Upsi, houve um erro, tente novamente➡ /start')

def process_martingale_cat_step(message):
        try:
            chat_id = message.chat.id
            martingale = message.text
            if (not martingale.isdigit()):
                msg = bot.reply_to(message, '❌Opção inválida, digite apenas números.')
                bot.register_next_step_handler(msg, process_martingale_cat_step)
                return
            dados = config_catalogador[chat_id]
            dados.martingale = martingale
            markup = types.ReplyKeyboardMarkup(resize_keyboard=True, row_width=10)
            markup.add('✅Guardar', 'Cancelar')
            msg = bot.reply_to(message,'✅Desejas guardar os dados?✅',reply_markup=markup)
            bot.register_next_step_handler(msg, process_guardar_cat_step)
        except Exception as e:
            bot.reply_to(message, '❌Upsi, houve um erro, tente novamente➡ /start')

def process_guardar_cat_step(message):
    try:
        chat_id = message.chat.id
        salvar = message.text
        dados = config_catalogador[chat_id]
        if salvar == u'✅Guardar':

            bot.send_message(message.chat.id, '✅Dados inseridos com sucesso✅' +
                '\nTime Frame: M'+str(dados.time_frame)+
                '\nQuantidade de dias: '+str(dados.dias)+
                '\nPorcentagem: '+str(dados.porcentagem)+
                '\nNível de Martingale:'+str(dados.martingale))

            bot_catalogador(message)
        else:
            dados.time_frame = None
            dados.dias = None
            dados.porcentagem = None
            dados.martingale = None
            bot_catalogador(message)
    except Exception as e:
        bot.reply_to(message, '❌Upsi, houve um erro, tente novamente➡ /start')

@bot.message_handler(func=lambda message: message.text == '⚙Configurar Tendência')
def config_da_tend(message):
        msg = bot.reply_to(message,"Escolha em qual conta Operar:\n 1 - Treinamento\n 2 - REAL:")
        bot.register_next_step_handler(msg, process_conta_tend_step)

def process_conta_tend_step(message):
        try:
            chat_id = message.chat.id
            conta = message.text
            if (not conta.isdigit()):
                msg = bot.reply_to(message,'❌Opção inválida, escolha: \n1 para conta de Treinamento \n2 para Real')
                bot.register_next_step_handler(msg, process_conta_tend_step)
                return
            dados = tendencia_config(conta)
            config_tend[chat_id] = dados
            msg = bot.reply_to(message,'Desejas operar na\n  1 - Digital\n  2 - Binaria:')
            bot.register_next_step_handler(msg, process_operacao_tend_step)
        except Exception as e:
            bot.reply_to(message,
                        '❌Upsi, ocorreu um erro, tente novamente /start❌')

def process_operacao_tend_step(message):
        try:
            chat_id = message.chat.id
            operacao = message.text
            if (not operacao.isdigit()):
                msg = bot.reply_to(message,'❌Opção inválida, escolha: \n1 para Digital \n2 para Binaria:')
                bot.register_next_step_handler(msg, process_operacao_tend_step)
                return
            dados = config_tend[chat_id]
            dados.operacao = operacao
            msg = bot.reply_to(message,'Em qual time frame deseja Operar?')
            bot.register_next_step_handler(msg, process_time_frame_tend_step)
        except Exception as e:
            bot.reply_to(message, '❌Upsi, houve um erro, tente novamente➡ /start')

def process_time_frame_tend_step(message):
        try:
            chat_id = message.chat.id
            time_frame = message.text
            if (not time_frame.isdigit()):
                msg = bot.reply_to(message,'❌Opção inválida, escolha: \n1 para M1, 5 para M5 ou 15 para M15:' )
                bot.register_next_step_handler(msg, process_time_frame_tend_step)
                return
            dados = config_tend[chat_id]
            dados.time_frame = time_frame
            msg = bot.reply_to(message, 'Digite a paradidade por onde operar\n' +
                'Ex.: EURUSD ou então EURUSD-OTC para mercado OTC:')
            bot.register_next_step_handler(msg, process_par_tend_step)
        except Exception as e:
            bot.reply_to(message, '❌Upsi, houve um erro, tente novamente➡ /start')

def process_par_tend_step(message):
        try:
            chat_id = message.chat.id
            par = message.text
            if par.isdigit() or par == '':
                msg = bot.reply_to(message,'❌Opção inválida, escolha por Ex.: EURUSD')
                bot.register_next_step_handler(msg, process_par_tend_step)
                return
            dados = config_tend[chat_id]
            dados.par = par
            msg = bot.reply_to(message,'Digite o valor de entrada')
            bot.register_next_step_handler(msg, process_valor_entrada_tend_step)
        except Exception as e:
            bot.reply_to(message, '❌Upsi, houve um erro, tente novamente➡ /start')

def process_valor_entrada_tend_step(message):
        try:
            chat_id = message.chat.id
            valor_entrada = message.text
            if float(valor_entrada) < 1:
                msg = bot.reply_to(message,'❌O valor de entrada não pode ser menor que 1')
                bot.register_next_step_handler(msg, process_valor_entrada_tend_step)
                return
            dados = config_tend[chat_id]
            dados.valor_entrada = valor_entrada
            msg = bot.reply_to(message, 'Indique a quantidade de Martingale\n' +
               'Aconcelho indicar no máximo 2 níveis de Martingale')
            bot.register_next_step_handler(msg, process_martingale_tend_step)
        except Exception as e:
            bot.reply_to(message, '❌Upsi, houve um erro, tente novamente➡ /start')

def process_martingale_tend_step(message):
        try:
            chat_id = message.chat.id
            martingale = message.text
            if (not martingale.isdigit()):
                msg = bot.reply_to(message, '❌Opção inválida, digite apenas número inteiros')
                bot.register_next_step_handler(msg, process_martingale_tend_step)
                return
            dados = config_tend[chat_id]
            dados.martingale = martingale
            msg = bot.reply_to(message, 'Digite o valor do stop Loss')
            bot.register_next_step_handler(msg, process_stop_loss_tend_step)
        except Exception as e:
            bot.reply_to(message, '❌Upsi, houve um erro, tente novamente➡ /start')

def process_stop_loss_tend_step(message):
        try:
            chat_id = message.chat.id
            stop_loss = message.text
            if float(stop_loss) < 1:
                msg = bot.reply_to(message,'❌Opção inválida, digite apenas números e maior ou igual a 1')
                bot.register_next_step_handler(msg, process_stop_loss_tend_step)
                return
            dados = config_tend[chat_id]
            dados.stop_loss = stop_loss
            msg = bot.reply_to(message, 'Digite o valor do Stop Gain')
            bot.register_next_step_handler(msg, process_stop_gain_tend_step)
        except Exception as e:
            bot.reply_to(message, '❌Upsi, houve um erro, tente novamente➡ /start')

def process_stop_gain_tend_step(message):
        try:
            chat_id = message.chat.id
            stop_gain = message.text
            if float(stop_gain) < 1:
                msg = bot.reply_to(message, '❌Opção inválida, digite apenas número e maior que 0')
                bot.register_next_step_handler(msg, process_stop_gain_tend_step)
                return
            dados = config_tend[chat_id]
            dados.stop_gain = stop_gain
            markup = types.ReplyKeyboardMarkup(resize_keyboard=True, row_width=10)
            markup.add('✅Guardar', 'Alterar')
            msg = bot.reply_to(message,'✅Desejas guardar os dados?✅',reply_markup=markup)
            bot.register_next_step_handler(msg, process_guardar_tend_step)
        except Exception as e:
            bot.reply_to(message, '❌Upsi, houve um erro, tente novamente➡ /start')

def process_guardar_tend_step(message):
        try:
            chat_id = message.chat.id
            salvar = message.text
            dados = config_tend[chat_id]
            if salvar == u'✅Guardar':

                bot.send_message(message.chat.id, '✅Dados inseridos com sucesso✅' +
                    '\nTipo de Conta: '+('Real' if int(dados.conta)==2 else 'Treinamento')
                    +'\nOperar na: '+('Digital' if int(dados.operacao)==1 else 'Binária') 
                    +'\nTime Frame: M' + str(dados.time_frame) 
                    +'\nParidade: '+str(dados.par)
                    +'\nValor de entrada: '+str(dados.valor_entrada) 
                    +'\nNível de Martingale: '+str(dados.martingale) 
                    +'\nStop Loss: '+str(dados.stop_loss)
                    +'\nStop Gain: '+str(dados.stop_gain))

                bot_tendencia(message)

            elif salvar == u'Alterar':
                msg = 'Escolha em qual conta Operar:\n 1 - Treinamento\n 2 - REAL:'
                bot.register_next_step_handler(msg, process_conta_tend_step)
            else:
                dados.conta = None
                dados.operacao = None
                dados.time_frame == None
                dados.par = None
                dados.valor_entrada = None
                dados.martingale = None
                dados.stop_loss == None
                dados.stop_gain = None
                bot_tendencia(message)
        except Exception as e:
            bot.reply_to(message, '❌Upsi, houve um erro, tente novamente➡ /start')


bot.enable_save_next_step_handlers(delay=2)
bot.load_next_step_handlers()
bot.polling(none_stop=True, interval=0)
