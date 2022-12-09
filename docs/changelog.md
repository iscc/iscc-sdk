## Changelog

## 0.5.1 - Unreleased
- Fix audio title embedding

## 0.5.0 - 2022-12-09
- Add audio cover art thumbnailing
- Integrate EPUB metadata embedding


## 0.4.9 - 2022-12-09
- Add EPUB cover image thumbnail extraction
- Add EPUB metadata embedding
- Retain existing PDF DocInfo metadata when embedding

### 0.4.8 - 2022-12-09
- Separeta ISCC_CORE and ISCC_SDK options
- Document ISCC_SDK option
- Integrate PDF thumbnail extraction

### 0.4.7 - 2022-12-08
- Add metadata embedding support for PDFs
- Add thumbnail support for PDFs
- Improve text metadata extraction mapping
- Improve documentation
- Update dependencies

### 0.4.6 - 2022-11-24
- Add support for earlier Pillow versions
- Add option to configure `image_max_pixels`
- Don´t embed empty titles in images
- Handle extracted metadata gracefully
- Fixed CVE-2007-4559
- Update to iscc-schema v0.4.0
- Update to iscc-core v0.2.12
- Update to tika 2.6.0
- Update dependencies

### 0.4.5 - 2022-07-04
- Update to iscc-schema v0.3.9
- Update to iscc-core v0.2.11
- Fix issue with embedded identifiers
- Add support for granular text features

### 0.4.4 - 2022-06-08
- Update to iscc-schema v0.3.8
- Updated dependencies

### 0.4.3 - 2022-05-08
- Moved changelog to seperate file
- Fixed pillow resampling deprecation warning
- Fixed exiv2 error on older linux versions
- Added support for lazy installation of cli-tools
- Added cleanup of cli-tool archives after installation
- Removed obsolete ffprobe tool
- Updated dependencies

### 0.4.2 - 2022-04-27
- Fix metadata extraction failure with long texts
- Embed Dublin Core metadata in images
- Support path object inputs for text_name_from_uri

### 0.4.1 - 2022-03-26
- Added video thumbnail support
- Added support for IPFS wrap-with-directory

### 0.4.0 - 2022-03-21
- Added Text-Code generation
- Added Video-Code generation
- Added text document metadata extraction
- Added video metadata embedding and extraction
- Added custom exeptions
- Changed embedding to create a new mediafile
- Set filename on IsccMeta
- Set @type on IsccMeta

### 0.3.0 - 2022-03-12
- Added support for Audio-Code with metadata embedding/extraction

### 0.2.0 - 2022-03-10
- Added IPFS support

### 0.1.0 - 22022-03-09
- Initial release with support for ISCC Content-Code Image
