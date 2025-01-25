# Doc2Ru

<a target="_blank" href="https://cookiecutter-data-science.drivendata.org/">
    <img src="https://img.shields.io/badge/CCDS-Project%20template-328F97?logo=cookiecutter" />
</a>

Этот сервис переводит любой документ с английского языка на русский

# ML System Design Doc (Translator)

## 1. Цели и предпосылки

### 1.1 Зачем идем в разработку продукта?

#### Бизнес-цели:
- Повышение скорости и качества анализа документов на иностранном языке.
- Обеспечение безопасности NDA данных.
- Автоматизация процесса перевода презентаций для сотрудников компании.
- Доступность в Российском регионе.
- Снижение издержек на перевод.

#### Проблематика:
- Большинство технических презентаций на английском языке.
- Временные и финансовые затраты на перевод.
- Неточная передача технических терминов.
- Сложности сохранения форматирования (таблицы, графики).

#### Преимущества использования ИИ:
- Быстрота перевода.
- Обучение модели на специфических данных.
- Снижение затрат при больших объемах.
- Простая доступность.

#### Критерии успеха:
- Уменьшение времени перевода.
- Сохранение форматирования документа.
- Перевод всех текстовых блоков.

### 1.2 Бизнес-требования и ограничения

#### Требования:
- Разработка интерфейса для перевода (Telegram Bot).
- Качественный перевод текста.
- Преобразование формата doc → doc с сохранением оформления.
- Защита данных.

#### Ограничения:
- Использование GPU Nvidia 3090.
- Краткие сроки на разработку.

#### Итерации проекта:
1. **PoC**: Прототипирование функционала в Jupyter Notebooks.
   - Извлечение текста.
   - Перевод с помощью LLM.
   - Сохранение форматирования.

2. **MVP**: Тестирование в контролируемой среде.
   - Расширение поддержки элементов.
   - Внедрение Telegram Bot.
   - Улучшение алгоритмов перевода.

---

## 2. Методология

### 2.1 Постановка задачи
Автоматизация перевода документов с сохранением точности, структуры и оформления.

### 2.2 Блок-схема решения
1. Подготовка данных: извлечение текста.
2. Выбор модели: настройка LLM.
3. Оптимизация: улучшение точности и скорости.
4. Тестирование: проверка на реальных данных.
5. Закрытие технического долга.
6. Интеграция интерфейса.

### 2.3 Этапы:
1. Извлечение данных (тексты, графики, таблицы).
2. Перевод текста с сохранением структуры.
3. Формирование документа.
4. Сбор обратной связи.
5. Формирование отчета.

---

## 3. Подготовка MVP

### Оценка эффективности:
- **Скорость**: перевод 1 слайда за 10–15 секунд.
- **Покрытие**: поддержка 95% типов фреймов.
- **Шрифты**: сохранение 70% оригинальных.
- **Интерфейс**: работа через Telegram Bot.
- **Точность**: BLEU/ROUGE ≥ 80%.
- **Обработка**: успешная обработка 95% слайдов.
- **Стабильность**: корректная работа при разных нагрузках.

---

## 4. Архитектура
- Презентация проекта с подробной архитектурой доступна по [ссылке](https://docs.google.com/presentation/d/1lZ9PASf-2Ngk5St_LYpK3-K-gRitVTxCkNtE6os5dzk/edit?usp=sharing)
- Сервер: Nvidia 3090 GPU, 24 GB RAM.
- Запись с демонстрацией работы сервиса доступна по [ссылке](https://drive.google.com/file/d/1HACVt8pPjjaivMyLk7k13JpX6DvBofMf/view?usp=sharing)

## **Project Organization**

```
├── LICENSE            <- Open-source license if one is chosen
├── Makefile           <- Makefile with convenience commands like `make data` or `make train`
├── README.md          <- The top-level README for developers using this project.
├── data
│   ├── external       <- Data from third party sources.
│   ├── interim        <- Intermediate data that has been transformed.
│   ├── processed      <- The final, canonical data sets for modeling.
│   └── raw            <- The original, immutable data dump.
│
├── docs               <- A default mkdocs project; see www.mkdocs.org for details
│
├── models             <- Trained and serialized models, model predictions, or model summaries
│
├── notebooks          <- Jupyter notebooks. Naming convention is a number (for ordering),
│                         the creator's initials, and a short `-` delimited description, e.g.
│                         `1.0-jqp-initial-data-exploration`.
│
├── pyproject.toml     <- Project configuration file with package metadata for 
│                         doc2ru and configuration for tools like black
│
├── references         <- Data dictionaries, manuals, and all other explanatory materials.
│
├── reports            <- Generated analysis as HTML, PDF, LaTeX, etc.
│   └── figures        <- Generated graphics and figures to be used in reporting
│
├── requirements.txt   <- The requirements file for reproducing the analysis environment, e.g.
│                         generated with `pip freeze > requirements.txt`
│
├── setup.cfg          <- Configuration file for flake8
│
└── doc2ru   <- Source code for use in this project.
    │
    ├── __init__.py             <- Makes doc2ru a Python module
    │
    ├── config.py               <- Store useful variables and configuration
    │
    ├── dataset.py              <- Scripts to download or generate data
    │
    ├── features.py             <- Code to create features for modeling
    │
    ├── modeling                
    │   ├── __init__.py 
    │   ├── predict.py          <- Code to run model inference with trained models          
    │   └── train.py            <- Code to train models
    │
    └── plots.py                <- Code to create visualizations
```

--------
