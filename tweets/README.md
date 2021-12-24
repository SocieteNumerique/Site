#Utilisation
- Ajouter cette application dans un projet Django
- Dans `settings.py` ajouter l'application `tweets`:
  ```
    INSTALLED_APPS = [
      ...,
      "tweets",
      ...
    ]

- Le fichier `settings.py` doit mettre à disposition un dictionnaire contenant les clés et le compte à utiliser, avec le format suivant:
  ```
  TWITTER = {
      "TWITTER_API_KEYS": xxx,
      "TWITTER_API_SECRET_KEYS": xxx,
      "TWITTER_API_ACCESS_TOKEN": xxx,
      "TWITTER_API_ACCESS_TOKEN_SECRET": xxx,
      "TWITTER_ID": xxx,
  }
  ```



- Installer les lib nécessaires et les rajouter dans le requirements
   ```
   pip install python-dateutil
   ```
