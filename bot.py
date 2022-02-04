# Required Modules

import requests
import telebot
from bs4 import BeautifulSoup
import sys
import io


#API Key Details

API_KEY = "Your API Key Here"
bot = telebot.TeleBot(API_KEY)

#Required Header JSON

h = {
    "Cache-Control": "no-cache",
    "Pragma": "no-cache"
}

#Start Command

@bot.message_handler(commands=['start'])
def start(message):
    bot.reply_to(message, 'Hey there! How are you!,\nType /latest to get latest Telanagana Covid figures.\nType /help to know more \nType /cases <state-name> to get Covid cases data \nType /jntu to get latest latest JNTU Circular \n Type /india to get latest Covid News')


#Help Command
    
@bot.message_handler(commands=['help'])
def help(message):
    bot.reply_to(message, "Hi There! This is a simple bot to check the current COVID data of Telangana by displaying real time data from Times Of India. Type /start to get started. Built by @ujjwalshiva")


#India Command
    
@bot.message_handler(commands=['india'])
def india(message):
    url = "https://timesofindia.indiatimes.com/coronavirus"
    req = requests.get(url, headers=h).text
    soup = BeautifulSoup(req, 'html.parser')
    news = soup.find('div', class_='pLrri').get_text()
    bot.reply_to(message, "Latest TOI Covid News"+'\n'+news)


#Latest Command
    
@bot.message_handler(commands=['latest'])
def latest(message):
    bot.reply_to(message, "Fetching latest COVID Telangana Figures")

    #Saves STDOUT as string
    old_stdout = sys.stdout
    new_stdout = io.StringIO()
    sys.stdout = new_stdout

    url = "https://health.telangana.gov.in/"

    r = requests.get(url)
    text = r.text

    soup = BeautifulSoup(text, 'html.parser')

    #Fetching Date from Telangana Health Ministry
    datehtml = soup.findAll('font')
    for i in datehtml:
        if ':' in i.get_text():
            date = i.get_text()

    print(f"As of *{date}*")
    print()

    #Fetching Cases Count
    caseshtml = soup.find('tbody')
    cases = caseshtml.findAll('b')

    j = 0
    for i in cases:
        if j % 2 == 0:
            print(i.get_text().title(), end=': ')
        else:
            print(i.get_text().title())
        j += 1

    print()
    print('* Data fetched from Telangana Health Ministry *')

    #Output Final message
    output = new_stdout.getvalue()
    sys.stdout = old_stdout
    bot.send_message(message.chat.id,output)

#JNTU Command
    
@bot.message_handler(commands=['jntu'])
def jntu(message):
    bot.reply_to(message, "Latest Post from JNTU Bulletin Board")
    url = "https://jntuh.ac.in/bulletins"
    r = requests.get(url, headers=h)
    text = r.text

    soup = BeautifulSoup(text, 'html.parser')
    #Fetching data by row
    status = soup.find('tr',class_='griderow1')
    new = status.find_all('td')
    link = status.find('a', href=True)['href']
    #print(link)
    new = [i.text.strip() for i in new]
    #print(new[1],': ', new[2])

    #URL to send Document in Telegram
    url = "https://api.telegram.org/bot<API_KEY>/sendDocument"

    payload = {
        "document": link,
        "caption": new[1]+': '+ new[2],
        "disable_notification": False,
        "chat_id": message.chat.id
    }
    headers = {
        "Accept": "application/json",
        "User-Agent": "Ujjwal",
        "Content-Type": "application/json"
    }

    response = requests.request("POST", url, json=payload, headers=headers)


#Cases Command
    
@bot.message_handler(commands=['cases'])
def cases(message):
    query = message.text.replace('/cases ', '')
    key = str(query.title())
    loc = key
    if key=='Kerala':
        key = 'Kerala***'

    #Base URL for COVID India API
    url = "https://api.rootnet.in/covid19-in/stats/latest"
    r = requests.get(url, headers=h).json()
    data = r["data"]["regional"]
    states = []
    for i in data:
        states.append(i['loc'])
    states_enum = enumerate(states, 0)
    states = dict((str(i), j) for j, i in states_enum)

    if states.get(key):
        location = data[states.get(key)]['loc']
        cases = data[states.get(key)]['confirmedCasesIndian']
        discharged = data[states.get(key)]['discharged']
        deaths = data[states.get(key)]['deaths']

        output = f"Total cases so far in {loc}: {cases} \nDischarged: {discharged} \nDeaths: {deaths}"
        bot.reply_to(message, output)

    else:
        output = "Please enter proper state name with correct spelling"
        bot.reply_to(message, output)

#Required command to keep Bot running
bot.polling()
