# Emosson

## Qu'est-ce que Emosson ?

Emosson est un site de prévention. Il s'inscrit dans un contexte de prévention des risques naturels et vise à proposer un outil web permettant d’informer les utilisateurs sur l’exposition d’un territoire aux risques d’inondations.

## Structure générale

Le site web est composé de plusieurs pages : 

### - Page d’accueil 
- Pour acceuillir le visiteur sur la platforme  

### - Page de présentation 
- Information sur le site et l'équipe dérriere la création du site

### - Page questionnaire 
- Destinée à recueillir un maximum d’informations sur le lieu et le type de logement
  
### - Page d'actualité
- Page d'actualité renvoyant vers différents sites d'informations 

### - Page de statistiques
- Page permmettant d'avoir accés au nombres et pourcentages de réponses par questions

### - Page d'avis 
- Cette page permet de receuillir les avis et ressentis des utilisateurs.

### - Page de résultats et bilan
- Accessible à l'issue du questionnaire et qui proposera un score de vulnérabilité et des recommandations pour protéger le bien de l'utilisateur avec la possibilité de télécharger le bilan sous forme de fichier PDF. 

## Mise en place de l'environnement d'Emosson

Emosson est hebergé dans un environnement Docker.

L’environnement est composé de 3 services (définis dans `docker-compose.yml`) :

| Service                | Nom interne | Rôle                                    | Ports exposés (hôte:docker) | Volume principal                         |
| ---------------------- | ----------- | --------------------------------------- | --------------------------- | ---------------------------------------- |
| **Flask**              | flask         | Serveur web pour application Flask      | `8000:5000`                 | `.:/app`        |
| **PostgreSQL+PostGIS** | db          | Base de données spatiale                | `5432`                      | `pg_data:/var/lib/postgresql/data`       |
| **pgAdmin**            | pgadmin     | Interface web pour gérer Postgres       | `5050:80`                   | `pgadmin_data:/var/lib/pgadmin`          |

## Détails des services

### Flask

- basé sur `./Emosson/Dockerfile`
- fichiers sources dans `./app.py`
- http://localhost:8000:5000

### Bibliothéque Python 

- Pour rajouter des bibliothéques dans l'environnement python il faut les renseigner dans le fichier "requirements.txt" à la racine du projet.
- Les bibliothéques seront installés à chaque nouvelle construction de l'environnement.

### Postgres+PostGIS

- user: `postgres`, pass: `postgres`, base: `mydb`, port: `5432`
- exécute `./db/init.sql` au premier démarrage (contruit une table points, avec 3 points)

### pgadmin

- user: `admin@admin.com`, pass: `admin`
- permet de se connecter à postgres si besoin (host `db`, port `5432`, user/pass, sans SSL)
- http://localhost:5050


## Volumes & persistance

Les volumes Docker permettent de conserver les données même si le conteneur est supprimé et/ou relancé :

- un volume pour Flask (monté sur le dossier`./app`)
- trois autres volumes Docker pour les données (attention, les données de ces volumes ne sont pas accessibles en local, voir «Sauvegarde» plus loin)
- un volume pour les données géospatiales (`./data`)

```yml
volumes:
  pg_data:
  pgadmin_data:
```
- `pg_data` stocke la base PostGIS (schémas, données, utilisateurs)
- `pgadmin_data` stocke les données pgadmin (connexions)

## Commandes de base


```sh
# lance l'environnement 
docker compose up
docker compose up -d # en mode daemon

# arrête l'environnement
docker compose down
docker compose down -v # supprime en plus les volumes
```

Ces commandes sont à lancer dans le dossier "Emosson"

## Sauvegarde

Pour récupérer en local les données de la BDD, exécutez les scripts respectifs depuis la racine du projet

```sh
# Export SQL de la base 
docker compose exec -t db pg_dump --inserts -U postgres -d mydb > "./db/backup.sql"
```

- un fichier `./db/backup.sql` est créé pour un dump de la BDD

