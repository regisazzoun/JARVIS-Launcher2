# JL-03 — Launcher V3 : accès distants et raccourcis

**Statut : besoin propriétaire consigné le 19 octobre 2026 ; développement non lancé.**  
**Projet :** futur Launcher V3, conserver JL-01 (V1) et JL-02 (V2) fonctionnels.  
**Source :** confirmation propriétaire de l'enrôlement Tailscale du Dell n°1 ; les tests VNC utilisateur restent à effectuer.

## Décision et état réellement établi

- Le propriétaire a exécuté `tailscale status` sur le Dell n°1 (`jarvis-dell`). La sortie confirme que **jarvis-dell** et **jarvis-macmini** apparaissent dans le même tailnet, avec deux clients macOS répertoriés (l'un hors ligne lors du relevé). L'état initial `NeedsLogin` du Dell n'est donc plus représentatif de ce contrôle utilisateur plus récent.
- Le Dell possède désormais une adresse Tailscale attribuée ; ne pas recopier les adresses privées du tailnet dans le dépôt public.
- **L'accès SSH direct via le tailnet et le bureau VNC/Tailscale n'ont pas encore été testés par le propriétaire.** Ne pas déclarer JL-03 réalisé ni la tâche 21.07 validée sur cette seule base.
- Infrastructure déjà livrée en mission 21 : session KDE Plasma/TigerVNC sur Dell n°1, serveur VNC lié au loopback `127.0.0.1:5921`. Procédure d'accès existante : tunnel SSH local vers cette écoute et client VNC local. Voir le référentiel `JARVIS-Local-AI-Lab` et `docs/missions/22/ACCES-BUREAU-DELL.md` sur la branche de mission 22.

## Raccourcis prévus pour Launcher V3

### Accès Dell n°1
1. **SSH Dell n°1 — LAN** : ouvrir une session SSH avec le compte existant `adminjarvis`, depuis un profil local.
2. **SSH Dell n°1 — Tailscale** : ouvrir SSH vers le nom MagicDNS ou l'adresse Tailscale obtenue dynamiquement depuis la configuration locale.
3. **Bureau Dell n°1 — VNC LAN** : en un clic, établir/vérifier le tunnel SSH `-L 15921:127.0.0.1:5921` vers le Dell par LAN, puis ouvrir `vnc://127.0.0.1:15921`.
4. **Bureau Dell n°1 — VNC Tailscale** : même mécanisme, avec cible SSH du Dell sur son tailnet, puis ouverture du client VNC local ; authentification VNC déjà provisionnée.
5. Afficher les états distincts : Dell joignable, SSH prêt, tunnel actif, VNC authentifié/écran reçu. Ne pas présenter « connexion réussie » quand seul un port ou le service est disponible.

### Accès Mac mini et postes
6. Conserver les raccourcis actuels JL-02 (JARVIS conversation, tunnel web, SSH, Codex, tmux, Open WebUI et Sandbox).
7. Prévoir les profils distincts Mac mini Debian, Dell n°1, MacBook Pro et clients macOS, avec préférences LAN/Tailscale et reprise des tunnels.
8. Envisager des raccourcis d'accès graphique aux autres machines **uniquement après inventaire et confirmation de leurs services graphiques disponibles**.

## Intégration et fonctionnement attendus

- UI cohérente avec la colonne des accès rapides actuelle, responsive et sans rallongement global de la page ; conserver le Sandbox et la conversation à défilement interne.
- Le site GitHub Pages seul ne peut pas ouvrir un tunnel SSH local arbitraire : les boutons de V3 devront réutiliser ou étendre le compagnon macOS / les mécanismes locaux déjà installés, sans simuler la connexion.
- Ne pas inscrire dans le frontend public mots de passe VNC, clés privées SSH, jetons Tailscale, données de session ou adresse spécifique de l'utilisateur. Résoudre les destinations sur le poste client ou via une configuration privée.
- Ne pas changer la Bbox ni ajouter de redirection Internet ; accès via LAN et tailnet existant.
- Éviter les conflits de ports locaux : vérifier si `15921` est libre ou affecter un port local par profil et afficher la destination réelle.
- Pas de modification de V1/V2 tant que le propriétaire n'a pas lancé le chantier JL-03 ; cette fiche est une **spécification**, pas une autorisation de déploiement.

## Réception future

- Depuis un Mac client réel : établir tunnel SSH LAN puis image KDE reçue via VNC ; fermer et relancer.
- Depuis le même client via tailnet : établir SSH, tunnel et image KDE réellement reçue ; vérifier les cas hors ligne / port local occupé.
- Contrôler la persistence et la non-régression des raccourcis existants et du Sandbox.
- Documenter les essais effectués par le propriétaire distinctement des tests automatisés Codex/JARVIS.

## Continuité du projet

**Priorités actuelles :** la mission 21.07 doit encore recevoir ses tests directs VNC/Tailscale ; la mission 22 garde sa réception distincte. La mission 14 demeure le déploiement du Dell n°2 par JARVIS lui-même. Le futur Launcher V3 sera un chantier séparé, sans renommer les missions 14, 20, 21 ou 22.

Directives consultées lors de la consignation : `AGENTS.md`, `docs/CHARTE_DIRECTIVES_JARVIS.md`, réception mission 21 et procédure Dell de mission 22 ; autorisations conservées : continuité du laboratoire et des Launchers précédents ; contradiction corrigée : état historique `NeedsLogin` désormais dépassé par le relevé utilisateur, sans en déduire un test VNC réussi.
