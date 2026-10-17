/* Shared, dependency-free policy for browsers and native macOS JXA. */
var JarvisCore = (function () {
  'use strict';
  var PROFILES = ['macbook-pro', 'mac-mini'];
  var ACTIONS = ['ssh', 'ssh-lan', 'codex', 'codex-tmux', 'tmux-attach', 'tmux-list', 'web-tunnel', 'services', 'workspace', 'check'];
  function fail(message) { throw new Error(message); }
  function has(list, value) { return list.indexOf(value) !== -1; }
  function text(value, pattern, name) {
    if (typeof value !== 'string' || !pattern.test(value) || /[\r\n\x00]/.test(value)) fail('Valeur invalide : ' + name);
    return value;
  }
  function port(value) { if (typeof value !== 'number' || value % 1 || value < 1024 || value > 65535) fail('Port invalide'); return value; }
  function quote(value) { return "'" + String(value).replace(/'/g, "'\\''") + "'"; }
  function validateConfig(c) {
    if (!c || c.version !== 1 || !c.profiles || !c.remote || !c.ui) fail('Configuration version 1 requise');
    PROFILES.forEach(function (id) {
      if (!Object.prototype.hasOwnProperty.call(c.profiles, id)) fail('Profil absent');
      var p = c.profiles[id];
      if (p.machine !== id) fail('Type de poste invalide');
      text(p.label, /^[A-Za-z0-9 À-ÿ_-]{1,40}$/, 'libellé');
      text(p.user, /^[a-z_][a-z0-9_-]{0,31}$/, 'utilisateur');
      [p.host, p.lanHost].forEach(function (h) { text(h, /^(?:[A-Za-z0-9][A-Za-z0-9.-]{0,252})$/, 'hôte'); });
      text(p.identityFile, /^~\/\.ssh\/[A-Za-z0-9_-][A-Za-z0-9._-]{0,79}$/, 'chemin de clé');
      if (p.sshPort !== 22) fail('Ce MVP accepte uniquement SSH port 22');
      port(p.localWebPort);
    });
    text(c.remote.directory, /^\/(?:[A-Za-z0-9._-]+\/)*[A-Za-z0-9._-]+$/, 'répertoire distant');
    if (c.remote.directory.split('/').some(function (part) { return part === '.' || part === '..'; })) fail('Répertoire non canonique');
    port(c.remote.webPort);
    if (!Array.isArray(c.remote.sessions) || !c.remote.sessions.length || c.remote.sessions.length > 20) fail('Sessions invalides');
    c.remote.sessions.forEach(function (s) { text(s, /^[A-Za-z0-9][A-Za-z0-9_-]{0,39}$/, 'session'); });
    if (!has(c.remote.sessions, c.remote.defaultSession)) fail('Session par défaut absente');
    return c;
  }
  function parseURL(url) {
    if (typeof url !== 'string' || url.length > 240) fail('URL invalide');
    var m = /^jarvis-launcher:\/\/launch\/(macbook-pro|mac-mini)\/([a-z-]+)(?:\?session=([A-Za-z0-9][A-Za-z0-9_-]{0,39}))?$/.exec(url);
    if (!m || m[0] !== url || (!has(ACTIONS, m[2]) && m[2] !== 'workspace')) fail('URL ou action non autorisée');
    if (m[3] && m[2] !== 'codex-tmux' && m[2] !== 'tmux-attach') fail('Argument interdit pour cette action');
    return { profile: m[1], action: m[2], session: m[3] || null };
  }
  function buildURL(profile, action, session) {
    var u = 'jarvis-launcher://launch/' + profile + '/' + action;
    if ((action === 'codex-tmux' || action === 'tmux-attach') && session) u += '?session=' + session;
    parseURL(u); return u;
  }
  function remoteScript(c, action, session) {
    var cd = 'cd -- ' + quote(c.remote.directory) + ' || { printf "%s\\n" "Répertoire JARVIS indisponible."; exec bash -l; }; ';
    var tmux = 'if ! command -v tmux >/dev/null 2>&1; then printf "%s\\n" "tmux indisponible ; shell JARVIS conservé."; exec bash -l; fi; ';
    var codex = 'if command -v codex >/dev/null 2>&1; then codex; else printf "%s\\n" "Codex indisponible ; shell JARVIS conservé."; fi; exec bash -l';
    if (action === 'codex') return cd + codex;
    if (action === 'codex-tmux') return cd + tmux +
      'if tmux has-session -t ' + quote('=' + session) + ' 2>/dev/null; then tmux attach-session -t ' + quote('=' + session) +
      '; elif command -v codex >/dev/null 2>&1; then tmux new-session -A -s ' + quote(session) + ' -c ' + quote(c.remote.directory) + ' ' + quote('codex; exec bash -l') +
      '; else printf "%s\\n" "Codex indisponible ; aucune session créée."; fi; exec bash -l';
    if (action === 'tmux-attach') return cd + tmux + 'if tmux has-session -t ' + quote('=' + session) + ' 2>/dev/null; then tmux attach-session -t ' + quote('=' + session) + '; else printf "%s\\n" "Session absente ; aucune création ni suppression."; fi; exec bash -l';
    if (action === 'tmux-list') return cd + tmux + 'tmux list-sessions || printf "%s\\n" "Aucune session tmux disponible."; exec bash -l';
    if (action === 'services') return cd + 'systemctl --no-pager --full status jarvis-conversation.service jarvis-ollama.service jarvis-open-webui.service; exec bash -l';
    return null;
  }
  function command(c, profile, action, session) {
    var p = c.profiles[profile];
    var args = ['/usr/bin/ssh', '-F', '/dev/null', '-p', '22', '-o', 'IdentitiesOnly=yes', '-o', 'StrictHostKeyChecking=ask', '-o', 'ForwardAgent=no', '-o', 'ForwardX11=no', '-o', 'ConnectTimeout=8', '-o', 'ServerAliveInterval=30', '-o', 'ServerAliveCountMax=3', '-o', 'ExitOnForwardFailure=yes'];
    var ssh = args.map(quote).join(' ') + ' -i "$HOME/' + p.identityFile.slice(2) + '"';
    var target = quote(p.user + '@' + (action === 'ssh-lan' ? p.lanHost : p.host));
    var script = remoteScript(c, action, session);
    if (action === 'web-tunnel') ssh += ' -N -L ' + quote('127.0.0.1:' + p.localWebPort + ':127.0.0.1:' + c.remote.webPort) + ' ' + target;
    else ssh += ' -tt ' + target + (script ? ' ' + quote('bash -lc ' + quote(script)) : '');
    return { action: action, ssh: ssh, remote: script, terminal: 'printf "%s\\n" ' + quote('JARVIS · ' + p.label + ' · ' + action) + '; ' + ssh + '; jarvis_launcher_rc=$?; printf "\\nSSH termine (code %s). Cette fenêtre reste ouverte.\\n" "$jarvis_launcher_rc"; if [ "$jarvis_launcher_rc" -ne 0 ]; then printf "%s\\n" "Vérifiez Tailscale ou le LAN, la clé SSH et la disponibilité de JARVIS. Aucun repli réseau automatique."; fi' };
  }
  function preview(c, profile, action, session) {
    validateConfig(c);
    var request = parseURL(buildURL(profile, action, session));
    session = request.session || c.remote.defaultSession;
    if (!has(c.remote.sessions, session)) fail('Session non autorisée localement');
    var actions = action === 'workspace' ? ['ssh', 'codex-tmux', 'web-tunnel'] : [action];
    return { profile: profile, action: action, session: session, label: c.profiles[profile].label, commands: action === 'check' ? [] : actions.map(function (a) { return command(c, profile, a, session); }) };
  }
  function planFromURL(c, url, installedProfile, actualMachine) {
    var r = parseURL(url);
    if (!has(PROFILES, installedProfile) || r.profile !== installedProfile) fail('Le profil sélectionné ne correspond pas au profil installé sur ce Mac.');
    if (actualMachine !== installedProfile) fail('Le matériel détecté ne correspond pas au profil installé. Action bloquée.');
    return preview(c, r.profile, r.action, r.session);
  }
  return { actions: ACTIONS, profiles: PROFILES, quote: quote, validateConfig: validateConfig, parseURL: parseURL, buildURL: buildURL, preview: preview, planFromURL: planFromURL, remoteScript: remoteScript };
}());
