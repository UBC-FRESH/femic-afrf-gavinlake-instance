# Metadata

Provenance ledgers for the Gavin Lake instance.

| File | Purpose |
| --- | --- |
| `legacy_archive.sha256` | SHA-256 of the source archive |
| `legacy_archive_inventory.csv` | Every archive entry and its disposition |
| `public_copy_inventory.csv` | The public copy's file hashes and sizes |

Rules:

- The archive hash is immutable. A new archive gets a new note.
- The inventory records omitted files with a reason.
- A derived file records its transformation in the provenance note.
- The metadata is updated in the same change set as the data it describes.
