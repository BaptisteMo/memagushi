#!/usr/bin/env python3
"""
lire.py — lit à voix haute une fiche du vault.

Le markdown n'est pas fait pour être écouté : wikilinks, frontmatter, tableaux
et callouts s'entendent si on les laisse passer. Ce script les traduit en texte
parlable, puis le confie à `say`.

    ./lire.py codex/monde/le-plan.md              parle tout de suite
    ./lire.py le-plan                             le chemin est facultatif
    ./lire.py le-lien --section 6                 une seule section
    ./lire.py le-plan -f                          génère un .m4a et l'ouvre
    ./lire.py le-plan --texte                     montre le texte, ne parle pas
    ./lire.py --voix                              liste les voix françaises

Aucune dépendance : stdlib seule, pour ne rien avoir à installer ni à maintenir.
"""

import argparse
import json
import os
import re
import subprocess
import sys
import tempfile
import unicodedata
from pathlib import Path

VAULT = Path(__file__).resolve().parent.parent.parent
PRONONCIATION = Path(__file__).resolve().parent / "prononciation.json"
VOIX_CHOISIE = Path(__file__).resolve().parent / "voix.conf"

# Voix « personnage » de macOS : très bien pour une alarme, épuisantes sur
# vingt minutes de prose. Écartées du choix automatique, jamais interdites.
NOUVEAUTE = {"eddy", "flo", "grandma", "grandpa", "reed", "rocko", "sandy",
             "shelley", "albert", "bahh", "bells", "boing", "bubbles",
             "cellos", "jester", "organ", "superstar", "trinoids",
             "whisper", "wobble", "zarvox"}

# Pauses, en millisecondes.
PAUSE_TITRE = 700
PAUSE_SECTION = 900
PAUSE_PARA = 350
PAUSE_LIGNE_TABLEAU = 250

MARQUEUR = "\x00P{}\x00"  # remplacé par [[slnc n]] en toute fin de traitement

ELISIONS = {"l", "d", "j", "n", "s", "c", "m", "t", "qu"}


def _sans_accents(s):
    plat = unicodedata.normalize("NFD", s.casefold())
    return "".join(c for c in plat if unicodedata.category(c) != "Mn").strip(" .:")


# --------------------------------------------------------------------------
# Lexique : slug de wikilink -> nom prononçable
# --------------------------------------------------------------------------

def _frontmatter(texte):
    """Renvoie le bloc frontmatter en dict très permissif, et le corps."""
    if not texte.startswith("---"):
        return {}, texte
    fin = texte.find("\n---", 3)
    if fin == -1:
        return {}, texte
    brut, corps = texte[3:fin], texte[fin + 4:]

    champs, cle = {}, None
    for ligne in brut.splitlines():
        if not ligne.strip() or ligne.lstrip().startswith("#"):
            continue
        if re.match(r"^\s*-\s", ligne) and cle:
            champs.setdefault(cle, []).append(ligne.split("-", 1)[1].strip())
        elif ":" in ligne and not ligne.startswith(" "):
            cle, valeur = ligne.split(":", 1)
            cle, valeur = cle.strip(), valeur.strip()
            if valeur.startswith("[") and valeur.endswith("]"):
                champs[cle] = [v.strip() for v in valeur[1:-1].split(",") if v.strip()]
            elif valeur:
                champs[cle] = valeur
            else:
                champs[cle] = []
    return champs, corps


def deskug(slug):
    """coeur-magique -> coeur magique ; l-epanchement -> l'epanchement."""
    morceaux = slug.split("-")
    sortie = ""
    for i, m in enumerate(morceaux):
        if i and m:
            sortie += "" if sortie.endswith("'") else " "
        sortie += m
        if m.lower() in ELISIONS and i + 1 < len(morceaux):
            sortie += "'"
    return sortie


def charger_lexique(vault):
    """slug -> nom lisible, tiré des aliases (sinon du titre H1, sinon dé-slugé)."""
    lexique = {}
    for chemin in vault.rglob("*.md"):
        if any(p.startswith(".") for p in chemin.parts):
            continue
        slug = chemin.stem
        try:
            texte = chemin.read_text(encoding="utf-8")
        except OSError:
            continue
        champs, corps = _frontmatter(texte)
        nom = None
        alias = champs.get("aliases")
        if isinstance(alias, list) and alias:
            nom = alias[0].strip("\"'[] ")
        if not nom:
            titre = re.search(r"^#\s+(.+)$", corps, re.M)
            if titre:
                nom = titre.group(1).strip()
        lexique[slug] = nom or deskug(slug)
    return lexique


def charger_prononciation():
    if PRONONCIATION.exists():
        try:
            return json.loads(PRONONCIATION.read_text(encoding="utf-8"))
        except (OSError, json.JSONDecodeError) as e:
            print(f"⚠️  prononciation.json ignoré ({e})", file=sys.stderr)
    return {}


# --------------------------------------------------------------------------
# Pré-traitement
# --------------------------------------------------------------------------

def preambule(champs, slug, lexique):
    """Trois secondes de contexte avant d'entrer dans le texte."""
    nom = lexique.get(slug) or deskug(slug)
    bouts = [nom + "."]
    detail = []
    for cle, gabarit in (("type", "fiche {}"), ("layer", "couche {}"),
                         ("status", "statut {}")):
        v = champs.get(cle)
        if isinstance(v, str) and v:
            detail.append(gabarit.format(v))
    if detail:
        bouts.append(", ".join(detail).capitalize() + ".")
    return " ".join(bouts)


def resoudre_liens(texte, lexique):
    """[[cible|affiché]] -> affiché ; [[cible]] -> nom lisible de la cible."""

    def remplacer(m):
        contenu = m.group(1)
        if "|" in contenu:
            affiche = contenu.split("|", 1)[1]
        else:
            cible = contenu.split("#", 1)[0].strip()
            affiche = lexique.get(cible) or deskug(cible)
            if "#" in contenu:
                ancre = contenu.split("#", 1)[1]
                num = re.match(r"\s*([\d.]+)", ancre)
                affiche += f", section {num.group(1)}" if num else ""
        return affiche

    return re.sub(r"\[\[([^\]]+)\]\]", remplacer, texte)


def linateur_tableau(lignes):
    """Une ligne de tableau devient une phrase ; l'en-tête et les séparateurs sautent."""
    sortie = []
    for ligne in lignes:
        if re.match(r"^\s*\|[\s:|-]+\|\s*$", ligne):
            continue
        cellules = [c.strip() for c in ligne.strip().strip("|").split("|")]
        cellules = [c for c in cellules if c]
        if cellules:
            sortie.append(" — ".join(cellules) + "." + MARQUEUR.format(PAUSE_LIGNE_TABLEAU))
    return sortie


def extraire_section(corps, numero):
    """Ne garde que la section '## <numero>.' jusqu'au prochain titre de même niveau."""
    motif = re.compile(rf"^##\s+{re.escape(numero)}[.\s]", re.M)
    debut = motif.search(corps)
    if not debut:
        motif = re.compile(rf"^#+\s.*{re.escape(numero)}", re.M)
        debut = motif.search(corps)
        if not debut:
            return None
    suite = re.search(r"^##\s", corps[debut.end():], re.M)
    return corps[debut.start(): debut.end() + suite.start()] if suite else corps[debut.start():]


def fusionner_pauses(t):
    """Séparateurs, lignes vides et titres empilent leurs silences : on ne garde
    que le plus long de chaque rafale, sinon l'écoute est hachée."""

    def plus_long(m):
        durees = [int(d) for d in re.findall(r"\x00P(\d+)\x00", m.group(0))]
        return MARQUEUR.format(max(durees))

    return re.sub(r"(?:\x00P\d+\x00\s*){2,}", plus_long, t)


def nettoyer(corps, lexique, prononciation, titre_annonce=None):
    t = corps

    # Ce qui ne se lit pas du tout.
    t = re.sub(r"```.*?```", "", t, flags=re.S)          # blocs de code, Dataview compris
    t = re.sub(r"<!--.*?-->", "", t, flags=re.S)          # commentaires HTML
    t = re.sub(r"^\s*!\[.*?\]\(.*?\)\s*$", "", t, flags=re.M)  # images

    t = resoudre_liens(t, lexique)
    t = re.sub(r"\[([^\]]+)\]\([^)]+\)", r"\1", t)        # liens markdown

    # Traitement ligne par ligne : titres, tableaux, listes, séparateurs.
    sortie, tampon = [], []
    for ligne in t.splitlines():
        if re.match(r"^\s*\|.*\|\s*$", ligne):
            tampon.append(ligne)
            continue
        if tampon:
            sortie.extend(linateur_tableau(tampon))
            tampon = []

        titre = re.match(r"^(#{1,6})\s+(.*)$", ligne)
        if titre:
            niveau, texte_titre = len(titre.group(1)), titre.group(2).strip()
            # Le H1 répète le nom déjà donné par le préambule : on le saute.
            if niveau == 1 and titre_annonce and \
                    _sans_accents(texte_titre) == _sans_accents(titre_annonce):
                continue
            pause = PAUSE_SECTION if niveau <= 2 else PAUSE_TITRE
            sortie.append(MARQUEUR.format(pause) + texte_titre + "." + MARQUEUR.format(PAUSE_PARA))
            continue

        if re.match(r"^\s*(---+|\*\*\*+|___+)\s*$", ligne):
            sortie.append(MARQUEUR.format(PAUSE_SECTION))
            continue

        callout = re.match(r"^>\s*\[!(\w+)\]\s*(.*)$", ligne)
        if callout:
            titre_c = callout.group(2).strip()
            sortie.append(f"Encadré. {titre_c}." if titre_c else "Encadré.")
            continue

        ligne = re.sub(r"^>\s?", "", ligne)               # citations
        ligne = re.sub(r"^\s*[-*+]\s+", "", ligne)        # puces
        ligne = re.sub(r"^\s*\d+\.\s+", "", ligne)        # listes numérotées
        sortie.append(ligne)

    if tampon:
        sortie.extend(linateur_tableau(tampon))
    t = "\n".join(sortie)

    # Conventions du vault. En tête de ligne, le ⚠️ annonce un trou volontaire ;
    # au fil du texte il vaut pour le nom de la chose (« quatre ⚠️ ouvertes »).
    t = re.sub(r"^\s*⚠️?\s*", "Point ouvert : ", t, flags=re.M)
    t = re.sub(r"\s*⚠️?\s*", " points ouverts ", t)

    # Chemins et noms de fichiers : imprononçables tels quels.
    t = re.sub(r"_(\w+)/", r"\1 ", t)          # _raw/ -> raw
    t = re.sub(r"\b([\w-]+)\.md\b", r"\1", t)  # journal.md -> journal

    # L'interpoint sépare des énumérations dans l'index : il doit s'entendre.
    t = t.replace(" · ", ", ").replace("·", ", ")
    t = re.sub(r"\s*→\s*", ". ", t)
    t = re.sub(r"\s*[–—]\s*", " — ", t)
    for emoji, mot in (("🔴", "rouge"), ("🟠", "orange"), ("🟢", "vert"),
                       ("✅", "validé"), ("❌", "manquant"), ("⏸️", "en pause")):
        t = t.replace(emoji, mot + ", ")
    t = re.sub(r"§\s*([\d.]+)", r"section \1", t)
    t = t.replace("§", "section ")

    # Emphase et code inline.
    t = re.sub(r"\*\*\*(.+?)\*\*\*", r"\1", t)
    t = re.sub(r"\*\*(.+?)\*\*", r"\1", t)
    t = re.sub(r"(?<!\w)\*(?!\s)(.+?)(?<!\s)\*(?!\w)", r"\1", t)
    t = re.sub(r"`([^`]+)`", r"\1", t)
    t = re.sub(r"~~(.+?)~~", r"\1", t)

    # Prononciation des noms propres inventés.
    for terme, phonetique in sorted(prononciation.items(), key=lambda kv: -len(kv[0])):
        t = re.sub(rf"\b{re.escape(terme)}\b", phonetique, t, flags=re.I)

    # Espacement et pauses de paragraphe.
    t = re.sub(r"\n{2,}", "\n" + MARQUEUR.format(PAUSE_PARA) + "\n", t)
    t = re.sub(r"[ \t]{2,}", " ", t)
    t = "\n".join(l.strip() for l in t.splitlines())
    t = fusionner_pauses(t)
    t = re.sub(r"\n{3,}", "\n\n", t).strip()

    # Les crochets restants seraient interprétés par `say` comme des commandes.
    return t.replace("[[", "").replace("]]", "")


# --------------------------------------------------------------------------
# Voix et lecture
# --------------------------------------------------------------------------

def est_premium(nom):
    return bool(re.search(r"premium|enhanced|amélior", nom, re.I))


def voix_fr():
    """Voix françaises, classées : Premium d'abord, puis les voix de lecture,
    France avant Canada, les voix « personnage » en dernier."""
    try:
        brut = subprocess.run(["say", "-v", "?"], capture_output=True,
                              text=True, check=True).stdout
    except (OSError, subprocess.CalledProcessError):
        return []
    trouvees = []
    for ligne in brut.splitlines():
        m = re.match(r"^(.*?)\s+(fr_[A-Z]{2})\s+#", ligne)
        if m:
            nom, locale = m.group(1).strip(), m.group(2)
            base = re.split(r"\s*\(", nom)[0].strip().casefold()
            trouvees.append((
                0 if est_premium(nom) else 1,     # qualité
                1 if base in NOUVEAUTE else 0,    # voix de lecture d'abord
                0 if locale == "fr_FR" else 1,    # France avant Canada
                nom))
    return [n for *_, n in sorted(trouvees)]


def voix_par_defaut():
    """Un choix figé par --choisir prime sur le classement automatique."""
    if VOIX_CHOISIE.exists():
        nom = VOIX_CHOISIE.read_text(encoding="utf-8").strip()
        if nom and nom in voix_fr():
            return nom
    dispo = voix_fr()
    return dispo[0] if dispo else None


def resoudre_fiche(cible):
    """Accepte un chemin, ou juste un nom de fiche."""
    p = Path(cible)
    if p.suffix == ".md" and p.exists():
        return p
    for base in (Path.cwd(), VAULT):
        q = base / cible
        if q.exists() and q.suffix == ".md":
            return q
    nom = cible if cible.endswith(".md") else cible + ".md"
    trouves = [c for c in VAULT.rglob(nom) if not any(x.startswith(".") for x in c.parts)]
    if len(trouves) == 1:
        return trouves[0]
    if len(trouves) > 1:
        print("Plusieurs fiches portent ce nom :", file=sys.stderr)
        for t in trouves:
            print("   ", t.relative_to(VAULT), file=sys.stderr)
        sys.exit(1)
    return None


def main():
    ap = argparse.ArgumentParser(
        description="Lit une fiche du vault à voix haute.",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=__doc__.split("Aucune dépendance")[0].split("\n\n", 2)[-1])
    ap.add_argument("fiche", nargs="?", help="chemin ou nom de la fiche")
    ap.add_argument("-s", "--section", help="ne lire qu'une section (ex. 6 ou 6.1)")
    ap.add_argument("-f", "--fichier", action="store_true",
                    help="générer un .m4a et l'ouvrir (pause, vitesse, retour arrière)")
    ap.add_argument("-t", "--texte", action="store_true",
                    help="afficher le texte parlable sans le lire")
    ap.add_argument("-v", "--voix-nom", metavar="NOM", help="forcer une voix")
    ap.add_argument("-r", "--vitesse", type=int, default=190,
                    help="mots par minute (défaut : 190)")
    ap.add_argument("--voix", action="store_true", help="lister les voix françaises")
    ap.add_argument("--choisir", metavar="NOM",
                    help="figer la voix par défaut (nom exact donné par --voix)")
    args = ap.parse_args()

    if args.choisir:
        if args.choisir not in voix_fr():
            print(f"Voix inconnue : {args.choisir}\n"
                  f"Utiliser exactement un des noms donnés par --voix.", file=sys.stderr)
            sys.exit(1)
        VOIX_CHOISIE.write_text(args.choisir + "\n", encoding="utf-8")
        print(f"Voix par défaut : {args.choisir}")
        return

    if args.voix:
        dispo = voix_fr()
        if not dispo:
            print("Aucune voix française installée.")
            return
        actuelle = voix_par_defaut()
        print("Voix françaises disponibles :\n")
        for nom in dispo:
            marque = "★" if est_premium(nom) else " "
            defaut = "  ← utilisée" if nom == actuelle else ""
            print(f"  {marque} {nom}{defaut}")
        if not any(est_premium(n) for n in dispo):
            print("\nAucune voix Premium ou Enhanced installée — ce sont les seules"
                  "\nvraiment écoutables sur la durée. Réglages Système → Accessibilité"
                  "\n→ Contenu énoncé → Voix système → Gérer les voix → Français."
                  "\nÉviter Eloquence (synthèse rétro) et les voix Siri, que `say`"
                  "\nne peut pas utiliser.")
        else:
            print("\n★ = voix Premium ou Enhanced.  Pour en figer une :"
                  "\n   lire.py --choisir \"Nom exact\"")
        return

    if not args.fiche:
        ap.error("indiquer une fiche, ou --voix pour lister les voix")

    chemin = resoudre_fiche(args.fiche)
    if not chemin:
        print(f"Fiche introuvable : {args.fiche}", file=sys.stderr)
        sys.exit(1)

    champs, corps = _frontmatter(chemin.read_text(encoding="utf-8"))
    lexique = charger_lexique(VAULT)
    prononciation = charger_prononciation()

    nom_fiche = lexique.get(chemin.stem) or deskug(chemin.stem)
    if args.section:
        section = extraire_section(corps, args.section)
        if section is None:
            print(f"Section {args.section} introuvable dans {chemin.name}", file=sys.stderr)
            sys.exit(1)
        corps, tete = section, f"{nom_fiche}, section {args.section}."
    else:
        tete = preambule(champs, chemin.stem, lexique)

    texte = (tete + MARQUEUR.format(PAUSE_SECTION) + "\n"
             + nettoyer(corps, lexique, prononciation, titre_annonce=nom_fiche))
    texte = fusionner_pauses(texte)
    texte = re.sub(r"\x00P(\d+)\x00", r"[[slnc \1]]", texte)

    if args.texte:
        print(texte)
        return

    voix = args.voix_nom or voix_par_defaut()
    if not voix:
        print("Aucune voix française installée.", file=sys.stderr)
        sys.exit(1)

    mots = len(re.findall(r"\w+", texte))
    minutes = mots / max(args.vitesse, 1)
    print(f"{chemin.relative_to(VAULT)} — {mots} mots, ~{minutes:.0f} min, voix « {voix} »")

    with tempfile.NamedTemporaryFile("w", suffix=".txt", delete=False,
                                     encoding="utf-8") as f:
        f.write(texte)
        source = f.name

    try:
        if args.fichier:
            sortie = Path(tempfile.gettempdir()) / f"{chemin.stem}.m4a"
            subprocess.run(["say", "-v", voix, "-r", str(args.vitesse),
                            "-f", source, "-o", str(sortie),
                            "--data-format=aac"], check=True)
            print(f"→ {sortie}")
            subprocess.run(["open", str(sortie)], check=False)
        else:
            print("(Ctrl-C pour arrêter)")
            subprocess.run(["say", "-v", voix, "-r", str(args.vitesse), "-f", source],
                           check=False)
    except KeyboardInterrupt:
        print("\nArrêté.")
    finally:
        os.unlink(source)


if __name__ == "__main__":
    main()
