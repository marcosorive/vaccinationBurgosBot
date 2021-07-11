# Vaccination in Burgos 💉
## What is this? 🤖
This is a telegram bot.
## What does it do? ❓
It notifies you when the vaccination points/dates in the province of Burgos change.
## Why does this even exists? 🤔
Because the health department of Castilla y León does not notify you when it's your time to get vaccinated. And I got tired of checking the website.
## Data source 💾
[Here](https://www.saludcastillayleon.es/es/covid-19-poblacion/vacunacion-covid-19/lugares-vacunacion/burgos)

# Try it!
[https://t.me/VacunasEnBurgosBot](https://t.me/VacunasEnBurgosBot) (Might not work if my raspberry pi is dead)

# Run the docker container
You need a .env file with a variable called BOT_API_KEY that contains the telegram api key.
```sudo docker run --env-file ./.env -v $(pwd)/chat_ids.txt:/app/chat_ids.txt vaccinationburgosbot:1.0```

