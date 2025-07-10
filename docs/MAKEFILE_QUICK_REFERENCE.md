# Makefile Quick Reference

## 🚀 Quick Start Commands

| Command | Description |
|---------|-------------|
| `make help` | Show all available commands |
| `make setup` | Complete development setup |
| `make quick-start` | Quick start with auto-reload |
| `make dev` | Start development environment |
| `make staging` | Start staging environment |
| `make prod` | Start production environment |

## 🐳 Docker Commands

| Command | Description |
|---------|-------------|
| `make docker-up` | Start all Docker services |
| `make docker-down` | Stop all Docker services |
| `make docker-logs` | Show Docker logs |
| `make docker-clean` | Clean Docker containers and images |
| `make docker-build` | Build Docker image |
| `make restart` | Restart all services |
| `make rebuild` | Rebuild and restart services |

## 🗄️ Database Commands

| Command | Description |
|---------|-------------|
| `make db-upgrade` | Apply database migrations |
| `make db-current` | Show current migration |
| `make db-history` | Show migration history |
| `make db-migrate` | Create new migration |
| `make db-reset` | Reset database (⚠️ destructive) |
| `make backup` | Create database backup |
| `make restore` | Restore database from backup |

## 🧪 Testing & Quality

| Command | Description |
|---------|-------------|
| `make test` | Run all tests |
| `make test-cov` | Run tests with coverage |
| `make lint` | Run linting |
| `make lint-fix` | Fix linting issues |
| `make format` | Format code |
| `make check` | Run all checks (lint, type, test) |
| `make type-check` | Run type checking |

## 📊 Monitoring & Status

| Command | Description |
|---------|-------------|
| `make status` | Show service status |
| `make health` | Check service health |
| `make monitor` | Monitor system resources |
| `make logs` | Show application logs |

## 🛠️ Development Tools

| Command | Description |
|---------|-------------|
| `make install` | Install Python dependencies |
| `make install-dev` | Install development dependencies |
| `make clean` | Clean cache and temporary files |
| `make shell` | Start Python shell |
| `make docs` | Generate API documentation |
| `make open-docs` | Open API docs in browser |

## 🚀 Deployment

| Command | Description |
|---------|-------------|
| `make deploy-dev` | Deploy to development |
| `make deploy-staging` | Deploy to staging |
| `make deploy-prod` | Deploy to production (⚠️ confirmation) |

## 📝 Common Workflows

### New Developer Setup
```bash
make setup
```

### Daily Development
```bash
make docker-up
make db-upgrade
make run-reload
```

### Before Committing
```bash
make format
make check
```

### Troubleshooting
```bash
make health          # Check service status
make docker-logs     # View logs
make restart         # Restart services
```

### Database Management
```bash
make db-current      # Check migration status
make db-upgrade      # Apply migrations
make backup          # Create backup
```

## ⚠️ Destructive Commands

These commands will delete data and require confirmation:

- `make db-reset` - Resets entire database
- `make deploy-prod` - Deploys to production
- `make restore` - Restores database from backup
- `make docker-clean` - Removes all Docker containers and images

## 🎨 Color Coding

- 🔵 **Blue**: Information messages
- 🟢 **Green**: Success messages
- 🟡 **Yellow**: Warning messages
- 🔴 **Red**: Error messages

## 📚 Full Documentation

For complete documentation, see:
- [README.md](README.md) - Main project documentation
- [MIGRATIONS.md](MIGRATIONS.md) - Database migration guide
- `make help` - Interactive command list 