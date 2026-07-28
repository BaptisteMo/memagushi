---
description: Lit une fiche du vault à voix haute
argument-hint: <fiche> [-s 6.1] [--direct]
allowed-tools: Bash(bash:*)
---

!`bash "$CLAUDE_PROJECT_DIR/_meta/outils/lire-cmd.sh" $ARGUMENTS`

Ci-dessus, le résultat de la commande de lecture.

Rends compte en **une seule ligne** : la fiche, sa durée estimée, la voix utilisée, et où est passé l'audio. N'explique pas le fonctionnement, ne propose rien, n'ajoute aucun commentaire — l'utilisateur écoute, il ne lit pas.

Si la commande a signalé une erreur (fiche introuvable, section absente, aucune voix), dis-le en une ligne avec la correction à faire.
