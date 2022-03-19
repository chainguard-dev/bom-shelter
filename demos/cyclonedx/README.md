# Demo of Multi-SBOM CycloneDX Parsing

Demonstrate ability of searching through SBOM for components
with a particular name and, if the user specifies, a version.

## Example Usage

Find all SBOMs containing a package named log4j and
returned the associated versions.

`$ go run demo.go --pkg log4j`

Find all SBOMs containing a package named log4j with a
version 1.9.0

`$ go run demo.go --pkg log4j --ver 2.14.1`

Find all SBOMs containing a package named alpine and
returned the associated versions.

`$ go run demo.go --pkg alpine`

Find all SBOMs containing a package named alpine with
a version 1.9.0

`$ go run demo.go --pkg alpine --ver 1.9.0`