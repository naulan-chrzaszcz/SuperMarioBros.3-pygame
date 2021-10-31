# **SuperMarioBros3 "like".**
![illustration-TitleScreen](https://eapi.pcloud.com/getpubthumb?code=XZzBbJZwEoDuWD0fJJRWCIYAEUjpBhiDCek&linkpassword=undefined&size=1280x345&crop=0&type=auto)
- ![discordLogo](https://eapi.pcloud.com/getpubthumb?code=XZj2bJZbGTjqDtGjLRdseh7mqUmlHwcHAFV&linkpassword=undefined&size=20x20&crop=0&type=auto) **Discord**: http://discord.chrz-development.fr
- **WebSite**: https://www.chrz-development.fr

➡ Ce code source **contien toutes les ressources nécessaires pour pouvoir lancé le jeu**.
Tous les fichiers ressource sont dans le fichier `res` du code source.
Ce jeux se joue uniquement au clavier ou bien sur une manette !

## **🗂 Sommaires:**
- ⌨ [Touches par défaut](#touches-par-défaut)
- [Compatibilité](#compatibilité)
- 💻 [Developpeurs](#developpeurs)
- 👷‍ [Bêta-testeurs](#bêta-testeurs)
- 🗣 [Langage de programmation utilisée](#langage-de-programmation-utilisée)
- ❔ [Comment le lancée ?](#comment-le-lancée-)
- 📑 [Les choses requises:](#les-choses-requises)

### Touches par défaut
La touche `Q` et `D` permet de dirigé Mario vers la gauche et vers la droite de l'écran.

La touche `Space` permet de faire un saut à Mario.


### Compatibilité:
Le jeu est compatible sur les platformes suivante:
- Windows.
- Linux.

Il est compatible manette et clavier.

### Developpeurs:
- Ce jeu est entierement codé par [CHRZASZCZ Naulan](https://www.instagram.com/naulan.chrzaszcz/).

![Escarbot Banner](https://eapi.pcloud.com/getpubthumb?code=XZmubJZO3RLKrQ4bwSiOupYtRg78SzGx3N7&linkpassword=undefined&size=1600x315&crop=0&type=auto)

### Bêta-testeurs:
- ![illustrationGabyUnderscore](https://eapi.pcloud.com/getpubthumb?code=XZwBbJZ34m6NkzajF5WX9eHQUDuyhK8drKy&linkpassword=undefined&size=20x20&crop=0&type=auto) [GabyUnderscore](https://www.twitch.tv/gabyunderscore)

### Langage de programmation utilisée:
- Ce jeux est entierement codé en langage Python.

## **Comment le lancée ?**
➡ Dans le fichier racine du code source (`./`), vous avez à votre disposition deux scripts, l'un pour un système d'exploitation 
Linux et l'autre pour un système d'exploitation Windows.
On peut les reconnaitre en visualisant leurs extensions de fichier. Mais vous n'êtes pas obligez de le lancé par ces 
scripts, vous pouvez lancer directement le jeux grâce à cette commande que Python possède nativement
```commandline
# Commande native lors que Python est installée sur la machine. 
python3 ./SuperMarioBros3.pyw
```
Sinon, si vous voulez un lancement qui fonctionnera à 100%, lancé les scripts suivant.
Sur Linux:
```commandline
./launch_on_Linux.sh
```
Sur Windows:
```commandline
#TODO
```
## **Les choses requises:**
Lors du lancement du jeux, si vous avez une erreur similaire comme si dessous:
```python
Traceback (most recent call last):
  File "P:\SuperMarioBros3-pygame\SuperMarioBros3.pyw", line 5, in <module>
    import pygame as pg
ModuleNotFoundError: No module named 'pygame'
```
Vous devez installer la librairie qui est mentionner dans l'erreur, mais la plupart du temps, juste `pygame` sera 
nécessaire, il vous suffit de entrez cette commande:
```commandline
python3 -m pip install pygame
```
Mais attention ! Il est possible que `python3` ne fonctionne pas... Si c'est le cas entré la commande suivante:
```commandline
python -m pip install pygame
```