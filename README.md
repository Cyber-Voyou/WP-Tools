# WP-Tools

Un utilitaire en ligne de commande pour exporter le contenu d'un site WordPress via une authentification administrateur et générer un fichier PHP contenant les données récupérées.

## Fonctionnalités

- Connexion au compte administrateur WordPress via le formulaire standard (`wp-login.php`).
- Récupération des principaux contenus via l'API REST (site, articles, pages, médias, catégories, étiquettes).
- Export des données dans un fichier PHP (`return array(...)`) prêt à être inclus dans un script PHP.

## Installation

1. Créez un environnement virtuel Python (facultatif mais recommandé)
   ```bash
   python -m venv .venv
   source .venv/bin/activate
   ```
2. Installez les dépendances :
   ```bash
   pip install -r requirements.txt
   ```

## Utilisation

Exemple de commande :

```bash
python -m wptools.cli \
  --url https://votre-site-wordpress.com \
  --username admin \
  --password 'votre-mot-de-passe' \
  --output export-wordpress.php
```

Pour obtenir des informations de diagnostic supplémentaires (requêtes HTTP, pages paginées, cookies retournés), ajoutez l'option `--debug` :

```bash
python -m wptools.cli \
  --url https://votre-site-wordpress.com \
  --username admin \
  --password 'votre-mot-de-passe' \
  --output export-wordpress.php \
  --debug
```

La commande :
1. Ouvre une session sur `wp-login.php` avec le compte administrateur.
2. Récupère le contenu exposé par l'API REST.
3. Génère un fichier PHP contenant l'ensemble des données sous forme de tableau associatif.

## Notes de sécurité

- Utilisez un compte disposant des autorisations nécessaires pour accéder aux endpoints REST désirés.
- Conservez le fichier d'export dans un endroit sécurisé car il peut contenir des informations sensibles.

## Tests

Les tests couvrent les conversions PHP de base :

```bash
pytest
```
