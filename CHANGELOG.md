# Changelog

All notable changes to the Varsom Alerts integration will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [1.0.0] - 2025-12-15

### Added
- Initial release of Varsom Alerts integration
- Single sensor per county with all alerts in attributes
- Support for landslide warnings from NVE API
- Support for flood warnings from NVE API
- Option to monitor both warning types simultaneously
- County selection from all Norwegian counties
- Bilingual support (Norwegian and English)
- Config flow for easy setup through UI
- Rich alert data including:
  - Activity levels (1-4: green, yellow, orange, red)
  - Danger types and warning text
  - Affected municipalities
  - Valid from/to timestamps
  - Advice and consequence information
  - Direct links to Varsom.no with interactive maps
- Automatic icon updates based on alert level
- 30-minute update interval for fresh data

### Technical Details
- Uses DataUpdateCoordinator pattern for efficient API polling
- Implements modern Home Assistant best practices
- Single sensor design (not multiple _2, _3, _4 sensors like older integrations)
- All alerts accessible via structured attributes array
- Proper error handling and logging

### Documentation
- Comprehensive README with usage examples
- Template sensor examples for municipality filtering
- Automation examples for notifications
- Lovelace card configuration examples

[1.0.0]: https://github.com/jm-cook/varsom/releases/tag/v1.0.0
