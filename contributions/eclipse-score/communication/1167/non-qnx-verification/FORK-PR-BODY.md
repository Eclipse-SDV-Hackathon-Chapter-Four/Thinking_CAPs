Runs the unchanged project Host workflows against the proposed merge source for eclipse-score/communication#1335.

Subject: `0b48ccc1d195297ab9c5e7e19f5b2250fd2f43fe`, with upstream base `c77751819b8885a902540dbef7f0fe25cf85d51c` and native PR head `a8e81c795b7f45e663d608a33c5e358cfd765ea9`. The diff against this fork's main contains only the original nine contribution files.

This verification PR supplies the pull_request event required by the native linter hold-the-line policy. It is for GCC15/module-integration, ASan/UBSan/leak, TSan, clang-tidy, clippy and Ruff evidence. QNX is excluded by the contributor's instruction; no test-qnx label is requested. Native upstream review and check approval remain separate.

The verified source and workflow files are unchanged. This is a verification branch for evidence collection; the upstream contribution remains PR #1335.
