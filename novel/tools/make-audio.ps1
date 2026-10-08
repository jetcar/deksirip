param(
    [string]$Chapter,
    [switch]$All,
    [ValidateSet('ru-RU-SvetlanaNeural', 'ru-RU-DmitryNeural')]
    [string]$Voice = 'ru-RU-SvetlanaNeural'
)

if (($Chapter -and $All) -or (-not $Chapter -and -not $All)) {
    throw 'Укажите -Chapter <имя-файла-без-md> или -All.'
}

$runtime = Join-Path $env:TEMP 'deksirip-edge-tts-runtime'
if (-not (Test-Path -LiteralPath $runtime)) {
    throw 'Рантайм синтеза речи не найден. Запустите подготовку аудио из Codex ещё раз.'
}

$scriptRoot = Split-Path -Parent $PSCommandPath
$novelRoot = Split-Path -Parent $scriptRoot
$pythonScript = Join-Path $scriptRoot 'synthesize_audio.py'
$env:PYTHONPATH = $runtime

$arguments = @($pythonScript, '--voice', $Voice)
if ($All) {
    $arguments += '--all'
} else {
    $arguments += @('--chapter', $Chapter)
}

py @arguments
