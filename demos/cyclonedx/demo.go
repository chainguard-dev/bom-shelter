package main

import (
    "flag"
	"fmt"
    "os"
    "path/filepath"

	cdx "github.com/CycloneDX/cyclonedx-go"
)

// checkComponentsForPackageVersion determines whether a particular SBOM contains a component
// with a particular name and version
// TODO: Consider rewriting signature to have an error returned too
func checkComponentsForPackageVersion(path, pkg, ver string) (purl string) {

    // open sbom file
	bomFile, err := os.Open(path)
    if err != nil {
		panic(err)
	}
	defer bomFile.Close()

	// decode the sbom
	bom := new(cdx.BOM)
	decoder := cdx.NewBOMDecoder(bomFile, cdx.BOMFileFormatJSON)
	if err = decoder.Decode(bom); err != nil {
		panic(err)
	}

    // check all components for a component with a particular name and version
    for _, cmp := range *bom.Components {
        // TODO: Consider using regular expression to check for component names that
        // contain the user-entered package name. This is because the messines of
        // SBOMs.
        if cmp.Name == pkg && cmp.Version == ver {
            return bom.Metadata.Component.PackageURL
        }
    }
    return ""

}

// checkComponentsForPackage returns the BOM's PURL and a slice of
// all identified versions of the specified package
// TODO: Consider rewriting signature to have an error returned too
func checkComponentsForPackage(path, pkg string) (purl string, versions []string) {

    // open sbom file
    bomFile, err := os.Open(path)
    if err != nil {
        panic(err)
    }
    defer bomFile.Close()

    // decode the sbom
    bom := new(cdx.BOM)
    decoder := cdx.NewBOMDecoder(bomFile, cdx.BOMFileFormatJSON)
    if err = decoder.Decode(bom); err != nil {
        panic(err)
    }

    // check all components for a component with a particular name
    // and create slice of versions found
    for _, cmp := range *bom.Components {
        // TODO: Consider using regular expression to check for component names that
        // contain the user-entered package name. This is because the messines of
        // SBOMs.
        if cmp.Name == pkg {
            versions = append(versions, cmp.Version)
        }
    }
    return bom.Metadata.Component.PackageURL, versions

}

func main() {

    // parse flags
    var pkg = flag.String("pkg", "", "Specify package")
    // TODO: Consider adding checking for range of versions
    // TODO: Consider adding checking for non-contiguous range of versions
    var ver = flag.String("ver", "", "Specify version")
    flag.Parse()
    if *pkg == "" {
        panic("Need to specify a package name.")
    }
    fmt.Printf("\nSearching for package: %s\n", *pkg)
    if *ver != "" {
        fmt.Printf("Searching for version: %s", *ver)
    }
    // identify all sample SBOMs
    bomFilePaths, err := filepath.Glob("./sample-sboms/*.json")
    if err != nil {
        panic(err)
    }
    // loop over sboms, checking for specified component
    var matchingSboms []string
    matchingSbomsMap := make(map[string][]string)
    for _, bomFilePath := range bomFilePaths {
        var purl string
        var versions []string
        if *ver != "" {
            purl = checkComponentsForPackageVersion(bomFilePath, *pkg, *ver)
        } else {
            purl, versions = checkComponentsForPackage(bomFilePath, *pkg)
        }
        if *ver != "" && purl != "" {
            matchingSboms = append(matchingSboms, purl)
        } else if len(versions) != 0 {
            matchingSbomsMap[purl] = versions
        }
    }
    // print out all matching sboms
    fmt.Printf("\n\nThese SBOMs contain the specified package:\n")
    if *ver != "" {
        for _, sbom := range matchingSboms {
            fmt.Println(sbom)
        }
    } else {
        for k, v := range matchingSbomsMap {
            fmt.Println(k, v)
        }
    }
    fmt.Println() // final break
}
