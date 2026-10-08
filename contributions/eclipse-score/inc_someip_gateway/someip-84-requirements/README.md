# SOME/IP #84: requirement mapping revision

The complete implementation now has a native proposal hierarchy: one stakeholder
need, one feature requirement and eight SOCom component requirements. Each
component requirement links to implementation, the native design guide and
specific passing test cases. [Requirement mapping](REQUIREMENT-MAPPING.md) lists
all links and verification limits. [License audit](LICENSE-HEADERS.md) covers all
tracked native code/build files and preserves existing attribution.

Native revision: `3a3a0d9ee0e502df99dc52279cdd2e536d361c0a`; baseline `f8a196c3b16d5172d898394ab99b0ed81346d63d`. Both commits in
[the prepared DCO mail series](submission-with-dco.patch) are signed off under
the user's continuing #84 authorization. [Full patch](submission.patch),
[incremental mapping patch](requirement-mapping.patch), changed source snapshots,
native policies and raw measurements are included. Earlier implementation
measurements and their original seal remain in `../someip-84-full/`.

Current checks: all 722 SOCom cases pass; 177 carry targeted partial requirement
links. All eight new component requirements have source and test links, with no
broken test references. The repository-wide graph still includes the eight
unrelated TC8 requirements; local SOCom tests do not verify them. Native full
build, formatting, copyright/REUSE/pre-commit and docs/trace checks pass.
SOCom Clang-Tidy passed for this exact revision.

Requirements are tagged `proposal` and marked `invalid` because the pinned
metamodel has no draft requirement status. This is an explicit unaccepted state,
not a declaration that tests failed. Link presence does not establish complete
verification. Committer requirement/API acceptance, exact-revision human AI and
IP review, remaining CI and the previous four QEMU capture permission failures
still prevent a merge-ready claim. No PR was created or published.

