# Contrôle d'accès JARVIS - Tests Quick-Actions

Six cas de validation exécutés sur `tests/quick-actions.jarvis.cjs` :

1. **parseURL accepte URL SSH valide** ✓
2. **parseURL refuse action inconnue "action-unknown"** ✓
3. **parseURL refuse argument session sur action ssh** ✓
4. **buildURL conserve session pour codex-tmux** ✓
5. **buildURL ne conserve pas session sur action incompatible** ✓
6. **actions contient bien les actions documentées** ✓

**Résultat :** 6/6 tests réussis (returncode: 0).

**Limite connue :** Aucun test natif macOS réalisé ; validation uniquement en environnement Node.js Debian. La compatibilité JXA/MacOS nécessite une vérification physique séparée.

Source : Exécution réelle via `host_exec`, evidence_id: `7f31b623a8b642a9b1646006cd3297c7`.