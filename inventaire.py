import os
import requests
import json
DOCKER = os.environ.get("DOCKER_API_URL", "http://127.0.0.1:2375")
NETBOX = os.environ.get("NETBOX_URL", "http://127.0.0.1:8080")
JETON = os.environ["NETBOX_TOKEN"]

docker = requests.Session()
docker.headers["Accept"] = "application/json"


def getContainerStats(id: str):
    reponse = docker.get(f"{DOCKER}/containers/{id}/stats", params={"stream": "false"}, timeout=10)
    reponse.raise_for_status()
    stats = reponse.json()
    cpu, avant = stats["cpu_stats"], stats["precpu_stats"]
    delta_cpu = cpu["cpu_usage"]["total_usage"] - avant["cpu_usage"]["total_usage"]
    delta_systeme = cpu["system_cpu_usage"] - avant.get("system_cpu_usage", 0)
    pourcent = delta_cpu / delta_systeme * cpu["online_cpus"] * 100 if delta_systeme else 0.0
    memoire_mo = stats["memory_stats"]["usage"] / 1024 / 1024
    return {"CPU": pourcent, "Memory": memoire_mo}

def getAllNames():
    reponse = docker.get(f"{DOCKER}/containers/json", params={"all": "true"}, timeout=10)
    reponse.raise_for_status()
    return {"code": reponse.status_code, "containers": reponse.json()}

def main():
    allNames = getAllNames()
    print(f"Code HTTP : {allNames['code']}")
    print("Liste des conteneurs : ")
    print("-----------------------------------------")
    for container in allNames["containers"]:
        name = container['Names'][0].replace("/", "")
        image = container['Image']
        state = container['State']
        id = container["Id"]
        print(f"Nom du conteneur : {name} | Image : {image} | Etat : {state} | ID : {id}")
        if state == "running":
            stats = getContainerStats(id)
        else:
            stats = {"CPU": 0, "Memory": 0}
        print(f"CPU : {stats['CPU']:.2f}%, Memoire : {stats['Memory']:.2f} Mo")
        print("-----------------------------------------")

main()