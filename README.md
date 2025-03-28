# LiveKit Agents deployment examples

This repository contains a collection of examples to deploy [LiveKit Agents](https://github.com/livekit/agents) into a production environment for a variety of cloud providers.

For more information about deployment, see the [documentation](https://docs.livekit.io/agents/deployment)

## Dockerfile examples

The following examples include a bare-bones agent and Dockerfile which is suitable for running in any containerized environment.

| Platform | Description |
|----------|-------------|
| [Python](/python-agent-example-app) | `Dockerfile` example for Python |
| [Node.js](/node-agent-example-docker) | `Dockerfile` example for Node.js |

## Provider templates

The following examples include a template configuration or manifest file for each provider. You should use these files in conjunction with the Dockerfile examples above.

| Provider | Description |
|----------|-------------|
| [AWS ECS](/aws-ecs) | `cloudformation.yaml` example for ECS |
| [Cerebrium](/cerebrium) | `cerebrium.toml` example for [Cerebrium](https://cerebrium.ai) |
| [Fly.io](/fly.io) | `fly.toml` example for [Fly.io](https://fly.io) |
| [Kubernetes](/kubernetes) | Example manifest file for any Kubernetes environment |
| [Render.com](/render.com) | `render.yaml` example for [Render](https://render.com) |

## Missing a provider?

Feel free to open a PR or issue to add instructions for your favorite provider!