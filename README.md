# Wordle Assistant

Petit outil pour aider à résoudre le jeu Wordle (anglais) :  
https://www.nytimes.com/games/wordle/index.html

## Principe
1. Tu joues Wordle normalement sur le site.
2. L’assistant propose un mot.
3. Tu cliques sur les lettres pour indiquer le feedback (gris / jaune / vert).
4. Il te propose les meilleurs mots à essayer ensuite.

Objectif : trouver le mot en 6 essais maximum.

## Prérequis
- Python 3.8 ou plus
- `valid-wordle-words.txt` (liste des mots de 5 lettres)
- `tkinter` (inclus dans Python)

## Lancer l’outil

```bash
python main.py
```