# Changelog

## [X.X.X] - 202X-XX-XX

## [0.3.0] - 2025-09-21

### Added

- Storing platform from Discord's `activity.platform` field (or a special case for Steam Deck). Defaults to `pc` if not specified. Existing activity will have `pc` set as their platform.

### Fixed

- Activities for games utilizing Discord rich presence (e.g. L.A. Noire) not being recorded due to Discord not reporting an activity start time.
- Activities not being recorded while playing music using a music player that supports Discord activities.

## [0.2.0] - 2025-04-23

### Added

- Parse game names out of activity details reported by "Discord Status" Decky plugin on Steam Deck

## [0.1.0] - 2025-01-18

- Initial release
