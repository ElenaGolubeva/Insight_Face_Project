﻿# Программный комплекс детектирования лиц в реальном времени (Задание на производственную практику)

## Задание для реализации
### Комплекс производит обработку входящего видеопотока с помощью InsightFace-REST, выделяя лица прямоугольной рамкой, извлекает и сохраняет их уникальные вектора в базу данных. Лицо с рамкой выводится в пользовательский интерфейс.

![Схема взаимодействия компонентов приложения.](assets/Scheme.png)
### Общие требования к программному комплексу
- Основным языком программирования при разработке комплекса является Python
- В процессе разработки комплекса необходимо создать минимальную документацию (Описание комплекса и краткое описание логики каждого из микросервисов). [Описание сервисов](https://docs.google.com/document/d/1npOQ2aFH9ho6O3TkJU2lKOWDBeMoCgNtdwlFFGmXBm0/edit?usp=sharing)
- Комплекс должен быть реализован в микросервисной архитектуре
    - Для общения между сервисами следует использовать Apache Kafka/RabbitMQ
    - Для общения с вышеописанными брокерами сообщений разработать интерфейс, позволяющий заменять один брокер другим.
- Набор сервисов в комплексе остаётся на усмотрение разработчика, но обязательными из них являются
    - Сервис-интерфейс для видеопотока
    - Сервис брокера сообщений
    - Сервис InsightFace-REST
    - Сервис базы данных векторов
    - Сервис пользовательского интерфейса
- Метод реализации пользовательского интерфейса остаётся на усмотрение разработчика
- Для хранения векторов лиц использовать базу данных Faiss [2]
- Каждый сервис (за исключением пользовательского интерфейса, в зависимости от реализации) необходимо поместить в Docker-контейнер
- На вход комплекса передаётся видеопоток посредством FFmpeg [3] mpegts или аналогичным способом.
- Комплекс должен производить обработку входного потока посредством InsightFaceREST [1], возвращая
    - Координаты рамок лиц
    - Уникальный вектор каждого лица
- Вектор каждого лица записывается в базу данных
-  Исходный видеопоток с наложенными рамками лиц поступает в пользовательский интерфейс и отображается там


## Описание сервисов

- **Сервис 1 - Ffmpeg**
  - **Описание**
  Отвечает за захват видеопотока с вебкамеры компьютера/ноутбука
  - **Use cases**
  Захват видеопотока в реальном времени
  - **Требования**
  Способность захватывать видеопоток с web-камеры

- **Сервис 2 - frame**
  - **Описание**
  Отвечает за раскадровку видеопотока
  - **Use cases**
    Получение видеопотока 
    Раскадровка видеопотока (1 кадр в секунду)
    Передача изображений в промежуточный сервис worker
  - **Требования**
    Обеспечение непрерывной обработки видеопотока
    Передача изображений в worker

- **Сервис 3 - worker**
  - **Описание**
  Промежуточный сервис, обеспечивающий взаимодействие ключевых сервисов
  - **Use cases**
    Получение изображений от сервиса Frame
    Передача изображений в сервис InsightFace-REST
    Получение векторов лиц и отправка их в сервис Faiss
    Передача обработанных изображений и информации о лицах (координаты рамок векторы) из сервиса InsightFace-REST в User Interface
  - **Требования**
    Надежная интеграция с сервисами frame, Faiss, InsightFace-REST и User Interface
    Эффективная обработка изображений в параллельном режиме для обеспечения высокой производительности

- **Сервис 4 - InsightFace-REST**
  - **Описание**
  Отвечает за детектирование и выделение лиц на изображениях, полученных от сервиса worker
  - **Use cases**
    Получение изображений от сервиса worker
    Обнаружение лиц на изображении
    Выделение лиц рамками
    Передача информации о лицах (векторы, координаты рамок) и обработанного изображения в сервис worker
  - **Требования**
    Высокая точность при обнаружении лиц
    Обработка изображений в параллельном режиме

- **Сервис 5 - Faiss**
  - **Описание**
  Отвечает за хранение уникальных векторов лиц
  - **Use cases**
    Получение векторов лиц от сервиса worker
    Проверка вектора на уникальность
    Добавление вектора в базу данных Faiss
  - **Требования**
    Обеспечение надежного хранения и целостности данных

- **Сервис 6 - User Interface**
  - **Описание**
  Отвечает за отображение результатов обработки видеопотока: изображения с лицом, выделенным рамкой, координат рамки, уникального вектора
  - **Use cases**
    Отображение видеопотока, где лица выделены рамками
    Вывод данных о каждом лице ( вектор и координаты рамки)
  - **Требования**
    Минимально возможная задержка передачи видеопотока



## Запуск приложения
### Для запуска приложения необходимо:
- Установить Docker (Docker Engine для Linux, Docker Desktop для Mac и Windows)
- Запустить Docker (открыть терминал и проверить запуск Docker командой ```docker -version```)
- Открыть корневую папку проекта
- Открыть терминал из текущей папки
- Ввести команду для запуска Ffmpeg для захвата видеопотока (Заменить название устройства, с которого будет производится захват видеопотока)
- Открыть еще один терминал из корневой папки проекта. Вводим следующую команду ```docker-compose up --build``` для развертывания сервисов и создания из docker-образов новых контейнеров.
- Переходим в папку ```cd client``` и запускаем скрипт ```python client.py```. Откроется окно где будет выведен обработанный видеопоток.
- Готово ;)