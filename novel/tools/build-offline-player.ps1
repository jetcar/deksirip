param(
  [string]$Source = (Join-Path $PSScriptRoot '..\audio\player.html'),
  [string]$Output = (Join-Path $PSScriptRoot '..\audio\offline-player.html'),
  [string]$Manuscript = (Join-Path $PSScriptRoot '..\MANUSCRIPT.md'),
  [string]$ChapterDirectory
)

$sourcePath = (Resolve-Path -LiteralPath $Source).Path
$template = Get-Content -LiteralPath $sourcePath -Raw
$marker = '<script id="embedded-chapters" type="application/json">[]</script>'

if (-not $template.Contains($marker)) {
  throw 'The player template has no embedded-chapters marker.'
}

$chapters = if ($ChapterDirectory) {
  $chapterDirectoryPath = (Resolve-Path -LiteralPath $ChapterDirectory).Path
  foreach ($chapterPath in (Get-ChildItem -LiteralPath $chapterDirectoryPath -Filter '*.md' -File | Sort-Object Name)) {
    $text = Get-Content -LiteralPath $chapterPath.FullName -Raw
    $heading = [regex]::Match($text, '(?m)^#\s+(.+)$')
    [pscustomobject]@{
      title = if ($heading.Success) { $heading.Groups[1].Value } else { $chapterPath.BaseName }
      file = $chapterPath.Name
      text = $text
    }
  }
} else {
  $manuscriptPath = (Resolve-Path -LiteralPath $Manuscript).Path
  $chapterDirectoryPath = Join-Path (Split-Path $manuscriptPath -Parent) 'chapters'
  $expression = [regex]'(?m)^\s*(?:\d+[\wа-яё-]*\.\s+)?\[([^\]]+)\]\(chapters/([^)]+\.md)\)'
  $seen = [System.Collections.Generic.HashSet[string]]::new()
  foreach ($match in $expression.Matches((Get-Content -LiteralPath $manuscriptPath -Raw))) {
    $file = $match.Groups[2].Value
    if ($seen.Add($file)) {
      [pscustomobject]@{
        title = $match.Groups[1].Value
        file = $file
        text = Get-Content -LiteralPath (Join-Path $chapterDirectoryPath $file) -Raw
      }
    }
  }
}

if (-not $chapters) { throw 'No chapters were found.' }

$json = $chapters | ConvertTo-Json -Depth 3 -Compress
$json = $json -replace '(?i)</', '<\/'
$offline = $template.Replace($marker, "<script id=`"embedded-chapters`" type=`"application/json`">$json</script>")
[System.IO.File]::WriteAllText($Output, $offline, [System.Text.UTF8Encoding]::new($false))
Write-Output "Built $Output with $($chapters.Count) chapters."
