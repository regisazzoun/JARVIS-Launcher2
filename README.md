# JARVIS Launcher V2 — JL-02

Interface de conversation et de pilotage agentique du laboratoire JARVIS. Projet distinct de [Launcher V1](https://regisazzoun.github.io/JARVIS-Launcher/), conservé inchangé.

- **Site public :** https://regisazzoun.github.io/JARVIS-Launcher2/
- **Espace privé connecté :** http://localhost:8765/launcher2/ après ouverture du tunnel SSH existant.
- **Réception :** [rapport JL-02](docs/RAPPORT-JL-02.md) et [rapport de collaboration Codex/JARVIS](docs/RAPPORT-AGENTIQUE-JL-02.md).

## Utiliser

Ouvrez le site, choisissez le profil du Mac client et lancez « Tunnel JARVIS ». Cliquez ensuite sur « Espace connecté ». Le compagnon JL-01 déjà installé reste utilisable ; le compte et la session de la passerelle JARVIS sont réutilisés. Le site public ne reçoit aucun mot de passe et ne contacte pas directement les API privées.

Prompt IA et Conversation vocale partagent le fil et la mémoire canonique. Le mode Mission agentique enregistre un objectif persistant. Le panneau Sandbox affiche tâches, preuves, opérations, erreurs et reprise ; les essais isolés et les opérations réelles utilisent le même journal, sans les confondre. La page reste à hauteur de fenêtre avec défilements indépendants.

## Architecture et installation serveur

Aucun nouveau serveur conversationnel, moteur de mémoire ou mécanisme d’authentification. Le service `jarvis-conversation` existant sert également `/launcher2/` et trois API privées de supervision. Ollama reste sur les moteurs existants, Whisper/Piper et SQLite sur le Mac mini.

```bash
# Sur JARVIS Debian, après revue des sources et en conservant les accès existants :
sudo python3 scripts/install-gateway.py
```

L’installateur sauvegarde les fichiers modifiés et la politique sous `/var/backups/jarvis-jl02-*`. Il ajoute un contrôle de télémétrie distant au profil Dell déjà vérifié, sans nouvelle clé ni compte. Il redémarre les services concernés. Les sessions web existantes sont réutilisées en utilisation normale ; un redémarrage du service invalide les sessions en RAM selon le fonctionnement antérieur de JARVIS.

Le compagnon macOS est repris sans modification de V1 dans `macos/`. Sa configuration locale et son installation ne sont pas écrasées. Son fonctionnement natif requiert le poste macOS réel ; le serveur Debian ne simule pas cette réception.

## Tester et publier

```bash
node tests/task-model.integration.cjs
node tests/format.test.cjs
# Autres tests réels : voir docs/TESTS.md (Playwright et environnement privé requis).
python3 scripts/build-pages.py
bash scripts/publish-pages.sh
```

Le frontend ne contient aucune donnée de conversation, clé privée ou jeton. Pas de démonstration remplie de mesures fictives. Les rapports exposent les limites et les preuves expurgées ; les journaux et captures privés restent hors dépôt.
