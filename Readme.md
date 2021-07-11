# Vaccination in Burgos 💉
## What is this? 🤖
This is a telegram bot.
## What does it do? ❓
It notifies you when the vaccination points/dates in the province of Burgos (or León, or other if you deploy it) change.
## Why does this even exists? 🤔
Because the health department of Castilla y León does not notify you when it's your time to get vaccinated. And I got tired of checking the website.
## Data source 💾
- [Here for Burgos](https://www.saludcastillayleon.es/es/covid-19-poblacion/vacunacion-covid-19/lugares-vacunacion/burgos)
- [Here for Burgos](https://www.saludcastillayleon.es/es/covid-19-poblacion/vacunacion-covid-19/lugares-vacunacion/leon)
- [List of provinces](https://www.saludcastillayleon.es/es/covid-19-poblacion/vacunacion-covid-19/lugares-vacunacion)

# Try it!
*Might not work if my raspberry pi is dead*
- For [Burgos](https://t.me/VacunasEnBurgosBot)
- For [León](https://t.me/VacunasEnLeonBot)

# Run the docker container
- You need a .env file with a variable called BOT_API_KEY that contains the telegram api key.
- You also need a chat_ids.txt file where docker can mount the volume. It should be empty for the first execution.
- The container is built for linux/amd64 and linux/arm/v7.
Use the following script to run it:
```sudo docker run -d --env-file ./.env -v $(pwd)/chat_ids.txt:/app/chat_ids.txt morive/vaccinationburgosbot:latest```

# Customization
There are 2 other environmental variable that you can use:
- **DATA_URL**: to change the URL to request the data. You can find the valid ones [here](https://www.saludcastillayleon.es/es/covid-19-poblacion/vacunacion-covid-19/lugares-vacunacion) The default URL is for Burgos.
- **TIME_TO_CHECK_SECS**: seconds between checks. Defaults to 3600 seconds. (1hour)

