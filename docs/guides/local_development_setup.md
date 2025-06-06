# Настройка Локального Окружения Разработки

Это руководство описывает шаги, необходимые для настройки вашего компьютера для разработки проекта "SCB DB".

## 1. Пререквизиты (Необходимое ПО)

Перед началом убедитесь, что на вашем компьютере установлены следующие инструменты:

### Git
Система контроля версий. Необходима для получения исходного кода проекта и управления изменениями.
*   **Проверка установки:** `git --version`
*   **Инструкции по установке:** [https://git-scm.com/book/en/v2/Getting-Started-Installing-Git](https://git-scm.com/book/en/v2/Getting-Started-Installing-Git)

### Python
Язык программирования для бэкенда и ETL.
*   **Требуемая версия:** 3.10 или выше.
*   **Проверка установки:** `python --version` или `python3 --version`
*   **Инструкции по установке:** [https://www.python.org/downloads/](https://www.python.org/downloads/)

### Poetry (Рекомендуется для Python)
Менеджер зависимостей и упаковщик для Python-проектов. Используется для бэкенда и ETL.
*   **Проверка установки:** `poetry --version`
*   **Инструкции по установке:** [https://python-poetry.org/docs/#installation](https://python-poetry.org/docs/#installation)
*   *Примечание: Если вы не используете Poetry, убедитесь, что у вас установлен `pip` (обычно идет с Python) для работы с `requirements.txt`.*

### Node.js и npm
Платформа JavaScript и менеджер пакетов для фронтенд-разработки.
*   **Рекомендуемая версия Node.js:** LTS (Long Term Support).
*   **Проверка установки:** `node -v` и `npm -v`
*   **Инструкции по установке:** [https://nodejs.org/](https://nodejs.org/) (npm устанавливается вместе с Node.js)

### Yarn (Опционально, альтернатива npm)
Если проект использует Yarn для управления фронтенд-зависимостями.
*   **Проверка установки:** `yarn --version`
*   **Инструкции по установке (через npm):** `npm install --global yarn`

### Docker и Docker Compose
Платформа для контейнеризации. Используется для запуска баз данных (MongoDB, ClickHouse) и Airflow в изолированных окружениях во время локальной разработки и для развертывания.
*   **Проверка установки:** `docker --version` и `docker-compose --version` (или `docker compose version`)
*   **Важно:** Убедитесь, что сервис Docker запущен на вашем компьютере.
*   **Инструкции по установке:** [https://www.docker.com/products/docker-desktop/](https://www.docker.com/products/docker-desktop/)

### Редактор Кода / IDE
Рекомендуется использовать IDE с хорошей поддержкой Python, TypeScript, Docker, например:
*   Visual Studio Code (VS Code)
*   PyCharm (для Python/Backend)
*   WebStorm (для TypeScript/Frontend)

Установите релевантные расширения/плагины для вашего IDE для улучшения процесса разработки (например, для линтинга, форматирования, автодополнения).

## 2. Получение Исходного Кода
(Этот шаг вы уже должны были выполнить)

Клонируйте репозиторий проекта:
```bash
git clone <URL_ВАШЕГО_УДАЛЕННОГО_РЕПОЗИТОРИЯ> scb-data-platform
cd scb-data-platform

## 3. Инициализация Подпроектов

После клонирования репозитория необходимо инициализировать каждый подпроект (backend, frontend, etl) и установить их зависимости.

### Backend (Python/Poetry)

1.  Перейдите в директорию `backend`:
    ```bash
    cd backend
    ```
2.  Установите зависимости с помощью Poetry:
    ```bash
    poetry install
    ```
    *Примечание: `poetry install` прочитает `pyproject.toml` и `poetry.lock` и установит все необходимые пакеты.*
3.  Вернитесь в корневую директорию проекта:
    ```bash
    cd ..
    ```

### ETL (Python/Poetry)
На данном этапе для MVP зависимости ETL будут управляться внутри Docker-образа Airflow. Если в будущем потребуется локальный запуск ETL-скриптов или утилит, связанных с Airflow, необходимо будет выполнить `poetry install` в директории `etl/` после добавления соответствующих зависимостей в `etl/pyproject.toml`.

### Frontend (Node.js/npm или Yarn)

1.  Перейдите в директорию `frontend`:
    ```bash
    cd frontend
    ```
2.  Установите зависимости с помощью npm:
    ```bash
    npm install
    ```
    Или, если проект использует Yarn:
    ```bash
    yarn install
    ```
3.  Вернитесь в корневую директорию проекта:
    ```bash
    cd ..
    ```
## 4. Запуск Базовых Сервисов (Docker Compose)" после раздела 

Docker Compose используется для запуска БД