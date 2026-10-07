$ErrorActionPreference = "Stop"
$root = $PSScriptRoot
$certs = Join-Path $root "certs"
$ca = Join-Path $certs "ca"
$server = Join-Path $certs "server"
$client = Join-Path $certs "client"
New-Item -ItemType Directory -Force -Path $ca, $server, $client | Out-Null

function Invoke-OpenSSL([string[]]$Arguments) {
    & openssl @Arguments
    if ($LASTEXITCODE -ne 0) { throw "OpenSSL failed: $($Arguments -join ' ')" }
}

Invoke-OpenSSL @("req", "-x509", "-newkey", "rsa:2048", "-nodes", "-keyout", "$ca/ca.key", "-out", "$ca/ca.crt", "-days", "3650", "-sha256", "-subj", "/C=VN/O=SecureChat/CN=SecureChat-CA", "-addext", "basicConstraints=critical,CA:TRUE", "-addext", "keyUsage=critical,keyCertSign,cRLSign")
Invoke-OpenSSL @("req", "-newkey", "rsa:2048", "-nodes", "-keyout", "$server/server.key", "-out", "$server/server.csr", "-subj", "/C=VN/O=SecureChat/CN=localhost")
Invoke-OpenSSL @("x509", "-req", "-in", "$server/server.csr", "-CA", "$ca/ca.crt", "-CAkey", "$ca/ca.key", "-CAcreateserial", "-out", "$server/server.crt", "-days", "365", "-sha256", "-extfile", "$root/openssl.cnf", "-extensions", "server_cert")
Invoke-OpenSSL @("req", "-newkey", "rsa:2048", "-nodes", "-keyout", "$client/client.key", "-out", "$client/client.csr", "-subj", "/C=VN/O=SecureChat/CN=securechat-client")
Invoke-OpenSSL @("x509", "-req", "-in", "$client/client.csr", "-CA", "$ca/ca.crt", "-CAkey", "$ca/ca.key", "-CAcreateserial", "-out", "$client/client.crt", "-days", "365", "-sha256", "-extfile", "$root/openssl.cnf", "-extensions", "client_cert")
Write-Host "Certificates created under $certs"
Write-Warning "These self-signed lab certificates and private keys are for local practice only."
