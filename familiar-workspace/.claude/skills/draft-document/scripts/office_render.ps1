<#
.SYNOPSIS
  Open a .pptx, .docx or .xlsx in the real Office application, read-only, and export what a
  person would see: one PNG per slide plus a PDF for a deck, an open check for a document (page,
  tracked-change and comment counts; a PDF only with -WordPdf), a recalculated open check for a
  workbook.

.DESCRIPTION
  LibreOffice is not a fidelity check for Office (fleet audit 2026-10-09: a deck that rendered
  cleanly there overlapped in PowerPoint, and three Word files LibreOffice accepted would not open
  in Word). This script is the Office-native final check on Windows hosts that have Office.

  It never edits the input: Office opens it read-only, without a window, with alerts off, and every
  export goes to -OutDir. It starts its own Office instance and never attaches to one the user has
  open. The work runs in a background job with a time limit (-TimeoutSeconds, default 180); if Office
  stalls, usually on a first-run, sign-in or safe-mode dialog, only the Office process this script
  started is stopped, and the result says so.

  Word's PDF export stalls when Word runs headless from a background process (seen 2026-10-24 on
  Windows 11 with Microsoft 365: open, count and close all work, the export never returns), so a
  document gets the open check by default; the open check is what catches a file Word refuses or
  must repair. Pass -WordPdf to try the export anyway; the time limit still applies.

  It prints one JSON object. "opened": false means the application refused the file, which is the
  defect to report; "error" says why. Windows PowerShell 5.1 compatible. Where Office is missing it
  reports "available": false and the caller falls back to the LibreOffice render, labelled as such.

.EXAMPLE
  powershell -NoProfile -ExecutionPolicy Bypass -File office_render.ps1 -Path deck.pptx -OutDir .scratch\render
  powershell -NoProfile -ExecutionPolicy Bypass -File office_render.ps1 -Check
#>
param(
  [string]$Path,
  [string]$OutDir,
  [int]$TimeoutSeconds = 180,
  [switch]$WordPdf,
  [switch]$Check
)

$ErrorActionPreference = 'Stop'

function Test-App($progId) {
  try { return ($null -ne [type]::GetTypeFromProgID($progId)) } catch { return $false }
}

$apps = @{
  powerpoint = (Test-App 'PowerPoint.Application')
  word       = (Test-App 'Word.Application')
  excel      = (Test-App 'Excel.Application')
}

if ($Check) {
  @{ available = ($apps.powerpoint -or $apps.word -or $apps.excel); apps = $apps } | ConvertTo-Json -Compress
  exit 0
}

if (-not $Path) { Write-Error 'give -Path <file> (and -OutDir), or -Check'; exit 2 }
$full = (Resolve-Path -LiteralPath $Path).ProviderPath
$ext = [System.IO.Path]::GetExtension($full).ToLowerInvariant()
if (-not $OutDir) { $OutDir = Join-Path (Split-Path $full -Parent) '.render' }
if (-not (Test-Path -LiteralPath $OutDir)) { New-Item -ItemType Directory -Path $OutDir | Out-Null }
$out = (Resolve-Path -LiteralPath $OutDir).ProviderPath

$kind = switch -Regex ($ext) {
  '^\.(pptx|pptm|potx)$' { 'powerpoint' }
  '^\.(docx|docm|dotx)$' { 'word' }
  '^\.(xlsx|xlsm|xltx)$' { 'excel' }
  default { '' }
}
$result = @{ file = $full; available = $true; opened = $false; app = $kind; pdf = ''; images = @(); error = '' }
if (-not $kind) {
  $result.error = "not an Office file familiar renders: $ext"
  $result | ConvertTo-Json -Compress; exit 1
}
if (-not $apps[$kind]) {
  $result.available = $false
  $result | ConvertTo-Json -Compress; exit 0
}

$procName = @{ powerpoint = 'POWERPNT'; word = 'WINWORD'; excel = 'EXCEL' }[$kind]
$before = @(Get-Process $procName -ErrorAction SilentlyContinue | ForEach-Object { $_.Id })
$started = Get-Date

$work = {
  param($kind, $full, $out, $wordPdf)
  $ErrorActionPreference = 'Stop'
  $r = @{ opened = $false; pdf = ''; images = @(); error = '' }
  $stem = [System.IO.Path]::GetFileNameWithoutExtension($full)
  try {
    if ($kind -eq 'powerpoint') {
      $pp = New-Object -ComObject PowerPoint.Application
      try {
        $pp.DisplayAlerts = 1  # ppAlertsNone
        $pres = $pp.Presentations.Open($full, -1, 0, 0)  # ReadOnly, not Untitled, no window
        $r.opened = $true
        $r.slides = $pres.Slides.Count
        $w = [double]$pres.PageSetup.SlideWidth; $h = [double]$pres.PageSetup.SlideHeight
        $scale = 1600 / [Math]::Max($w, 1)
        $imgs = @()
        for ($i = 1; $i -le $pres.Slides.Count; $i++) {
          $png = Join-Path $out ('{0}_slide{1:D2}.png' -f $stem, $i)
          $pres.Slides.Item($i).Export($png, 'PNG', [int]($w * $scale), [int]($h * $scale))
          $imgs += $png
        }
        $r.images = $imgs
        $pdf = Join-Path $out ($stem + '_pptx.pdf')
        $pres.SaveAs($pdf, 32)  # ppSaveAsPDF writes a copy; the source is untouched
        $r.pdf = $pdf
        $pres.Close()
        [void][System.Runtime.InteropServices.Marshal]::ReleaseComObject($pres)
      } finally { $pp.Quit(); [void][System.Runtime.InteropServices.Marshal]::ReleaseComObject($pp) }
    } elseif ($kind -eq 'word') {
      $wd = New-Object -ComObject Word.Application
      try {
        $wd.Visible = $false
        $wd.DisplayAlerts = 0  # wdAlertsNone
        $doc = $wd.Documents.Open($full, $false, $true, $false)  # no conversion prompt, read-only, not in recent files
        $r.opened = $true
        $r.pages = $doc.ComputeStatistics(2)  # wdStatisticPages
        $r.revisions = $doc.Revisions.Count
        $r.comments = $doc.Comments.Count
        if ($wordPdf) {
          $pdf = Join-Path $out ($stem + '_docx.pdf')
          $doc.ExportAsFixedFormat($pdf, 17)  # wdExportFormatPDF
          $r.pdf = $pdf
        }
        $doc.Close(0)  # wdDoNotSaveChanges
        [void][System.Runtime.InteropServices.Marshal]::ReleaseComObject($doc)
      } finally { $wd.Quit(); [void][System.Runtime.InteropServices.Marshal]::ReleaseComObject($wd) }
    } else {
      $xl = New-Object -ComObject Excel.Application
      try {
        $xl.Visible = $false
        $xl.DisplayAlerts = $false
        $wb = $xl.Workbooks.Open($full, 0, $true)  # do not update links, read-only
        $r.opened = $true
        $xl.CalculateFull()
        $sheets = @(); $errors = 0
        foreach ($ws in $wb.Worksheets) {
          $sheets += $ws.Name
          try { $errors += $ws.UsedRange.SpecialCells(-4123, 16).Count } catch { }  # formulas that return an error
        }
        $r.sheets = $sheets
        $r.formula_errors = $errors
        $wb.Close($false)
        [void][System.Runtime.InteropServices.Marshal]::ReleaseComObject($wb)
      } finally { $xl.Quit(); [void][System.Runtime.InteropServices.Marshal]::ReleaseComObject($xl) }
    }
  } catch { $r.error = $_.Exception.Message }
  [GC]::Collect(); [GC]::WaitForPendingFinalizers()
  $r
}

$job = Start-Job -ScriptBlock $work -ArgumentList $kind, $full, $out, ([bool]$WordPdf)
if (Wait-Job $job -Timeout $TimeoutSeconds) {
  $r = Receive-Job $job
  foreach ($k in 'opened', 'pdf', 'images', 'error', 'slides', 'pages', 'revisions', 'comments', 'sheets', 'formula_errors') {
    if ($null -ne $r.$k) { $result[$k] = $r.$k }
  }
} else {
  Stop-Job $job
  $mine = @(Get-Process $procName -ErrorAction SilentlyContinue |
            Where-Object { ($before -notcontains $_.Id) -and $_.StartTime -ge $started.AddSeconds(-2) })
  foreach ($p in $mine) { Stop-Process -Id $p.Id -Force -ErrorAction SilentlyContinue }
  $result.error = "timed out after $TimeoutSeconds s; stopped the $procName instance this script started " +
                  "($($mine.Count) process). Office may be waiting on a first-run, sign-in or safe-mode dialog: open the app once by hand, then rerun."
}
Remove-Job $job -Force -ErrorAction SilentlyContinue

# A headless Office instance can linger after Quit. Give the one this script started ten seconds to
# exit, then stop it; an instance the user had open before the script ran is never touched.
$deadline = (Get-Date).AddSeconds(10)
do {
  $mine = @(Get-Process $procName -ErrorAction SilentlyContinue |
            Where-Object { ($before -notcontains $_.Id) -and $_.StartTime -ge $started.AddSeconds(-2) })
  if ($mine.Count -eq 0) { break }
  Start-Sleep -Milliseconds 500
} while ((Get-Date) -lt $deadline)
foreach ($p in $mine) { Stop-Process -Id $p.Id -Force -ErrorAction SilentlyContinue }

$result | ConvertTo-Json -Compress -Depth 4
if ($result.error -or -not $result.opened) { exit 1 }
exit 0
