# Rapport agentique JL-02 — Codex et JARVIS

17 octobre 2026. Ce rapport distingue les opérations réellement exécutées de la simple génération de texte. Le moteur utilisé par JARVIS est `qwen3.5:27b-q4_K_M` sur le Dell ; son planificateur et ses outils s’exécutent sur le Mac mini.

## Échanges et délégations

Les objectifs sont soumis par Codex à l’API authentifiée `/api/missions`, puis exécutés par le worker canonique. Qwen choisit les appels d’outils ; aucun appel de modèle factice ni réponse de test substituée. Les identifiants et opérations expurgés sont dans [evidence/delegations.json](evidence/delegations.json). Les objectifs complets et traces brutes restent privés.

| Délégation | Travail réel de JARVIS | Vérification / intervention Codex |
| --- | --- | --- |
| Composant des tâches | Lecture du contrat, écritures réelles de `site/task-model.js`, états/progression et logique de preuve. | Contribution partielle : lectures répétées, absence de tests livrés et erreur de syntaxe. Codex conserve [le prototype original](task-model-jarvis-original.txt), corrige la syntaxe, adapte les preuves natives et ajoute 13 assertions d’intégration. Le run reste interrompu ; aucune réussite autonome inventée. |
| Diagnostic et correction de durée | Exécution du test en échec, correction de `site/format.js`, exécution des tests, commit local Git réel `78bf7c3`, vérification Git et rapport. | La faute initiale de durée était une fixture contrôlée introduite par Codex pour cette expérimentation. Codex vérifie indépendamment le commit et les quatre assertions, sans modifier les assertions pendant la correction. Run complété avec preuve. |
| Audit des accès rapides | Création de `tests/quick-actions.jarvis.cjs`, tests du module hérité et correction de son propre test lorsque nécessaire. | Six tests passent, vérifiés indépendamment. Codex a identifié le mauvais nom d’export et transmis le diagnostic ; JARVIS a réellement corrigé son test, l’a exécuté et a écrit CONTROLE-ACCES-JARVIS.md. Aucune exécution native macOS déduite de Node. |

## Travaux effectués par Codex

Architecture, interface HTML/CSS et client JavaScript, reprise des composants JL-01, adaptation de la passerelle canonique, métriques réelles et événements, contrôles de périmètre des fichiers, interruption/reprise, finalisation du prototype de tâches, tests navigateur/API, intégration voix, scripts d’installation/publication et documentation. Les preuves opérateur sont séparées des checkpoints JARVIS dans le panneau.

Le commit JARVIS ne contient que `site/format.js` et `tests/format.test.cjs`. Le reste du frontend n’est pas attribué à JARVIS. Les fichiers de tests et documents supplémentaires de JARVIS sont identifiés dans les traces ; leur réception reste indépendante de ses déclarations.

## Incidents et limites réellement observés

- La première délégation longue a répété des lectures et réécrit le prototype sans atteindre les tests. L’augmentation du plafond de génération de 1 100 à 4 096 tokens n’a pas suffi à garantir une bonne planification. Codex a finalisé cette partie ; la contribution n’est pas déclarée totalement autonome.
- Déplacement physique demandé par le propriétaire : checkpoints sauvegardés, deux runs interrompus, extinction propre du Dell après garde d’identité. Au retour réseau à 21 h 06, un contrôle SSH épinglé et Ollama ont permis la reprise automatique des mêmes identifiants. Les compteurs de tentatives comprennent ces reprises ; ils ne désignent pas tous des pannes.
- Dans la tâche durée, une première validation a utilisé un identifiant de tâche absent. JARVIS a ensuite enregistré le plan correct et validé la tâche ; le registre conserve l’échec antérieur.
- Dans l’audit des accès, JARVIS a d’abord supposé un export `ACTIONS` inexistant. Cet échec doit rester visible dans les preuves, sans modifier le module V1 pour rendre son test artificiellement vert.
- Les états et commandes sont persistants ; la reprise ne garantit pas exactly-once. Une tâche ne reçoit pas une coche parce que le modèle a écrit « terminé ».

**Conclusion : collaboration réelle démontrée sur des tâches ciblées ; autonomie générale encore partielle.** Les boucles de lecture et erreurs de contrats d’outils restent des réserves. La qualité du frontend final ne doit pas les masquer.

## Correction du raccordement par Codex

Pour les seules missions agentiques, les extraits de souvenirs/documents injectés sont bornés afin de conserver les observations des outils dans le contexte. La mémoire SQLite stockée n’est pas modifiée. Un test unitaire dédié, explicitement à transport simulé, vérifie ce budget ; il ne remplace pas les délégations réelles. La boucle est également interruptible entre les appels d’une même série d’outils.

Le dernier audit avait déjà enregistré son rapport avant un redémarrage de service, mais a repris des vérifications. Après réception indépendante des six tests et du document, Codex a interrompu cette poursuite redondante via l’API. Son état final ne doit pas être présenté comme une clôture autonome sans assistance. Les traces et le rapport de réception distinguent cette intervention.

## Réception depuis l’interface

Le premier lancement de réception par le formulaire a donné un rapport sans opération réelle, affirmant à tort que le test précédent était acquis. Codex a rejeté cette réponse : aucun fichier, aucune preuve d’écriture. Le second lancement, avec un objectif direct, a produit les appels host_write_file puis host_read_file et le fichier vérifié. Les deux identifiants sont conservés dans agent-ui.json. Le succès retenu repose sur les traces et le fichier, pas sur le texte du modèle.
