# TP1 : exploration des API Docker et NetBox

## 1. Conteneurs de test
- `docker run -d --name web1 --label adminapi.managed=true nginx:alpine` : conteneur étiqueté, dans le périmètre de l'API
- `docker run -d --name intrus nginx:alpine` : conteneur sans label, hors périmètre

## 2. API Docker

Adresse : `D=http://127.0.0.1:2375`

| Action | Commande cURL | Code HTTP | Observation |
|---|---|---|---|
| Version de Docker | `curl -s http://127.0.0.1:2375/version` | 200 | Renvoie la version du moteur |
| Tous les conteneurs | `curl -s "$D/containers/json?all=true"` | 200 | Renvoie l'état et la config de tout les conteneurs |
| Seulement les conteneurs étiquetés | `curl -s --get $D/containers/json --data-urlencode 'all=true' --data-urlencode 'filters={"label":["adminapi.managed=true"]}'`| 200 | Renvoie l'état et la config des conteneurs étiquetés |
| Détail de web1 | `curl -s $D/containers/web1/json` | 200 | Renvoie l'état et la config de web1 |
| Arrêt de web1 (1re fois) | `curl -i -X POST $D/containers/web1/stop` | 204 | No Content : web1 est arrêté, la réponse n'a pas de corps |
| Arrêt de web1 (2e fois) | `curl -i -X POST $D/containers/web1/stop` | 304 | Not Modified : web1 était déjà arrêté, Docker n'a rien fait |
| Conteneur inexistant | `curl -i $D/containers/nexistepas/json` | 404 | Not Found : le conteneur n'existe pas |

## 3. API NetBox

Adresse : `N=http://127.0.0.1:8080/api`

Authentification : `A="Authorization: Bearer $NETBOX_TOKEN"` (token rangé dans `.env`, forme `nbt_<key>.<token>`)

| Action | Commande cURL | Code HTTP | Observation |
|---|---|---|---|
| Obtenir un token | `curl -i -X POST $N/users/tokens/provision/ -H "Content-Type: application/json" -H "Accept: application/json" -d '{"username": "admin", "password": "admin"}'` | 201 | Created : crée une `key` (partie visible) et un `token` (partie secrète) |
| Créer le type de cluster Docker | `curl -i -X POST $N/virtualization/cluster-types/ -H "$A" -H "Content-Type: application/json" -H "Accept: application/json" -d '{"name": "Docker", "slug": "docker"}'` | 201 | Created : type de cluster créé avec l'`id` 1, header `location` vers `/cluster-types/1/` |
| Créer le cluster docker-local | `curl -i -X POST $N/virtualization/clusters/ -H "$A" -H "Content-Type: application/json" -H "Accept: application/json" -d '{"name": "docker-local", "type": 1}'` | 201 | Created : cluster `docker-local` créé, rattaché au type `Docker` (`id` 1) |
| Token mal formé (bonus) | `curl -s -o /dev/null -w "%{http_code}\n" $N/status/ -H "$A"` | 403 | Forbidden : NetBox refuse un token qui ne respecte pas la forme `nbt_<key>.<token>` |

## 4. Ce que j'en retiens
- Quand le token est invalide ou mal formé, ça renvoie le code HTTP 403 et non 200
- Idempotence (2e arrêt : 204 puis 304) : le conteneur était déjà arrêté donc Docker n'a rien fait. Répéter l'arrêt donne le même état final : l'opération est idempotente, d'où un 304 (rien n'a changé) et pas une erreur
- Familles de codes rencontrées (2xx, 3xx, 4xx) et ce que veut dire 201 + header `location` : 2xx = succès (200 OK, 201 Created, 204 No Content), 3xx = ici 304 Not Modified (rien n'a changé), 4xx = erreur du client (403 Forbidden, 404 Not Found). 201 répond à une création, et le header `location` donne l'URL de la ressource créée (ce n'est pas une redirection)
- Rôle du filtre par label `adminapi.managed=true` (web1 vs intrus) : la liste complète contient web1 et intrus, la liste filtrée seulement web1. Le filtre délimite le périmètre de l'API : elle ne doit voir et toucher que les conteneurs étiquetés
- Format du nom dans la liste Docker (`"/web1"`) par rapport au contrat (`"web1"`) : Docker préfixe le nom par un `/`, le contrat attend le nom seul, l'API devra donc retirer ce `/`
- Pourquoi le cluster se crée après le type (`"type": 1`) : le cluster référence son type par son `id`, le type doit donc exister avant. Les ressources REST sont reliées par leurs identifiants 
