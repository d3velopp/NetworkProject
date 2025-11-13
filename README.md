Here is the clean Markdown file content without citations.

***

# Rapport de Projet Python : Jeu de la Vie

**Institution :** INSA Centre Val de Loire
---

## 1. Introduction
Le "Jeu de la vie" est un automate cellulaire imaginé par John Horton Conway en 1970. Notre projet est une simulation conçue pour capturer les subtilités de l'évolution biologique via la programmation Python. Inspiré par la reproduction, la mutation génétique et la sélection naturelle, le jeu met en scène des entités autonomes appelées "Bobs" évoluant dans un monde virtuel. Ce projet vise à être un outil éducatif illustrant de manière ludique les concepts évolutifs.



---

## 2. Choix de modélisation et d'implémentation

### a. Architecture
Le projet est structuré de manière modulaire.

#### Fichiers Principaux
* **`main.py`** : Initialise Pygame, l'écran, l'horloge, le menu et lance la boucle de jeu.
* **Répertoire `GameControl`** : Gère les activités et interactions.
    * **`game.py`** : Gère les instances du jeu (`gameController`) et du graphique (`world`). Il contient la boucle de jeu (`run()`) qui gère l'horloge, les événements et le rendu.
    * **`EventManager.py`** : Gère les entrées du menu et des paramètres.
    * **`saveAndLoad.py`** : Permet de sauvegarder et charger l'état du jeu depuis le dossier `save`.
    * **`setting.py`** : Contient les paramètres du jeu, utilisant le "Singleton pattern" pour la cohérence.
    * **`gameController.py`** : Le cœur du jeu. Il contient les listes de `tiles` (grid), de nourriture (`listFoods`) et de Bobs (`listBobs`). Il gère les files d'attente pour les naissances (`newBornQueue`) et les décès (`diedQueue`) à chaque tick.

#### Entités (Tiles & Bobs)
* **`tile.py`** : Gère les cases (coordonnées et énergie/nourriture). L'énergie d'une case représente la nourriture qui se régénère chaque jour. Elle gère aussi la conversion de coordonnées pour le rendu graphique.
* **`bob.py`** : Gère le cycle de vie et les actions des Bobs.
    * **Action** : Détermine l'ordre d'exécution des activités.
    * **Interact** : Gère les interactions sur une même case.
    * **Scan** : Utilise la perception pour repérer proies ou nourriture.
    * **DetermineNextTile** : Algorithme de déplacement (fuite, chasse, nourriture, hasard).
    * **Mémoire** : Mémorisation des cases visitées et des sources de nourriture.

#### Affichage (View)
* **`world.py`** : Génère les images de la carte et des entités sur l'écran.
* **`camera.py`** : Permet le contrôle de la position de la vue (Haut, Bas, Gauche, Droite).
* **`texture.py`** : Charge les images depuis le répertoire `asset/graphic`.

### b. Fonctionnalités

* **Menu Principal** : Options pour "NEW GAME", "LOAD GAME", "SETTINGS" (musique, luminosité) et "QUIT".
* **La Carte** : Générée avec des blocs d'herbe et de fleurs alternés aléatoirement.
* **Les Bobs** :
    * **Forme normale** : Apparaissent en vert.
    * **Prédation** : Deviennent violets lorsqu'ils chassent une proie.
* **Mode Simulation** : Accélère le jeu pour observer l'évolution sur le long terme.
* **Mode Pause** : Permet d'arrêter le mouvement et de consulter les statistiques détaillées d'un Bob (ID, énergie, masse, vision, etc.) en le survolant avec la souris.
* **Graphes** : Visualisation de l'évolution des populations, naissances, décès, et moyennes des caractéristiques (masse, vision, vélocité).



---

## 3. Manuel du jeu

### Contrôles Clavier
* **Escape** : Quitter le jeu immédiatement.
* **Space** : Mettre le jeu en pause.
* **Backspace** : Ouvrir les "In-game settings".
* **S** : Activer/Désactiver le mode Simulation.
* **M** : Retourner au menu principal (sans sauvegarde).
* **Touches 1 à 5** : Sauvegarder la partie dans l'emplacement correspondant.
* **G** : Consulter les graphes de statistiques.
* **Flèches directionnelles** : Déplacer la caméra.

### Paramètres (Settings)
Les joueurs peuvent modifier de nombreux paramètres via le menu, notamment :
* **FPS** (Vitesse du jeu).
* **Grid Length** (Taille de la carte).
* **Number Bob** (Population initiale).
* **Energy Settings** : Coûts énergétiques pour le mouvement, la reproduction, l'accouchement, etc.
* **Mutations** : Taux de variation pour la masse, la vélocité, la vision et la mémoire.



---

## 4. Difficultés Rencontrées

1.  **Architecture** : Refonte complète nécessaire au milieu du projet pour adopter une structure orientée objet adaptée.
2.  **Animation et Mouvement** : Gestion complexe pour rendre les déplacements fluides via une liste `previousTiles`.
3.  **Performance** : Chute de FPS sur les grandes cartes (ex: 200x200).
    * *Solution* : Rendu limité à la zone visible par la caméra. Le FPS est stabilisé à environ 18 FPS.
4.  **Consommation d'énergie** : Dilemme sur l'application du coût énergétique avant ou après l'action.
    * *Décision* : Consommation appliquée **avant** l'action. Le Bob a une dernière "impulsion" avant de mourir s'il n'a plus d'énergie.
5.  **Arrondi des flottants** : Problème avec la méthode d'arrondi de Python pour les mutations génétiques (ex: x.5 arrondi au pair le plus proche).
6.  **Graphismes** : Manque de ressources pour créer des textures esthétiques avancées.
