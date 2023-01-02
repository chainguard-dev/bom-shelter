"""Create csv of top dockerhub images by popularity.

Help from this SO post: https://stackoverflow.com/questions/43426746/api-to-get-top-docker-hub-images

"""

import csv
import json

import requests

RESULTS_FILENAME = "most-popular-dockerhub-images.csv"
FIELDNAMES = ["image_name"]

# create new file to store results
with open(RESULTS_FILENAME, "w", encoding="utf-8") as file:
    writer = csv.writer(file)
    writer.writerow(FIELDNAMES)

# append results to the csv
with open(RESULTS_FILENAME, "a", encoding="utf-8", newline="") as file:
    writer = csv.DictWriter(file, fieldnames=FIELDNAMES)
    # range(1, 11) translates to 1, 2, ... 10
    for page in range(1, 11):
        # note: the dockerhub api is poorly (not?) documented, but this api appears
        # to list images (community images?) by popularity.
        response = requests.get(
            f"https://store.docker.com/api/content/v1/products/search?page={page}&page_size=100&q=%2B&source=community&type=image%2Cbundle"
        )

        if not response.ok:
            print(response.status_code, response.reason, response.text)

        data = json.loads(response.text or response.content)

        for image in data["summaries"]:
            # write each each image name to a new row in the csv
            writer.writerow(
                {
                    "image_name": image["name"],
                }
            )
