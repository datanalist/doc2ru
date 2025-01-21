## Порядок запуска:
1. На сервере:
   1. `docker exec -d ollama ollama run qwen2.5:14b`
   2. `docker run --net=host -it -e NGROK_AUTHTOKEN=xxx ngrok/ngrok:latest http 80`
2. На компе с ботом:
   1. Запускаем `main.py`