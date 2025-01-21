# Запуск эксперимента

1. Создайте виртуальную рабочую среду:
   
   `python3 -m venv .env`
2. Установите *poetry*:

   `pip install poetry`
3. Установите зависимости:

   `poetry install`
4. Поместите сохраненную pdf-версию презентации "business-policy.pptx" в data/interim/
5. Поместите свой файл .env в корневой каталог. Важно иметь API:
   - GPT_TUNNEL_KEY: от https://gptunnel.ru/
   - BOT_HUB_KEY: от https://bothub.chat
6. Запустите Notebook
7. Выполните шаги в инструкции по запуску (см. Notebook)