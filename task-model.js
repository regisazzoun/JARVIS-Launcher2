// Finalisation Codex : syntaxe, preuves natives et données absentes, après contribution JARVIS.
// JL-02: Module UMD sans dépendances
(function (root, factory) {
    if (typeof module !== 'undefined' && module.exports) {
        module.exports = factory();
    } else {
        root.JLTasks = factory();
    }
}(this, function () {

    const STATUTS = {
        pending: "En attente",
        queued: "File d'attente",
        running: "En cours",
        validated: "Réussie et vérifiée",
        completed: "Terminé",
        failed: "Échoué",
        blocked: "Bloqué",
        incomplete: "Incomplet",
        interrupted: "Interrompu",
        reported: "Rapporté"
    };

    function statusLabel(state) {
        return Object.prototype.hasOwnProperty.call(STATUTS,state) ? STATUTS[state] : "Indisponible";
    }

    function taskView(task = {}) {
        const { id, title, state, evidence } = task;
        
        let verified = false;
        
        if (state === 'validated' && evidence) {
            let evidenceList = Array.isArray(evidence) ? evidence : [];
            
            if (typeof evidence === 'string') {
                try {
                    const parsed = JSON.parse(evidence);
                    evidenceList = Array.isArray(parsed) ? parsed : [parsed];
                } catch (e) {
                    // Ignorer les erreurs de parse
                }
            }
            
            for (const item of evidenceList) {
                if (!item || typeof item !== 'object') continue;
                if (item.ok === true && item.result && typeof item.result.evidence_id === 'string' && item.result.evidence_id.trim() && (item.result.returncode === undefined || item.result.returncode === 0)) { verified = true; break; }
                // Cas 1: objet avec result.ok=true et returncode absent ou 0
                if (item.result && item.result.ok === true) {
                    const returncode = item.result.result ? item.result.result.returncode : undefined;
                    if (returncode === undefined || returncode === 0) {
                        verified = true;
                        break;
                    }
                }
                
                // Cas 2: objet avec ok=true et evidence_id non vide
                if (item.ok === true && typeof item.evidence_id === 'string' && item.evidence_id.trim() !== '' && (item.returncode === undefined || item.returncode === 0)) {
                    verified = true;
                    break;
                }
            }
        }
        
        return {
            id,
            title,
            label: statusLabel(state),
            verified
        };
    }

    function progressView(progress = {}) {
        const { percent, measured, total, validated } = progress;
        
        // Bornage du pourcentage si nombre fini
        let boundedPercent = null;
        if (typeof percent === 'number' && isFinite(percent)) {
            boundedPercent = Math.max(0, Math.min(100, percent));
        }
        
        let kind = 'indeterminate';
        let label = 'Activité indéterminée';
        
        if (measured === true && boundedPercent !== null) {
            kind = 'measured';
            label = `Mesuré : ${boundedPercent}%`;
        } else if (typeof total === 'number' && total > 0 && Number.isFinite(validated)) {
            if (boundedPercent === null) boundedPercent = Math.max(0, Math.min(100, 100 * validated / total));
            kind = 'tasks';
            label = `${validated}/${total} tâches vérifiées`;
        } else if (boundedPercent !== null) {
            kind = 'estimated';
            label = `Estimé : ${boundedPercent}%`;
        }
        
        return {
            kind,
            percent: boundedPercent,
            label
        };
    }

    return {
        statusLabel,
        taskView,
        progressView
    };
}));