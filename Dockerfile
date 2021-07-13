FROM python:3.9

WORKDIR /app
RUN pip install pipenv
COPY main.py .
COPY Pipfile .
COPY Pipfile.lock .
RUN touch bot.log
RUN pipenv install --system --deploy --ignore-pipfile

CMD python /app/main.py