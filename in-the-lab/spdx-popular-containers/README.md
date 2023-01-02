# SPDX SBOMs Created from Popular Containers

This folder contains SPDX SBOMs created "in the lab," that is, generated via an SBOM-generating tool for the purpose of creating a large SPDX SBOM dataset. These 3,000+ SBOMs were created with four different tools (`syft`, `trivy`, `bom`, and `tern`) from a list of 1,000 popular containers.

Relevant files:

`create_top_docker_image_list.py` - A script for generating a list of of 1,000 popular container images from Docker Hub.

`most-popular-dockerhub-images.csv` - CSV of popular container images from Docker Hub used to create this SBOM dataset.

`generate_sbom_dataset.py` - A script for generating the SBOM dataset.

`data` - Folder containing these SPDX SBOMs. Files use this naming convention: `spdx-{generation-tool}-{image_name}-{image_digest}.json`, e.g. `spdx-bom-airbyte_bootloader-sha256:2a8e24d79fe158517e492ebfec01797c78cf7008523c3304f933323ea6d97479.json`