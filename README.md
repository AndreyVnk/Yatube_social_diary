# Yatube

**Yatube** - это блог, в котором пользователи могут публиковать свои записи и фото.

Функционал проекта:

- Записи
- Комментарии
- Группы

Реализована возможность подписываться на других пользователей.

**Технологии:**

* Python 3
* Django
* SQLite

## Запуск проекта ##
### 1. Склонировать репозиторий
```
git clone https://github.com/AndreyVnk/Yatube_social_diary.git
```

### 2. Создать виртуальное окружение и активировать его
Перейти в папку с проектом _Yatube_social_diary/_ выполнить команды
```
python -m venv venv
source venv/Scripts/activate (для Windows) | source venv/bin/activate (для Linux)
```

### 3. Установить необходимые пакеты
```
pip install -r requirements.txt
```
### 4. Выполнить миграции
Из папки *Yatube_social_diary/yatube/*, выполнить команду
```
python manage.py migrate
```
### 5. Запустить проект
```
python manage.py runserver
```
Проект будет доступен по адресу: http://127.0.0.1:8000/ .
