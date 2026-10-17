# Rapport d’exécution JL-02 — JARVIS Launcher V2

Date : 17 octobre 2026. Dépôt distinct : `regisazzoun/JARVIS-Launcher2`.

**Verdict : GO AVEC RÉSERVES pour l’interface et la collaboration agentique ciblée.** La publication publique est vérifiée séparément dans les preuves de déploiement ; aucune réception exhaustive des Macs et périphériques physiques n’est revendiquée.

## Livré

- Interface responsive, espace principal environ 83 % et colonne de raccourcis à droite ; sur téléphone, les raccourcis passent en barre horizontale défilante. Hauteur fixée à la fenêtre, historiques et Sandbox défilant indépendamment.
- Prompt IA et conversation vocale partagent le fil et l’historique canonique. Prompts longs, sélection des modèles configurés, réponses, transcription Whisper et synthèse Piper existantes ; états microphone/transcription/génération/lecture et arrêt audio.
- Supervision des missions persistantes, tâches, agents, commandes, erreurs, preuves, fichiers autorisés, progression par tâches et activité indéterminée. Agrandissement/réduction, interruption coopérative et reprise.
- Télémétrie mesurée Mac mini/Dell 1 : CPU/RAM, GPU/température/VRAM, Ollama et modèle actif. Dell 2 explicitement indisponible. Aucun chiffre de démonstration affiché comme mesure réelle.
- Accès rapides SSH, Codex, tmux, tunnel, services et liens, basés sur les composants JL-01 inchangés.
- Une passerelle existante étendue, sans nouveau serveur de conversation, base de mémoire parallèle, compte ni clé. Aucun secret dans le frontend public.

## Preuves

[Tests navigateur](evidence/browser-checks.json) : connexion canonique, conversation réelle Qwen sur Dell, session commune texte/voix, événements réellement persistés, coche liée à une preuve, défilements et absence de débordement bureau/tablette/téléphone, panneau redimensionnable, lien protocole V1, logout et absence d’erreur JavaScript.

[Tests API](evidence/api-checks.json) : authentification obligatoire, origine étrangère refusée, confinement des fichiers, mesures réelles, Dell 2 indisponible, Piper WAV réel et transcription Whisper, interruption/reprise et ancien point d’entrée conversation préservé.

27 tests existants du backend réussis après intégration initiale. Treize assertions du composant de tâches et quatre cas de durée réussissent. Les six tests d’accès rapides produits par JARVIS passent aussi. Un test unitaire supplémentaire vérifie le budget de contexte (transport simulé, distinct des preuves d’exécution réelle). Les contrôles shell et compilation Python passent. Les délégations, commits et limites sont décrits dans [le rapport agentique](RAPPORT-AGENTIQUE-JL-02.md).

## Utilisation réelle

Le site Pages est le point d’entrée public. Ouvrir le tunnel JARVIS puis **Espace connecté** conduit à `http://localhost:8765/launcher2/`, qui réutilise le cookie de session de la passerelle. Il ne s’agit pas de rendre les conversations ou Ollama publics. Open WebUI garde son propre tunnel et sa propre authentification.

## Réserves

- Microphone/haut-parleur physiques, Safari et installation native sur les deux Macs non testés depuis Debian. Les essais audio utilisent un fichier synthétique ; aucune validation acoustique n’en est déduite.
- Les actions macOS reprennent les composants V1 et les URL de protocole testées ; ouvrir réellement Terminal.app sur les Macs nécessite ces postes. Aucune simulation ne vaut ce test.
- JARVIS a réellement produit, corrigé, testé et commité du code, mais une délégation est restée partielle et a été finalisée par Codex. Les répétitions observées restent documentées.
- Les heures de début absentes des anciens checkpoints sont indiquées indisponibles, sans valeur fabriquée. Le pourcentage des tâches ne prédit pas la durée restante.
- Reprise persistante, sans garantie d’exécution unique des effets externes. L’interruption laisse se terminer l’opération déjà engagée.

La V1 et le laboratoire principal sont préservés. Aucun merge automatique dans JARVIS-Local-AI-Lab.

## Parcours vocal navigateur

Le [test vocal Chromium](evidence/voice-browser.json) a réussi : source micro synthétique issue d’un WAV Piper, capture MediaRecorder, transcription Whisper réelle, inférence Qwen réelle, nouvelle synthèse Piper, démarrage de lecture audio puis arrêt. Une première exécution alors que le moteur agentique était occupé a échoué ; l’interface a affiché cet échec. La reprise à moteur disponible a réussi. Cela ne valide pas les microphones ni haut-parleurs physiques.
