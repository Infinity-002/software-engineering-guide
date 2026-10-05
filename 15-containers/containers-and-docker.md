# Containers, images, and local environments

Relay works on one developer's machine but fails elsewhere because runtime versions, libraries, filesystem paths, and startup assumptions differ. A container image packages an execution environment and startup contract. A running container is still a process, usually sharing the host kernel with other containers.

## Isolation and accounting are separate mechanisms

Linux namespaces give processes different views of resources such as process IDs, mounts, network interfaces, and host names. Cgroups account for and limit resources such as CPU and memory. Filesystem layering supplies a packaged root filesystem. These mechanisms cooperate; no single one is “the container.”

Containers are not full virtual machines with independent guest kernels in the ordinary Linux model. On desktop platforms a Linux VM may host Linux containers, which explains another networking/filesystem boundary. Containers improve isolation and repeatability, but kernel vulnerabilities, privileged settings, host mounts, and broad capabilities can weaken the boundary.

## Images are immutable inputs; containers have runtime state

An image consists of filesystem layers and metadata. A container adds a writable layer and runtime configuration. Deleting/replacing the container can discard that writable layer. Put durable database data in correctly managed volumes or external storage, and back it up. A volume is persistence across container replacement, not a disaster-recovery strategy.

A registry stores/distributes images. Tags are names that may move; digests identify content. Promote a tested image digest through environments rather than rebuilding “the same” source separately for production. Record the source revision and build provenance for diagnosis.

## A focused Dockerfile

This example assumes a Node project with a lockfile, a build script producing `dist/server.js`, and runtime dependencies declared correctly. The base version is illustrative; choose a supported, patched version and pin a digest in a real release process.

```dockerfile
FROM node:22-bookworm-slim AS build
WORKDIR /app
COPY package*.json ./
RUN npm ci
COPY . .
RUN npm run build
RUN npm prune --omit=dev

FROM node:22-bookworm-slim AS runtime
ENV NODE_ENV=production
WORKDIR /app
COPY --from=build --chown=node:node /app/package*.json ./
COPY --from=build --chown=node:node /app/node_modules ./node_modules
COPY --from=build --chown=node:node /app/dist ./dist
USER node
EXPOSE 3000
CMD ["node", "dist/server.js"]
```

Copying dependency manifests before source allows dependency-layer reuse when only source changes. A multi-stage build keeps build tools and source out of the final stage when unnecessary. A `.dockerignore` should exclude local `node_modules`, secrets, VCS data, and generated clutter. Removing a secret in a later layer does not reliably remove it from earlier image history; use build-secret mechanisms rather than copying credentials.

`EXPOSE` documents a port; it does not publish it to the host. The process must listen on an appropriate container interface, commonly `0.0.0.0`, not only its loopback address. The exec-form `CMD` avoids an extra shell that can interfere with signal delivery. If the application launches children, process reaping and init behavior need attention.

## Networking and Compose

Inside a container, `localhost` normally refers to that container's network namespace. The PostgreSQL container is reached through its service name on a shared network, not the API container's localhost. Publishing a port creates host reachability under the runtime's configuration; do not publish database ports broadly just because local debugging is convenient.

Docker Compose describes cooperating local services, networks, volumes, and configuration. It is useful for reproducible API/PostgreSQL/Redis labs. Startup ordering alone is not readiness: a database process can exist before it accepts queries. Health conditions and application connection retry behavior should handle initialization without infinite waiting.

Separate host bind mounts from managed volumes. Bind mounts are convenient for source development but depend on host paths and permissions. A production image should not accidentally rely on a developer's mounted directory. Resource limits make failures reproducible: test memory pressure and CPU throttling rather than assuming host capacity.

## Failure modes and judgment

A container is killed with no JavaScript exception: inspect memory limits and kernel/runtime events. A process handles `SIGTERM` but is killed before draining: align shutdown budgets with the platform grace period. A database loses data after `compose down` with volume removal: distinguish container lifecycle from explicitly destructive volume operations.

Why not put every dependency in one container? Separate lifecycles and resource ownership are easier when each service has its own process/container boundary. Why not use containers for every tiny script? They add build, registry, patching, and runtime overhead; reproducibility can sometimes be achieved with a simpler environment. Use them when packaging and operational consistency justify the cost.

## Exercises

1. **Predict:** Why does `localhost:5432` fail from the API container while PostgreSQL is healthy in another container?
2. **Implementation:** Containerize Project 1, use a persistent database volume, and verify a container replacement preserves data.
3. **Debug:** Compare managed heap, process RSS, and cgroup memory limit during a forced-memory experiment.
4. **Design:** Specify image provenance, secret injection, health checks, and graceful shutdown for Relay.
5. **Interview:** Explain namespaces, cgroups, images, and volumes without calling a container a small VM.

<details><summary>Hints</summary>

Network namespaces and service discovery define addresses. Memory outside the managed heap still counts toward limits. Persistent storage needs independent backup/restore and explicit ownership of destructive lifecycle commands.

</details>

## Further reading and connections

[Docker images and containers](https://docs.docker.com/get-started/docker-concepts/the-basics/what-is-a-container/), [Dockerfile reference](https://docs.docker.com/reference/dockerfile/), and [Compose documentation](https://docs.docker.com/compose/). Connect to [Linux processes](../02-operating-systems-linux/linux-debugging.md), [CI/CD](../18-ci-cd/safe-delivery.md), and [Kubernetes](../17-kubernetes/kubernetes-model.md).
