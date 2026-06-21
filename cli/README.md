# sda-cli

CLI tool for Spec-Driven Architecture (SDA). See the [project README](../readme.md) for full documentation.

## Quick start

```bash
pip install sda-cli
sda init                 # scaffold a new SDA project
sda capture "API latency spike"
sda check                # validate ADRs, services, refs, and classification labels
sda index                # generate the knowledge-graph index
sda graph static         # single-file offline interactive graph
sda graph view           # self-contained dockview viewer (graph + docs + diagrams + search)
sda graph serve          # local read-only server for the viewer
sda build                # regenerate index + graph in one step
sda status
```
