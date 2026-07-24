## Changelog

## 0.9.5 - Unreleased

- Updated `iscc-tika` to 0.6.0 (Apache Tika 3.3.x), removing the `<0.5.0` stability pin — the macOS
    native-image crash on embedded images is fixed upstream and linux/aarch64 wheels are now
    available
- **BREAKING**: Text metadata extraction now picks the first value when Tika returns multiple values
    for single-valued `IsccMeta` fields (e.g. an EPUB3 with multiple `<dc:title>` elements);
    Meta-Code and `metahash` differ from earlier releases for such assets
- Fixed EPUB metadata embed→extract round-trip: the embedded title is now returned instead of the
    document's pre-existing title
- Added regression tests for upstream Tika EPUB parser fixes (TIKA-198 spine path traversal,
    TIKA-237 deeply nested XML)
- Updated test expectations for Tika 3 whitespace normalization in extracted text
- Updated lint configuration for the expanded default rule set of ruff 0.16 (protects the
    load-order-sensitive imports in `iscc_sdk/__init__.py` from autofix re-sorting)
- Updated CLI tests for typer 0.27 error message formatting
- Updated `sct`/`sci` extras to request the CPU ONNX runtime (`iscc-sct[cpu]`, `iscc-sci[cpu]`) —
    iscc-sct 0.2.x and iscc-sci 0.3.x moved the onnxruntime dependency behind `cpu`/`gpu` extras
- Updated CI actions to latest major versions

## 0.9.4 - 2026-07-09

- Fixed process abort (uncatchable `std::terminate` → SIGABRT) in `image_meta_extract()` when an
    image carries a metadata value that exiv2 cannot convert to UTF-8, e.g. an EXIF `UserComment`
    declared UNICODE with an invalid UTF-16 payload as written by some early-2000s digital cameras;
    undecodable fields are now skipped with a warning instead of crashing the process

## 0.9.3 - 2026-06-04

- Added SVG cover image support for EPUB thumbnails (rasterized via `resvg`)
- Added `IsccThumbExtractionError` for recoverable thumbnail extraction failures
- Changed `code_iscc()` to handle thumbnail extraction failures gracefully (logs warning, continues
    without thumbnail instead of raising); genuinely corrupt or invalid source files still raise
    `IsccExtractionError`
- Changed `code_iscc()` to generate thumbnails early, before heavy content processing
- Removed EPUB cover fallback to first manifest image (only explicit cover references are used)
- Fixed EPUB3 cover-image detection for manifests with multiple space-separated property tokens
- Fixed EPUB cover extraction when archive entries store UTF-8 filename bytes without the ZIP UTF-8
    flag (CP437→UTF-8 recovery)
- Fixed EPUB cover extraction for OPF hrefs containing `..`/`.` path segments
- Fixed PNG cover thumbnail extraction failing on Photoshop-exported covers with large zTXt metadata
    chunks (raised `PngImagePlugin.MAX_TEXT_CHUNK` to 4 MB)
- Wrapped `iscc-tika` parse failures (`TypeError` from native bridge, e.g. TIKA-237 on EPUBs with
    deeply nested XHTML) as `IsccExtractionError` in `text_extract` and `text_meta_extract`
- Improved API documentation for `code_iscc()`, `code_iscc_mt()`, `code_content()`, and
    `code_text()` options
- Refactored `code_iscc_mt()` for improved parallelism: text extraction runs before submitting
    content/semantic futures, thumbnail generation overlaps with sum/meta computation, and result
    merging follows the same order as `code_iscc()`
- Removed redundant `onnxruntime` from `sci` and `sct` optional dependency groups (already a
    transitive dependency of `iscc-sci` and `iscc-sct`)
- Fixed CI: skip semantic code tests on macOS Python 3.12 (`onnxruntime` 1.26.0 has no macOS wheels
    for that version)
- Updated `iscc-schema` floor to `>=0.8.0` (version-pinned `@context`/`$schema` URLs now resolve to
    `0.8.0`)

## 0.9.2 - 2026-04-21

- Replaced `pdf-oxide` with `pypdfium2` for PDF text extraction
- Replaced `pymupdf` with `pypdfium2` for PDF thumbnail rendering
- Replaced `pymupdf` with `pypdf` for PDF metadata embedding

## 0.9.1 - 2026-04-14

- Pinned `pdf-oxide<0.3.20` and `iscc-tika<0.5.0` for stability
- Updated `uv_build` requirement to `>=0.11.2,<0.12.0`
- Removed deprecated PEP 639 license classifier

## 0.9.0 - 2026-04-12

- Added SVG as supported media type with rasterization, metadata, and thumbnail support
- Added RDF/Dublin Core metadata extraction and embedding for SVG files
- Added URL support to CLI `create` and `extract` commands
- Added optional `file_name` parameter to `extract_metadata` and `mediatype_and_mode`
- Added descriptive User-Agent header for URL downloads
- Added file extension from content sniffing for extensionless downloads
- Fixed URL scheme validation in `download_file` for security (S310)
- Fixed type checking errors in `extract_metadata`
- Fixed audio/ogg detection for OGG/OPUS audio files
- Suppressed noisy pdf-oxide TrueType cmap warnings
- Replaced defusedxml with lxml safe parser for SVG XML parsing
- Upgraded ffmpeg/ffprobe from 6.1 to 8.1
- Upgraded fpcalc (chromaprint) from 1.5.1 to 1.6.0
- Automated documentation deployment on release

## 0.8.9 - 2026-03-29

- Fixed EPUB cover extraction for URL-encoded paths in OPF manifest
- Added EPUB3 `cover-image` property detection for cover extraction

## 0.8.8 - 2026-03-29

- Replaced extractous with iscc-tika for text/metadata extraction
- Added pre-commit quality gates with prek (formatting, linting, type checking)
- Resolved all zuban type checking errors
- Removed unused explicit `click` dependency (already a transitive dependency of `typer`)

## 0.8.7 - 2026-03-18

- Migrated from Pydantic v1 compatibility layer to native Pydantic v2 API
- Replaced pdftext with pdf-oxide for PDF text extraction (~150x faster)
- Renamed CLI command from `idk` to `iscc-sdk`
- Rounded audio and video duration to integer seconds
- Fixed CLI tests for Typer 0.24.x (error messages moved to stderr, exit code changes)
- Dropped Python 3.10 support, added Python 3.14
- Updated dependencies

## 0.8.6 - 2026-03-03

- Replaced iscc-sum with iscc-lib for Data/Instance/Sum code generation
- Simplified `code_data`, `code_instance`, and `code_sum` using iscc-lib's optimized generators
- Removed iscc-sum dependency
- Migrated from iscc-core to iscc-lib for core ISCC algorithms
- Removed iscc-core from dependencies (blake3, loguru, bitarray, xxhash now explicit)
- Added optional `outpath` parameter to `embed_metadata` for custom output file paths (closes #71)
- Added support for passing `dict` as metadata to `embed_metadata`
- Fixed `code_iscc_mt` to accept `name`, `description`, and `meta` parameters like `code_iscc`
- Migrated from Poetry to uv for dependency management and build backend
- Replaced IPFS binary tool with pure Python CIDv1 computation (no external dependency)
- Fixed installer script referencing removed IPFS tool functions
- Fixed memory usage in IPFS CID computation for large files (stream-hash per chunk)
- Updated CI GitHub Actions to latest versions
- Updated dependencies

## 0.8.5 - 2025-05-12

- Fixed TypeError with Semantic-Code image in granular processing mode.

## 0.8.4 - 2025-05-12

- Fixed issue with passing incompatible options to iscc-sct in experimental mode
- Improved test coverage

## 0.8.3 - 2025-05-12

- Added `code_sum` function for efficient combined Data-Code and Instance-Code generation
- Updated `code_iscc` & `code_meta` to accept custom metadata and optionally skip file metadata
    extraction
- Updated `code_iscc` to compute Data & Instance Code in one go and process data sequentially
- Added separate `code_iscc_mt` for multihreaded processing
- Updated dependencies

## 0.8.2 - 2025-05-02

- Added experimental semantic codes for text and image with optional iscc-sct and iscc-sci packages
- Added `byte_offsets` option to support UTF-8 byte positions in granular simprints
- Improved image transparency handling with more robust conversion logic
- Improved text sanitization
- Updated lock file dependencies

## 0.8.1 - 2025-04-09

- Added `text_keep` option to store extracted text on `IsccMeta.text` property
- Changed PDF text extraction to use pypdfium2 with reading order reconstruction
- Re-added pillow-avif-plugin (Pillow dropped bundling libavif)

## 0.8.0 - 2025-04-02

- Added support for optional ISCC-UNITS and configurable bit size (256-bit).
- Added `extract` command to CLI for text extraction with error handling.
- Added AVIF thumbnail format support and metadata stripping for thumbnails.
- Added robust EPUB cover image extraction with multiple fallback strategies.
- Added fixed layout EPUB detection with namespace support.
- Added container processing support for embedded elements in epub files.
- Added min_image_size option to filter images during EPUB processing.
- Added text sanitization and HTML cleaning for metadata extraction.
- Added image_strip_metadata function for thumbnail generation.
- Added AVIF thumbnail format support.
- Modified code_iscc to conditionally generate meta-code based on create_meta option.
- Updated text features generation to use 256-bit MinHash algorithm.
- Updated video feature extraction with improved hash bits and metadata structure.
- Simplified media processing functions by removing redundant optional parameters.
- Updated dependencies.

## 0.7.0 - 2025-03-23

- Added Python 3.13 support
- Added support for scene based granular video code processing
- Added ffprobe video metadata extraction (duration, fps, width, height, language)
- Added support str and Path objects for all file inpunts
- Added `generator` (name and version of software) to ISCC metadata
- Added optional fallback to ISCC-SUM for unsupported media types
- Handle unsupported SVG files gracefully
- Replaced python-magic with puremagic wrapper for cross-platform compatibility
- Replaced exiv2 CLI tool with native python bindings
- Replaced Tika Java dependency with native extractous package
- Fix bug with thumbnail generation for image modes

## 0.6.2 - 2024-06-13

- Update and relax dependencies
- Update ISO project status

## 0.6.1 - 2024-02-05

- Improved robustness of granular text features
- Added `extract_meta` & `create_thumb` parameters
- Fixed redundant metadata extraction
- Updated dependencies

## 0.6.0 - 2024-01-22

- Add avif and heic image format support
- Update to Exiv2 0.27.7
- Update to Tika 2.9.1
- Update to FFMPEG 6.1
- Add Python 3.12 Support
- Add Pydantic v2 Support
- Dropped Python 3.8 Support

## 0.5.9 - 2023-06-21

- Fix stdout decoding

## 0.5.8 - 2023-06-21

- Add `install` cli command
- Ignore signature files in batch cli command
- Fix encoding of result files
- Updated dependencies

## 0.5.7 - 2023-06-21

- Added parallel processing of ISCC-UNITs
- Handle video thumbnail extraction errors gracefully
- Add basic command line interface for batch processing
- Add option to keep MP7 Video Signature
- Support concurrent audio metadata extraction
- Updated dependencies
- Fixed mkdocstrings

## 0.5.6 - 2023-04-28

- Don´t install tika more than once per session
- Don´t pin poetry build requirement version
- Publish wheels
- Use latest poetry with default settings in CI
- Update dependencies

## 0.5.5 - 2023-03-26

- Switch to official pytaglib distribution
- Update dependencies

## 0.5.4 - 2023-03-15

- Added global `extract_metadata` option
- Removed taglib installation from CI

## 0.5.3 - 2023-03-12

- Update to iscc-core 1.0.3 using binary wheels

## 0.5.2 - 2023-03-11

- Added Python 3.11 support
- Added WavPack support
- Added docx metadata embedding support
- Improved error messages for unsupported mediatypes
- Improved robustness of audio metadata extraction
- Normalize mediatype application/xml to text/xml
- Nomralize mediatype application/vnd.ms-asf video/x-ms-asf
- Normalize mediatype application/vnd.adobe.flash.movie to application/x-shockwave-flash
- Add docx and xlsx extensions to mediatypes
- Updated to iscc-core 1.0.1
- Updated various dependencies

## 0.5.1 - 2022-12-09

- Fix audio title embedding

## 0.5.0 - 2022-12-09

- Add audio cover art thumbnailing
- Integrate EPUB metadata embedding

## 0.4.9 - 2022-12-09

- Add EPUB cover image thumbnail extraction
- Add EPUB metadata embedding
- Retain existing PDF DocInfo metadata when embedding

## 0.4.8 - 2022-12-09

- Separeta ISCC_CORE and ISCC_SDK options
- Document ISCC_SDK option
- Integrate PDF thumbnail extraction

## 0.4.7 - 2022-12-08

- Add metadata embedding support for PDFs
- Add thumbnail support for PDFs
- Improve text metadata extraction mapping
- Improve documentation
- Update dependencies

## 0.4.6 - 2022-11-24

- Add support for earlier Pillow versions
- Add option to configure `image_max_pixels`
- Don´t embed empty titles in images
- Handle extracted metadata gracefully
- Fixed CVE-2007-4559
- Update to iscc-schema v0.4.0
- Update to iscc-core v0.2.12
- Update to tika 2.6.0
- Update dependencies

## 0.4.5 - 2022-07-04

- Update to iscc-schema v0.3.9
- Update to iscc-core v0.2.11
- Fix issue with embedded identifiers
- Add support for granular text features

## 0.4.4 - 2022-06-08

- Update to iscc-schema v0.3.8
- Updated dependencies

## 0.4.3 - 2022-05-08

- Moved changelog to seperate file
- Fixed pillow resampling deprecation warning
- Fixed exiv2 error on older linux versions
- Added support for lazy installation of cli-tools
- Added cleanup of cli-tool archives after installation
- Removed obsolete ffprobe tool
- Updated dependencies

## 0.4.2 - 2022-04-27

- Fix metadata extraction failure with long texts
- Embed Dublin Core metadata in images
- Support path object inputs for text_name_from_uri

## 0.4.1 - 2022-03-26

- Added video thumbnail support
- Added support for IPFS wrap-with-directory

## 0.4.0 - 2022-03-21

- Added Text-Code generation
- Added Video-Code generation
- Added text document metadata extraction
- Added video metadata embedding and extraction
- Added custom exeptions
- Changed embedding to create a new mediafile
- Set filename on IsccMeta
- Set @type on IsccMeta

## 0.3.0 - 2022-03-12

- Added support for Audio-Code with metadata embedding/extraction

## 0.2.0 - 2022-03-10

- Added IPFS support

## 0.1.0 - 2022-03-09

- Initial release with support for ISCC Content-Code Image
