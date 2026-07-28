---
id: 2026-07-28-ingestion-raw-design
aliases: [Spec — ingestion _raw]
type: meta
status: valide
maj: 2026-07-28
---

# Spec — pipeline d'ingestion `_raw/`

> **But.** Permettre de déposer dans le vault des fiches `.md` rédigées ailleurs (Claude Projects branché au dépôt GitHub) sans que le canon se dégrade. Le rangement est l'étape finale ; la valeur du dispositif est le contrôle qui la précède.

---

## 1. Le problème

Claude Projects lit un instantané du dépôt. Il ne remonte pas les chaînes `depends_on` jusqu'aux invariants, ne consulte pas la liste « Écartés » d'`index.md`, et ne cherche pas si un terme qu'il invente existe déjà ailleurs sous un autre angle. Ses fiches sont donc structurellement suspectes sur trois plans :

1. **Contradiction d'invariant** — la fiche s'appuie sur une règle que le canon a verrouillée autrement.
2. **Reproposition d'un écarté** — l'idée figure déjà dans « Écartés (ne pas reproposer) ».
3. **Réinvention lexicale** — un concept déjà nommé dans le vault reçoit un second nom.

Un agent qui range sans filtrer automatise l'entrée de ces trois défauts et les rend invisibles, ce qui est pire que le report manuel. L'agent est donc un **douanier**, pas un rangeur.

## 2. Ce qui n'est pas dans le périmètre

- `_inbox/` conserve son rôle actuel : sas des stubs vides créés par clic Obsidian sur un lien non résolu. Le pipeline n'y touche pas. Un stub vide et une fiche rédigée externe ne se traitent pas de la même manière.
- L'agent ne rédige pas de contenu de canon. Il normalise, range, propage. Il ne comble pas les trous d'une fiche entrante.
- L'agent n'attribue jamais `status: canon`.

## 3. Arborescence

```
_raw/                          ← dépôt des fiches externes
_raw/README.md                 ← règle du dossier
_raw/_rapports/                ← sortie de la passe 1
_raw/_rapports/AAAA-MM-JJ-<slug>.md
```

`_raw/` est hors du périmètre des requêtes Dataview d'`index.md` (`FROM "codex" OR "tension" OR "chronique"`) : rien de ce qui y séjourne ne pollue l'état du corpus.

## 4. Forme technique

Une **skill de projet** invocable, pas un sous-agent.

Motif : un sous-agent rend un texte et disparaît. Or la sortie de la passe 1 est un objet de débat — sur une collision ORANGE, il faut pouvoir discuter la résolution proposée avec un interlocuteur qui a le canon en contexte. La skill s'exécute dans la session principale.

Conséquence assumée : la passe 1 est lourde en lecture. Sur cinq fiches entrantes touchant [[le-lien]] et [[couleurs-magiques]], elle remonte une part significative du codex. C'est le prix du contrôle.

## 5. Passe 1 — audit (`/ingerer`)

**Invariant de la passe : aucune écriture hors de `_raw/_rapports/`.**

1. Inventorier `_raw/*.md` (hors `README.md` et `_rapports/`).
2. Lire `index.md` et `journal.md` intégralement.
3. Pour chaque fiche entrante, extraire : noms propres, concepts nommés, affirmations structurantes.
4. Pour chaque terme extrait, `grep` sur l'ensemble du vault — le concept existe-t-il déjà sous un autre nom ?
5. Confronter chaque affirmation à trois listes d'`index.md` : « Ce qui est verrouillé », « Écartés », et les ⚠️ déjà tranchées.
6. Ouvrir les fiches que la fiche entrante touche, **et leurs `depends_on` remontés jusqu'aux `invariant`**.
7. Écrire `_raw/_rapports/AAAA-MM-JJ-<slug>.md`.

### Verdicts

| Verdict | Sens | Suite |
|---|---|---|
| **VERT** | Aucune collision. Frontmatter et rangement déductibles. | Applicable sans arbitrage. |
| **ORANGE** | Collision non bloquante : réinvention lexicale, `depends_on` faux, chevauchement avec une fiche existante. | Arbitrage requis. Le rapport propose une résolution par **unification**, jamais par renommage. |
| **ROUGE** | Contredit un invariant verrouillé, ou repropose un écarté. | Arbitrage requis. Le rapport cite **textuellement** l'invariant heurté et la ligne d'« Écartés » concernée. |

### Structure du rapport

```markdown
---
id: AAAA-MM-JJ-<slug>
type: meta
status: en-attente-arbitrage   # en-attente-arbitrage | arbitre | applique
---

# Rapport d'ingestion — AAAA-MM-JJ

## <nom-du-fichier-brut>.md — 🔴 ROUGE

**Résumé** — ce que la fiche prétend établir, en deux lignes.

**Destination proposée** — `codex/<thème>/<id>.md`, `layer: <couche>`, `status: draft`.

**Collisions**
1. **Contredit [[le-lien]]** — la fiche pose X. Invariant verrouillé : « <citation exacte> ».
   *Résolution proposée* — <unification>.
2. **Repropose un écarté** — « <intitulé exact de la ligne Écartés> ».

**Propagation prévue** — fiches dont le `touches` change, ⚠️ refermées, lignes de `journal.md`.

## Arbitrage

<!-- À remplir à la main. L'agent ne modifie jamais cette section. -->
```

Le `status` du rapport porte l'état du pipeline. C'est ce qui permet à la passe 2 de s'exécuter dans une autre session que la passe 1.

## 6. Passe 2 — application (`/ingerer appliquer`)

Traite les fiches VERT, plus les ORANGE et ROUGE dont la section `## Arbitrage` est renseignée. Refuse toute fiche ROUGE ou ORANGE non arbitrée.

1. **Normaliser** au gabarit de `_meta/templates/` correspondant au `type` (`codex.md`, `race.md`, `tension.md`, `chronique.md`) :
   - frontmatter complet, `id` = nom de fichier ;
   - champs relationnels en **wikilinks entre guillemets** — jamais en backticks ;
   - une fiche de race porte les **quatre axes obligatoires** ; s'il en manque un, l'axe est marqué ⚠️ et listé dans le callout `> [!warning] Trous volontaires` ;
   - sections finales `## Choix abandonnés` et `## Dernière validation` présentes ;
   - tout ce que le corps marquait comme ancien ou corrigé est **déplacé** dans « Choix abandonnés », horodaté.
2. **Ranger** dans le dossier **thématique** déduit (`codex/monde/`, `codex/races/`, `codex/institutions/`, `codex/histoire/`, `codex/lieux/`, `tension/`, `chronique/`). Jamais un dossier par couche : la couche vit dans le frontmatter.
3. **Statuer** — `status: draft` par défaut. `canon` n'est jamais attribué par l'agent.
4. **Propager** :
   - ajouter la nouvelle fiche au `touches` des fiches amont qu'elle contraint ;
   - refermer partout ailleurs les ⚠️ que l'arbitrage a tranchées ;
   - une ligne par décision dans `journal.md` ; les idées écartées vont dans la section « Écartés (et pourquoi) » avec leur motif ;
   - mettre à jour la **moitié manuelle** d'`index.md` — « Ce qui est verrouillé », « Décisions en suspens », « Nommage en souffrance », « Chantiers », « Écartés ». Ne jamais toucher aux blocs Dataview.
5. **Nettoyer** — supprimer le fichier brut de `_raw/`, passer le rapport à `status: applique`.

La propagation ne demande pas d'autorisation : `CLAUDE.md` §7 la qualifie de maintenance, pas de décision de canon. Elle est mentionnée en une ligne à la fin.

## 7. Critères de réussite

- Aucune fiche entrante ne rejoint `codex/` sans être passée par un rapport.
- Une contradiction d'invariant est nommée avec citation, jamais résolue en silence.
- Après application, les requêtes Dataview « Dette structurelle » et « Fiches invoquées mais jamais écrites » d'`index.md` reflètent l'état réel — c'est-à-dire que le frontmatter écrit est juste.
- Un rapport rédigé dans une session peut être appliqué dans une autre sans perte.

## 8. Choix abandonnés

- **Réutiliser `_inbox/` comme dossier de dépôt** *(abandonné le 2026-07-28)* — mélange deux flux de nature différente : stubs vides d'Obsidian et fiches rédigées externes.
- **Ranger en quarantaine (`status: idea` + bloc de collisions en tête de fiche)** *(abandonné le 2026-07-28)* — les fiches non fiables entrent quand même dans le graphe et s'y accumulent.
- **Laisser l'agent trancher seul les contradictions** *(abandonné le 2026-07-28)* — fait dériver le canon sur des arbitrages structurants sans validation.
- **Sous-agent au lieu d'une skill** *(abandonné le 2026-07-28)* — contexte isolé, aucun débat possible sur une collision après restitution.
- **Rapport rendu en conversation seulement** *(abandonné le 2026-07-28)* — la passe 2 ne survivrait pas à un changement de session.

## 9. Dernière validation

**2026-07-28** — design validé en session, avant implémentation.
