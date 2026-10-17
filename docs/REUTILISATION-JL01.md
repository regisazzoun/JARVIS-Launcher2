# Composants JL-01 réutilisés

Référence locale V1 : commit `ce95648d7672729b8b5c1c8e29de2f92c16f1732`. Le propriétaire avait confirmé des actions sur Mac mini puis MacBook Pro les 14/15 octobre ; les limites du rapport historique restent distinguées de ces observations plus récentes.

| Élément | Réutilisation V2 |
| --- | --- |
| site/core.js | Copie identique : profils, validation URL, commandes SSH, sessions exactes tmux, quoting. |
| site/config.json | Configuration initiale reprise ; configuration locale du compagnon reste prioritaire pour l’exécution native. |
| macos/ | Sources identiques ; compagnon existant conservé, aucune réinstallation obligatoire. |
| Authentification JARVIS | Compte et cookie de la passerelle existante, sans second compte. |
| Mémoire et voix 13F | SQLite/FTS5 canonique, Whisper Small et Piper Tom existants. |
| Suivi 13D-E / mission 11 | Principe de preuve avant coche, planificateur durable et checkpoints déjà installés ; pas de nouveau worker parallèle. |

Le dépôt V1, son HEAD, ses fichiers et sa branche Pages doivent être comparés avant/après publication V2. Aucun script de publication V1 n’est exécuté. Le nouveau frontend et la nouvelle publication vivent exclusivement dans JARVIS-Launcher2.
