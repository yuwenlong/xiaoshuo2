param([string]$DocxPath, [string]$PdfPath)
$word = New-Object -ComObject Word.Application
$word.Visible = $false
try {
    $doc = $word.Documents.Open($DocxPath, $false, $true)
    $pages = $doc.ComputeStatistics(2)  # wdStatisticPages = 2
    $words = $doc.ComputeStatistics(0)  # wdStatisticWords = 0
    $doc.ExportAsFixedFormat($PdfPath, 17)  # wdExportFormatPDF = 17
    $doc.Close($false)
    Write-Output "PAGES=$pages WORDS=$words"
} finally {
    $word.Quit()
}
