on run
  display dialog "JARVIS Launcher est installé. Ouvrez le site et choisissez le profil de ce Mac. Le bouton Vérifier affiche le diagnostic local. Aucun service HTTP n’est démarré." with title "JARVIS Launcher" buttons {"OK"} default button "OK"
end run

on open location incomingURL
  set resourceFolder to (POSIX path of (path to me)) & "Contents/Resources/"
  set runnerPath to resourceFolder & "launcher.js"
  try
    do shell script "/usr/bin/osascript -l JavaScript " & quoted form of runnerPath & " " & quoted form of incomingURL & " " & quoted form of resourceFolder
  on error errorMessage number errorNumber
    if errorNumber is not -128 then
      display dialog errorMessage with title "JARVIS Launcher — action refusée" buttons {"OK"} default button "OK" with icon caution
    end if
  end try
end open location
