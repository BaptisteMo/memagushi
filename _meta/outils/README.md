---
id: outils-readme
type: meta
status: vivant
---

# _meta/outils

Outillage local du vault. Rien ici n'est du canon.

---

## `lire.py` — écouter une fiche

Le markdown n'est pas fait pour être écouté. Wikilinks, frontmatter, tableaux, callouts et ⚠️ s'entendent tous si on les laisse passer : `[[le-lien#6. L'échelle d'harmonie|le-lien §6]]` se prononce « crochet crochet le tiret lien dièse six ». Ce script les traduit en texte parlable avant de le confier à `say`.

```bash
python3 _meta/outils/lire.py le-plan              # parle tout de suite
python3 _meta/outils/lire.py le-lien -s 6.1       # une seule section
python3 _meta/outils/lire.py le-plan -f           # génère un .m4a et l'ouvre
python3 _meta/outils/lire.py le-plan -t           # affiche le texte, ne parle pas
python3 _meta/outils/lire.py --voix               # liste les voix françaises
```

Le chemin est facultatif : `lire.py le-plan` retrouve la fiche où qu'elle soit dans le vault.

**Le mode `-f` compte.** `say` ne sait ni mettre en pause ni revenir en arrière. Sur une fiche de trois cents lignes, générer le `.m4a` et l'ouvrir dans le lecteur donne pause, vitesse et navigation. Le mode direct convient aux sections courtes.

Aucune dépendance : stdlib seule. Rien à installer, rien qui casse à la prochaine mise à jour de Python.

### Installer une voix correcte — à faire une fois

Les voix livrées par défaut sont les **compactes**, celles de VoiceOver, et elles sont mauvaises. Les versions **Premium** ou **Enhanced** se téléchargent :

> Réglages Système → Accessibilité → Contenu énoncé → Voix système → Gérer les voix → Français → choisir *Premium* (≈ 500 Mo)

`lire.py` prend automatiquement la meilleure voix disponible : Premium d'abord, France avant Canada. `--voix` montre ce qui est installé et signale s'il n'y a rien de Premium. `-v "Nom"` force une voix, `-r 220` accélère.

### Ce que le pré-traitement fait

| Dans la fiche | À l'oreille |
|---|---|
| frontmatter | *« Le Plan. Fiche codex, couche invariant, statut draft. »* |
| `[[coeur-magique]]` | « Le Cœur magique » — via les `aliases` de la fiche cible |
| `[[le-lien#6. …\|le-lien §6]]` | « le lien, section 6 » |
| `⚠️` en tête de ligne | « Point ouvert : » |
| `> [!warning] Trous volontaires` | « Encadré. Trous volontaires. » |
| `🔴` `🟠` `🟢` | « rouge », « orange », « vert » |
| tableau | une ligne = une phrase, cellules jointes par un tiret |
| ```` ```dataview ```` | supprimé |
| `**gras**`, `` `code` ``, `<!-- -->` | retirés |
| `·`, `→`, `§` | « , », « . », « section » |
| titres, `---` | silences de 350 à 900 ms |

**Les noms lisibles viennent des `aliases`.** Le script parcourt le vault au démarrage et construit une table `slug → nom`. Une fiche neuve avec un `aliases` correct est donc bien prononcée sans rien configurer. Une fiche non écrite (nœud gris) retombe sur un dé-slugage.

### `prononciation.json`

Les noms inventés se font massacrer par un TTS français. Ce fichier les corrige : clé = ce qui est écrit dans les fiches, valeur = orthographe bidouillée qui sonne juste.

```json
{ "Sirrhal": "Sirral", "Enaär": "Éna-ar", "agôgè": "agogué" }
```

La substitution ignore la casse et ne touche que les mots entiers. **À compléter au fil du nommage** — chaque terme du [[lexique]] y a sa place. Les clés commençant par `_` sont ignorées, ce qui permet d'y laisser des commentaires.

### Limites connues

- `⚠️` au fil d'une phrase (« quatre ⚠️ ouvertes ») donne « quatre points ouverts ouvertes ». Cas rare, le sens passe.
- Les tableaux à plus de trois colonnes deviennent longs à l'oreille : les cellules sont juxtaposées sans rappeler l'en-tête.
- Le mode direct n'a pas de pause. Utiliser `-f` pour les longues fiches.

### Raccourci

Pour ne plus taper le chemin, ajouter à `~/.zshrc` :

```bash
alias lire='python3 ~/memagushi/_meta/outils/lire.py'
```

Puis `lire le-plan -s 6`.

---

## Commande `/lire`

Dans Claude Code, `.claude/commands/lire.md` expose le script en slash command :

```
/lire le-plan             génère l'audio et l'ouvre dans le lecteur
/lire le-lien -s 6.1      une seule section
/lire le-plan --direct    parle tout de suite, en tâche de fond
/lire le-plan -t          affiche le texte parlable
/lire                     rappelle l'usage et liste les voix
```

Le mode par défaut génère un `.m4a` **volontairement** : lire une fiche en direct bloquerait la session Claude Code pendant toute la durée. `--direct` détache le processus et rend le PID pour pouvoir le couper.

Le wrapper est `lire-cmd.sh` ; toute la logique de traitement reste dans `lire.py`, appelable seul.
