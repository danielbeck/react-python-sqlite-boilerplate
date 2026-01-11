# Configuration Guide

This boilerplate uses `config.json` to manage deployment settings, allowing you to deploy multiple apps to the same server with different subdirectories.

## Configuration File

The `config.json` file in the root directory controls:
- Deployment server and credentials
- Base directory and subdirectory paths
- Production domain
 - `backendRoot` (optional): absolute server document-root prefix used to build the deployed backend path

### Default Configuration

```json
{
  "deployment": {
    "host": "home557350892.1and1-data.host",
    "user": "u79456718",
    "baseDir": "nb/",
    "subDir": "",
    "backendRoot": "/kunden/homepages/29/d557350892/htdocs/"
  },
  "production": {
    "domain": "https://nosebeep.com"
  }
}
```

### Configuration Options

#### deployment.host
The server hostname for SSH/rsync deployment.

#### deployment.user
The SSH username for server access.

#### deployment.baseDir
The base directory on your server where apps are deployed (e.g., `nb/`).
- Must end with `/`
- This is the root directory that contains all your apps

#### deployment.subDir (optional)
A subdirectory within baseDir for this specific app.
- Leave empty (`""`) or omit to deploy directly to baseDir
- Add a subdirectory (e.g., `"myapp/"`) to deploy to `baseDir/subDir`
- Must end with `/` if specified

#### production.domain
The full production domain URL (e.g., `https://nosebeep.com`).

## Deployment Scenarios

### Scenario 1: Single App (Direct to Base)

Deploy directly to `nb/`:

```json
{
  "deployment": {
    "baseDir": "nb/",
    "subDir": ""
  }
}
```

Result:
- Files deployed to: `nb/backend/`, `nb/frontend/`, `nb/index.html`, etc.
- Accessible at: `https://nosebeep.com/`
- API endpoint: `https://nosebeep.com/backend/api.cgi/`

### Scenario 2: Multiple Apps (Subdirectories)

**App 1** (`config.json`):
```json
{
  "deployment": {
    "baseDir": "nb/",
    "subDir": "game1/"
  }
}
```

Result:
- Files deployed to: `nb/game1/backend/`, `nb/game1/frontend/`, etc.
- Accessible at: `https://nosebeep.com/game1/`
- API endpoint: `https://nosebeep.com/game1/backend/api.cgi/`

**App 2** (separate project with different `config.json`):
```json
{
  "deployment": {
    "baseDir": "nb/",
    "subDir": "game2/"
  }
}
```

Result:
- Files deployed to: `nb/game2/backend/`, `nb/game2/frontend/`, etc.
- Accessible at: `https://nosebeep.com/game2/`
- API endpoint: `https://nosebeep.com/game2/backend/api.cgi/`

## How It Works

### Backend Configuration

1. **deploy.sh**: Reads `config.json` and constructs the deployment path
2. **api.cgi**: The deployed `api.cgi` contains a deploy-time placeholder (`__DEPLOY_BACKEND_DIR__`) which `deploy.sh` replaces with the computed absolute backend directory. This avoids requiring `config.json` on the host for shared-host compatibility.
3. **config_helper.py**: A local helper that can parse `config.json` when running locally; not required on the server when using deploy-time templating.

### Frontend Configuration

1. **generate-config.js**: Reads `config.json` and generates `frontend/src/config.js`
2. **vite.config.js**: Reads `config.json` to set the base URL for asset paths
3. **api.js**: Imports generated config to construct correct API URLs
4. **npm run build**: Automatically runs `generate-config.js` before building

## Usage

### Initial Setup

1. Copy this boilerplate to a new directory for each app
2. Edit `config.json` with your deployment settings
3. Set `subDir` to a unique value for each app

### Development

No configuration changes needed - development always uses local proxies.

```bash
cd frontend
npm run dev
```

### Building for Production

The build process automatically generates the correct configuration:

```bash
cd frontend
npm run build
```

Or manually generate the config:

```bash
cd frontend
npm run generate-config
```

### Deployment

Simply run the deployment script:

```bash
./deploy.sh
```

The script reads `config.json` and deploys to the configured location.

## Troubleshooting

### Config Not Found

If `config.json` is missing:
- **deploy.sh**: Will exit with an error
- **api.cgi**: Falls back to hardcoded path `/kunden/homepages/29/d557350892/htdocs/nb/backend`
- **Frontend build**: Uses default base path `/`

### Wrong Paths After Deployment

1. Verify `config.json` has correct `baseDir` and `subDir`
2. Rebuild the frontend: `cd frontend && npm run build`
3. Redeploy: `./deploy.sh`

### API Not Found (404)

Check that:
1. `subDir` in `config.json` matches your deployment
2. Frontend was built after updating `config.json`
3. Backend `api.cgi` and `config_helper.py` were deployed together

## Best Practices

1. **Keep config.json in version control** - But consider using environment-specific configs
2. **Use consistent subdirectory naming** - Use lowercase, hyphens, and trailing slashes
3. **Test locally first** - Always test with `npm run dev` before deploying
4. **Rebuild after config changes** - Always rebuild frontend after changing `config.json`
5. **One config per app** - Each app should have its own `config.json` with unique `subDir`
