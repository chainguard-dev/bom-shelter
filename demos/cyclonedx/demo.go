package main

import (
    "flag"
	"fmt"
    "os"
    "path/filepath"

	cdx "github.com/CycloneDX/cyclonedx-go"
)

// checkComponents determines whether a particular SBOM contains a component
// with a particular name and version
func checkComponents(path, pkg, ver string) {

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
            fmt.Println(bom.Metadata.Component.PackageURL)
            break
        }
    }

}

func main() {

    // parse flags
    var pkg = flag.String("pkg", "", "Specify package")
    var ver = flag.String("ver", "", "Specify version")
    flag.Parse()
    if *pkg == "" {
        panic("Need to specify a package name.")
    }
    if *ver == "" {
        panic("Need to specify a version number.")
    }
    fmt.Printf("\nSearching for package: %s\n", *pkg)
    fmt.Printf("Searching for version: %s\n\n", *ver)

    // identify all sample SBOMs
    bomFilePaths, err := filepath.Glob("./sample-sboms/*.json")
    if err != nil {
        panic(err)
    }
    fmt.Println("These SBOMs contain the specified package:")
    // loop over sboms, checking for specified component
    for _, bomFilePath := range bomFilePaths {
	   checkComponents(bomFilePath, *pkg, *ver)
    }
    fmt.Println()
}
