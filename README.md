![](https://img.shields.io/badge/Python-3.8.5-blue) 
![](https://img.shields.io/badge/Django-3.2.6-green)
![](https://img.shields.io/badge/DjangoRestFramework-3.12.4-red)
![](https://badgen.net/badge/icon/postgresql?icon=postgresql&label)

# Foodgram - продуктовый помощник
![workflow](https://github.com/Amaterasq/foodgram-project-react/actions/workflows/foodgram_workflow.yml/badge.svg)

## Описание проекта
Сайт для публицации пользователями рецептов.
Пользователи могут создавать рецепты блюд, подписываться на обновления других пользователей, добавлять блюда в избранное и список покупок.
Список покупок состоит из ингредиентов и их количества, которые нужны для приготовления блюд. Его можно скачать с сайта в формате .txt.

## :computer: Технологии в проекте
:small_blue_diamond: Python <br>
:small_blue_diamond: Django <br>
:small_blue_diamond: Django REST Framework <br>
:small_blue_diamond: React JS <br>
:small_blue_diamond: PostgreSQL <br>
:small_blue_diamond: Docker <br>

## Необходимое ПО
Docker: https://www.docker.com/get-started <br />
Docker-compose: https://docs.docker.com/compose/install/

## :pencil2: Инструкции по запуску на удаленном сервере (Ubuntu)
1. Склонировать репозиторий через консоль:
```sh
git clone https://github.com/Amaterasq/foodgram-project-react.git
```
2. Выполнить вход на удаленный сервер:
```sh
ssh <username>@<IP-сервера>
```
3. Обновите менеджер пакетов, установите docker и docker-compose на сервер:
```sh
sudo apt-get update
sudo apt install docker.io 
sudo apt-get install docker-compose
```
4. Скопируйте необходимые для запуска файлы на сервер
(В дополнительном окне shell)
```sh
scp -r <путь_до_infra_на_устройстве>/ <username>@<host>:/home/<username>/infra
scp -r <путь_до_frontend_на_устройстве>/ <username>@<host>:/home/<username>/frontend
scp -r <путь_до_docs_на_устройстве>/ <username>@<host>:/home/<username>/docs
(проверить и добавить)
```
5. Cоздайте .env файл:
На сервере создайте файл и заполните переменные окружения:
```sh
touch .env
nano .env
```
```sh
SECRET_KEY=<SECRET_KEY>
DEBUG=<True/False>
DB_ENGINE=django.db.backends.postgresql
DB_NAME=postgres
POSTGRES_USER=postgres
POSTGRES_PASSWORD=postgres
DB_HOST=db
DB_PORT=5432
```
6. Добавьте Secrets:
Добавьте в Secrets GitHub переменные окружения для работы workflow:
```sh
DB_ENGINE=django.db.backends.postgresql
DB_NAME=postgres
POSTGRES_USER=postgres
POSTGRES_PASSWORD=postgres
DB_HOST=db
DB_PORT=5432
DOCKER_PASSWORD=<пароль DockerHub>
DOCKER_USERNAME=<имя пользователя DockerHub>
USER=<username для подключения к серверу>
HOST=<IP сервера>
PASSPHRASE=<пароль для сервера, если он установлен>
SSH_KEY=<ваш SSH ключ (cat ~/.ssh/id_rsa) >
```
7. Запуск проекта и миграций на удаленном сервере
### Собрать docker-compose:
```sh
sudo docker-compose up -d --build
```
### Создать и применить миграции
```sh
sudo docker-compose exec backend python manage.py makemigrations
sudo docker-compose exec backend python manage.py migrate
```
### Загрузить статику
```bash
sudo docker-compose exec backend python manage.py collectstatic --noinput 
```
### Наполнить базу данных ингредиентов данными
```bash
sudo docker-compose exec backend python manage.py db_fill_ingredient
```
### Создать суперюзера
```bash
sudo docker-compose exec backend python manage.py createsuperuser
```
## Проект запущен и доступен на http:/<публичный IP-сервера>/
## Документация к проекту:
```html
http://<публичный IP-сервера или localhost>/api/docs/redoc.html
```

## :bust_in_silhouette: Авторы проекта 
### :small_orange_diamond: Влад Перепечко _(Vlad Vi. Perepechko)_
```html
e-mail: perepechcko.vlad@ya.ru
```
```html
https://github.com/Amaterasq
```
```html
telegram: @amaterasutengu
```