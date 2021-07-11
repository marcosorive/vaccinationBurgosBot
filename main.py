import requests
import os
from bs4 import BeautifulSoup
from telegram import Update
from telegram.ext import Updater, CommandHandler, CallbackContext
from dotenv import load_dotenv

load_dotenv()

VACCINE_PLACES_FILENAME = 'vaccine_places.txt'
TEMPORAL_VACCINE_FILENAME = 'vaccine_places_temporal.txt'
VACCINE_URL_BURGOS = os.environ.get('DATA_URL') or 'https://www.saludcastillayleon.es/es/covid-19-poblacion/vacunacion-covid-19/lugares-vacunacion/burgos'
CHAT_ID_FILENAME = 'chat_ids.txt'
INTERVAL_CHECK_IN_SECS = os.environ.get('TIME_TO_CHECK_SECS') or 3600


'''
This function writes a file called vaccine_places.txt with the list of vaccine places for a city in Castilla y León.
url: is the url to request. Should look like this: https://www.saludcastillayleon.es/es/covid-19-poblacion/vacunacion-covid-19/lugares-vacunacion/burgos
filename: the filename were the vaccination places are gonna be stored.
'''


def write_vaccine_places(url: str, filename: str) -> None:
    r = requests.get(url)
    soup = BeautifulSoup(r.text, 'lxml')
    list_of_files = soup.find_all('span', {'class': 'resourceData2'})
    list_of_vaccine_places = [place.text for place in list_of_files]
    with open(filename, 'w') as file:
        for index, element in enumerate(list_of_vaccine_places):
            if(index == len(list_of_vaccine_places)-1):
                file.write("%s" % element)
            else:
                file.write("%s\n" % element)


def are_file_equal(filename1: str, filename2: str):
    with open(filename1, 'r') as file1:
        lines_from_1 = file1.read().split('\n')
    with open(filename2, 'r') as file2:
        lines_from_2 = file2.read().split('\n')
    return lines_from_1 == lines_from_2


def delete_file_with_name(filename: str):
    if os.path.exists(filename):
        os.remove(filename)
    else:
        print("The file does not exist")


def rename_file(old_name: str, new_name: str):
    os.rename(old_name, new_name)


def add_user_to_list(chat_id):
    if os.path.exists(CHAT_ID_FILENAME):
        chat_ids = get_all_chat_id()
        if chat_ids[0]=='':
            chat_ids.pop(0)
        if str(chat_id) in chat_ids:
            return False
        chat_ids.append(str(chat_id))
        operation = 'a'
        text_to_write = '\n'.join(chat_ids)
    else:
        operation = 'w'
        text_to_write = str(chat_id)
    with open(CHAT_ID_FILENAME, operation) as file:
        file.write(text_to_write)
    return True


def delete_user_from_list(chat_id):
    chat_ids = get_all_chat_id()
    string_id = str(chat_id)
    if os.path.exists(CHAT_ID_FILENAME) and string_id in chat_ids:
        chat_ids.remove(string_id)
        with open(CHAT_ID_FILENAME, 'w') as file:
            file.write('\n'.join(chat_ids))
        return True
    else:
        return False


def get_all_chat_id():
    if os.path.exists(CHAT_ID_FILENAME):
        with open(CHAT_ID_FILENAME) as filename:
            chat_ids = filename.read().split('\n')
        return chat_ids
    else:
        return list()


def start_bot_action(update: Update, context: CallbackContext) -> None:
    user = update.effective_user
    if add_user_to_list(user.id):
        update.message.reply_markdown_v2(
            fr'Hola {user.mention_markdown_v2()}\! Recibirás notificaciones de las vacunas'
        )
    else:
        update.message.reply_text('Ya estás suscrito a las notificaciones')


def stop_bot_action(update: Update, context: CallbackContext) -> None:
    id = update.effective_user.id
    if delete_user_from_list(id):
        update.message.reply_text('No recibirás más notificaciones')
    else:
        update.message.reply_text('Parece que no estabas suscrito')


def update_vaccine_bot_action(context: CallbackContext):
    print('Creating temporal file to compare')
    write_vaccine_places(VACCINE_URL_BURGOS, TEMPORAL_VACCINE_FILENAME)
    print('Temporal file created')
    equal_files = are_file_equal(
        VACCINE_PLACES_FILENAME, TEMPORAL_VACCINE_FILENAME)
    if not equal_files:
        print('There are changes, notifying the user and changing file names')
        chat_ids = get_all_chat_id()
        message = 'Parece que se ha actualizado la lista de las vacunas. Compruébalo  haciendo [click aqui](' + \
            VACCINE_URL_BURGOS+')'
        for id in chat_ids:
            context.bot.sendMessage(
                chat_id=id, text=message, parse_mode='Markdown')
        delete_file_with_name(VACCINE_PLACES_FILENAME)
        rename_file(TEMPORAL_VACCINE_FILENAME, VACCINE_PLACES_FILENAME)
    else:
        delete_file_with_name(TEMPORAL_VACCINE_FILENAME)
        print('Files are equal, no changes in vaccines.')


if(not os.path.exists(VACCINE_PLACES_FILENAME)):
    print('Initial file did not exist. Creating...')
    write_vaccine_places(VACCINE_URL_BURGOS, VACCINE_PLACES_FILENAME)
    print('Initial file created')

if __name__ == '__main__':
    updater = Updater(token=os.environ.get('BOT_API_KEY'), use_context=True)

    dispatcher = updater.dispatcher

    job = updater.job_queue
    job.run_repeating(update_vaccine_bot_action, int(INTERVAL_CHECK_IN_SECS), 5)

    dispatcher.add_handler(CommandHandler("start", start_bot_action))
    dispatcher.add_handler(CommandHandler("stop", stop_bot_action))

    updater.start_polling()
    updater.idle()