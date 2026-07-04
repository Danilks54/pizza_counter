# 🍕Pizza Counter🍕

Веб-приложение для подсчёта пицц на фотографиях с использованием нейросети YOLOv8.

**Цель работы:** разработка системы для автоматического учёта приготовленных пицц в кафе на основе компьютерного зрения.

## Технологии

- **Python 3.11**
- **Flask**
- **YOLOv8**
- **OpenCV**
- **SQLite**
- **HTML5 / CSS3 / JavaScript**

## Установка и запуск

### Клонирование репозитория
```bash
git clone https://github.com/Ваш_ник(Danilks54)/pizza-counter.git
cd pizza-counter

## создание виртуального окружения
python -m venv .venv
## В Win (PowerShell)
.\.venv\Scripts\activate

## Установка зависимостей
python -m pip install -r requirements.txt

# Запуск приложения
python app.py

# После запуска переходим по адресу 
http://localhost:5000