import csv
import requests
from bs4 import BeautifulSoup
import telebot
import time
from io import BytesIO
from PIL import Image
from telebot import types

# Reemplaza con tu token de bot y el ID de tu chat
bot_token = '7611698734:AAHtOPYYOoLdkiPrYcPKV2FhKlz1DfQfHZ8'
chat_id = 168278914



# Archivo CSV para almacenar los IDs de las entradas enviadas
sent_post_ids_file = 'sent_post_ids.csv'


def check_for_updates():
    url = "https://plotn08.org/"

    try:
        # Realizar la solicitud y procesar el HTML
        response = requests.get(url)
        response.raise_for_status()  # Levanta una excepción si la solicitud falla
        soup = BeautifulSoup(response.content, 'html.parser')

        posts = soup.find_all('div', class_='postEntry')

        # Leer los IDs de las entradas ya enviadas del archivo CSV
        sent_post_ids = set()
        try:
            with open(sent_post_ids_file, 'r') as f:
                reader = csv.reader(f)
                for row in reader:
                    if row:  # Verifica si la fila no está vacía
                        post_id = row[0]
                        sent_post_ids.add(row[0])
        except FileNotFoundError:
            # Si el archivo no existe, se crea uno nuevo (vacío)
            pass

        for post in posts:
            if 'id' in post.attrs:
                post_id = post['id']
                # Verificar si el post es el que queremos omitir
                if post_id != 'post-501555':
                   if post_id not in sent_post_ids:
                      try:
                    # ... (tu código para procesar la entrada)
                         post_meta = post.find('div', class_='postMeta')
                         title = post_meta.find('h1').text
                         link = post_meta.find('a')['href'] 
                
                         category_b = post_meta.find('b', class_='additional_category_img')
                         category = category_b.text.strip()

                         post_content = post.find('div', class_='postContent')
                         image_url = post_content.find('img')['src']

                        # Descargar la imagen
                         response = requests.get(image_url)
                         img = Image.open(BytesIO(response.content))
                         img_bytes = BytesIO()
                         if img.mode == 'RGBA':
                            img = img.convert('RGB')
                         img.save(img_bytes, format='JPEG')
                         img_bytes.seek(0)

                         # Crear un teclado inline con un botón
                         markup = types.InlineKeyboardMarkup()
                         button = types.InlineKeyboardButton(text="Ver artículo", url=link)
                         markup.add(button)

                         # Enviar el mensaje con la imagen y el botón
                         bot.send_photo(chat_id, photo=img_bytes, caption=f"☑ Título: {title}\n🎧 Género: {category}", reply_markup=markup)
                      except Exception as e:
                          print(f"Error al procesar la entrada {post_id}: {e}")
                      else:
                          sent_post_ids.add(post_id)
                else:
                    print(f"El post {post_id} está fijado y será omitido.")
            else:
                print(f"Advertencia: El post no tiene un atributo 'id'.")

        # Escribir los IDs actualizados en el archivo CSV
        with open(sent_post_ids_file, 'w') as f:
            writer = csv.writer(f)
            for post_id in sent_post_ids:
                writer.writerow([post_id])

    except requests.exceptions.RequestException as e:
        print(f"Error en la solicitud HTTP: {e}")
    except Exception as e:
        print(f"Error general: {e}")

bot = telebot.TeleBot(token=bot_token)

# Ejecutar el bot en un bucle infinito
while True:
    try:
        check_for_updates()
    except Exception as e:
        print(f"Error en la ejecución: {e}")
    time.sleep(60 * 5)  # Ejecutar cada 5 minutos