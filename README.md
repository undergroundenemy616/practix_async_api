# Стек:
Python, Fast API, Reids, Elastic Search, Nginx, Docker.
## Как запустить проект:

После клонирования проекта локально необходимо выполнить команду:
```
cp template.env .env
```
И передать значения переменным, указанным в появившемся файле .env

Затем выполнить команду:
```
docker-compose up
```

Дополненные проекты с сервисами ETL располагаются в следующих репозиториях: 
https://github.com/undergroundenemy616/ETL/

Для запуска тестов необходимо поднять докер с тестовым стендом:
```
docker-compose -f docker-compose.test.yaml up --build
```
