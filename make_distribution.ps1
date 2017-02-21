# Clean up items
Remove-Item .\distribution\*
$destination = "C:\Users\dsx.AD3\Code\arcproject-wq-processing\distribution.zip"
If(Test-Path $destination) {Remove-Item $destination}

# Make the wheel and copy files to the distribution folder
& "C:\Program Files\ArcGIS\Pro\bin\Python\envs\arcproject-wq-processing\python" .\setup.py bdist_wheel
Copy-Item .\dist\arcproject*.whl .\distribution
Copy-Item .\*.pyt .\distribution
Copy-Item *.pyt.xml .\distribution
Copy-Item .\Installation_Instructions.url
Copy-Item .\README.md .\distribution\README.txt

# zip the files in the distribution folder to a single file
$source = "C:\Users\dsx.AD3\Code\arcproject-wq-processing\distribution"
Add-Type -assembly "system.io.compression.filesystem"
[io.compression.zipfile]::CreateFromDirectory($source, $destination)