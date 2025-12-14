# Telegram-бот для аналитики видео по запросам на естественном языке

Бот принимает вопросы на русском языке в произвольной форме и отвечает **только одним числом** — результатом аналитики по базе данных видео-контента.

Примеры вопросов:
- Сколько всего видео есть в системе?
- Сколько видео у креатора с id ecd8a4e4-1f24-4b97-a944-35d17078ce7c вышло с 1 по 5 ноября 2025?
- Сколько видео набрало больше 100 000 просмотров за всё время?
- На сколько просмотров в сумме выросли все видео 28 ноября 2025?
- Сколько разных видео получали новые просмотры 27 ноября 2025?

## Технологии

- **Python 3.11**
- **aiogram 3.x** — асинхронный фреймворк для Telegram-бота
- **Groq API** (Llama 3.1 70B) — сверхбыстрая генерация SQL из естественного языка
- **SQLAlchemy 2.0** + **psycopg2** — работа с PostgreSQL
- **PostgreSQL** — хранилище данных (таблицы: creators, videos, video_snapshots)
- **Docker** + **docker-compose** — для локального запуска и деплоя

## Архитектура и подход

1. Пользователь пишет боту любой текстовый вопрос на русском.
2. Бот отправляет вопрос в Groq API с мощным промптом, содержащим полную схему БД и примеры запросов.
3. LLM генерирует чистый PostgreSQL-запрос (только SELECT с агрегатными функциями).
4. Бот выполняет запрос к БД через SQLAlchemy **от имени read-only пользователя** (максимальная безопасность).
5. Результат (одно число) возвращается пользователю.

**Безопасность:**
- Подключение к БД от пользователя с правами только на SELECT.
- Дополнительная проверка: запрос должен начинаться с SELECT.
- Никаких INSERT/UPDATE/DELETE/DROP физически невозможны.
## Безопасность подключения к БД

Для максимальной защиты данных бот подключается к PostgreSQL **от имени отдельного read-only пользователя**, который физически не может выполнять INSERT, UPDATE, DELETE, DROP и другие опасные операции.

### Создание безопасного пользователя (выполнить один раз в psql или pgAdmin)

```sql
-- Создаём пользователя для бота
CREATE USER bot_reader WITH PASSWORD 'strong_password_123';

-- Даём право подключаться к базе
GRANT CONNECT ON DATABASE video_analyst_db TO bot_reader;

-- Даём доступ к схеме public
GRANT USAGE ON SCHEMA public TO bot_reader;

-- Даём право только на чтение всех существующих таблиц
GRANT SELECT ON ALL TABLES IN SCHEMA public TO bot_reader;

-- Важно: автоматически даём SELECT на все новые таблицы, которые будут созданы в будущем
ALTER DEFAULT PRIVILEGES IN SCHEMA public GRANT SELECT ON TABLES TO bot_reader;
```

## Как запустить локально
### Вариант 1: С Docker (рекомендуется)

1. Склонируй репозиторий:
   ```bash
   git clone https://github.com/Crecker76/natural_language_video_analyst.git
   cd natural_language_video_analyst
   ```
### Вариант 2: Без Docker (локально)

1. Установи Python 3.11
2. Склонируй репозиторий и перейди в папку
3. Создай виртуальное окружение и установи зависимости:
```bash
python -m venv venv
```
```bash
source venv/bin/activate  # Windows: venv\Scripts\activate
pip install -r requirements.txt
```
4. Создай файл .env
5. Запусти бота:
```bash
python start_project.py
```
Таблицы создаются автоматически при запуске проекта


## Структура файла .env
https://console.groq.com/keys - ccылка для получение ключа к API

```bazaar
#Режим запуска всего проекта
ENVIRONMENT=development

#данные для локального подкючения
LOCAL_DB_USER_NAME=your_name_user
LOCAL_DB_PASSWORD=your_password

# данные для подключения к БД
PORT_DB=your_port
NAME_DB=your_name_db

# Данные бота
TEST_BOT_TOKEN=5059172479:XXXX

# API KEY
GROQ_API_KEY=gsk_gC235XXXX
```

## Структура проекта
```
natural_language_video_analyst/ - корень проекта
├── config_project/ - файлы с настройкой проекта 
│   ├── __init__.py
│   ├── config.py
│   ├── config_db.py
│   ├── constants.py
│   ├── log_config.py
│   └── prompt.py
├── src/
│   ├── api_open_ai/ - модуль для подключения api GROQ
│   │   ├── __init__.py
│   │   └── generating_requests_to_AI.py
│   ├── database/ - модуль с функция БД
│   │   ├── __init__.py
│   │   ├── db_selectors.py
│   │   ├── engine.py
│   │   ├── method_db.py
│   │   └── models.py
│   ├── tests/ - модуль для покрытия кода тестами
│   │   └── __init__.py
│   └── vpn_bot/ - модуль бота
│       ├── handlers/
│       │   ├── __init__.py
│       │   ├── bot.py
│       │   └── utils_bot.py
│       └── __init__.py
├── .env
├── .gitignore
├── create_test_data.py - файл для создания тестовых данных из json
├── requirements.txt
├── start_project.py - файл для локального запуска проекта
├── videos.json - файл json
└── README.md
```