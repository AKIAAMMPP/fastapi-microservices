Description de l'application
Cette application est un système de microservices basé sur FastAPI, conçu pour gérer un inventaire de produits et le traitement des commandes. Elle comprend trois principaux composants :

Service d'inventaire : Gère la création, la mise à jour et la liste des produits, stockés dans Redis.
Service de paiement : Traite les commandes en vérifiant la disponibilité des produits et en mettant à jour l'inventaire, avec un traitement asynchrone.
Frontend : Une interface utilisateur simple permettant d'afficher les produits, créer de nouveaux produits et passer des commandes.
Les services sont orchestrés avec Docker Compose, utilisant Redis comme base de données persistante, et incluent une fonctionnalité de rechargement à chaud pour le développement.


Construction avec Docker
Pour construire et exécuter l'application avec Docker, suivez ces étapes :

Prérequis :

Installez Docker et Docker Compose sur votre machine .


Cloner le dépôt :
bashgit clone https://github.com/AKIAAMMPP/fastapi-microservices.git
cd fastapi-microservices

Construire et lancer les conteneurs :

bashdocker-compose up --build -d

Le flag -d exécute les conteneurs en arrière-plan.
