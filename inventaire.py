import os
import requests
import json
DOCKER = os.environ.get("DOCKER_API_URL", "http://127.0.0.1:2375")
NETBOX = os.environ.get("NETBOX_URL", "http://127.0.0.1:8080")
JETON = os.environ["NETBOX_TOKEN"]

docker = requests.Session()
docker.headers["Accept"] = "application/json"

def getAllNames():
    reponse = docker.get(f"{DOCKER}/containers/json", timeout=10)
    reponse.raise_for_status()
    return {"code": reponse.status_code, "containers": reponse.json()}

def main():
    allNames = getAllNames()
    print(f"Code HTTP : {allNames['code']}")
    print("Liste des conteneurs : ")
    for container in allNames["containers"]:
        name = container['Names'][0].replace("/", "")
        image = container['Image']
        state = container['State']
        print(f"Nom du conteneur : {name} | Image : {image} | Etat : {state}")

main()