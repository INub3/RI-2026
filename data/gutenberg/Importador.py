import os
import requests
from bs4 import BeautifulSoup
import time
import re
from urllib.parse import urlparse

def descargar_top_100_gutenberg():
    # 1. Configuración de rutas y URL
    base_url = "https://www.gutenberg.org"
    list_url = "https://www.gutenberg.org/browse/scores/top1000.php"
    folder_path = r"C:\Users\Michael\Documents\7mo\ir2026\data\gutenberg\data"
    
    # Crear la carpeta si no existe
    if not os.path.exists(folder_path):
        os.makedirs(folder_path)
        print(f"Carpeta creada en: {folder_path}")

    print("Obteniendo lista de libros...")
    try:
        response = requests.get(list_url, timeout=10)
        response.raise_for_status()
    except Exception as e:
        print(f"Error al acceder a la página: {e}")
        return

    soup = BeautifulSoup(response.text, 'html.parser')
    
    # 2. Localizar la sección "Top 1000 EBooks yesterday"
    # Buscamos el encabezado h2 que contiene el texto y luego la lista ol siguiente
    header = soup.find('h2', string=re.compile(r'Top 1000 EBooks yesterday', re.I))
    if not header:
        print("No se pudo encontrar la sección de los Top 1000.")
        return

    top_list = header.find_next('ol')
    items = top_list.find_all('li')[:1000] # Limitamos a los primeros 1000

    print(f"Se encontraron {len(items)} libros. Iniciando descarga...")

    for index, item in enumerate(items, start=1):
        # Extraer nombre y link de la página del ebook
        link_tag = item.find('a')
        if not link_tag:
            continue
            
        book_title = link_tag.get_text()
        # Limpiar el título para que sea un nombre de archivo válido
        clean_title = re.sub(r'[\\/*?:"<>|]', "", book_title)
        book_page_url = base_url + link_tag['href']
        
        try:
            # Entrar a la página del libro para buscar el link del TXT
            book_page = requests.get(book_page_url, timeout=10)
            book_soup = BeautifulSoup(book_page.text, 'html.parser')
            
            # Buscar el enlace que contiene el texto plano
            txt_link = None
            for a in book_soup.find_all('a', href=True):
                if ".txt.utf-8" in a['href']:
                    txt_link = a['href']
                    break
            
            if txt_link:
                # Si el link es relativo, completar la URL
                if txt_link.startswith('/'):
                    txt_link = base_url + txt_link
                
                # Obtener el nombre del archivo de la URL, removiendo .utf-8 si existe
                parsed = urlparse(txt_link)
                path = parsed.path
                if path.endswith('.utf-8'):
                    path = path[:-6]
                file_name = "pg" + os.path.basename(path)
                
                full_path = os.path.join(folder_path, file_name)
                
                # Descargar el contenido del TXT
                txt_content = requests.get(txt_link, timeout=30).text
                
                with open(full_path, "w", encoding="utf-8") as f:
                    f.write(txt_content)
                
                print(f"Descargado ({index}/1000): {file_name}")
            else:
                print(f"No se encontró formato TXT para: {book_title}")

            # Pequeña pausa para no saturar el servidor
            time.sleep(0.5)

        except Exception as e:
            print(f"Error descargando {book_title}: {e}")

    print("\nProceso finalizado. Revisa tu carpeta en el Escritorio.")

if __name__ == "__main__":
    descargar_top_100_gutenberg()