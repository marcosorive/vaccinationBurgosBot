import requests
import os
import ssl
from bs4 import BeautifulSoup
from telegram import Update
from telegram.ext import Updater, CommandHandler, CallbackContext
from dotenv import load_dotenv
from pymongo import MongoClient
import logging

load_dotenv()

MONGOURI = os.environ.get("MONGO_URI")
VACCINE_PLACES_FILENAME = 'vaccine_places.txt'
TEMPORAL_VACCINE_FILENAME = 'vaccine_places_temporal.txt'
VACCINE_URL_BURGOS = os.environ.get(
    'DATA_URL') or 'https://www.saludcastillayleon.es/es/covid-19-poblacion/vacunacion-covid-19/lugares-vacunacion/burgos'
CHAT_ID_FILENAME = 'chat_ids.txt'
INTERVAL_CHECK_IN_SECS = os.environ.get('TIME_TO_CHECK_SECS') or 3600


def write_vaccine_places(url: str, filename: str) -> None:
    '''
        This function writes a file called vaccine_places.txt with the list of vaccine places for a city in Castilla y León.
        url: is the url to request. Should look like this: https://www.saludcastillayleon.es/es/covid-19-poblacion/vacunacion-covid-19/lugares-vacunacion/burgos
        filename: the filename were the vaccination places are gonna be stored.
    '''
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


def are_file_equal(filename1: str, filename2: str) -> None:
    with open(filename1, 'r') as file1:
        lines_from_1 = file1.read().split('\n')
    with open(filename2, 'r') as file2:
        lines_from_2 = file2.read().split('\n')
    return lines_from_1 == lines_from_2


def delete_file_with_name(filename: str) -> None:
    if os.path.exists(filename):
        os.remove(filename)
        logging.info("File with name " + filename + " deleted")
    else:
        logging.info("The file does not exist")


def rename_file(old_name: str, new_name: str):
    os.rename(old_name, new_name)


def add_user_to_list(chat_id: str) -> bool:
    logging.info('Adding user with ID' + chat_id)
    try:
        to_add = {"id": str(chat_id)}
        if(not chat_ids_collection.find_one(to_add)):
            chat_ids_collection.insert_one(to_add)
            logging.info("Added.")
            return True
        else:
            logging.info('It was already added')
            return False
    except Exception as e:
        logging.error('Error adding user' + e)
        return False



def delete_user_from_list(chat_id: str) -> bool:
    logging.info('Deleting user user with ID' + chat_id)
    try:
        to_delete = {"id": str(chat_id)}
        deleted_result = chat_ids_collection.delete_one(to_delete).deleted_count == 1
        if(deleted_result):
            logging.info('Deleted successful')
        else:
            logging.info('Couldn\'t delete, it wasn\'t added probably.')
        return deleted_result
    except Exception as e:
        logging.error(e)
        return False


def get_all_chat_id() -> list:
    try:
        remote_ids = chat_ids_collection.find()
        ids = [i["id"] for i in remote_ids ]
        return ids
    except:
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
    logging.info('Creating temporal file to compare')
    write_vaccine_places(VACCINE_URL_BURGOS, TEMPORAL_VACCINE_FILENAME)
    logging.info('Temporal file created')
    equal_files = are_file_equal(
        VACCINE_PLACES_FILENAME, TEMPORAL_VACCINE_FILENAME)
    if not equal_files:
        logging.info('There are changes, notifying the user and changing file names')
        chat_ids = get_all_chat_id()
        message = 'Parece que se ha actualizado la lista de las vacunas. Compruébalo  haciendo [click aqui](' + \
            VACCINE_URL_BURGOS+')'
        for id in chat_ids:
            context.bot.sendMessage(
                chat_id=id, text=message, parse_mode='Markdown')
        delete_file_with_name(VACCINE_PLACES_FILENAME)
        rename_file(TEMPORAL_VACCINE_FILENAME,VACCINE_PLACES_FILENAME)
        delete_file_with_name(TEMPORAL_VACCINE_FILENAME)
    else:
        delete_file_with_name(TEMPORAL_VACCINE_FILENAME)
        logging.info('Files are equal, no changes in vaccines.')


if __name__ == '__main__':
    logging.basicConfig(level=logging.INFO, filename='bot.log', encoding='utf-8')
    logging.info("Connecting to database...")
    if(not os.path.exists(VACCINE_PLACES_FILENAME)):
        logging.info('Initial file did not exist. Creating...')
        write_vaccine_places(VACCINE_URL_BURGOS, VACCINE_PLACES_FILENAME)
        logging.info('Initial file created')
    client = MongoClient(MONGOURI, ssl_cert_reqs=ssl.CERT_NONE)
    db = client["vaccinationBurgosBot"]
    chat_ids_collection = db["chat_ids"]
    vaccination_places_collection = db["vaccination_places"]
    logging.info("Connected.")
    updater = Updater(token=os.environ.get('BOT_API_KEY'), use_context=True)

    dispatcher = updater.dispatcher

    job = updater.job_queue
    job.run_repeating(update_vaccine_bot_action,int(INTERVAL_CHECK_IN_SECS), 5)

    dispatcher.add_handler(CommandHandler("start", start_bot_action))
    dispatcher.add_handler(CommandHandler("stop", stop_bot_action))

    updater.start_polling()
    updater.idle()
    logging.info("Bot started.")

