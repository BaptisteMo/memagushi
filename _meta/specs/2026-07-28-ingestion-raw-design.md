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
6. **Commiter** — un commit par fiche ingérée (voir §7).

La propagation ne demande pas d'autorisation : `CLAUDE.md` §7 la qualifie de maintenance, pas de décision de canon. Elle est mentionnée en une ligne à la fin.

## 7. Git

Le dépôt GitHub n'est pas seulement l'historique du vault : c'est le **canal de retour vers Claude Projects**, qui lit `main`. Le commit et le push sont donc la dernière étape fonctionnelle du pipeline, pas une hygiène annexe.

### Séquence

| Moment | Action git |
|---|---|
| Avant la passe 1 | Commit des bruts déposés dans `_raw/` — trace de ce qui est entré et sous quelle forme. Puis tag `pre-ingest-AAAA-MM-JJ`. |
| Fin de passe 1 | Commit du rapport d'audit. |
| Après arbitrage | Commit du rapport arbitré. La décision est datée séparément de son application. |
| Passe 2 | **Un commit par fiche ingérée.** |
| Fin de passe 2 | `git push` sur `main`. |

### Granularité : un commit par fiche, jamais par lot

Une ingestion touche la fiche neuve, le `touches` des fiches amont, `journal.md`, `index.md` et la suppression du brut. Ces cinq mutations tiennent dans **un seul** commit.

Motif : si la fiche se révèle fausse plus tard, `git revert <sha>` défait la fiche **et toute sa propagation** en une opération. Un commit couvrant cinq fiches rend ce retour arrière impraticable — il faudrait démêler à la main la propagation de la mauvaise fiche de celle des quatre bonnes.

Le tag `pre-ingest-AAAA-MM-JJ` couvre le cas inverse : annuler le lot entier, sans énumérer les `sha`.

### Garde-fou : working tree propre exigé

**La passe 2 refuse de s'exécuter si `git status` n'est pas propre.**

C'est le point le plus facile à négliger et le plus coûteux. Obsidian écrit en continu et ignore git. Si des édits manuels sont en cours au moment de l'application, le commit d'ingestion les embarque — et le `revert` censé annuler l'ingestion détruit ce travail au passage. En cas de working tree sale, l'agent s'arrête et énumère ce qu'il faut commiter d'abord.

### Format des messages

Français, impératif ou infinitif, cohérent avec l'historique existant. Sujet ≤ 60 caractères. Corps obligatoire en passe 2 : ce qui a été rangé et où, puis la liste de ce que la propagation a touché.

```
Ingère <id-fiche> depuis _raw/

Rangée dans codex/<thème>/. Verdict d'audit : <VERT|ORANGE|ROUGE>.

Propagation :
- touches mis à jour dans <fiche-amont>
- ⚠️ <intitulé> refermée dans <fiche>
- journal.md : <décision>
- index.md : <section touchée>
```

### Push

Push automatique sur `main` en fin de passe 2. Les commits antérieurs (bruts, rapport, arbitrage) restent locaux jusque-là.

Motif : Projects lit `main`. Un canon validé mais non poussé produit des fiches entrantes qui contredisent des décisions déjà prises — exactement la panne que ce pipeline existe pour supprimer. Contrepartie assumée : un retour arrière après push est un commit public.

## 8. Critères de réussite

- Aucune fiche entrante ne rejoint `codex/` sans être passée par un rapport.
- Une contradiction d'invariant est nommée avec citation, jamais résolue en silence.
- Après application, les requêtes Dataview « Dette structurelle » et « Fiches invoquées mais jamais écrites » d'`index.md` reflètent l'état réel — c'est-à-dire que le frontmatter écrit est juste.
- Un rapport rédigé dans une session peut être appliqué dans une autre sans perte.
- Toute ingestion est annulable par un `git revert` unique, sans effet de bord sur les autres fiches du même lot.
- Aucun commit d'ingestion ne contient d'édition manuelle non liée.

## 9. Choix abandonnés

- **Réutiliser `_inbox/` comme dossier de dépôt** *(abandonné le 2026-07-28)* — mélange deux flux de nature différente : stubs vides d'Obsidian et fiches rédigées externes.
- **Ranger en quarantaine (`status: idea` + bloc de collisions en tête de fiche)** *(abandonné le 2026-07-28)* — les fiches non fiables entrent quand même dans le graphe et s'y accumulent.
- **Laisser l'agent trancher seul les contradictions** *(abandonné le 2026-07-28)* — fait dériver le canon sur des arbitrages structurants sans validation.
- **Sous-agent au lieu d'une skill** *(abandonné le 2026-07-28)* — contexte isolé, aucun débat possible sur une collision après restitution.
- **Rapport rendu en conversation seulement** *(abandonné le 2026-07-28)* — la passe 2 ne survivrait pas à un changement de session.
- **Branche `ingest/<date>` mergée après validation** *(abandonné le 2026-07-28)* — Obsidian ignore les branches ; un oubli de retour sur `main` fait diverger le vault en silence. Le contrôle est déjà assuré par la passe 1 : la branche déplace le risque au lieu de le réduire.
- **Un commit par lot d'ingestion** *(abandonné le 2026-07-28)* — rend impossible le retour arrière sur une seule fiche et sa propagation.
- **Aucun push automatique** *(abandonné le 2026-07-28)* — un canon validé mais non poussé laisse Claude Projects raisonner sur un état périmé, ce qui régénère le problème d'origine.

## 10. Dernière validation

**2026-07-28** — design validé en session, git inclus, avant implémentation.
