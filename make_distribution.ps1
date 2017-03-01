# Clean up items
Remove-Item .\distribution\*
Move-Item .\dist\* .\versions -Force # save any old versions, but get them out of the dist folder so that we can copy any wheels in here to the final package
$destination = "C:\Users\dsx.AD3\Code\arcproject-wq-processing\distribution.zip"
If(Test-Path $destination) {Remove-Item $destination}

# Make the wheel and copy files to the distribution folder
& "C:\Program Files\ArcGIS\Pro\bin\Python\envs\arcproject-wq-processing\python" .\setup.py bdist_wheel
Copy-Item .\user_setup.py .\distribution
Copy-Item .\dist\arcproject*.whl .\distribution
Copy-Item .\*.pyt .\distribution
Copy-Item *.pyt.xml .\distribution
Copy-Item .\Installation_Instructions.url .\distribution\Installation_Instructions.url
Copy-Item .\README.md .\distribution\README.txt

# zip the files in the distribution folder to a single file
$source = "C:\Users\dsx.AD3\Code\arcproject-wq-processing\distribution"
Add-Type -assembly "system.io.compression.filesystem"
[io.compression.zipfile]::CreateFromDirectory($source, $destination)


