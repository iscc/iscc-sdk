## Changelog

## 0.8.4 - Unreleased


## 0.8.3 - 2025-05-12

- Added `code_sum` function for efficient combined Data-Code and Instance-Code generation
- Updated `code_iscc` & `code_meta` to accept custom metadata and optionally skip file metadata extraction
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
