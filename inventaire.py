import os
import requests
import json
DOCKER = os.environ.get("DOCKER_API_URL", "http://127.0.0.1:2375")
NETBOX = os.environ.get("NETBOX_URL", "http://127.0.0.1:8080")
JETON = os.environ["NETBOX_TOKEN"]

def getAllNames():
    reponse = requests.get(
    f"{DOCKER}/containers/json",
    params={"all": "true"},
    timeout=10,
)
    return {"code": reponse.status_code, "containers": reponse.json()}

def main():
    allNames = getAllNames()
    print(f"Code HTTP : {allNames['code']}")
    print("Nom des conteneurs : ")
    for container in allNames["containers"]:    
        print(container['Names'][0].replace("/", ""))

main()



