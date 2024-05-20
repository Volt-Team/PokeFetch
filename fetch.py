import io
import os
import requests
from bs4 import BeautifulSoup
from PIL import Image

from benchmark import Benchmark

# Base URL for the Pokémon page on Bulbapedia
baseURL = "https://archives.bulbagarden.net/wiki/"

bm = Benchmark()
bm.start()

# Fetching the list of Pokémon from the PokeAPI
pokeapi_url = "https://pokeapi.co/api/v2/pokemon?limit=151&offset=0"
pokeapi_response = requests.get(pokeapi_url)
pokeapi_data = pokeapi_response.json()

images_per_pokemon = 7

image_directory_name = "image_data"


def fetch():
    # Check if the request was successful
    if pokeapi_response.status_code == 200:
        # Extracting the names of the Pokémon
        names = [pokemon['name'] for pokemon in pokeapi_data['results']]

        # Ensure the 'image_directory_name' directory exists
        if not os.path.exists(image_directory_name):
            os.makedirs(image_directory_name)

        for pokemonName in names:
            url = baseURL + "Category:" + pokemonName.replace(' ', '_')
            print(url)

            response = requests.get(url=url)

            if response.status_code == 200:
                soup = BeautifulSoup(response.text, "html.parser")

                img_tags = soup.find_all("li", {"class": "gallerybox"})

                image_count = 0  # Initialize the counter for images per Pokémon

                for tag in img_tags:
                    width_tag = tag.find("div", style=lambda value: value and "width: 155px" in value)

                    thumb_tag = width_tag.find("div", {"class": "thumb"})

                    margin_tag = thumb_tag.find("div", style=lambda value: value and "margin:" in value)

                    image = margin_tag.find("img", {"alt": ""})

                    src = image["src"]

                    # Construct the path where the image will be saved
                    pokemon_dir = os.path.join(image_directory_name, pokemonName.lower().replace(' ', '_'))
                    os.makedirs(pokemon_dir, exist_ok=True)  # Create the directory if it doesn't exist

                    # Directly convert the image to PNG without saving as JPG
                    image_response = requests.get(src)
                    img = Image.open(io.BytesIO(image_response.content))
                    png_path = os.path.join(pokemon_dir, f"{image_count}.png")
                    img.save(png_path, "PNG")

                    image_count += 1  # Increment the counter for each image fetched

                    if image_count >= images_per_pokemon:  # Stop fetching images once 7 have been fetched
                        break
            else:
                print(f"Failed to open {url}")
    else:
        print(f"Failed to open {pokeapi_url}")


if __name__ == "__main__":
    fetch()

bm.stop()
bm.print()