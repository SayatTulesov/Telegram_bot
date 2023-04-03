import telebot
from telebot import types
import random
import requests
from config import WEATHER_API_KEY, CURRENCY_API_KEY, BOT_TOKEN, IMAGE_DIR, GIF_DIR

bot = telebot.TeleBot(BOT_TOKEN)

@bot.message_handler(commands=['start'])
def start(message):
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True, row_width=2)
    media = types.KeyboardButton('Funny gif or image')
    weather = types.KeyboardButton('Weather in some city')  
    exchange_rate = types.KeyboardButton('Exchange rate')
    website = types.KeyboardButton('Our website')
    markup.add(media, weather, exchange_rate, website)
    bot.send_message(message.chat.id, f'Hello, <b>{message.from_user.first_name} {message.from_user.last_name}</b>!', reply_markup=markup, parse_mode='html')

@bot.message_handler(content_types=['text'])
def bot_message(message):
    match message.chat.type:
        case 'private':
            match message.text:
                #WEBSITE
                case 'Our website':
                    bot.send_message(message.chat.id, f'Visit our official website:\n https://ttc.kz/ru/')
                    
                case 'Hi' | 'hi' | 'Hello' | 'hello':
                    bot.send_message(message.chat.id, f'Hello, <b>{message.from_user.first_name} {message.from_user.last_name}</b>!', parse_mode='html')
                
                #SENDING GIF OR IMAGE    
                case 'Funny gif or image':
                    markup = types.InlineKeyboardMarkup(row_width=2)
                    gif = types.InlineKeyboardButton(text='GIF', callback_data='gif')
                    images = types.InlineKeyboardButton(text='Images', callback_data='images')
                    back_to_main = types.InlineKeyboardButton(text='Back to main menu', callback_data='back')
                    markup.add(gif, images, back_to_main)
                    bot.send_message(message.chat.id, f'<b>What you want to get?</b>', reply_markup=markup, parse_mode='html')
                
                case 'Cat' | 'Dog' | 'Monkey' | 'Turtle' | 'Penguin' | 'Owl':
                    gif_number = random.randint(0,19)
                    gif_file = "/" + message.text.lower() + str(gif_number) + ".gif"                    
                    with open(GIF_DIR + gif_file, 'rb') as gif:
                        bot.send_animation(message.chat.id, gif)
                
                case 'Cats' | 'Dogs' | 'Monkeys' | 'Turtles' | 'Penguins' | 'Owls':
                    image_number = random.randint(0,15)
                    image_file = "/" + message.text.lower() + str(image_number) + ".jpg"
                    with open(IMAGE_DIR + image_file, 'rb') as image:
                        bot.send_photo(message.chat.id, image)
                   
                #BACK FROM GIF/IMAGE CHOICE        
                case 'Back':
                    markup = types.InlineKeyboardMarkup(row_width=2)
                    gif = types.InlineKeyboardButton(text='GIF', callback_data='gif')
                    images = types.InlineKeyboardButton(text='Images', callback_data='images')
                    back_to_main = types.InlineKeyboardButton(text='Back to main menu', callback_data='back')
                    markup.add(gif, images, back_to_main)
                    bot.send_message(message.chat.id, f'<b>What you want to get?</b>', reply_markup=markup, parse_mode='html')
                
                #EXCHANGE RATE API    
                case 'Exchange rate':
                    msg = bot.send_message(message.chat.id, f'Enter 2 currency codes <b>separated by a space</b>', parse_mode='html')
                    bot.register_next_step_handler(msg, exchange_rate)
                    
                #WEATHER API    
                case 'Weather in some city':
                    msg = bot.send_message(message.chat.id, f'Enter the name of the city')
                    bot.register_next_step_handler(msg, print_weather)

#EXCHANGE RATE API FUNCTION     
def exchange_rate(message):
    currency_from = message.text[0:3]
    currency_to = message.text[4:7]
    url = "https://v6.exchangerate-api.com/v6/" + CURRENCY_API_KEY + "/pair/" + currency_from + "/" + currency_to
    response = requests.get(url)
    match response.status_code:
        case 200:
            data = response.json()
            last_update = data['time_last_update_utc']
            from_currency = data['base_code']
            to_currency = data['target_code']
            conversion_rate = data['conversion_rate']
            bot.send_message(message.chat.id, f'Exchange rate from {from_currency} to {to_currency}: {conversion_rate}\nLast update: {last_update}')
        case _:
            bot.send_message(message.chat.id, f'ERROR! Try again')
            
#WEATHER API FUNCTION                         
def print_weather(message):
    city = message.text
    endpoint = "https://api.openweathermap.org/data/2.5/weather?q="
    url = endpoint + city + "&appid=" + WEATHER_API_KEY + "&units=metric"
    response = requests.get(url)
    match response.status_code:
        case 200:
            data = response.json()
            weather_description = data['weather'][0]['description']
            temperature = int(data['main']['temp'])
            feels_like = int(data['main']['feels_like'])
            pressure = int(data['main']['pressure'])
            wind_speed = int(data['wind']['speed'])
            bot.send_message(message.chat.id, f'Weather in <b>{str.title(city)}</b>:\n Current temperature: {temperature}°C;\n Feels like: {feels_like}°C;\n' 
                                            f' Atmospheric pressure: {pressure} hPa;\n Wind speed: {wind_speed} meter/sec;\n'
                                            f' Weather description: {str.title(weather_description)}', parse_mode='html')
        case _:
            bot.send_message(message.chat.id, f'No such city has been found. Try another one!')

#CHOOSING GIF OR IMAGE
@bot.callback_query_handler(func=lambda call: True)
def choosing(call):
    match call.data:
        case 'gif':
            markup = types.ReplyKeyboardMarkup(resize_keyboard=True, row_width=3)
            cat = types.KeyboardButton('Cat')
            dog = types.KeyboardButton('Dog')
            monkey = types.KeyboardButton('Monkey')
            penguin = types.KeyboardButton('Penguin')
            turtle = types.KeyboardButton('Turtle')
            owl = types.KeyboardButton('Owl')
            back = types.KeyboardButton('Back')
            markup.add(cat, dog, monkey, penguin, turtle, owl, back)
            bot.send_message(call.message.chat.id, f'What you want to see?', reply_markup=markup)
            bot.answer_callback_query(callback_query_id=call.id)
        case 'images':
            markup = types.ReplyKeyboardMarkup(resize_keyboard=True, row_width=3)
            cats = types.KeyboardButton('Cats')
            dogs = types.KeyboardButton('Dogs')
            monkeys = types.KeyboardButton('Monkeys')
            pinguins = types.KeyboardButton('Penguins')
            turtles = types.KeyboardButton('Turtles')
            owls = types.KeyboardButton('Owls')
            back = types.KeyboardButton('Back')
            markup.add(cats, dogs, monkeys, pinguins, turtles, owls, back)
            bot.send_message(call.message.chat.id, f'What you want to see?', reply_markup=markup)
            bot.answer_callback_query(callback_query_id=call.id)
        #BACK TO MAIN MENU FROM GIF/IMAGE CHOICE  
        case 'back':
            markup = types.ReplyKeyboardMarkup(resize_keyboard=True, row_width=2)
            media = types.KeyboardButton('Funny gif or image')
            weather = types.KeyboardButton('Weather in some city')  
            exchange_rate = types.KeyboardButton('Exchange rate')
            website = types.KeyboardButton('Our website')
            markup.add(media, weather, exchange_rate, website)
            bot.send_message(call.message.chat.id, f"Choose an option:", reply_markup=markup)
            bot.answer_callback_query(callback_query_id=call.id)

bot.polling(none_stop=True)