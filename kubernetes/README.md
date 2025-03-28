# Kubernetes Deployment for LiveKit Agents

This directory provides an example Kubernetes deployment manifest for LiveKit Agents, making it easy to deploy and scale your agents on any Kubernetes cluster.

You also need a working agents app and Dockerfile. See the examples for [Python](/python-agent-example-app) or [Node.js](/node-agent-example-docker) if necessary.

## Deployment Steps

The basic steps are as follows:

1. Review and modify the `agent-manifest.yaml` file to suit your needs:
   - Update the environment variables with your LiveKit API key, secret, and other configurations.
   - Adjust resource limits and requests as needed for your workload.

2. Apply the manifest to your Kubernetes cluster:
   ```bash
   kubectl apply -f agent-manifest.yaml
   ```

See the [Kubernetes documentation](https://kubernetes.io/docs/home/) for more information on managing your Kubernetes cluster.