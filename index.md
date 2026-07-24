---
id: index
aliases: [Index, Accueil]
type: meta
status: vivant
maj: 2026-07-22
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

```dataview
TABLE WITHOUT ID
  file.link AS "Fiche",
  type AS "Type",
  layer AS "Couche",
  status AS "Statut",
  length(file.outlinks) AS "Liens sortants"
FROM "codex" OR "tension" OR "chronique"
WHERE type
SORT status DESC, layer ASC, file.name ASC
```

### Les invariants et ce qui en dépend

```dataview
TABLE WITHOUT ID
  file.link AS "Fiche",
  depends_on AS "Dépend de",
  touches AS "Contraint"
FROM "codex" OR "tension" OR "chronique"
WHERE type
SORT layer ASC
```

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

- **Le Cycle est une respiration, pas un robinet.** La gemme exhale du Flux indifférencié ; le vivant le différencie ; la gemme réinspire. Le vivant est un **organe**, pas un bénéficiaire.
- **Boucle de rétroaction.** La gemme inspire d'autant plus fort qu'elle reçoit moins. L'escalade des Rétractations est physiologique, pas morale.
- **Deux respirations imbriquées.** Pouls court (~2 ans) / Grande Étreinte (~10 ans, irrégulière, proportionnelle à la dette).
- **Fenêtre unique.** Le lien ne se forme qu'une fois, dans la petite enfance. Tout lien ultérieur est artificiel, coûteux, transgressif.
- **Aucune espèce n'est l'axe.** Une dyade = réceptacle + utilisateur. Il existe des dyades sans humain.
- **Réceptacle / utilisateur.** Le réceptacle capte et différencie mais sature ; l'utilisateur dépense mais s'assèche. Symbiose, pas exploitation — l'utilisateur est une **soupape**.
- **L'harmonie est une distance, pas un interrupteur.** Seule condition binaire : **on ne se lie que dans sa famille chromatique** (loi originelle). À l'intérieur d'une famille, tout est degré, sur les trois valeurs.
- **La Tisseuse modèle les trois paramètres**, pas seulement la teinte — et c'est un artisanat : deux praticiennes n'obtiennent pas le même résultat.
- **Une teinte est un geste, pas une matière.** Rouge = **séparer**, vert = **lier**, bleu = **suspendre**. Le rouge n'est pas le feu ; le système élémentaire est refusé.
- **Les secondaires sont déduites, jamais choisies.** Additif : jaune = transformer, cyan = soigner, magenta = extraire. Un usage qui ne se lit pas comme la somme de ses primaires est une erreur de canon.
- **La magie n'est pas vitale, elle est constitutive.** On en manque comme d'un sens, pas comme d'air. La Rétractation affaiblit, elle ne tue que les plus fragiles, et indirectement. La société tourne autour de la magie sans en dépendre pour survivre.
- **La magie est une pratique, et elle progresse en finesse, pas en puissance.** Les deux rôles ont une maîtrise comparable — celle du réceptacle est le débit et l'anticipation.
- **Six familles nommées** (3 primaires + 3 secondaires) comme grille canonique ; le continuum en degrés sert à la mesure, pas à structurer la magie.
- **Rien n'est figé, tout est coûteux.** Aucune valeur n'est verrouillée : seul le **prix** change. Une faculté innée est un **tarif préférentiel**, pas un pouvoir exclusif. Dragons = axe **S**, humains = axe **H**. *(Remplace la « loi du figement ».)*
- **Chacun est enfermé dans la dimension de l'autre.** Un dragon ne changera jamais de domaine, un humain ne sera jamais puissant — sauf en dyade mixte, seul objet du monde mobile sur deux axes.
- **Le lien se renforce avec le temps, et plafonne.** Une dyade converge sur autant d'axes que ses deux membres en apportent de distincts — **deux** pour humain+dragon, **un seul** pour une dyade homogène, **jamais trois** (deux membres ne portent pas trois axes). L'harmonie parfaite est donc structurellement hors d'atteinte : on peut monter, on ne peut pas rejoindre ceux qui sont nés parfaits.
- **La mixité est mécaniquement supérieure à l'endogamie** — ce qui réfute le « calcul » dragon.
- **Deux registres.** Celui des naissances (ce que tu étais) et le statut réévalué (ce que tu vaux). Lequel fonde la caste = ligne de fracture sociale.
- **Le cercle entier est une absence de résistance**, pas un pouvoir — et réservé à un personnage. Jamais une faction, jamais une lignée.
- **La privation est le moteur du rite.** Trauma collectif que personne ne nomme.
- **Les Tisseuses éditent la teinte** d'un enfant à vie. Officielle / déchue = différence de degré, pas de nature.
- **La saturation gouverne la mobilité.** Haute saturation → puissant mais **ancré** ; faible saturation → **mobile** mais faible. S est le prix de la mobilité sur H. Les dragons montent en S et se verrouillent ; les humains restent bas et se déplacent.
- **Faculté humaine = la mobilité chromatique.** La teinte se déplace avec le travail (l'effet cascade sur la dyade) ; l'humain **choisit sa voie**, mais reste faible partout. Se spécialiser lui coûte sa mobilité même.
- **Aucun accordeur universel.** Chacun se greffe à un autre par **affinité** ; nul ne s'accorde à tous. Le cercle entier est **polyvalence** (produit tout domaine), pas une clé universelle.
- **Aucune race n'a d'outil de lecture supérieur.** Les différences sont doctrinales.
- **Gabarit de race : quatre axes obligatoires.**

---

## Décisions en suspens

### Structurantes (bloquent d'autres fiches)

- **Naît-on secondaire ?** Un être peut-il naître cyan, ou les secondaires ne s'obtiennent-elles que par composition (deux dyades, ou un humain) ? *Détermine si le monde compte six familles de naissance ou trois. Bloque toutes les fiches de race.*
- **L'interruption du geste.** Chez Shirahama, couper la ligne annule le sort — la magie y est dramatiquement vulnérable. Le Sillage n'a pas d'équivalent : la distance joue-t-elle, peut-on brouiller un lien sans le rompre ?
- **L'Unification sous le [[triarcat|Triarcat]]** — plus grosse dette historique. Tout le présent devrait en être la cicatrice.
- **La Purge** — nom, date, doctrine, déroulé, modalités actuelles de l'« entretien ». *Bloque : [[la-purge]], et la moitié de [[humain]].*
- **Il manque une race qui glorifie le réceptacle** et méprise les humains comme dépensiers stériles. 3 à 5 races au total visées.

### Incohérences tenues à l'œil

*Points structurants volontairement non tranchés. Ne pas les perdre de vue : chacun contraint des fiches à venir.*

- **⚠️ L'écart de saturation : barrière ou rendement ?** Voir [[le-lien#6. L'échelle d'harmonie : la lecture chromatique|le-lien §6]]. **Barrière** → la puissance ne s'apparie qu'à la puissance, et la noblesse devient une contrainte physique que l'aristocratie peut invoquer sans mentir. **Rendement** (privilégié) → le lien tient mais fuit ; dyade vivable et dissonante. *Le plus lourd des points ouverts.*
- **⚠️ Où va la déperdition ?** Si l'écart dissipe du Flux hors du Cycle, une dyade mal accordée **aggrave la Rétractation pour tous** — et les mal-appariés sont les pauvres et les forcés. L'élite bien accordée pourrait alors se dire vertueuse.
- **⚠️ La luminosité ne veut rien dire.** Teinte = domaine, saturation = puissance, troisième axe = ⚠️. *Bloque [[couleurs-magiques]]. Piste : ce serait l'axe de faible résistance d'une race non écrite.*
- **⚠️ Le statut réévalué** — qui mesure, à quelle fréquence, et **lequel des deux registres fonde légalement la caste** ?
- **⚠️ Quels deux axes convergent** dans une dyade qui travaille — les mêmes pour tous, ou selon les espèces ?
- **⚠️ Le seuil de famille chromatique** — combien de degrés d'écart avant l'impossible, et est-ce le même pour toutes les races ?
- **⚠️ La plage humaine franchit-elle les frontières de famille ?** Si oui, la faculté humaine **contourne la loi originelle de liaison** — et devient bien plus subversive que ce que [[humain]] en dit aujourd'hui.

### Ouvertes, non bloquantes

- ⚠️ Seuil légal de forçage — où passe la limite, qui l'a fixée.
- ⚠️ L'arc dragon peut-il s'élargir avec l'entraînement ? *(Si oui : accordeurs universels, plus besoin de personne. Savoir qui vaut une guerre.)*
- ⚠️ L'élite dragonne connaît-elle le secret du besoin ? *(Recommandation en attente : quelques-uns le savent.)*
- ⚠️ Hypothèse de la **diversification respiratoire** — les dyades humaines adouciraient-elles la Rétractation localement ? À valider ou écarter.
- ⚠️ Le rôle est-il détectable avant l'Épanchement ? *(Détermine si une famille peut cacher un enfant réceptacle dès la naissance.)*
- ⚠️ Les Inliés développent-ils leur propre caractéristique magique ? *(Un cœur qui ne se déverse jamais — ouvert le 2026-07-22.)*
- ⚠️ Le signal de fin de Stabilisation.
- ⚠️ La dette respiratoire est-elle mesurable, et par qui ?
- ⚠️ Les gemmes sont-elles conscientes ? *(À laisser irrésolu, probablement.)*
- ⚠️ Formule du ratio dragon — à définir ou garder opaque.
- ⚠️ Y a-t-il un plafond à la croissance dragonne ?
- ⚠️ Les [[korr-siir|Korr-Siir]] : aboutissement de la doctrine de l'utilisateur, ou hérésie ?

### Nommage en souffrance

Endonymes humain et dragon · exonymes croisés · les deux branches de Tisseuses (caste noble / mot-injure) · les lieux de rite (générique + noms propres) · les grades d'harmonie · l'agôgè dragonne et ses étapes · les déclassés · les teintes dominantes de chaque race.

→ Tout ça converge vers [[lexique]], non écrit. Principe du **planisphère** : aucun terme n'est neutre.

---

## Chantiers

**Prioritaires** — **⏸️ trancher [[chantier-systeme-magie]]** (refonte de la base des couleurs, *bloquée au carrefour Voie A / Voie B* — gèle [[couleurs-magiques]] tant que ce n'est pas décidé ; **deux états de l'art disponibles** : [[recherche-systemes-magie]] — *ce qu'est une magie, ~46 sources* — et [[recherche-magie-difficulte]] — *ce qui la rend difficile : échec, apprentissage, coût, identité, 103 systèmes*) · les autres races (chacune : 4 axes) · l'Unification sous le Triarcat · [[la-purge]].

**En attente** — [[lumens]] **(débloqué : marché premium/classique, raffinage par teinte, perfusion en récession — concept mûr, prêt à écrire)** · [[heredite]] **(promu : reproduction, sexualité, transmission des teintes — sujet central d'une société, fiche dédiée demandée)** · [[ecoles]] (doctrines profondeur/ouverture) · [[lexique]] · [[la-rupture]] (le crime suprême, l'upgrade, le droit qui en découle) · couche **ground** (vie quotidienne, cycle de vie, culture de la mort, géographie vécue, templates POV).

---

## Écartés (ne pas reproposer)

Modèle « robinet » du Cycle · longévité comme trait dragon · outil de mesure exclusif aux dragons · amplitude humaine comme apport à la dyade · plafond de maturité à la mort de l'humain · race liée à une phase du Cycle (quatre bêtes chinoises) · checklist plate des aspects du monde · **teinte comme condition binaire** · **accords sur teintes complémentaires** · **arc humain comme gradient de saturation** · **cercle entier obtenu par entraînement** · **découpage culturel variable du spectre** · **teinte = élément** (rouge/feu, bleu/eau) · **primaires « force / forme / mémoire »** (trop proche de corps-esprit-âme, non déduit du monde) · **alphabet de glyphes tracés** (second système redondant : la combinatoire vient déjà des couleurs) · **loi du figement des valeurs** (remplacée par la loi de résistance ; figeait les personnages à leur naissance) · **bleu = « fixer »** (méta-geste parasite du vert, remplacé par « suspendre ») · **les réceptacles humains comme « accordeurs du monde »**.

→ Motifs détaillés dans [[journal#Écartés (et pourquoi)|journal.md]].
