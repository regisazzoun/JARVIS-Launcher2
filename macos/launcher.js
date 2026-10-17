/* Native JXA runtime. Never reads code, hosts, paths or commands from a URL. */
ObjC.import('Foundation');
function readText(path) {
  var value = $.NSString.stringWithContentsOfFileEncodingError($(path), $.NSUTF8StringEncoding, null);
  if (!value) throw new Error('Fichier local inaccessible : ' + path);
  return ObjC.unwrap(value);
}
function run(argv) {
  if (argv.length !== 2) throw new Error('Arguments invalides');
  var source = readText(argv[1] + 'core.js');
  eval(source); // Installed, trusted application resource; never URL/page content.
  eval(readText(argv[1] + 'hardware.js'));
  var configPath = ObjC.unwrap($.NSHomeDirectory()) + '/Library/Application Support/JARVIS Launcher/config.json';
  var config = JSON.parse(readText(configPath));
  var plan = JarvisCore.planFromURL(config, argv[0], config.clientProfile, hardwareType());
  var app = Application.currentApplication(); app.includeStandardAdditions = true;
  if (plan.action === 'check') {
    app.displayDialog('Lanceur local disponible sur ce Mac.\nProfil installé et matériel : ' + plan.label + '\nConfiguration : ' + configPath + '\nSSH, Tailscale et les actions distantes ne sont pas validés par ce diagnostic.', { withTitle: 'JARVIS Launcher — diagnostic local', buttons: ['OK'], defaultButton: 'OK' });
    return 'Diagnostic affiché';
  }
  var key = ObjC.unwrap($.NSHomeDirectory()) + '/' + config.profiles[plan.profile].identityFile.slice(2);
  if (!$.NSFileManager.defaultManager.fileExistsAtPath($(key))) throw new Error('La clé SSH configurée est absente de ce Mac. Vérifiez la configuration locale ; aucune clé n’est téléchargée ou créée.');
  app.displayDialog('Poste : ' + plan.label + '\nServeur : ' + config.profiles[plan.profile].user + '@' + (plan.action === 'ssh-lan' ? config.profiles[plan.profile].lanHost : config.profiles[plan.profile].host) + '\nAction : ' + plan.action + '\nSession : ' + plan.session + '\nFenêtres Terminal : ' + plan.commands.length + '\n\nCette demande peut provenir de n’importe quel site. Continuer ?', { withTitle: 'JARVIS Launcher — confirmer', buttons: ['Annuler', 'Ouvrir'], defaultButton: 'Ouvrir', cancelButton: 'Annuler' });
  var terminal = Application('com.apple.Terminal');
  terminal.activate();
  plan.commands.forEach(function (command) { terminal.doScript(command.terminal); });
  return 'Demandes Terminal transmises';
}
