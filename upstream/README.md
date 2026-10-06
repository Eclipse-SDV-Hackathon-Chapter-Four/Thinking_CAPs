# Upstream Dependencies

Git submodules for upstream Eclipse projects.

## Submodules
```bash
# Add submodules
git submodule add https://github.com/eclipse-opensovd/opensovd-core.git opensovd-core
git submodule add https://github.com/eclipse-score/inc_diagnostics.git inc_diagnostics
git submodule add https://github.com/eclipse-score/inc_someip_gateway.git inc_someip_gateway
git submodule add https://github.com/eclipse-score/score.git score

# Initialize
git submodule update --init --recursive
```

## Projects
- `opensovd-core/` - OpenSOVD implementation
- `inc_diagnostics/` - Diagnostic libraries
- `inc_someip_gateway/` - SOME/IP gateway (Teammate)
- `score/` - S-CORE base libraries
