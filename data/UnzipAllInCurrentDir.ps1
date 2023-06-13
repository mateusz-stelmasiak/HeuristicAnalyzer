$files = Get-Childitem .
foreach($fs in $files){Expand-Archive $fs -DestinationPath .}