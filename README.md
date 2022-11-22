## PR-vigilante

### Description:
Python application to track down and automatically mark pull request messages  
in Slack channel as approved after reviewing associated pull request in GitHub.  
If multiple PRs are found in a single message it will be marked as approved after  
all the pull requests will be reviewed/approved.  

Application is built around [GHAPI](https://ghapi.fast.ai) and [Python Slack SDK](https://slack.dev/python-slack-sdk/)

### Requited Slack token permissions:
`channels:history`, `groups:history`, `im:history`, `mpim:history`,  
`reactions:read` and `reactions:write` are required scopes for Slack API token

### Things to consider:
1. Slack API rate limit tiers - based on methods used, e.g.  
    https://api.slack.com/methods/conversations.history and  
    https://api.slack.com/methods/reactions.add etc
2. GitHub API rate limits

### Application structure:
```
├── clients <- External clients 
│   ├── __init__.py
│   ├── git.py
│   └── slack.py
├── helpers <- Helper classes and functions
│   ├── __init__.py
│   ├── git.py
│   ├── helpers.py
│   └── slack.py
├── main.py <- Main entrypoint 
├── utils   <- External clients' utilities
│   ├── __init__.py
│   ├── git.py
│   └── slack.py
```

### Build and publish:
```commandline
docker buildx build --platform linux/amd64 -t slack-tools:<tag> . 
docker tag slack-tools:<tag> <repo>:<tag>
docker push <repo>:<tag>
```
change Helm Chart `version`, `image.repository` and `appVersion` accordingly

### Apply & Delete:
```
helmfile apply --interactive --kube-context <context> (uses current context by default)
helmfile destroy
```

### TODO:
1. ~~Support lookup of PRs inside of slack threads~~
