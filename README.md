# Система обработки платежей

Система обработки платежей на базе **FastAPI**, **PostgreSQL**, **RabbitMQ** с использованием паттерна **Outbox**.

---

# Описание проекта

Проект демонстрирует **надёжную event-driven архитектуру** для обработки платежей:

- API принимает запросы на создание платежей
- Данные сохраняются в PostgreSQL
- Паттерн Outbox гарантирует консистентность событий
- Фоновый worker публикует события в RabbitMQ
- Consumer обрабатывает события асинхронно

---

# Архитектура

```text
Клиент
  ↓
FastAPI (API сервис)
  ↓
PostgreSQL (Payments + Outbox)
  ↓
Outbox Worker
  ↓
RabbitMQ
  ↓
Payment Consumer
```

---

# ⚙️ Технологии

- FastAPI — REST API
- PostgreSQL 15 — основная база данных
- RabbitMQ — брокер сообщений
- SQLAlchemy (async) — ORM
- Alembic — миграции базы данных
- Docker & Docker Compose — контейнеризация и оркестрация

---

# 🚀 Быстрый старт

## 📌 Требования

- Docker
- Docker Compose

---

## Клонирование репозитория

```bash
git clone https://github.com/Maksonchik26/payments_processing.git
cd payments_processing
```

---

## ⚙️ Конфигурация

Скопируйте файл:
   ```bash
   cp .env.example .env
   ```
   
---


## ▶️ Запуск проекта

```bash
docker compose up --build -d
```

После запуска будут доступны:

- API → http://localhost:8000  
- RabbitMQ UI → http://localhost:15672  
- PostgreSQL → localhost:5432  

---

# 🧱 Архитектура запуска

## 🔹 Порядок старта сервисов

```text
PostgreSQL (healthy)
   ↓
RabbitMQ (healthy)
   ↓
Миграции (alembic upgrade head)
   ↓
API + Workers
```

---


# 📡 API

## ➕ Создание платежа

POST /payments

### Тело запроса

```json
{
    "amount": 1244.244,
    "currency": "RUB",
    "description": "Платеж определенного банка",
    "webhook_url": "http://url.ru"
}
```

### Пример ответа

```json
{
    "payment_id": "7b83688f-be61-453b-95bf-4a9cd688339d",
    "status": "pending",
    "created_at": "2026-04-22T05:38:06.850227Z"
}
```

---

## 📥 Получение платежа

GET /payments/{payment_id}

### Пример ответа

```json
{
    "payment_id": "2ff3c9d3-3897-40d7-8ca8-6ac9836f7c5c",
    "amount": "1244.24",
    "currency": "RUB",
    "description": "Платеж определенного банка",
    "metadata_json": {
        "key": "val"
    },
    "status": "succeeded",
    "webhook_url": "http://url.ru/",
    "created_at": "2026-04-22T05:06:52.292373Z",
    "processed_at": "2026-04-22T05:13:10.460124Z"
}
```

---

# 📨 Поток обработки событий (Outbox Pattern)

## Гарантии:

- отсутствие потери событий
- согласованность базы данных и брокера сообщений
- надёжная асинхронная обработка

```text
API → транзакция БД
        ↓
   таблица outbox
        ↓
 Outbox Worker
        ↓
 RabbitMQ
        ↓
 Consumer
```

---

# 🔒 Надёжность системы

## ✔ Реализовано

- транзакционный Outbox Pattern
- healthcheck для PostgreSQL и RabbitMQ
- корректный порядок запуска сервисов
- безопасная Docker-оркестрация
- отдельный контейнер для миграций

---

# 🧪 Проверка работы

## 1. Запуск системы

docker compose up --build -d

---

## 2. Создать платёж
```bash
curl -X POST http://localhost:8000/v1/payments \
  -H "Content-Type: application/json" \
  -H "X-API-Key: my_secret_static_key_123" \
  -H "Idempotency-Key: 555" \
  -d '{
      "amount": 1244.244,
      "currency": "RUB",
      "description": "Платеж определенного банка",
      "webhook_url": "http://url.ru"
}'
```
---

## 3. Получение информации оп латеже
```bash
curl http://localhost:8000/v1/payments/{payment_id} \
  -H "Content-Type: application/json" \
  -H "X-API-Key: my_secret_static_key_123" \
```

---

## 4. RabbitMQ UI

http://localhost:15672  

логин / пароль:
guest / guest

---

# 🧩 Ключевые архитектурные решения

## 1. Outbox Pattern
Обеспечивает гарантированную доставку событий даже при сбоях.

## 2. Отдельный контейнер миграций
Исключает гонки при создании схемы БД.

## 3. Healthcheck + service_completed_successfully
Гарантирует правильный порядок запуска сервисов.

## 4. Stateless workers
Позволяет горизонтальное масштабирование обработки сообщений.

---


# 🏁 Итог

Проект реализует надёжную event-driven архитектуру с:

- гарантированной доставкой сообщений
- безопасным запуском сервисов
- воспроизводимой инфраструктурой
- готовностью к масштабированию
