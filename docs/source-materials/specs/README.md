# FUNCTIONcalled() Repo Scaffold

This repository implements the FUNCTIONcalled() naming and metadata conventions.

## Structure

- **standards/**: specifications and schemas
- **tools/**: validators and registry builder scripts
- **examples/**: canonical metadata examples
- **registry/**: generated catalogues
- **core**, **interface**, **logic**, **application**: base layers for your project
- **archive/**: place for frozen history or old versions

## Usage

1. Install Python dependencies (e.g. `jsonschema`) if necessary.
2. Run `make validate` to validate all metadata files.
3. Run `make registry` to build the registry into `registry/registry.json`.
4. Run `make hook-install` to install the pre-commit hook that validates metadata on commit.

See `standards/FUNCTIONcalled_Spec_v1.0.md` for the full specification and `standards/FUNCTIONcalled_Metadata_Sidecar.v1.1.schema.json` for the metadata schema.
