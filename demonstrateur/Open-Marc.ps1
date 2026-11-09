# Poste opérateur uniquement. Aucun secret ne transite par stdout ou le presse-papiers.
param([switch]$ValidateOnly)

$ErrorActionPreference = 'Stop'
$form = $null
$passwordField = $null
$records = $null
$reader = $null
$process = $null
$buffer = $null
try {
    Add-Type -AssemblyName System.Formats.Tar
    $spec = Join-Path $PSScriptRoot 'compose.yaml'
    Push-Location -LiteralPath $PSScriptRoot
    try {
        $id = (& docker --context desktop-linux compose --project-name thiga-corrige-20261109 --file $spec ps --all --quiet bootstrap).Trim()
        if ($LASTEXITCODE -ne 0 -or $id -notmatch '^[a-f0-9]{64}$') { throw 'bootstrap' }
        $format = '{{index .Config.Labels "com.docker.compose.project"}}|{{index .Config.Labels "com.docker.compose.service"}}|{{.State.Status}}|{{.State.ExitCode}}|{{range .Mounts}}{{if eq .Destination "/admin"}}{{.Name}}{{end}}{{end}}'
        $target = & docker --context desktop-linux inspect --format $format $id
        if ($LASTEXITCODE -ne 0 -or $target -ne 'thiga-corrige-20261109|bootstrap|exited|0|thiga-corrige-20261109_admin') { throw 'identity' }
        $start = [System.Diagnostics.ProcessStartInfo]::new('docker')
        $start.UseShellExecute = $false
        $start.CreateNoWindow = $true
        $start.RedirectStandardOutput = $true
        $start.RedirectStandardError = $true
        foreach ($arg in @('--context', 'desktop-linux', 'cp', "${id}:/admin/credentials.json", '-')) {
            $start.ArgumentList.Add($arg)
        }
        $process = [System.Diagnostics.Process]::Start($start)
        $reader = [System.Formats.Tar.TarReader]::new($process.StandardOutput.BaseStream, $true)
        while ($null -ne ($entry = $reader.GetNextEntry())) {
            if ($entry.Name -ne 'credentials.json') { continue }
            if ($null -ne $records -or $entry.Length -lt 1 -or $entry.Length -gt 16384 -or
                $entry.EntryType -notin @('RegularFile', 'V7RegularFile')) { throw 'archive' }
            $buffer = [System.IO.MemoryStream]::new()
            $entry.DataStream.CopyTo($buffer)
            $records = [System.Text.Encoding]::UTF8.GetString($buffer.ToArray()) | ConvertFrom-Json
        }
        if (-not $process.WaitForExit(5000) -or $process.ExitCode -ne 0 -or $records.passwords.marc.Length -lt 32) {
            throw 'credential'
        }
    } finally { Pop-Location }

    if ($ValidateOnly) {
        [pscustomobject]@{ project = 'thiga-corrige-20261109'; account = 'marc'; credential_available = $true; revealed = $false }
        return
    }

    Add-Type -AssemblyName System.Windows.Forms
    $form = [System.Windows.Forms.Form]::new()
    $form.Text = 'THIGA — accès local confidentiel'
    $form.Width = 690
    $form.Height = 185
    $form.StartPosition = 'CenterScreen'
    $label = [System.Windows.Forms.Label]::new()
    $label.Text = 'Compte fictif marc@thiga.example.com  |  http://127.0.0.1:3039/'
    $label.SetBounds(16, 15, 630, 25)
    $passwordField = [System.Windows.Forms.TextBox]::new()
    $passwordField.SetBounds(16, 51, 630, 25)
    $passwordField.ReadOnly = $true
    $passwordField.ShortcutsEnabled = $false
    $passwordField.UseSystemPasswordChar = $true
    $passwordField.Text = $records.passwords.marc
    $reveal = [System.Windows.Forms.CheckBox]::new()
    $reveal.Text = 'Afficher temporairement pour la saisie locale dans Chrome'
    $reveal.SetBounds(16, 86, 630, 30)
    $reveal.Add_CheckedChanged({ $passwordField.UseSystemPasswordChar = -not $reveal.Checked })
    $form.Controls.AddRange(@($label, $passwordField, $reveal))
    [void]$form.ShowDialog()
} catch {
    Write-Error 'Accès local indisponible. Vérifier le projet thiga-corrige-20261109 et la réussite du bootstrap.'
} finally {
    if ($passwordField) { $passwordField.Clear() }
    if ($form) { $form.Dispose() }
    if ($records) { $records.passwords.marc = $null }
    if ($buffer) {
        $bytes = $buffer.GetBuffer()
        [Array]::Clear($bytes, 0, $bytes.Length)
        $buffer.Dispose()
    }
    if ($reader) { $reader.Dispose() }
    if ($process) { $process.Dispose() }
}
