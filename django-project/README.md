# Django project
## Запуск
- ``` make env ``` -  Создаст .env файл в папке project. Его можно настроить, но это не обязательно.
- ``` docker compose build ```
- ``` docker compose run migrate ``` - Запустит миграции (в том числе добавит тестовые данные, если в .env DEBUG=True). Возможно придется подождать
- ``` docker compose up ``` - Запустит сервис по url http://127.0.0.1:8000
- Swagger доступен по url http://127.0.0.1:8000/swagger/
