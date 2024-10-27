# Отчёт к занятию 28.10
* Подготовлена первая версия [онтологии наивной теории множеств в текстовом виде](https://github.com/aVorotnikov/ontologer/blob/master/ontology_inserter/ontologies/set_theory.json) для загрузки в БД.
* Реализована загрузка онтологий в БД - [скрипт](https://github.com/aVorotnikov/ontologer/blob/master/ontology_inserter/ontology_inserter.py).
* Реализована первая версия формирования промта по отнологиям - [скрипт](https://github.com/aVorotnikov/ontologer/blob/master/bot/construct_sequence.py).
* Начаты работы по проектированию конечной системы - бота:
    + [Модель предметной области](https://github.com/aVorotnikov/ontologer/blob/master/docs/diagrams/bot_domain.png)
    + [Машина состояний бота при работе с пользователем](https://github.com/aVorotnikov/ontologer/blob/master/docs/diagrams/state_machines/main.png) - с вынесенными состояниями пока непонятно, возможно там не получится отобразить работу через состояния
    + [Диаграмма размещения](https://github.com/aVorotnikov/ontologer/blob/master/docs/diagrams/bot.png)
