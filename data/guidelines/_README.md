# Guideline corpus

The retrieval index is intentionally small and hardcoded so every verifier check is reproducible without a network call.

Chunks are defined as Python constants in `src/maitri/rag/corpus.py`, currently ten in total. Each chunk has a stable identifier, a source label, a title, a year, a section, and the verbatim text. The verifier cites these identifiers when accepting or rejecting a claim.

Sources cited in the chunks:

- World Health Organization recommendations on antenatal care for a positive pregnancy experience, 2016
- World Health Organization recommendations on antepartum hemorrhage, 2018
- World Health Organization hemoglobin concentrations for the diagnosis of anaemia, 2011
- World Health Organization recommendations for routine antenatal care, 2018
- FIGO initiative on pre eclampsia, 2019
- Indian Ministry of Health Reproductive Maternal Newborn Child and Adolescent Health programme, 2013

No PDFs are committed. The chunks contain only the small excerpts the demo cites. A judge can read every chunk by opening the corpus file.

For a future scale up the loader would pull versioned source URLs into a LanceDB index, but that is not in the current MVP scope.
