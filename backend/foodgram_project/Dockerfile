FROM python:3.8.5
WORKDIR /app
COPY . .
RUN pip3 install -r requirements.txt
CMD ["gunicorn", "foodgram_project.wsgi:application", "--bind", "0:8000" ] 
