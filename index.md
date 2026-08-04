---
id: index
aliases: [Index, Accueil]
type: meta
status: vivant
maj: 2026-07-28
cssclasses: []
---

# Index — Le Sillage Luminal

> **Usage.** Carte du corpus. À lire en premier, à chaque session.
>
> Cet index a **deux moitiés**. Ce qui suit immédiatement est **calculé** à partir du frontmatter des fiches : ça ne peut pas mentir tant que le frontmatter est juste. Ce qui vient après « Ce qui est verrouillé » est **rédigé à la main** : ce sont des jugements, aucune requête ne les produira. Voir `CLAUDE.md` §7.

> [!info] Dataview requis
> Les blocs ci-dessous s'affichent en code brut tant que le module **Dataview** n'est pas installé.
> *Paramètres → Modules complémentaires → Parcourir → « Dataview » → Installer, puis Activer.*

---

## État du corpus

<!-- QueryToSerialize: TABLE WITHOUT ID file.link AS "Fiche", type AS "Type", layer AS "Couche", status AS "Statut", length(file.outlinks) AS "Liens sortants" FROM "codex" OR "tension" OR "chronique" WHERE type SORT status DESC, layer ASC, file.name ASC -->
<!-- SerializedQuery: TABLE WITHOUT ID file.link AS "Fiche", type AS "Type", layer AS "Couche", status AS "Statut", length(file.outlinks) AS "Liens sortants" FROM "codex" OR "tension" OR "chronique" WHERE type SORT status DESC, layer ASC, file.name ASC -->
| Fiche | Type | Couche | Statut | Liens sortants |
| ----- | ---- | ------ | ------ | -------------- |
| [[economie]] | codex | consequence | draft | 42 |
| [[coeur-magique]] | codex | invariant | draft | 32 |
| [[le-lien]] | codex | invariant | draft | 82 |
| [[le-plan]] | codex | invariant | draft | 43 |
| [[le-cycle]] | codex | invariant | canon | 52 |
<!-- SerializedQuery END -->

### Les invariants et ce qui en dépend

<!-- QueryToSerialize: TABLE WITHOUT ID file.link AS "Fiche", depends_on AS "Dépend de", touches AS "Contraint" FROM "codex" OR "tension" OR "chronique" WHERE type SORT layer ASC -->
<!-- SerializedQuery: TABLE WITHOUT ID file.link AS "Fiche", depends_on AS "Dépend de", touches AS "Contraint" FROM "codex" OR "tension" OR "chronique" WHERE type SORT layer ASC -->
| Fiche | Dépend de | Contraint |
| ----- | --------- | --------- |
| [[economie]] | [[le-cycle]], [[le-lien]], [[le-plan]] | [[lumens]], [[roche-memoire]], [[prismes-noirs]], [[vexhards]], [[tisseuses]], [[geographie]], [[la-purge]] |
| [[coeur-magique]] | [[le-cycle]], [[le-plan]], [[flux]] | [[le-lien]], [[l-epanchement]], [[races-liees]], [[inlies]] |
| [[le-cycle]] | [[gemmes]], [[flux]], [[coeur-magique]] | [[le-lien]], [[le-plan]], [[races-liees]], [[roche-memoire]], [[lumens]], [[vexhards]], [[oracles]], [[economie]], [[la-purge]], [[geographie]] |
| [[le-lien]] | [[coeur-magique]], [[le-plan]], [[sirrhal]], [[le-cycle]] | [[inlies]], [[tisseuses]], [[veilleurs-du-souffle]], [[castes]], [[hauts-harmoniques]], [[races-liees]], [[eclats-nus]], [[la-rupture]], [[vexhards]], [[lexique]], [[geographie]], [[la-voix]], [[lumens]] |
| [[le-plan]] | [[le-cycle]], [[flux]] | [[coeur-magique]], [[le-lien]], [[l-epanchement]], [[lumens]], [[prismes-noirs]], [[roche-memoire]], [[tisseuses]], [[humain]], [[dragon]], [[races-liees]], [[lexique]] |
<!-- SerializedQuery END -->

---

## Dette structurelle

*Fiches marquées `canon` alors qu'une de leurs dépendances n'est pas écrite, ou n'est pas elle-même `canon`. Toute ligne ici est un endroit où le canon repose sur du vide.*

```dataviewjs
const pages = dv.pages('"codex" or "tension" or "chronique"').where(p => p.type)
const statut = new Map(pages.map(p => [p.file.name, p.status]))
const rows = []
for (const p of pages) {
  for (const d of (p.depends_on ?? [])) {
    const nom = d.path ? d.path.split("/").pop().replace(/\.md$/, "") : String(d)
    const s = statut.get(nom)
    if (s === undefined) rows.push([p.file.link, nom, "❌ fiche inexistante", p.status])
    else if (p.status === "canon" && s !== "canon") rows.push([p.file.link, nom, "⚠️ dépendance " + s, p.status])
  }
}
if (rows.length) dv.table(["Fiche", "Dépendance", "Problème", "Statut de la fiche"], rows)
else dv.paragraph("✅ Aucune dette : toute dépendance déclarée existe et est au moins aussi solide que la fiche qui s'appuie dessus.")
```

## Fiches invoquées mais jamais écrites

*Les nœuds gris du graphe. Chacune est un chantier implicite que quelqu'un a déjà présupposé.*

```dataviewjs
const pages = dv.pages('"codex" or "tension" or "chronique"').where(p => p.type)
const existantes = new Set(dv.pages().map(p => p.file.name))
const manquantes = new Map()
for (const p of pages) {
  for (const l of p.file.outlinks) {
    const nom = l.path.split("/").pop().replace(/\.md$/, "")
    if (existantes.has(nom)) continue
    if (!manquantes.has(nom)) manquantes.set(nom, [])
    manquantes.get(nom).push(p.file.link)
  }
}
const rows = [...manquantes.entries()]
  .sort((a, b) => b[1].length - a[1].length)
  .map(([nom, refs]) => [nom, refs.length, refs])
dv.paragraph(`**${rows.length}** fiches invoquées, jamais écrites. Les plus réclamées d'abord.`)
dv.table(["Fiche manquante", "Réclamée par", "Où"], rows)
```

---

## Ce qui est verrouillé (ne pas contredire)

> **Refonte du 2026-07-28 — les couleurs n'existent plus.** Le système chromatique est supprimé du monde et remplacé par [[le-plan|le Plan]]. Aucune fiche ne doit mentionner teinte, saturation ou luminosité hors de ses « Choix abandonnés ». Voir [[journal#Refonte du système de magie — les couleurs disparaissent (2026-07-28)|journal.md]].

**Physique du monde**

- **Le Cycle est une respiration, pas un robinet.** La gemme exhale du Flux indifférencié ; le vivant le différencie ; la gemme réinspire. Le vivant est un **organe**, pas un bénéficiaire.
- **Le Cycle est une conservation.** Le Flux n'est ni créé ni détruit. L'énergie qu'un praticien engage est **tirée du Cycle**, jamais fabriquée.
- **Boucle de rétroaction.** La gemme inspire d'autant plus fort qu'elle reçoit moins. L'escalade des Rétractations est physiologique, pas morale.
- **Deux respirations imbriquées.** Pouls court (~2 ans) / Grande Étreinte (~10 ans, irrégulière, proportionnelle à la dette).
- **La magie n'est pas vitale, elle est constitutive.** On en manque comme d'un sens, pas comme d'air. La Rétractation affaiblit, elle ne tue que les plus fragiles, et indirectement. La société tourne autour de la magie sans en dépendre pour survivre.

**Le Plan — deux axes, et rien d'autre**

- **La magie n'a ni couleur ni élément.** Elle agit sur la matière ordinaire, et se situe entièrement par deux grandeurs : l'**énergie** (combien — une jauge) et l'**entropie** (dans quel sens on pousse l'ordre — une boussole).
- **Tout acte est un point du plan**, portant les deux coordonnées à la fois. Il n'existe pas de gestes séparés qu'on choisirait dans une liste.
- **Les états de la matière sont des résultats, pas des opérations.** Fondre de la glace et fondre de la roche est le même geste ; seul le *combien* diffère.
- **Pas de transmutation de substance.** La magie déplace et énergise la matière, elle ne change pas un élément en un autre.
- **Les deux pôles d'entropie sont non-moraux.** Vers le dispersé : l'ordre se dissipe, le monde reprend son dû. Vers l'ordonné : l'ordre est verrouillé, et l'univers paie ailleurs — la Rétractation s'aggrave. Une culture de la permanence honore l'un, une culture du moment vivant honore l'autre.
- **Tout détournement respiratoire est un ordre verrouillé.** Roche-Mémoire, Lumens, Prismes Noirs ont la même signature physique. *Corollaire : une civilisation qui bâtit pour durer creuse sa propre disette.*
- **L'identité est une position, pas un domaine.** On naît en un point du plan : il n'interdit rien, il fixe ce qui est bon marché et ce qui est ruineux. **Jamais de déblocage, seulement un continuum de coût.**
- **Rien n'est figé, tout est coûteux.** Une faculté innée est un **tarif préférentiel**, jamais un pouvoir exclusif.
- **Règle de rédaction impérative :** ne jamais écrire un **état**, toujours une **direction**. « Untel fait du solide » rouvre la magie-élément ; « pour untel, tout ce qui va vers l'ordre est bon marché » tient le système.

**Le cœur et la dyade**

- **Deux rôles, deux temps d'un même acte.** Le réceptacle **charge** (met le Flux sous tension, rien ne sort encore) ; l'utilisateur **libère** (relâche sur le réel). Aucun cœur ne tient les deux.
- **Chaque rôle blesse celui qui le tient seul.** Le réceptacle **sature**, l'utilisateur **s'assèche**. Deux manques opposés dans deux monnaies : symbiose, pas exploitation — l'utilisateur est une **soupape**. Le mépris du réceptacle n'a **aucune base technique**.
- **Le rôle est fixé à la naissance et illisible avant l'Épanchement.** On ne peut donc lier personne avant lui.
- **« Un cœur rempli ne s'ouvre pas ».** L'Épanchement exige un manque. Revers : **combler un enfant est un moyen de l'empêcher de s'ouvrir — l'amour comme verrou.**
- **Aucune espèce n'est l'axe.** Une dyade = réceptacle + utilisateur. Il existe des dyades sans humain.
- **Fenêtre unique.** Le lien ne se forme qu'une fois, dans la petite enfance. Tout lien ultérieur est artificiel, coûteux, transgressif.

**Le lien et sa société**

- **L'harmonie est une distance, pas un interrupteur** — l'écart entre deux positions dans le Plan.
- **Il n'existe aucune barrière absolue d'appariement.** Aucune position n'étant interdite, tout lien est théoriquement possible et **le prix seul décide**. *Plus dur que l'ancienne loi binaire : il n'y a plus de fatalité à invoquer, donc plus d'excuse.*
- **Un Inlié n'est pas quelqu'un qu'on ne pouvait pas lier**, c'est quelqu'un que le rite **n'a pas su financer**.
- **La Tisseuse modèle les deux coordonnées** et déplace la position d'origine d'un enfant **à vie** — c'est un artisanat : deux praticiennes n'obtiennent pas le même résultat. Officielle / déchue = différence de degré, pas de nature.
- **La privation est le moteur du rite.** Trauma collectif que personne ne nomme.
- **Deux registres.** Celui des naissances (ce que tu étais) et le statut réévalué (ce que tu vaux). Lequel fonde la caste = ligne de fracture sociale.
- **Aucun accordeur universel.** Chacun se greffe à un autre par **affinité** ; nul ne s'accorde à tous.

**Les races**

- **Aucune race ne porte de règle mécanique propre.** Le cœur et ses deux rôles sont universels. Ce qui varie est la **région d'origine** dans le Plan, et ce que la **culture** en fait. Les différences sont **doctrinales avant d'être biologiques**.
- **Aucune race n'a d'outil de lecture supérieur.**
- **Gabarit de race : quatre axes obligatoires.**

---

## Décisions en suspens

### Structurantes (bloquent d'autres fiches)

- **⚠️ Le plafond de convergence d'une dyade.** Rouvert par la refonte du 2026-07-28 : l'ancien calcul par axes est mort. Le Plan a **deux** axes, une dyade **deux** membres — plus rien n'interdit à un couple qui travaille d'atteindre l'harmonie parfaite sans l'avoir reçue au berceau. **Si ça tient, la noblesse de naissance perd toute justification en une génération.** *Piste : converger coûterait de l'énergie prise sur le budget de la dyade — plafond économique, pas géométrique.* Voir [[le-lien#6.1 Le tissage est un instant T — le lien, lui, évolue|le-lien §6.1]]. **Le plus lourd des points ouverts.**
- **⚠️ La forme du Plan** — quatre pôles francs, ou régions continues autour d'un centre ? *Devenu structurant depuis la suppression des couleurs : décide si le monde garde des « familles » d'appariement ou un pur continuum. Bloque les fiches de race.*
- **⚠️ Ce que la magie ne touche pas.** L'esprit, l'âme, le lien lui-même sont-ils soumis aux deux axes ? *Décide si le [[sirrhal|Sirrhal]] est un objet manipulable, donc si [[la-rupture]] relève de la physique ou du sacrilège.*
- **⚠️ Le nombre et l'emplacement des origines** — combien de points de départ typiques, et où. *Gelé tant que [[humain]] et [[dragon]] ne sont pas réécrits.*
- **L'interruption du geste.** Chez Shirahama, couper la ligne annule le sort — la magie y est dramatiquement vulnérable. Le Sillage n'a pas d'équivalent : la distance joue-t-elle, peut-on brouiller un lien sans le rompre ?
- **L'Unification sous le [[triarcat|Triarcat]]** — plus grosse dette historique. Tout le présent devrait en être la cicatrice.
- **La Purge** — nom, date, doctrine, déroulé, modalités actuelles de l'« entretien ». *Bloque [[la-purge]] et la réécriture de [[humain]].*
- **Il manque une race qui glorifie le réceptacle** et méprise les humains comme dépensiers stériles. 3 à 5 races au total visées.

### Incohérences tenues à l'œil

*Points structurants volontairement non tranchés. Ne pas les perdre de vue : chacun contraint des fiches à venir.*

- **⚠️ L'écart d'énergie : barrière ou rendement ?** Voir [[le-lien#6. L'échelle d'harmonie : la lecture des positions|le-lien §6]]. **Barrière** → la puissance ne s'apparie qu'à la puissance, et la noblesse devient une contrainte physique que l'aristocratie peut invoquer sans mentir. **Rendement** (privilégié) → le lien tient mais fuit ; dyade vivable et dissonante.
- **⚠️ Où va la déperdition ?** Si l'écart dissipe du Flux hors du Cycle, une dyade mal accordée **aggrave la Rétractation pour tous** — et les mal-appariés sont les pauvres et les forcés. L'élite bien accordée pourrait alors se dire vertueuse.
- **⚠️ Qu'est-ce qui rend un enfant inliable en pratique ?** Le lieu, la praticienne, ou l'enfant ? *Puisque aucun appariement n'est impossible, la réponse désigne un **coupable** — c'est tout le procès social des Inliés.*
- **⚠️ Peut-on re-disperser un ordre verrouillé ?** Passage à sens unique, ou dette remboursable ?
- **⚠️ Le statut réévalué** — qui mesure, à quelle fréquence, et **lequel des deux registres fonde légalement la caste** ?
- **⚠️ Le rôle est-il détectable avant l'Épanchement ?** *(Détermine si une famille peut cacher un enfant réceptacle dès la naissance. Piste privilégiée en [[coeur-magique]] : aucun signal réel, mais une caste qui prétend le contraire — art divinatoire, charlatans, marché.)*

### Ouvertes, non bloquantes

- ⚠️ « Vider le cœur » : arrachement affectif ou saignée physiologique ? *(Les deux ne font pas la même horreur. Renvoyé à [[l-epanchement]].)*
- ⚠️ Des cœurs qui ne s'ouvrent jamais — par nature, ou par échec du déclenchement ?
- ⚠️ Seuil légal de forçage — où passe la limite, qui l'a fixée.
- ⚠️ Hypothèse de la **diversification respiratoire** — des dyades différenciant largement adouciraient-elles la Rétractation localement ? À valider ou écarter.
- ⚠️ Les Inliés développent-ils leur propre caractéristique magique ? *(Un cœur qui charge sans jamais se déverser — ouvert le 2026-07-22.)*
- ⚠️ Le signal de fin de Stabilisation.
- ⚠️ La dette respiratoire est-elle mesurable, et par qui ?
- ⚠️ Les gemmes sont-elles conscientes ? *(À laisser irrésolu, probablement.)*
- ⚠️ Les [[korr-siir|Korr-Siir]] : aboutissement de la doctrine de l'utilisateur, ou hérésie ?

### Nommage en souffrance

Endonymes humain et dragon · exonymes croisés · les deux branches de Tisseuses (caste noble / mot-injure) · les lieux de rite (générique + noms propres) · les grades d'harmonie · l'agôgè dragonne et ses étapes · les déclassés · **tout le vocabulaire du Plan** (comment le vulgaire nomme les deux axes, les régions, les positions — le registre chromatique est mort et rien ne l'a remplacé).

→ Tout ça converge vers [[lexique]], non écrit. Principe du **planisphère** : aucun terme n'est neutre.

---

## Chantiers

**Prioritaires** — **réécrire [[humain]] et [[dragon]]** *(supprimées le 2026-07-28 ; à refaire comme cultures portant une région d'origine et une doctrine, plus une règle mécanique — contenu récupérable dans git)* · **trancher le plafond de convergence** ([[le-lien]] §6.1) · **[[flux]] et [[l-epanchement]]** *(invoquées par [[le-plan]] et [[coeur-magique]], jamais écrites : le Flux est supposé porter énergie et entropie sans qu'aucune fiche l'établisse)* · les autres races (chacune : 4 axes) · l'Unification sous le Triarcat · [[la-purge]].

**En attente** — [[lumens]] **(débloqué : marché premium/classique, charge par position, perfusion en récession — concept mûr, prêt à écrire)** · [[heredite]] **(promu : reproduction, sexualité, transmission de la position d'origine — sujet central d'une société)** · [[ecoles]] · [[lexique]] · [[la-rupture]] (le crime suprême, l'upgrade, le droit qui en découle) · couche **ground** (vie quotidienne, cycle de vie, culture de la mort, géographie vécue, templates POV).

**Clos** — [[chantier-systeme-magie]] *(carrefour tranché le 2026-07-28 par une troisième voie ; conservé pour son §5, le cimetière des pistes)* · [[piste-etats-matiere]] *(écartée, mais sa couche « difficulté » survit sous le Plan)*. États de l'art toujours utiles : [[recherche-systemes-magie]] et [[recherche-magie-difficulte]].

---

## Écartés (ne pas reproposer)

**Refonte du 2026-07-28 — supprimés du monde, pas seulement écartés :** le **système chromatique entier** (teinte, saturation, luminosité) · la **teinte comme opération** (séparer / lier / suspendre) · la **synthèse additive des secondaires** (transformer / soigner / extraire) · les **six familles nommées** · la **teinte comme état de la matière** · l'**axe de faible résistance par espèce** (dragons sur S, humains sur H) · la **mobilité chromatique** comme faculté humaine · le **plafond arithmétique des dyades** et la **supériorité mécanique de la mixité** · la **loi originelle de famille chromatique** · la **grammaire composable** façon *Atelier des Sorciers*.

**Antérieurs :** modèle « robinet » du Cycle · longévité comme trait dragon · outil de mesure exclusif aux dragons · amplitude humaine comme apport à la dyade · plafond de maturité à la mort de l'humain · race liée à une phase du Cycle (quatre bêtes chinoises) · checklist plate des aspects du monde · teinte comme condition binaire · accords sur teintes complémentaires · arc humain comme gradient de saturation · cercle entier obtenu par entraînement · découpage culturel variable du spectre · teinte = élément · primaires « force / forme / mémoire » · alphabet de glyphes tracés · loi du figement des valeurs · bleu = « fixer » · les réceptacles humains comme « accordeurs du monde ».

→ Motifs détaillés dans [[journal#Écartés (et pourquoi)|journal.md]].
