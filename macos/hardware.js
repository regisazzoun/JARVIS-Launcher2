/* Shared native helper, imported only from trusted installed resources. */
function hardwareType() {
  var task = $.NSTask.alloc.init;
  var pipe = $.NSPipe.pipe;
  task.launchPath = '/usr/sbin/system_profiler';
  task.arguments = ['SPHardwareDataType', '-json'];
  task.standardOutput = pipe;
  task.standardError = $.NSFileHandle.fileHandleWithNullDevice;
  task.launch;
  var data = pipe.fileHandleForReading.readDataToEndOfFile;
  task.waitUntilExit;
  if (task.terminationStatus !== 0) throw new Error('Identification matérielle impossible');
  var parsed = JSON.parse(ObjC.unwrap($.NSString.alloc.initWithDataEncoding(data, $.NSUTF8StringEncoding)));
  var name = String(parsed.SPHardwareDataType[0].machine_name || '').toLowerCase();
  if (name === 'macbook pro') return 'macbook-pro';
  if (name === 'mac mini') return 'mac-mini';
  throw new Error('Matériel non reconnu : seules les familles MacBook Pro et Mac mini sont autorisées.');
}
