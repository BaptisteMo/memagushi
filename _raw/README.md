---
id: raw-readme
type: meta
status: vivant
---

# _raw — dépôt des fiches rédigées hors du vault

Dépose ici les `.md` produits ailleurs — typiquement par Claude Projects branché au dépôt GitHub. Nom de fichier libre, frontmatter facultatif, format quelconque.

**Ne range rien à la main depuis ce dossier.** Lance `/ingerer`.

---

## Pourquoi ce sas existe

Claude Projects lit un instantané du dépôt. Il ne remonte pas les chaînes `depends_on` jusqu'aux invariants, ne consulte pas la liste « Écartés » d'`index.md`, et ne vérifie pas qu'un terme qu'il invente n'existe pas déjà ailleurs sous un autre angle. Ses fiches sont donc suspectes sur trois plans : contradiction d'invariant, reproposition d'un écarté, réinvention lexicale.

Ranger sans filtrer automatiserait l'entrée de ces trois défauts **et les rendrait invisibles** — pire que le report manuel.

## Le circuit

1. Tu déposes un ou plusieurs `.md` ici.
2. `/ingerer` — audite, ne touche à rien, écrit un rapport dans `_rapports/`.
3. Tu remplis la section `## Arbitrage` du rapport pour tout ce qui est 🟠 ou 🔴.
4. `/ingerer appliquer` — normalise, range, propage, commite, pousse.
5. Le brut disparaît d'ici. Git en garde la trace.

Rien ne doit rester dans ce dossier une fois le lot appliqué.

## Ce que l'ingestion ne fait pas

- Elle ne rédige pas de contenu de canon. Un trou reste un trou, marqué ⚠️.
- Elle n'attribue jamais `status: canon`.
- Elle ne tranche jamais une contradiction seule.

## À ne pas confondre avec `_inbox/`

`_inbox/` est le sas des **stubs vides** créés par un clic Obsidian sur un lien non résolu. Deux flux distincts, deux traitements distincts. `/ingerer` ne touche pas à `_inbox/`.

---

Spec complète : [[2026-07-28-ingestion-raw-design]].
