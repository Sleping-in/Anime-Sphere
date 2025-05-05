# AnimeSphere - Advanced Anime Management for Kodi

A comprehensive Kodi plugin for managing and streaming anime content.

## Features

- Integration with MyAnimeList API
- Advanced anime search and filtering
- Watch history tracking
- Custom playlists and favorites
- High-quality streaming sources

## Setup Instructions

### 1. Get MyAnimeList API Credentials

1. Go to [MyAnimeList Developer Console](https://myanimelist.net/apiconfig/references/authorization)
2. Create a new application:
   - Application Type: OAuth2
   - Name: AnimeSphere
   - Description: Kodi plugin for anime management
   - Redirect URI: `urn:ietf:wg:oauth:2.0:oob`
   - Enable PKCE: Yes
3. Copy your Client ID and Client Secret

### 2. Install the Plugin

1. Download the latest release from [GitHub Releases](https://github.com/windsurf/plugin.video.animesphere/releases)
2. In Kodi:
   - Go to Add-ons
   - Click the "Download" icon
   - Click "Install from zip file"
   - Select the downloaded zip file

### 3. Configure the Plugin

1. Go to Add-ons > Video Add-ons > AnimeSphere
2. Click the settings icon (gear)
3. Enter your MyAnimeList credentials:
   - Client ID: Paste your Client ID
   - Client Secret: Paste your Client Secret
4. Click "Connect to MyAnimeList"
5. Follow the browser instructions to authorize the application

### 4. Using the Plugin

1. Launch AnimeSphere from your Kodi video add-ons
2. Browse anime categories
3. Search for specific anime
4. Add anime to your watchlist
5. Track your progress

## Troubleshooting

### Common Issues

1. **Authentication Failed**
   - Verify your Client ID and Client Secret are correct
   - Make sure PKCE is enabled in your MAL application settings
   - Try disconnecting and reconnecting

2. **No Results Found**
   - Check your internet connection
   - Verify the plugin is properly authorized
   - Try clearing the cache

### Resetting Authentication

1. Go to Add-on settings
2. Click "Disconnect from MyAnimeList"
3. Reconnect following the setup instructions

## Contributing

1. Fork the repository
2. Create your feature branch
3. Commit your changes
4. Push to the branch
5. Create a Pull Request

## License

This plugin is released under the GPL v3 license.
