from pathlib import Path

# Главные пути проекта
BASE_DIR = Path(__file__).resolve().parent.parent

# Секретный ключ (остается твоим стандартным)
SECRET_KEY = 'django-insecure-4ju(@-rs*@4hfb1fp1=-&vol+4sdx1*xsll78_alfzm5)+y@ge'

# Режим отладки (True — для разработки, False — перед сдачей клиенту)
DEBUG = True

# Разрешенные домены для работы сайта
ALLOWED_HOSTS = ['127.0.0.1', 'localhost', 'ya-studio.shop', 'www.ya-studio.shop', '85.198.98.67']

# Доверенные адреса для безопасной работы админки через HTTPS
CSRF_TRUSTED_ORIGINS = ['https://ya-studio.shop', 'https://ya-studio.shop']

# Подключенные приложения (Django + твои каталоги)
INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'catalog',
    'orders',
]

# Системные прослойки (исправлено middleware)
MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = 'workshop_project.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [BASE_DIR / 'templates'],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
            ],
        },
    },
]

WSGI_APPLICATION = 'workshop_project.wsgi:application'

# Подключение базы данных SQLite
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': BASE_DIR / 'db.sqlite3',
    }
}

# Валидаторы паролей
AUTH_PASSWORD_VALIDATORS = [
    {'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator'},
    {'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator'},
    {'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator'},
    {'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator'},
]

# Язык и часовой пояс (Сайт будет на русском языке)
LANGUAGE_CODE = 'ru-ru'
TIME_ZONE = 'UTC'
USE_I18N = True
USE_TZ = True

# Настройки статики (CSS, JS, шрифты)
STATIC_URL = 'static/'
STATIC_ROOT = BASE_DIR / 'static/'

# Настройки медиа (картинки товаров из админки)
MEDIA_URL = 'media/'
MEDIA_ROOT = BASE_DIR / 'media/'

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'
# НАСТРОЙКИ ИНТЕРНЕТ-ЭКВАЙРИНГА Т-БАНКА (ТЕСТОВЫЙ РЕЖИМ)
TINKOFF_TERMINAL_KEY = 'TinkoffBankTest'
TINKOFF_SECRET_KEY = 'TinkoffBankTestSecret'
TINKOFF_API_URL = 'https://tinkoff.ru'
# НАСТРОЙКИ TELEGRAM УВЕДОМЛЕНИЙ
TELEGRAM_BOT_TOKEN = '8985203102:AAHZQ09XLnk_I0GQGS0DxYeBXNjVBYMK49Y'
TELEGRAM_CHAT_ID = '964789318'
# НАСТРОЙКИ ОТПРАВКИ EMAIL УВЕДОМЛЕНИЙ ЧЕРЕЗ BEGET (УНИВЕРСАЛЬНЫЙ ЛОКАЛЬНЫЙ ХОСТ)
# НАСТРОЙКИ ОТПРАВКИ EMAIL УВЕДОМЛЕНИЙ ЧЕРЕЗ BEGET (НАДЕЖНОЕ SMTP С ШИФРОВАНИЕМ)
EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
EMAIL_HOST = 'smtp.beget.com'                 # Официальный SMTP-сервер Beget
EMAIL_PORT = 465                               # Защищенный SSL-порт
EMAIL_USE_SSL = True                           # Включаем SSL-шифрование
EMAIL_USE_TLS = False
EMAIL_HOST_USER = 'info@ya-studio.shop'        # Твой почтовый ящик
EMAIL_HOST_PASSWORD = '2345Yjdsqgfhjkm!!'   # Пароль от почты info@ya-studio.shop
DEFAULT_FROM_EMAIL = 'info@ya-studio.shop'     # Адрес, от имени которого будут уходить письма


