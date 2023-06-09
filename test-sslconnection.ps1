param(
    $openssl_path='C:\Program Files\Git\usr\bin\openssl.exe',
    $server="www.mit.edu:443")


if (-not(Test-Path -Path $openssl_path)) {
    write-host "Resource file not found: $($openssl_path)"
    exit 1
}

$certfile_path = "$($env:temp)\tmp_cert_file.pem"
if (test-path -path $certfile_path) {
	remove-item -path $certfile_path -force
}


write-host "Server: $($server)"

$s_client = Write-Output "q`n" | & $openssl_path s_client -connect $server -status 2>$null

$certificate = @()

# capture elements of interest from stdout
foreach ($line in $s_client) {
    # capture content of the subject
    if ($line -match '^subject=') {
        $subject = $line
        # clean captured content
        $subject = $subject -replace '^subject=',''
    }
    
    # capture content of the server cert
    if ($line -match '^-----BEGIN CERTIFICATE-----') {
        $inCert = $true
    }

    if ($inCert -eq $true) {
        $certificate += $line
    }

    if ($line -match '^-----END CERTIFICATE-----') {
        $inCert = $false
        # clean the captured content
    }        
}

# write server certificate to tmp file
$certfile_path = "$($env:temp)\tmp_cert_file.pem"
$certificate | Set-Content -Path $certfile_path

if ($certificate) {

	write-host "-Server Certificate Subject: $($subject)"

	# list 
	$x509 = & $openssl_path x509 -in $certfile_path -text 2>$null
	foreach ($line in $x509) {
	    $entry = $line | Select-String -Pattern "^\s+DNS:"
	    if ($entry) {
	        $entry = $entry.tostring().trim()
      	  $entries = $entry -split ", "
	        foreach ($entry in $entries) {
	            $entry = $entry -replace '^DNS:',''
	            write-host "-Server Certificate SAN DNS Entry: $($entry)"
	        }
	    }
	}
} else {
	write-host "s_client connection to server failed."
}
