from PIL import Image
from io import BytesIO
from dotenv import load_dotenv
from pathlib import Path
from typing import *

import asyncio
import fitz
import requests
import json
import os

from dotenv import load_dotenv
from pathlib import Path
from typing import *
from copy import deepcopy

from typing import  Any

from pydantic import BaseModel, Field

from openai import OpenAI



GPT_TUNNEL = "https://gptunnel.ru/v1/chat/completions"
BOT_HUB =  "https://bothub.chat/api/v2/openai/v1/chat/completions"


# Определим классы для Structured outputs
class Block(BaseModel):
    block_num: int = Field(description="Unique identifier for a text block or line number in the document")
    translated: list[str] = Field(description="List of translations of the original text lines into Russian")

class Page(BaseModel):
    blocks: list[Block] = Field(description="List of text blocks with their Russian translations, organized by block number. Each block contains translated lines corresponding to the original text structure.")


def set_model(model_name: str):
    """Задает имя модели для перевода

    Args:
        model_name (str): Имя модели
    """
    global model
    model = model_name

def set_env_file(env_:Optional[str]):
    """Установить файл с переменными среды
    """
    if env_ is None:
        env_ = input("Введите путь к файлу с переменными среды: ").replace('"', '')
    env = Path(env_).as_posix()
    assert os.path.isfile(env), "No such ENV file!"
    return env


ENV_FILE = set_env_file(r"C:\Users\vallo\Documents\Raft\.env")

def load_env(env_name: str, env_file=ENV_FILE) -> str:
    """Возвращает значение переменной среды 

    Args:
        env_name (str): переменная среды
    Returns:
        str: значение переменной среды
    """
    load_dotenv(env_file)
    with open(env_file, "r") as file:
        try:
            strings = file.readlines()
            variables = {field[0] : field[1].replace("\n", "") for field in [string.split("=") for string in strings]}
    
            return variables[env_name]
        except IndexError:
            print("Your file is empty!")

def get_service_models(url: str, key_name: str) -> list:
    """Просмотр доступных моделей у поставщика

    Args:
        url (str): URL-адрес поставщика
        key_name (str): название API-ключа

    Returns:
        list: список доступных моделей
    """
    api_key = load_env(key_name)
    models = requests.get(
        url,
        headers={
            'Content-Type': 'application/json',
            'Authorization': f'Bearer {api_key}',
        },
    ).json()["data"]
    return [model["id"] for model in models]

def get_chat_completion(service: str, 
                        prompt: str, 
                        model: str, 
                        temperature=0.5,
                        messages: List[Dict[str, str]]=None) -> str:
    """Отвечает на вопрос, используя разных поставщиков моделей

    Args:
        service (str): поставщик
        prompt (str): запрос
        model (str): название модели
        temperature (float, optional): температура для креативности. Defaults to 0.5.
        messages (List[Dict[str, str]]): формализованные сообщения. Defaults None

    Raises:
        Exception: проблема с сетью
        ValueError: проблема с api-key

    Returns:
        str: ответ
    """
    if service == GPT_TUNNEL:
        # Подключение к GPtunnel
        api_key = load_env("GPT_TUNNEL_KEY")
    elif service == BOT_HUB:
        # Подключение к bothub
        api_key = os.load_env("BOT_HUB_KEY")
    elif service == "MISTRAL":
        api_key = load_env("MISTRAL_API_KEY")
        client = Mistral(api_key=api_key)
        chat_response = client.chat.complete(
            temperature = temperature,
            model = model,
            messages = [
                {
                    "role": "user",
                    "content": prompt,
                },
            ]
        )
        return chat_response.choices[0].message.content
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json"
        }
    if messages is None:
        messages = [
            {
                "role": "user",
                "content": prompt
            }
        ]
    data = {
        "temperature": temperature,
        "model": model,
        "messages": messages
    }
    response = requests.post(service, headers=headers, data=json.dumps(data))

    if response.status_code == 200:
        return response.json()['choices'][0]['message']['content']

    else:
        raise Exception(f"Request failed with status code {response.status_code}: {response.text}")

    if not api_key:
        raise ValueError("API key not found. Please set yor KEY!")

async def translate_text(page_dict,
                   method,
                   model, 
                   session=None, 
                   base_url:str='http://176.99.133.170:11434/v1') -> str:
    """Переводит текст с помощью стороннего API

    Args:
        text (str): текст для перевода
        method (Literal["OPENAI", "GPT_TUNNEL", "BOT_HUB"]): API перевода
        model (str): модель для перевода

    Returns:
        str: переведенный
    """
    def get_lengths(input_dict):
        value_lengths = []
        for key, value in input_dict.items():
            value_lengths.append(len(value))
        return (len(value_lengths), value_lengths)
    
    len_dict,  values_lenghts= get_lengths(page_dict)
    system_prompt = "You are a powerful language model. Your task is to process an input dictionary and return a new dictionary that satisfies the following conditions:" \
                    f"\n1. The number of key-value pairs in the returned dictionary must be strictly equal {len_dict}" \
                    "\n2. For each key, the length of the value (a list of strings) in the returned dictionary must be strictly equal to the length of the value (a list of strings) in the input dictionary." \
                    f"\n3. You must translate the content of the strings in the values into Russian, but the length of the list of strings for each key must match the list {values_lenghts}." \
                    "\n4. The returned dictionary must be a valid Python object." \
                    f"\nMake sure that the number of key-value pairs {len_dict} and the list of string lengths for each key match {values_lenghts} the original ones!"
    user_prompt = f"Translate the following dictionary in to Russian: {str(page_dict)}"

    if method == "OPENAI":
        api_key = load_env("OPENAI_API_KEY")
        client = OpenAI(api_key=api_key)
        completion = client.beta.chat.completions.parse(
            model=model,
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt},
            ],
            response_format=Page,
            temperature=0.3,
            max_tokens=1500
        )  

        event = completion.choices[0].message.parsed
        return event

    elif method == "GPT_TUNNEL":
        translated_text = get_chat_completion(GPT_TUNNEL, "", model, messages=messages)
        return translated_text

    elif method == "BOT_HUB":
        translated_text = get_chat_completion(BOT_HUB, "", model, messages=messages)
        return translated_text
    
    elif method == "local":
        client = OpenAI(
            base_url = base_url,
            api_key='ollama', # required, but unused
        )
        completion = client.beta.chat.completions.parse(
            model=model,
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt},
            ],
            response_format=Page,
            temperature=0.3,
            max_tokens=1500
        )   

        event = completion.choices[0].message.parsed
        return event
    
async def translate_structured(pdf_info: dict, 
                            base_url: Optional[str]=None):
    """
    Возврат переведенного текста по местам
    """
    def page_to_dict(page: Page) -> dict:
        """
        Преобразует объект Page в словарь формата {block_num: translated_lines}
        
        Args:
            page (Page): Объект Page с переведенными блоками текста
            
        Returns:
            dict: Словарь, где ключ - номер блока, значение - список переведенных строк
        """
        return {block.block_num: block.translated for block in page.blocks}
    
    pages_list = []
    for page_info in pdf_info["pages"]:
        text_dict = {}
        for block in page_info["text_frames"]:
            if block["type"] == 0:
                block_text = [span["text"] for line in block["lines"] for span in line["spans"]]
                text_dict[int(block["number"])] = block_text
                # json_page = json.dumps(text_dict)
        pages_list.append(text_dict)

    to_translate = [translate_text(
                                    page,
                                    method="OPENAI",
                                    model=model
                                ) for page in pages_list]

    translated = await asyncio.gather(*to_translate)
    translated_dict = [page_to_dict(page_translated) for page_translated in translated]
    return translated_dict

def fill_translated_meatadata(original_meta: dict, 
                              translated_dict):
    pdf_info = deepcopy(original_meta)
    for page_info, text_dict in zip(pdf_info["pages"], translated_dict):
        for block in page_info["text_frames"]:
            if block["type"] == 0:
                block_key = int(block['number'])
                if block_key in text_dict:
                    translated_lines = text_dict[block_key]
                    line_index = 0
                    for line in block["lines"]:
                        for span in line["spans"]:
                            if line_index < len(translated_lines):
                                span["text"] = translated_lines[line_index]
                                line_index += 1
    return pdf_info

def extract_metadata_pymupdf(pdf_path: str) -> Dict[Dict[dict, dict], List[int]]:
    """Извлекает метаданные из pdf файла

    Args:
        pdf_path (str): путь к pdf

    Returns:
        Dict[Dict[dict, dict], List[int]]: словарь из метаданных
    """
    document = fitz.open(pdf_path)
    pdf_info = {
        "document_title": document.metadata.get("title", "Unknown"),
        "pages": []
    }

    for page_number in range(len(document)):
        # Бегаем по страницам
        page = document.load_page(page_number)
        #  Нас интересуют: номер, ее ширина и высота, текстовые фреймы и картинки
        page_info = {
            "page_number": page_number + 1,
            "bbox": {"width" : None, "height" : None},
            "text_frames": [],
            "graphics": page.get_drawings()
        }
        page_data = page.get_text("dict")
        page_info["bbox"]["width"] = page_data["width"]
        page_info["bbox"]["height"] = page_data["height"]
        page_info["text_frames"] = page_data["blocks"]
        pdf_info["pages"].append(page_info)
    return pdf_info

def get_color_rgb(color: Any) -> Any:
    """Преобразование цветов для формата PyMuPDF

    Args:
        color (Any): цветовая палитра

    Returns:
        Any: преобразованная цветовая палитра
    """
    r = (color >> 16) & 0xFF
    g = (color >> 8) & 0xFF
    b = color & 0xFF
    color_rgb = (r / 255, g / 255, b / 255)
    return color_rgb

def scale_dimension(val, source_size, target_size):
    return val * (target_size / source_size)

def create_pdf_pymupdf(pdf_info: dict, 
                       path_to: str) -> str:
    """Создает переведенный pdf

    Args:
        pdf_info (str): словарь с данными pdf
        path_to (str): путь к сформированному pdf
    Returns:
        str: переданный путь к сформированному pdf
    """
    supported_fonts = ["Times-Roman", "Helvetica", "Courier", "Times-Bold", "Helvetica-Bold"]
    status = "OK"

    try:
        document = fitz.open()

        for page_info in pdf_info["pages"]:
            width = page_info["bbox"]["width"]
            height = page_info["bbox"]["height"]
            page = document.new_page(width=width, height=height)

            paths = page_info['graphics']
            shape = page.new_shape()
            for path in paths:
                for item in path["items"]:
                    if item[0] == "l":  # line
                        shape.draw_line(item[1], item[2])
                    elif item[0] == "re":  # rectangle
                        shape.draw_rect(item[1])
                    elif item[0] == "qu":  # quad
                        shape.draw_quad(item[1])
                    elif item[0] == "c":  # curve
                        shape.draw_bezier(item[1], item[2], item[3], item[4])

                shape.finish(
                    fill=path["fill"],  # fill color
                    color=path["color"],  # line color
                    dashes=path["dashes"],  # line dashing
                    even_odd=path.get("even_odd", True),  # control color of overlaps
                    closePath=path["closePath"],  # whether to connect last and first point
                    width=path["width"],  # line width
                )
            shape.commit()

            # Работаем с картинками и текстом
            for block in page_info["text_frames"]:
                if block["type"] == 1:  # Картинка
                    bbox = fitz.Rect(block["bbox"])
                    image_bytes = block["image"]
                    width = block["width"]
                    height = block["height"]

                    # Фильтрация по размерам
                    if 10 <= width <= 100 and 10 <= height <= 100:
                        # Загрузка изображения с помощью PIL
                        image = Image.open(BytesIO(image_bytes)).convert("RGBA")

                        data = image.getdata()
                        new_data = []
                        for item in data:
                            if item[0] < 30 and item[1] < 30 and item[2] < 30:
                                new_data.append((0, 0, 0, 0))  # Прозрачный
                            else:
                                new_data.append(item)
                        image.putdata(new_data)

                        # Конвертация изображения в байты для хранения в метаданных
                        output_buffer = BytesIO()
                        image.save(output_buffer, format="PNG")
                        output_buffer.seek(0)

                        page.insert_image(bbox, stream=output_buffer.getvalue())
                    else:
                        page.insert_image(bbox, stream=image_bytes)

                elif block["type"] == 0:  # Текстовый блок
                    for line in block["lines"]:
                        for span in line["spans"]:
                            # ПРОБЛЕМА С ВЫХОДОМ ДЛИННОГО ТЕКСТА ЗА ГРАНИЦЫ СЛАЙДА РЕШЕНА ЧАСТИЧНО!
                            text = span['text']
                            font = span["font"]
                            color = get_color_rgb(span['color'])
                            flag = span["flags"]
                            if flag & 2 ** 4:  # Bold
                                font = "tibo"
                            if flag & 2 ** 1:  # Italic
                                font = "tiit"
                            if font not in supported_fonts:
                                font = "tiro"
                            font = fitz.Font(font)
                            fontsize = span["size"] * 0.6 if span["size"] * 0.6 <= 26 else 26
                            page.insert_font(fontname="F0", fontbuffer=font.buffer)
                            page.insert_text(
                                point=(span['origin'][0], span['origin'][1]),
                                text=text,
                                fontname="F0",
                                fontsize=fontsize,
                                color=color
                            )

        document.save(path_to)
    except Exception as e:
        status = "FAILED"
        print(f"{status}: {e}")
    return path_to   
