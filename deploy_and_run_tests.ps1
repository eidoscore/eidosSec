# Konfigurasi server
$server = "43.245.249.18"
$username = "admin" # Ganti dengan username yang sesuai
$password = ConvertTo-SecureString "password" -AsPlainText -Force # Ganti dengan password yang sesuai
$cred = New-Object System.Management.Automation.PSCredential($username, $password)

# Salin kode ke server
$localPath = "d:\Project\eidosSec\*"
$remotePath = "/home/admin/eidosSec" # Ganti dengan path yang sesuai

# Buat direktori di server jika belum ada
Invoke-Command -ComputerName $server -Credential $cred -ScriptBlock {
    param($remotePath)
    if (-not (Test-Path $remotePath)) {
        New-Item -ItemType Directory -Path $remotePath
    }
} -ArgumentList $remotePath

# Salin file
Copy-Item -Path $localPath -Destination "\\$server\$remotePath" -Recurse -Force

# Jalankan skrip pengujian di server
Invoke-Command -ComputerName $server -Credential $cred -ScriptBlock {
    cd /home/admin/eidosSec
    .\run_all_tests.ps1
}
