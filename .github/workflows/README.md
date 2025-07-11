# GitHub Actions Workflows

This directory contains GitHub Actions workflows for the OCR Identity REST API project.

## Workflows Overview

### 1. CI/CD Pipeline (`ci-cd.yml`)

**Triggers:** Push to main/develop, Pull requests to main/develop, Release published

**Jobs:**
- **Test & Quality Checks**: Runs linting, type checking, and tests with PostgreSQL and Redis services
- **Security Scan**: Runs Bandit and Safety security checks
- **Docker Build**: Builds development and production Docker images
- **Deploy**: Deploys to production on main branch pushes

**Features:**
- Multi-environment testing (Python 3.11, 3.12)
- Code coverage reporting
- Docker image building and testing
- Automated deployment to production

### 2. Manual Deploy (`deploy.yml`)

**Triggers:** Manual workflow dispatch

**Purpose:** Manual deployment to staging or production environments

**Inputs:**
- `environment`: Choose between staging or production
- `version`: Docker image version to deploy (default: latest)

**Features:**
- Manual deployment control
- Environment-specific deployment
- Health checks after deployment

### 3. Release (`release.yml`)

**Triggers:** Release published

**Jobs:**
- **Build Release Assets**: Creates Python packages and archives
- **Docker Release**: Builds and pushes versioned Docker images

**Features:**
- Automatic release asset creation
- Multi-platform Docker images (amd64, arm64)
- Semantic versioning support

### 4. Security Scan (`security.yml`)

**Triggers:** Weekly schedule (Mondays), Manual dispatch, Push to main/develop

**Jobs:**
- **Security Analysis**: Bandit, Safety, and pip-audit scans
- **Dependency Scan**: Snyk vulnerability scanning
- **Container Scan**: Trivy container vulnerability scanning

**Features:**
- Comprehensive security scanning
- Scheduled security checks
- GitHub Security tab integration

### 5. Documentation (`docs.yml`)

**Triggers:** Changes to docs/ or README.md, Manual dispatch

**Jobs:**
- **Build Documentation**: Builds MkDocs documentation
- **Check Links**: Validates documentation links
- **Deploy Docs**: Deploys to GitHub Pages (main branch only)

**Features:**
- Automatic documentation building
- Link validation
- GitHub Pages deployment

## Required Secrets

### Repository Secrets

```bash
# Docker Hub
DOCKER_USERNAME=your-docker-username
DOCKER_PASSWORD=your-docker-password

# Production Environment
PRODUCTION_HOST=your-production-server-ip
PRODUCTION_USERNAME=your-production-username
PRODUCTION_SSH_KEY=your-production-ssh-private-key
PRODUCTION_URL=https://your-production-domain.com

# Staging Environment
STAGING_HOST=your-staging-server-ip
STAGING_USERNAME=your-staging-username
STAGING_SSH_KEY=your-staging-ssh-private-key
STAGING_URL=https://your-staging-domain.com

# Security Tools
SNYK_TOKEN=your-snyk-token

# Notifications (Optional)
SLACK_WEBHOOK_URL=your-slack-webhook-url
```

## Environment Setup

### GitHub Environments

Create the following environments in your GitHub repository:

1. **staging**
   - Protection rules: Required reviewers
   - Deployment branches: develop

2. **production**
   - Protection rules: Required reviewers
   - Deployment branches: main

## Usage Examples

### Manual Deployment

1. Go to Actions tab in GitHub
2. Select "Manual Deploy" workflow
3. Click "Run workflow"
4. Choose environment (staging/production)
5. Optionally specify Docker image version
6. Click "Run workflow"

### Creating a Release

1. Create a new release in GitHub
2. Tag with semantic version (e.g., v2.0.0)
3. Publish the release
4. Workflows will automatically:
   - Build release assets
   - Create Docker images with version tags
   - Push to Docker Hub

### Security Monitoring

- Weekly automated security scans
- Manual security scans via workflow dispatch
- Security reports available as artifacts
- Integration with GitHub Security tab

## Workflow Optimization

### Caching

The workflows use GitHub Actions cache for:
- Poetry dependencies
- Docker layer caching
- Build artifacts

### Parallel Execution

Jobs are designed to run in parallel where possible:
- Test and Security jobs run simultaneously
- Documentation jobs run independently
- Release jobs run after CI/CD completion

### Resource Optimization

- Uses Ubuntu latest runners
- Efficient Docker layer caching
- Minimal dependency installation
- Parallel job execution

## Troubleshooting

### Common Issues

1. **Docker Build Failures**
   - Check Dockerfile syntax
   - Verify build context
   - Check for missing dependencies

2. **Test Failures**
   - Verify database connection
   - Check environment variables
   - Review test dependencies

3. **Deployment Failures**
   - Verify SSH key permissions
   - Check server connectivity
   - Review deployment scripts

4. **Security Scan Failures**
   - Review security findings
   - Update vulnerable dependencies
   - Check scan configuration

### Debugging

1. **Enable Debug Logging**
   ```bash
   # Add to workflow
   env:
     ACTIONS_STEP_DEBUG: true
   ```

2. **Check Artifacts**
   - Download workflow artifacts
   - Review log files
   - Check security reports

3. **Local Testing**
   - Use `act` for local workflow testing
   - Test Docker builds locally
   - Verify environment setup

## Best Practices

1. **Branch Protection**
   - Require status checks to pass
   - Enforce review requirements
   - Protect main branch

2. **Secret Management**
   - Use GitHub secrets for sensitive data
   - Rotate secrets regularly
   - Use environment-specific secrets

3. **Workflow Maintenance**
   - Keep workflows up to date
   - Monitor workflow performance
   - Review and update dependencies

4. **Security**
   - Regular security scans
   - Dependency updates
   - Container vulnerability scanning

## Contributing

When adding new workflows or modifying existing ones:

1. Follow the established patterns
2. Add appropriate documentation
3. Test workflows thoroughly
4. Update this README
5. Consider security implications 