import json
import shutil

import aiohttp
import asyncio
import os
from bs4 import BeautifulSoup
from PIL import Image
from io import BytesIO

from benchmark import Benchmark

# Base URL for the Pokémon page on Bulbapedia
baseURL = "https://archives.bulbagarden.net/wiki/"

# Fetching the list of Pokémon from the PokeAPI
pokeapi_url = "https://pokeapi.co/api/v2/pokemon?limit=1025&offset=0"

with open("config.json", "r") as config_file:
    config = json.load(config_file)

image_directory = config["image_directory"]
images_per_pokemon = config["images_per_pokemon"]
clear_image_directory = config["clear_image_directory"]


async def fetch_pokemon_names(session):
    async with session.get(pokeapi_url) as response:
        return await response.json()


async def fetch_images_for_pokemon(session, pokemon_name):
    url = baseURL + "Category:" + pokemon_name.replace(' ', '_')
    async with session.get(url) as response:
        if response.status == 200:
            print(f"Fetching", pokemon_name)
            soup = BeautifulSoup(await response.text(), "html.parser")
            img_tags = soup.find_all("li", {"class": "gallerybox"})
            image_count = 0
            for tag in img_tags:
                width_tag = tag.find("div", style=lambda value: value and "width: 155px" in value)
                thumb_tag = width_tag.find("div", {"class": "thumb"})
                margin_tag = thumb_tag.find("div", style=lambda value: value and "margin:" in value)
                image = margin_tag.find("img", {"alt": ""})
                src = image["src"]
                pokemon_dir = os.path.join(image_directory, pokemon_name.lower().replace(' ', '_'))
                os.makedirs(pokemon_dir, exist_ok=True)
                async with session.get(src) as image_response:
                    img = Image.open(BytesIO(await image_response.read()))
                    png_path = os.path.join(pokemon_dir, f"{image_count}.png")
                    img.save(png_path, "PNG")
                    image_count += 1
                    if image_count >= images_per_pokemon:
                        break
        else:
            print(f"Failed to open {url}")


async def main():
    async with aiohttp.ClientSession() as session:
        pokeapi_data = await fetch_pokemon_names(session)
        names = [pokemon['name'] for pokemon in pokeapi_data['results']]
        print(f"Pokemon:", len(names))

        if clear_image_directory and os.path.exists(image_directory):
            print("Cleaning image directory")
            shutil.rmtree(image_directory)

        if not os.path.exists(image_directory):
            os.makedirs(image_directory)

        tasks = []
        for pokemonName in names:
            task = asyncio.create_task(fetch_images_for_pokemon(session, pokemonName))
            tasks.append(task)
        await asyncio.gather(*tasks)

if __name__ == "__main__":
    bm = Benchmark()
    bm.start()
    asyncio.run(main())
    bm.stop()
    bm.print()
