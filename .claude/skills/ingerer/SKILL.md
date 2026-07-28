---
name: ingerer
description: Ingère dans le vault les fiches déposées dans _raw/ — fiches rédigées hors du vault, typiquement par Claude Projects. Deux passes. `/ingerer` audite et écrit un rapport de collisions sans rien modifier. `/ingerer appliquer` normalise, range, propage les dépendances, commite et pousse, uniquement après arbitrage. À utiliser dès qu'un fichier apparaît dans _raw/, ou quand l'utilisateur parle d'ingérer, ranger, intégrer ou importer une fiche externe.
---

# Ingestion `_raw/`

Tu n'es pas un rangeur, tu es un **douanier**. Le rangement est l'étape finale et la moins importante. Ta valeur est le filtre qui la précède.

Les fiches de `_raw/` viennent d'un modèle qui a lu un instantané du dépôt sans remonter les `depends_on` jusqu'aux invariants, sans consulter la liste « Écartés » d'`index.md`, et sans vérifier qu'un terme qu'il invente n'existe pas déjà. Traite chaque fiche entrante comme suspecte par défaut.

Spec de référence : `_meta/specs/2026-07-28-ingestion-raw-design.md`.

## Aiguillage

- `/ingerer` (sans argument) → **passe 1, audit**. N'écrit que dans `_raw/_rapports/`.
- `/ingerer appliquer` → **passe 2, application**.

Commence toujours par `date +%F` pour la date réelle. Ne la devine jamais.

---

# Passe 1 — audit

**Règle absolue : aucune écriture hors de `_raw/_rapports/`.** Pas de normalisation « au passage », pas de déplacement, pas de correction de frontmatter dans une fiche existante. Si tu es tenté, c'est la passe 2.

Crée une tâche par étape ci-dessous et coche-les au fur et à mesure.

## 1. Recensement et commit d'entrée

```bash
date +%F
git status --short
ls _raw/*.md
```

Ignore `_raw/README.md` et tout ce qui est dans `_raw/_rapports/`. S'il n'y a aucun brut, dis-le et arrête-toi.

Commite les bruts déposés pour tracer ce qui est entré et sous quelle forme, puis pose le point de restauration du lot :

```bash
git add _raw && git commit -m "Dépose <n> fiche(s) dans _raw/"
git tag pre-ingest-<AAAA-MM-JJ>
```

Si le tag existe déjà (deuxième lot le même jour), suffixe `-2`, `-3`.

## 2. Reconstruction du canon

Lis **intégralement**, dans cette session, sans te fier à ta mémoire d'une session antérieure :

- `index.md` — en particulier « Ce qui est verrouillé », « Décisions en suspens », « Écartés (ne pas reproposer) », « Nommage en souffrance »
- `journal.md` — section « Écartés (et pourquoi) » pour les motifs détaillés
- `CLAUDE.md` si tu ne l'as pas déjà en contexte

## 3. Extraction

Pour chaque brut, relève :

- les **noms propres** (races, institutions, lieux, événements, personnages)
- les **concepts nommés** (mécanismes, doctrines, phénomènes)
- les **affirmations structurantes** — tout ce qui prétend établir une règle du monde
- les **liens** déclarés (`depends_on`, `touches`, wikilinks du corps)

## 4. Confrontation

Trois vérifications, dans l'ordre. Aucune n'est facultative.

### a. Le terme existe-t-il déjà ?

Pour chaque nom propre et concept extrait :

```bash
grep -rin "<terme>" --include="*.md" . | grep -v "^./_raw/"
```

Cherche aussi les **synonymes et périphrases** — le monde est dense, la moitié des « inventions » existent déjà sous un autre angle. Un concept déjà nommé qui reçoit un second nom est une collision 🟠.

### b. Contredit-elle un invariant ?

Confronte chaque affirmation structurante à « Ce qui est verrouillé ». En cas de heurt, **relève la citation exacte** de l'invariant. Ne paraphrase pas.

### c. Repropose-t-elle un écarté ?

Confronte à la liste « Écartés » d'`index.md` et à celle de `journal.md`. Une idée écartée qui revient est 🔴, même bien argumentée — le motif d'abandon est dans `journal.md`, cite-le.

Vérifie aussi les ⚠️ : la fiche tranche-t-elle une ⚠️ ouverte (c'est une décision, elle demande arbitrage), ou rouvre-t-elle une ⚠️ déjà tranchée ailleurs (c'est 🔴) ?

## 5. Remontée des dépendances

Ouvre les fiches que le brut touche, **et leurs `depends_on` en remontant jusqu'aux `invariant`**. C'est là que se cachent les collisions que les trois vérifications ratent.

Si tu n'as pas pu vérifier quelque chose, écris-le dans le rapport. Ne réponds jamais comme si tu l'avais vérifié.

## 6. Verdict

| Verdict | Critère |
|---|---|
| 🟢 **VERT** | Aucune collision. Type, couche et dossier déductibles sans ambiguïté. |
| 🟠 **ORANGE** | Collision non bloquante : réinvention lexicale, `depends_on` faux, chevauchement avec une fiche existante, type ou couche ambigus, ⚠️ tranchée en passant. |
| 🔴 **ROUGE** | Contredit un invariant verrouillé, ou repropose un écarté, ou rouvre une ⚠️ déjà tranchée. |

En cas de doute entre deux verdicts, prends le plus sévère.

Pour toute collision, propose une résolution par **unification** — faire des deux versions un même système avec une tension — et non par renommage. Le renommage laisse deux concepts concurrents dans le monde.

## 7. Rapport

Écris `_raw/_rapports/<AAAA-MM-JJ>-<slug>.md`. Le slug décrit le lot (`triarcat`, `deux-races`, `divers`).

```markdown
---
id: <AAAA-MM-JJ>-<slug>
type: meta
status: en-attente-arbitrage
---

# Rapport d'ingestion — <AAAA-MM-JJ>

<n> fiche(s) auditée(s) : 🟢 <n> · 🟠 <n> · 🔴 <n>

---

## `<nom-du-brut>.md` — 🔴 ROUGE

**Résumé** — ce que la fiche prétend établir, deux lignes maximum.

**Destination proposée** — `codex/<thème>/<id>.md` · `type: <type>` · `layer: <couche>` · `status: draft`

**Collisions**

1. **Contredit [[le-lien]]** — la fiche pose que X.
   Invariant verrouillé : « <citation exacte d'index.md> ».
   *Résolution proposée* — <unification, pas renommage>.
2. **Repropose un écarté** — « <intitulé exact de la ligne Écartés> ».
   Motif d'abandon (`journal.md`) : « <citation> ».

**Trous** — ce que la fiche laisse ouvert et qui devra devenir une ⚠️.

**Propagation prévue** — fiches dont le `touches` change · ⚠️ refermées et où · lignes de `journal.md` · sections d'`index.md`.

**Non vérifié** — ce que tu n'as pas pu confirmer, s'il y a lieu.

## Arbitrage

<!-- À remplir à la main. L'agent ne modifie jamais cette section.
     Une décision par collision numérotée. -->
```

Une section `##` par brut. Les 🟢 gardent la même structure, avec « Collisions : aucune ».

Commite :

```bash
git add _raw/_rapports && git commit -m "Audite le lot d'ingestion du <AAAA-MM-JJ>"
```

## 8. Restitution

En conversation, une ligne par brut : verdict, destination proposée, et pour les 🟠/🔴 la collision la plus lourde en une phrase. Puis rappelle qu'il faut remplir `## Arbitrage` avant `/ingerer appliquer`.

**N'applique rien. N'enchaîne pas sur la passe 2 de ta propre initiative.**

---

# Passe 2 — application

## 0. Garde-fous — avant toute chose

```bash
git status --short
```

**Working tree sale → arrête-toi.** Énumère les fichiers modifiés et demande de les commiter d'abord. Motif : Obsidian écrit en continu et ignore git ; si des édits en cours partent dans le commit d'ingestion, le `revert` censé annuler l'ingestion les détruira.

Les fichiers de `_raw/` que *tu* vas modifier ne comptent pas comme saleté — mais ils devraient déjà être commités par la passe 1.

Puis lis le rapport le plus récent de `_raw/_rapports/`.

**Refuse toute fiche 🟠 ou 🔴 dont la section `## Arbitrage` ne tranche pas.** Une section vide, ou qui ne couvre pas toutes les collisions numérotées, bloque cette fiche. Traite les autres, dis clairement laquelle tu as laissée et pourquoi.

Les 🟢 passent sans arbitrage.

Relis les fiches concernées **dans cette session** avant de les modifier. Ne te fie pas au rapport pour leur contenu actuel.

## Traite une fiche à la fois, de bout en bout

Pour **chaque** fiche retenue, exécute les cinq étapes puis commite. Ne groupe jamais deux fiches dans un commit.

### 1. Normaliser

Pars du gabarit de `_meta/templates/` correspondant au `type` : `codex.md`, `race.md`, `tension.md`, `chronique.md`.

- `id` = nom de fichier, sans extension, en kebab-case
- `aliases` : le nom lisible, pour que `[[Nom Lisible]]` fonctionne en prose
- **champs relationnels en wikilinks entre guillemets** — `- "[[le-cycle]]"`. Jamais de backticks : une fiche en `` `le-cycle` `` est invisible du graphe. Jamais de chemin relatif : les wikilinks se résolvent par nom de fichier.
- Un lien vers une fiche non écrite est **voulu** — nœud gris, il matérialise le trou. Ne le supprime pas.
- Sections finales `## Choix abandonnés` et `## Dernière validation` présentes, datées du jour.
- Tout ce que le corps marque comme ancien, corrigé ou remplacé est **déplacé** dans « Choix abandonnés », horodaté `*(abandonné le AAAA-MM-JJ)*` avec son motif. Le corps ne contient que ce qui est vrai.
- Les trous deviennent des ⚠️ dans le corps **et** sont listés dans le callout `> [!warning] Trous volontaires`. L'emoji reste sur chaque ligne pour rester greppable.
- **Fiche de race : les quatre axes sont obligatoires** — faculté innée, idéologie du rôle, blessure historique, apport à la dyade. Un axe manquant devient une ⚠️ explicite, jamais une omission silencieuse. Sans l'axe 4, personne n'a de raison de se lier à cette race.

Tu ne rédiges pas de contenu de canon. Un trou reste un trou.

### 2. Ranger

Dossier **thématique**, déduit du sujet :

```
codex/monde/          physique du monde
codex/races/          fiches de race
codex/institutions/   tisseuses, la-voix, veilleurs, écoles…
codex/histoire/       la-purge, l-unification, la-rupture…
codex/lieux/          géographie, lieux de rite
tension/              type: tension
chronique/            type: chronique
```

**Jamais de dossier par couche.** `invariant`/`consequence`/`history`/`ground` vivent dans le frontmatter — une fiche qui change de couche ne change pas de place.

Utilise `git mv` pour préserver la traçabilité.

### 3. Statuer

`status: draft` par défaut. **`canon` n'est jamais attribué par l'agent** — il ne se donne que si l'ossature est verrouillée, et c'est un jugement humain. Si l'arbitrage demande explicitement `canon`, vérifie d'abord qu'aucune dépendance déclarée n'est en dessous de `canon`, et signale-le sinon.

### 4. Propager

C'est l'étape qui justifie le dispositif. Ne l'abrège pas.

- **`touches` amont** — ajoute la nouvelle fiche au `touches` de chaque fiche qu'elle contraint. Un `depends_on` sans le `touches` réciproque se voit dans le graphe.
- **⚠️ refermées** — une ⚠️ tranchée par l'arbitrage doit être fermée **partout où elle apparaît**, pas seulement dans la fiche neuve. `grep -rn "⚠️" --include="*.md" .` pour les retrouver toutes.
- **Obsolescence** — si la décision rend caduc quelque chose écrit ailleurs, corrige-le et déplace l'ancienne version dans les « Choix abandonnés » de la fiche concernée.
- **`journal.md`** — une ligne par décision : ce qui a été tranché, et pourquoi. Les idées écartées vont dans « Écartés (et pourquoi) » avec leur motif.
- **`index.md`, moitié manuelle uniquement** — « Ce qui est verrouillé », « Décisions en suspens », « Nommage en souffrance », « Chantiers », « Écartés ». **Ne touche jamais aux blocs Dataview** : ils lisent le frontmatter et ne peuvent pas mentir tant que celui-ci est juste.

Cette propagation ne demande pas d'autorisation — `CLAUDE.md` §7 la qualifie de maintenance. Mentionne-la, ne la soumets pas.

### 5. Nettoyer et commiter

Supprime le brut de `_raw/` (`git rm`). Git en garde la trace.

Un commit par fiche, propagation comprise :

```
Ingère <id-fiche> depuis _raw/

Rangée dans codex/<thème>/. Verdict d'audit : <VERT|ORANGE|ROUGE>.

Propagation :
- touches mis à jour dans <fiche-amont>
- ⚠️ <intitulé> refermée dans <fiche>
- journal.md : <décision>
- index.md : <section touchée>
```

Motif de la granularité : si la fiche se révèle fausse plus tard, `git revert <sha>` défait la fiche **et toute sa propagation** en une opération. Un commit couvrant plusieurs fiches rend ce retour arrière impraticable.

## Clôture du lot

1. Passe le rapport à `status: applique`, commite-le.
2. `git push`.
3. Restitue : une ligne par fiche ingérée avec sa destination, la liste de ce que la propagation a touché, et **ce que tu n'as pas appliqué et pourquoi**.
4. Si `_raw/` n'est pas vide, dis ce qui reste et ce qui le bloque.

Retour arrière : `git revert <sha>` pour une fiche, `git reset --hard pre-ingest-<AAAA-MM-JJ>` pour le lot entier.

---

# Ce que tu ne fais jamais

- Écrire dans le vault pendant la passe 1.
- Appliquer une fiche 🟠 ou 🔴 non arbitrée.
- Résoudre seul une contradiction avec un invariant.
- Attribuer `status: canon`.
- Rédiger du contenu de canon pour combler un trou.
- Toucher aux blocs Dataview d'`index.md`.
- Toucher à `_inbox/` — c'est le sas des stubs vides d'Obsidian, autre flux, autre traitement.
- Grouper plusieurs fiches dans un commit.
- Commiter sur un working tree que tu n'as pas vérifié.
