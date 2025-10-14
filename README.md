# Invoice Billing System

## Installations
### Clone the repository
```
# Using ssh
git clone git@github.com:Reyozaki/invoice-biling-system.git
```

- **Python version>3.12**
- **Install Docker**
- **uv package manager**

### Setup Environment
```
# install dependencies for development
uv sync --dev

# install dependencies for deployment or production
uv sync
```

Edit the .env files with your values.
```
# copy .env.example from root and docker directories and name them .env
cp .env.example .env docker/.env.example docker/.env
```

### Start the server (bash terminal)
```
# start docker container with postgres and backend server
bash start.sh
```
