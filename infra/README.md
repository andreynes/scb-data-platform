# Инфраструктура Проекта "SCB DB"

## Локальное Окружение с Docker Compose

Для локальной разработки и тестирования используется Docker Compose для запуска необходимых сервисов, таких как базы данных.

### Запуск Баз Данных (MongoDB и ClickHouse)

1.  Убедитесь, что у вас установлен Docker и Docker Compose.
2.  Перейдите в директорию `infra/compose/`:
    ```bash
    cd infra/compose
    ```
3.  Создайте файл `.env` из шаблона `.env.example`:
    ```bash
    cp .env.example .env
    ```
4.  Отредактируйте файл `.env` и укажите ваши учетные данные для MongoDB и ClickHouse.
    **Важно:** Не коммитьте файл `.env` в Git!
5.  Запустите контейнеры:
    ```bash
    docker-compose up -d
    ```
    (Или `docker compose up -d` для новых версий Docker).
6.  Чтобы проверить статус контейнеров:
    ```bash
    docker-compose ps
    ```
7.  Чтобы остановить контейнеры:
    ```bash
    docker-compose down
    ```
    Для удаления томов с данными (ВНИМАНИЕ: ДАННЫЕ БУДУТ УДАЛЕНЫ):
    ```bash
    docker-compose down -v
    ```