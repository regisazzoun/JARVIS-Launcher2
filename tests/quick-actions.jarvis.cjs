// @ts-check
'use strict';

const fs = require('node:fs');
const vm = require('node:vm');
const assert = require('node:assert/strict');

// --- Chargement de JarvisCore via vm.runInNewContext (comme dans le code réel) ---
const coreSource = fs.readFileSync('./site/core.js', 'utf8');
const jarvisContext = vm.createContext({ fail: (msg) => { throw new Error(msg); } });
vm.runInNewContext(coreSource, jarvisContext);

// On récupère JarvisCore depuis le contexte sandboxé
const JarvisCore = jarvisContext.JarvisCore;

if (!JarvisCore || typeof JarvisCore.parseURL !== 'function') {
  throw new Error("Échec de chargement : JarvisCore n'est pas défini ou parseURL absent.");
}

// Correction: utilisation de actions (minuscules) au lieu de ACTIONS pour correspondre à l'exposition réelle de JarvisCore
const { parseURL, buildURL, actions: ACTIONS } = JarvisCore;

console.log('=== TESTS QUICK-ACTIONS JARVIS-LAUNCHER2 ===\n');

let testsPassed = 0;
let testsFailed = 0;

function test(name, fn) {
  try {
    fn();
    console.log(`[✓] ${name}`);
    testsPassed++;
  } catch (err) {
    console.log(`[✗] ${name}`);
    console.error(`    Erreur : ${err.message}`);
    testsFailed++;
  }
}

// --- Cas de test ---

// 1. parseURL accepte jarvis-launcher://launch/macbook-pro/ssh
test('parseURL accepte URL SSH valide', () => {
  const url = 'jarvis-launcher://launch/macbook-pro/ssh';
  const result = parseURL(url);
  assert.strictEqual(result.profile, 'macbook-pro');
  assert.strictEqual(result.action, 'ssh');
  assert.strictEqual(result.session, null);
});

// 2. parseURL refuse une action inconnue
test('parseURL refuse action inconnue "action-unknown"', () => {
  const url = 'jarvis-launcher://launch/macbook-pro/action-unknown';
  assert.throws(() => parseURL(url), /URL ou action non autorisée/);
});

// 3. parseURL refuse session sur ssh (non autorisé)
test('parseURL refuse argument session sur action ssh', () => {
  const url = 'jarvis-launcher://launch/macbook-pro/ssh?session=mytmux';
  assert.throws(() => parseURL(url), /Argument interdit pour cette action/);
});

// 4. buildURL conserve exactement une session tmux (pour codex-tmux)
test('buildURL conserve session pour codex-tmux', () => {
  const profile = 'macbook-pro';
  const action = 'codex-tmux';
  const session = 'jarvis-codex';
  const url = buildURL(profile, action, session);
  
  assert.ok(url.includes(`?session=${session}`), `La session doit être présente dans l'URL : ${url}`);
  
  // Vérification par re-parsing pour cohérence interne
  const parsed = parseURL(url);
  assert.strictEqual(parsed.session, session);
});

// 5. buildURL ne ajoute PAS de session pour une action qui n'en accepte pas (ex: ssh)
test('buildURL ne conserve pas session sur action incompatible', () => {
  const profile = 'mac-mini';
  const action = 'ssh';
  const session = 'fake-session'; // Doit être ignorée
  const url = buildURL(profile, action, session);
  
  assert.ok(!url.includes('session='), `La session ne doit pas apparaître dans l'URL pour cette action : ${url}`);
  const parsed = parseURL(url);
  assert.strictEqual(parsed.session, null);
});

// 6. Vérification que actions correspond au tableau attendu
test('actions contient bien les actions documentées', () => {
  const expectedActions = ['ssh', 'ssh-lan', 'codex', 'codex-tmux', 'tmux-attach', 'tmux-list', 'web-tunnel', 'services', 'workspace', 'check'];
  assert.strictEqual(ACTIONS.length, expectedActions.length);
  expectedActions.forEach(act => {
    assert.ok(ACTIONS.includes(act), `Action manquante : ${act}`);
  });
});

// --- Résumé ---
console.log(`\n=== RÉSUMÉ DES TESTS ===`);
console.log(`Total: ${testsPassed + testsFailed}`);
console.log(`Réussis: ${testsPassed}`);
console.log(`Échecs: ${testsFailed}`);

if (testsFailed > 0) {
  console.error('\n[ERREUR] Un ou plusieurs tests ont échoué.');
  process.exit(1);
} else {
  console.log('\n[SUCCÈS] Tous les tests ont été validés.');
  process.exit(0);
}
