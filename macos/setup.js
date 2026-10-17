/* Runs during local installation only, using native Foundation and JXA. */
ObjC.import('Foundation');
function readText(path) {
  var value = $.NSString.stringWithContentsOfFileEncodingError($(path), $.NSUTF8StringEncoding, null);
  if (!value) throw new Error('Fichier inaccessible : ' + path);
  return ObjC.unwrap(value);
}
function run(argv) {
  if (argv.length !== 3) throw new Error('Usage : setup.js SOURCE DESTINATION PROFIL');
  eval(readText(argv[0] + '/site/core.js'));
  eval(readText(argv[0] + '/macos/hardware.js'));
  if (hardwareType() !== argv[2]) throw new Error('Profil incompatible avec le matériel détecté. Installation arrêtée.');
  var config;
  if ($.NSFileManager.defaultManager.fileExistsAtPath($(argv[1]))) {
    config = JarvisCore.validateConfig(JSON.parse(readText(argv[1])));
    if (config.clientProfile !== argv[2]) throw new Error('Configuration existante d’un autre profil. Elle est conservée ; corrigez-la explicitement.');
    return 'Configuration existante conservée';
  }
  config = JarvisCore.validateConfig(JSON.parse(readText(argv[0] + '/site/config.json')));
  config.clientProfile = argv[2];
  var ok = $(JSON.stringify(config, null, 2) + '\n').writeToFileAtomicallyEncodingError($(argv[1]), true, $.NSUTF8StringEncoding, null);
  if (!ok) throw new Error('Impossible de créer la configuration locale');
  return 'Configuration locale créée';
}
