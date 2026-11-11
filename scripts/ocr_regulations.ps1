$ErrorActionPreference = "Stop"
Add-Type -AssemblyName System.Runtime.WindowsRuntime
$null = [Windows.Storage.StorageFile,Windows.Storage,ContentType=WindowsRuntime]
$null = [Windows.Data.Pdf.PdfDocument,Windows.Data.Pdf,ContentType=WindowsRuntime]
$null = [Windows.Data.Pdf.PdfPageRenderOptions,Windows.Data.Pdf,ContentType=WindowsRuntime]
$null = [Windows.Storage.Streams.InMemoryRandomAccessStream,Windows.Storage.Streams,ContentType=WindowsRuntime]
$null = [Windows.Storage.Streams.DataReader,Windows.Storage.Streams,ContentType=WindowsRuntime]
$null = [Windows.Graphics.Imaging.BitmapDecoder,Windows.Graphics.Imaging,ContentType=WindowsRuntime]
$null = [Windows.Media.Ocr.OcrEngine,Windows.Media.Ocr,ContentType=WindowsRuntime]
$null = [Windows.Globalization.Language,Windows.Globalization,ContentType=WindowsRuntime]

$asTaskGeneric = ([System.WindowsRuntimeSystemExtensions].GetMethods() | Where-Object {
  $_.Name -eq "AsTask" -and $_.GetParameters().Count -eq 1 -and $_.GetParameters()[0].ParameterType.Name -eq "IAsyncOperation``1"
})[0]
function Await($op, $type) {
  $method = $asTaskGeneric.MakeGenericMethod($type)
  $task = $method.Invoke($null, @($op))
  $task.Wait(-1) | Out-Null
  $task.Result
}
function AwaitAction($op) {
  $method = ([System.WindowsRuntimeSystemExtensions].GetMethods() | Where-Object {
    $_.Name -eq "AsTask" -and $_.GetParameters().Count -eq 1 -and -not $_.IsGenericMethod
  })[0]
  $task = $method.Invoke($null, @($op))
  $task.Wait(-1) | Out-Null
}

$path = (Resolve-Path "source-originals\regulations-and-guidelines-2026.pdf").Path
$file = Await ([Windows.Storage.StorageFile]::GetFileFromPathAsync($path)) ([Windows.Storage.StorageFile])
$pdf = Await ([Windows.Data.Pdf.PdfDocument]::LoadFromFileAsync($file)) ([Windows.Data.Pdf.PdfDocument])
$engine = [Windows.Media.Ocr.OcrEngine]::TryCreateFromUserProfileLanguages()
if (-not $engine) { throw "No Windows OCR language is installed." }
$out = New-Object System.Text.StringBuilder
[void]$out.AppendLine("id: src-003")
[void]$out.AppendLine("title: Regulations and Guidelines for the Conduct of Elections, 2026")
[void]$out.AppendLine("url: https://inecnigeria.org/documents/guidelines/REGULATIONS-AND-GUIDELINES-FOR-2026.pdf")
[void]$out.AppendLine("last_verified:")
[void]$out.AppendLine("ocr: true")
[void]$out.AppendLine("scope: nigeria")
[void]$out.AppendLine("---")
for ($index = 0; $index -lt $pdf.PageCount; $index++) {
  $pageNo = $index + 1
  $page = $pdf.GetPage($index)
  $options = New-Object Windows.Data.Pdf.PdfPageRenderOptions
  $options.DestinationWidth = [uint32]([Math]::Min(2400, [Math]::Round($page.Size.Width * 3)))
  $stream = New-Object Windows.Storage.Streams.InMemoryRandomAccessStream
  AwaitAction ($page.RenderToStreamAsync($stream, $options))
  $stream.Seek(0) | Out-Null
  $decoder = Await ([Windows.Graphics.Imaging.BitmapDecoder]::CreateAsync($stream)) ([Windows.Graphics.Imaging.BitmapDecoder])
  $bitmap = Await ($decoder.GetSoftwareBitmapAsync()) ([Windows.Graphics.Imaging.SoftwareBitmap])
  $result = Await ($engine.RecognizeAsync($bitmap)) ([Windows.Media.Ocr.OcrResult])
  [void]$out.AppendLine("")
  [void]$out.AppendLine("--- page $pageNo ---")
  foreach ($line in $result.Lines) {
    [void]$out.AppendLine($line.Text)
  }
  $page.Dispose()
  $bitmap.Dispose()
  $stream.Dispose()
  Write-Output ("page " + $pageNo)
}
[System.IO.File]::WriteAllText((Join-Path (Get-Location) "knowledge\src-003.txt"), $out.ToString(), [System.Text.UTF8Encoding]::new($false))
Write-Output "wrote knowledge/src-003.txt"
