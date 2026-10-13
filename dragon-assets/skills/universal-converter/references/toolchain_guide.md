# Universal Converter Toolchain Guide

This guide provides core command patterns for the integrated toolchains.

## 1. Pandoc (Document Hub)
Used for converting between markdown, docx, pdf, html, and more.
- **MD to DOCX**: `pandoc input.md -o output.docx`
- **MD to PDF**: `pandoc input.md -o output.pdf --pdf-engine=xelatex`
- **HTML to MD**: `pandoc input.html -t commonmark -o output.md`

## 2. FFmpeg (Multimedia Commander)
Used for audio/video processing.
- **Transcode**: `ffmpeg -i input.mp4 -c:v libx264 -crf 23 -c:a aac -b:a 192k output.mp4`
- **Extract Audio**: `ffmpeg -i input.mp4 -vn -acodec libmp3lame -q:a 2 output.mp3`
- **Create GIF**: `ffmpeg -i input.mp4 -vf "fps=10,scale=320:-1:flags=lanczos" output.gif`

## 3. ImageMagick (Image Factory)
Used for image manipulation.
- **Convert & Resize**: `magick input.png -resize 800x600 output.jpg`
- **Batch Processing**: `magick mogrify -format webp *.jpg`
- **Combine to PDF**: `magick *.png output.pdf`

## 4. Stirling-PDF (PDF Expert)
Patterns for PDF surgical operations (via API or CLI wrapper).
- **Merge**: `stirling-pdf merge -i file1.pdf file2.pdf -o merged.pdf`
- **OCR**: `stirling-pdf ocr -i scan.pdf -o searchable.pdf -l chi_sim`

## 5. Calibre (E-book Engine)
Using `ebook-convert` for book formats.
- **EPUB to AZW3**: `ebook-convert input.epub output.azw3`
- **Fix Metadata**: `ebook-meta output.epub --title "New Title" --author "Author Name"`

## 6. MeshLab (3D Consultant)
Using `meshlabserver` (or modern `meshlab` CLI).
- **Format Swap**: `meshlabserver -i input.stl -o output.obj -s script.mlx`
- **Simplification**: Use Quadric Edge Collapse Decimation via filter script.
