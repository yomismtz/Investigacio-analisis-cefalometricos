$ErrorActionPreference = 'Stop'

$outDir = 'dist-installer-yornis'
New-Item -ItemType Directory -Force -Path $outDir | Out-Null

$rsa = [System.Security.Cryptography.RSA]::Create(3072)
$subject = [System.Security.Cryptography.X509Certificates.X500DistinguishedName]::new('CN=Yornis Development Code Signing')
$req = [System.Security.Cryptography.X509Certificates.CertificateRequest]::new(
    $subject,
    $rsa,
    [System.Security.Cryptography.HashAlgorithmName]::SHA256,
    [System.Security.Cryptography.RSASignaturePadding]::Pkcs1
)

$keyUsage = [System.Security.Cryptography.X509Certificates.X509KeyUsageFlags]::DigitalSignature
$req.CertificateExtensions.Add([System.Security.Cryptography.X509Certificates.X509KeyUsageExtension]::new($keyUsage, $true))
$oids = [System.Security.Cryptography.OidCollection]::new()
[void]$oids.Add([System.Security.Cryptography.Oid]::new('1.3.6.1.5.5.7.3.3', 'Code Signing'))
$req.CertificateExtensions.Add([System.Security.Cryptography.X509Certificates.X509EnhancedKeyUsageExtension]::new($oids, $true))
$req.CertificateExtensions.Add([System.Security.Cryptography.X509Certificates.X509BasicConstraintsExtension]::new($false, $false, 0, $true))

$notBefore = [DateTimeOffset]::UtcNow.AddMinutes(-5)
$notAfter = [DateTimeOffset]::UtcNow.AddYears(3)
$cert = $req.CreateSelfSigned($notBefore, $notAfter)

$password = [Guid]::NewGuid().ToString('N') + [Guid]::NewGuid().ToString('N')
$pfxPath = Join-Path $env:RUNNER_TEMP 'yornis-development-codesign.pfx'
$cerPath = Join-Path $outDir 'Yornis_Development_CodeSigning.cer'

[IO.File]::WriteAllBytes($pfxPath, $cert.Export([System.Security.Cryptography.X509Certificates.X509ContentType]::Pfx, $password))
[IO.File]::WriteAllBytes($cerPath, $cert.Export([System.Security.Cryptography.X509Certificates.X509ContentType]::Cert))

"YORNIS_PFX=$pfxPath" | Out-File -FilePath $env:GITHUB_ENV -Append
"YORNIS_PFX_PASSWORD=$password" | Out-File -FilePath $env:GITHUB_ENV -Append
"YORNIS_CERT_THUMBPRINT=$($cert.Thumbprint)" | Out-File -FilePath $env:GITHUB_ENV -Append

Write-Host "Created ephemeral RSA-3072 SHA-256 code-signing certificate: $($cert.Subject)"
Write-Host "Thumbprint: $($cert.Thumbprint)"
Write-Host "Public certificate: $cerPath"
Write-Host 'Private key remains only in the temporary GitHub runner PFX and is never uploaded.'
