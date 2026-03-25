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
- un volume pour les données (`./data`)

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

## Comment ajouter ou modifier le questionaires d'Emosson ? 

 Pour fonctionner, le questionnaire fait appel à des tables codé en SQL. 

 Il  existe 3 tables sur les différentes catégories du questionnaire :
- zone_inondable
- questions_logement
- protection_personnes


### Structure des tables SQL du questionnaire 

Les tables qui constituent le questionnaire suivent ce paterne : 

| id               | critere | question  | reponse | scores_vunerabilite | a_dependance| id_question_liee |recommandations |inclure_stats|
| -----------------| --------| --------- | --------| ----------------    | ------------| ---------------- | ---------------|---------------|
| Rang de la question     | Le critére d'appartenance sous forme de str   |   L'intitulé de la question sous forme de str      | réponses possibles à la question sous forme "d'array". Mettre seulement "x" s'il s'agit d'une valeur à renseigner | Score par réponse. A renseigner sous forme d'array de même taille que question avec les index correspondant à chaque question. | Indication d'interdépendance d'une question. Mettre "true" la question dépends d'une autre (question fille) | Rang de la question Mére | Recommandations sous forme d'array de str ({str}) suivant la même taille et le même index que la colonne question  | Boléen qui précise si une question doit faire partie la comptabilité des statistiques |

### Ajout de question 

Actuellement pour ajouter des questions il existe 2 maniére de faire :

#### Méthode 1 ( Ne sauvegarde pas la question de maniére définitive) : 

Connectez-vous au service web de pgAdmin via docker. Ouvrez ensuite le terminal de requêtes et taper la commande suivante : 

```sql
INSERT INTO public.table_sql (critere, question, reponses, scores_vulnerabilite, a_dependance, id_question_liee, recommandations, inclure_stats);
```
En remplacant chaque variable comme il convient. Exemple : 

```sql
INSERT INTO public.questions_logement ('Terrasse extérieure', 'Quel type de dalles utilisez-vous ?', ARRAY['Dalles en béton + revêtement', 'Dalles, en béton ou pierre, sur sable'], ARRAY[0, 1], FALSE, NULL, ARRAY['', '']);
```
La question apparaitra dans la table concerné mais disparaîtra si vous reconstruisez l'environement docker.

#### Méthode 2 ( Sauvegarde la question de maniére définitive) : 

Vous souhaitez ajouter des questions de manière définitive dans le questionnaire. Pour ce faire, suivez le chemin `Emosson/db/init.sql` et ouvrez le fichier. Vous trouverez le fichier qui permet de créer la base SQL à la création de l'environnement docker. Suivez les commentaires et ajoutez les questions directement sous la commande d'insertion. L'ajout doit prendre cette forme : 

```sql
INSERT INTO public.table_sql (critere, question, reponses, scores_vulnerabilite, a_dependance, id_question_liee, recommandations, inclure_stats) VALUES
(critere, question, 
reponses, 
scores_vulnerabilite, a_dependance, id_question_liee, 
recommandations, inclure_stats),
....
```
Exemple pour 2 questions : 

```sql
INSERT INTO public.questions_logement (critere, question, reponses, scores_vulnerabilite, a_dependance, id_question_liee, recommandations) VALUES
('Murs', 'Vos murs sont-ils faits en bois ?', 
 ARRAY['Oui', 'Non'], 
 ARRAY[7.5, 0], FALSE, NULL, 
 ARRAY['Lors de vos futurs travaux ou aménagements, privilégiez l''utilisation de matériaux hydrofuges, qui sont beaucoup plus résistants à l''immersion.', '']),

('Isolant', 'Quel matériau d''isolation est utilisé dans votre logement ?', 
 ARRAY['Fibre minérale (laine de verre)', 'Fibre végétale', 'Vermiculite', 'Plastique alvéolaire', 'Je ne sais pas'], 
 ARRAY[10, 10, 10, 0, 10], FALSE, NULL, 
 ARRAY['Lors de vos futurs travaux ou aménagements, privilégiez l''utilisation de matériaux hydrofuges, qui sont beaucoup plus résistants à l''immersion.', 'Lors de vos futurs travaux ou aménagements, privilégiez l''utilisation de matériaux hydrofuges, qui sont beaucoup plus résistants à l''immersion.', 'Lors de vos futurs travaux ou aménagements, privilégiez l''utilisation de matériaux hydrofuges, qui sont beaucoup plus résistants à l''immersion.', '', 'Lors de vos futurs travaux ou aménagements, privilégiez l''utilisation de matériaux hydrofuges, qui sont beaucoup plus résistants à l''immersion.']);
```

##### Attention !!!  Mettre un ';' termine une requête sql et risque d'entrainer des erreurs si placé au mauvais endroit. Placez là toujours à la fin de la derniere question de la commande d'insertion.

Enregistrez le fichier et reconstruisez l'environnement Docker. Les questions devraient maintenant apparaître dans le questionnaire.

## Comment voir les avis et retours ? 

Le projet Emosson est dans une optique continuelle d'amélioration. Consulter les avis permet de voir quels axes corriger et quel fonctionnalités implémenter afin d'améliorer le site. Un système d'avis existe et celui-ci récupére les avis sous la forme d'une table SQL. 
Elle prends la forme suivante : 

|id |commentaire|note|date_avis|
|---|--------|----|---------|
|Rang de l'avis| Texte du commentaire sous forme de str| Note comprise entre 1 et 5    | date à laquelle a été posté l'avis |

Pour consulter les avis il faut se rendre sur pgAdmin et dans le terminal de requête il faut entrer la requête suivante :

```sql
SELECT * FROM public.avis
ORDER BY id ASC 
```
D'autres requêtes permettent aussi de trier les avis par date :

```sql
SELECT * FROM public.avis
ORDER BY date_avis ASC
```
Pour voir les avis les plus vieux

```sql
SELECT * FROM public.avis
ORDER BY date_avis DESC
```
Pour voir les avis les plus ancients 


