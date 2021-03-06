## Changelog

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
