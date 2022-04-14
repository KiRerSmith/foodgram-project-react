# praktikum_new_diplom
##### В этом проекте реализован API сайта рецетов. Пользователи могут создавать рецепты для приготовления пищи, просматривать рецепты других пользователей, сортировать их по тэгам. На сайте реализованы такие функции как: подписки, добавление в избранное и формирование продуктовой корзины из ингредиентов.

### Технологии:
``Python 3.7``; ``Django``; ``Django REST Framework``; ``PostgreSQL``; ``Docker``; ``React``

### Запуск:

1. В папке ``infra`` выполните команду ``docker-compose up``. Сформируются контейнеры docker-compose ``frontend``, ``backend``,``db``, ``nginx``.
При выполнении команды сервис frontend, описанный в ``docker-compose.yml`` подготовит файлы, необходимые для работы фронтенд-приложения, а затем прекратит свою работу;
2. "Соберите статику" командой 
``docker-compose exec backend python manage.py collectstatic --no-input``;
3. Выполните миграции базы данных 
``docker-compose exec backend python manage.py migrate``;
4. Создайте суперпользователя 
``docker-compose exec backend python manage.py createsuperuser``;
5. Импортируйте фикстуры ингредиентов в базу 
``docker-compose exec backend python manage.py import_i --path data/ingredients.csv``.

Сайт доступен по адресу http://51.250.103.18/

login admin@mail.ru

pass admin

