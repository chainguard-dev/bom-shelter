"""Generate dataset of container sboms with several tools.

Requires: grype, syft, docker, tern, and bom
"""

import csv
import json
import logging
import os
import subprocess

logging.basicConfig(level=logging.INFO)


def generate_syft_sbom(image, digest, output_filename):
    """Create and store a syft SBOM.

    Args:
        image (str) - image name, e.g. alpine
        digest (str) - the digest of the image, e.g. sha256:8914eb54f968791faf6a8638949e480fef81e697984fba772b3976835194c6d4
        output_filename (str) - path to a location for storing output

    Returns:
        Null
    """
    result = subprocess.run(
        [
            "syft",
            "packages",
            "-o",
            "spdx-json",
            "--file",
            output_filename,
            f"registry:{image}@{digest}",
        ],
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        check=True,
    )


def generate_trivy_sbom(image, digest, output_filename):
    """Create and store a trivy SBOM.

    Args:
        image (str) - image name, e.g. alpine
        digest (str) - the digest of the image, e.g. sha256:8914eb54f968791faf6a8638949e480fef81e697984fba772b3976835194c6d4
        output_filename (str) - path to a location for storing output

    Returns:
        Null
    """
    result = subprocess.run(
        [
            "trivy",
            "image",
            "--format",
            "spdx-json",
            "--output",
            output_filename,
            f"{image}@{digest}",
        ],
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        check=True,
    )


def generate_tern_sbom(image, digest, output_filename):
    """Create and store a tern SBOM.

    Args:
        image (str) - image name, e.g. alpine
        digest (str) - the digest of the image, e.g. sha256:8914eb54f968791faf6a8638949e480fef81e697984fba772b3976835194c6d4
        output_filename (str) - path to a location for storing output

    Returns:
        Null
    """
    # because of piping, use shell=True approach
    cmd = f"docker run --rm ternd report -f spdxjson -i {image}@{digest} > {output_filename}"
    print(cmd)
    ps = subprocess.Popen(
        cmd, shell=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT
    )
    print(ps)


def generate_bom_sbom(image, tag, output_filename):
    """Create and store a bom SBOM.

    Args:
        image (str) - image name, e.g. alpine
        tag (str) - the tag of the image, e.g. latest
        output_filename (str) - path to a location for storing output

    Returns:
        Null
    """
    result = subprocess.run(
        [
            "bom",
            "generate",
            "--format",
            "json",
            "--output",
            output_filename,
            "--image",
            # bom does not accept digests (yet)
            f"{image}:{tag}",
        ],
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        check=True,
    )


def generate_sboms(tool, image, tag, digest, output_filename):
    """Create and store SBOMs.

    Args:
        tool (str) - which sbom generation tool to be used
        tag (str) - image name, e.g. latest
        image (str) - image name, e.g. alpine
        digest (str) - the digest of the image, e.g. sha256:8914eb54f968791faf6a8638949e480fef81e697984fba772b3976835194c6d4
        output_file (str) - path to a location for storing output

    Returns:
        Null
    """
    if tool == "syft":
        generate_syft_sbom(image, digest, output_filename)
    elif tool == "trivy":
        generate_trivy_sbom(image, digest, output_filename)
    elif tool == "tern":
        generate_tern_sbom(image, digest, output_filename)
    elif tool == "bom":
        generate_bom_sbom(image, tag, output_filename)


def get_image_digest_and_tag(image):
    """Retrieve digest and tag of an image.

    Args:
        image (str) - image name, e.g. alpine

    Returns:
        digest (str) - digest of an image
        tag (str) - the tag used
    """
    # assume latest tag is available
    tag = "latest"

    result = subprocess.run(
        [
            "crane",
            "ls",
            image,
        ],
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        check=True,
    )
    tags = result.stdout.decode("utf-8")
    # if latest tag not available, grab tag
    # at end of crane ls command
    if "latest" not in tags:
        tag = tags.split("\n")[-2]

    result = subprocess.run(
        [
            "crane",
            "digest",
            f"{image}:{tag}",
        ],
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        check=True,
    )
    digest = result.stdout.decode("utf-8").strip("\n")

    return digest, tag


if __name__ == "__main__":

    sbom_format = "spdx"
    TOOLS = ["tern", "syft", "trivy", "bom"]

    # read in list of most popular dockerhub images
    images = []
    with open("most-popular-dockerhub-images.csv") as csvfile:
        r = csv.reader(csvfile)
        r.__next__()  # skip first row, which is a header
        for row in r:
            images.append(row[0])

    for image in images[::-1]:
        # outer try catches an error with getting digest and tag
        try: 
            digest, tag = get_image_digest_and_tag(image)
            
            for tool in TOOLS:

                # inner try catches error with generating an SBOM for a
                # particular tool
                try:
                    output_filename = (
                        f"data/{sbom_format}-{tool}-{image.replace('/', '_')}-{digest}.json"
                    )

                    # skip if this file already exists
                    if not os.path.exists(output_filename):
                        logging.info(f"Analyzing {image} with {tool}")
                        generate_sboms(tool, image, tag, digest, output_filename)
                    else:
                        logging.info(f"Skipping: {output_filename} already exists")
                except subprocess.CalledProcessError as e:
                    logging.error(f"Analyzing {image} with {tool}: {e}")
        
        except subprocess.CalledProcessError as e:
            logging.error(f"Error using crane with {image}: {e}")

