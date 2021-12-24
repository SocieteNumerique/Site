# Pour mettre à jour les models :

    python manage.py makemigrations
    python manage.py migrate

# Pour mettre à jour les traductions :

- Créer ou mettre à jour un fichier de traductions :
    `django-admin makemessages -l fr`
- Renseigner à la main les traductions dans les fichiers .po autogénéré
- Compiler les fichiers de traductions:
    `django-admin compilemessages`

# Utilisation de l'app django Tweets

Lire le README correspondant à l'app Tweets


# Pages obligatoires pour un bon fonctionnement

Il y a plusieurs pages à créer dans l'admin pour un fonctionnement optimum de l'application
Ces pages doivent être des pages filles de la HomePage

- La page d'accueil avec le slug `accueil`
- Une page actualité avec le slug `actualite`
- Une page notre mission avec le slug `mission`
- Une page accessibilité avec le slug `accessibilite`
- Une page mentions légales avec le slug `mentions-legales`

# Images obligatoire pour un bon fonctionnement

- Une image pour les actualités dont le titre est `journal`

# Système de traduction utilisé

Le système de traduction utilisé est [wagtail-localize](https://www.wagtail-localize.org/)
> Attention : Si une langue est rajouté il faudra (en plus du système de base de wagtail localize) adapter le switch de langue du header
