# MLFlow

## Installation

Installer MLFlow

`pip install mlflow[extras]`

## Entrainement

Lancer un training :

`./train.py`

## MLFlow UI

Lancer l'interface de MLFlow depuis la ligne de commande depuis le répertoire où l'entrainement a été lancé :

`mlflow ui`

## Servir le modèle

Après avoir choisi un modèle d'après les entrainements, récupérer l'identifiant et exécuter la commande suivante :

`mlflow models serve -m mlruns/0/<Run ID>/artifacts/model/ -p 8888`
    example (use --no-conda if the user doesn't have conda):
`mlflow models serve -m mlruns/0/76cfd4db6dba48a180970769d362f4a4/artifacts/model/ -p 8888 --no-conda`

Requêter le modèle :

Invoke-WebRequest -Uri http://127.0.0.1:8888/invocations `
    -Method POST `
    -Headers @{ "Content-Type" = "application/json" } `
    -Body '{"dataframe_split": {"columns": ["crim", "zn", "indus", "chas", "nox", "rm", "age", "dis", "rad", "tax", "ptratio", "b", "lstat"],"data": [[0.02731, 0, 7.07, 0, 0.469, 6.421, 78.9, 4.9671, 2, 242, 17.8, 396.9, 9.14]]}
}'

