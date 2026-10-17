# Utilisation

1. Ouvrez https://regisazzoun.github.io/JARVIS-Launcher2/ et choisissez votre poste client.
2. Lancez Tunnel JARVIS via le compagnon macOS déjà installé. Le lien présente aussi une commande de secours à copier.
3. Cliquez Espace connecté : http://localhost:8765/launcher2/. La session de l’interface JARVIS sur cette même origine est partagée. En cas d’expiration, utilisez votre compte habituel ; aucune clé n’est demandée au navigateur.
4. Prompt IA : question ou prompt long, modèle choisi parmi ceux configurés. Entrée envoie, Maj+Entrée ajoute une ligne. La case Mission agentique transmet un objectif au planificateur au lieu d’une conversation ordinaire.
5. Conversation vocale : autorisez le microphone, démarrez/arrêtez l’enregistrement, relisez la transcription puis envoyez. La réponse utilise Piper si la lecture est cochée ; Arrêter coupe la lecture. Le chargement d’un fichier audio est aussi disponible.
6. Sandbox : sélectionnez une mission, ouvrez une tâche ou un journal. Les coches exigent des preuves. Pause arrête la poursuite après l’opération engagée ; Reprendre conserve les checkpoints. Agrandir/réduire ne modifie pas la mission.

Le site public affiche indisponible pour les données privées. Le navigateur ne peut pas vérifier le compagnon natif à lui seul. Open WebUI utilise localhost:3000 et nécessite son tunnel propre. SSH, Codex et WebUI conservent leurs authentifications respectives.

Les sessions, modèles et fichiers ne sont pas supprimés en fermant le Launcher. Pour restaurer le serveur, utilisez la sauvegarde root créée par l’installateur ; la mémoire et les accès ne sont pas remplacés. Voir ARCHITECTURE.md et TESTS.md.
