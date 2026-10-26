Data Publication Boundary
=========================

This is a public model instance. The boundary below follows the MKRF precedent:
publish the open model, keep private financial detail out.

Published surfaces
------------------

- the sanitized legacy H matrix under ``data/legacy_gavinlake/tracks/H/``;
- the legacy spatial inventory and topology under
  ``data/legacy_gavinlake/spatial/``;
- the legacy pin and scenario scripts under ``data/legacy_gavinlake/``;
- the derived fragment tables;
- the ws4 translation files, schedules, and evidence;
- documentation, ADRs, and provenance ledgers.

Excluded surfaces
-----------------

- raw cost, revenue, contractor-rate, and cash-flow workbooks;
- private financial overlays and their derived tables;
- credentials, tokens, and private keys;
- machine-specific home directories and user profile paths; and
- raw transcripts and unpublished third-party documents.

Sanitization
------------

The legacy text files were normalized to LF. Home-directory comments were
replaced with ``[legacy-path]``. The machine-specific build, log, and report
scripts that are not needed for the ws4 benchmark were left out of the public
copy. Their archive entries and dispositions are recorded in
``metadata/legacy_archive_inventory.csv``.

Audit
-----

Run the workflow validator before each push:

.. code-block:: bash

   python scripts/check_workflow.py

It rejects control characters, personal paths, and secret-shaped strings in
tracked text files. The green dashboard runs the same validator.

Source terms
------------

The legacy model data and AFRF spatial inventory retain their source terms.
The repository's MIT license covers the original code and documentation, not a
relicensing of the legacy data. See
``data/legacy_gavinlake/PROVENANCE.md``.

If a future use needs a stricter redistribution boundary, record it here and in
the provenance note before adding the material.
