# Tests JL-02

Les résultats expurgés sont dans `docs/evidence/`. Les identifiants permettent de corréler les opérations aux traces privées, sans publier la mémoire, les secrets ou les captures authentifiées.

```bash
node tests/task-model.integration.cjs
node tests/format.test.cjs
node tests/quick-actions.jarvis.cjs
python3 -m py_compile backend/*.py scripts/*.py
bash -n macos/install.sh macos/uninstall.sh scripts/publish-pages.sh
```

`tests/reception_browser.py` utilise Playwright/Chromium sur Debian et l’installation réelle localhost:8765. Il exige les identifiants privés existants, lus localement et jamais journalisés. Les captures authentifiées sont privées. Le script ne simule ni le backend ni l’inférence.

`tests/reception_api.py` vérifie le périmètre des API et utilise un WAV généré par Piper, puis réellement transcrit par Whisper. Le scénario d’interruption/reprise crée un run de test identifié et le laisse interrompu. Aucun microphone physique n’est revendiqué.

Le test de durée a commencé en échec sur une fixture contrôlée de Codex. JARVIS l’a corrigée et a réellement exécuté Git. Les tests du prototype de tâches, écrits par Codex après la contribution partielle JARVIS, ne sont pas attribués à JARVIS.

Contrôles de publication : HTTP public, version publiée, assets, absence d’accès privé depuis Pages, contrôle du dépôt/Pages V1 et comparaisons des composants réutilisés. Les contrôles macOS natifs restent à réaliser sur les postes réels.

`tests/reception_voice_browser.py` exerce le chemin microphone de Chromium à partir d’un fichier synthétique : ce test ne revendique aucun matériel audio réel. `tests/test_context_budget.py` est un test unitaire avec transport factice ; il est explicitement séparé des essais API, du navigateur réel et des délégations Qwen.

`tests/reception_public.py` visite le vrai site GitHub Pages dans Chromium, vérifie l’absence d’appels privés avant connexion, le protocole V1 et le passage vers localhost avec réutilisation d’une session valide. Il compare aussi le SHA Pages V1 avant/après et son HTTP 200. Les captures publiées montrent uniquement l’interface publique déconnectée ; aucune donnée de conversation privée.

`tests/reception_agent_ui.py` soumet une véritable mission par le formulaire du Launcher, attend les preuves hôte et vérifie le fichier indépendamment. Le premier essai sans action n’est pas accepté ; le second a fourni l’écriture/lecture réelle et les événements affichés.
