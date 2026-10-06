# F003 entities
Deployment: owned run ID, project/network labels, release pins, management subnet, private
state path, peer/device/cluster UUIDs, image IDs and lifecycle preparing/online/deployed/removed.
Peer: distinct name/identity, own management IP, DUT veth/IP, own config/setup/IPC state.
Cluster: exactly two DUT devices, leader A, actual GRE/bridge membership, rollout status.
Evidence: redacted CLEO results, routes/interfaces, selected traffic summary, receiver requests,
negative/recovery timestamps, cleanup verdict. Keys/setup strings never belong to evidence.
Validation: reject address overlap, unknown owned resources and version/digest mismatch;
failed readiness is blocked, not online. No automatic unrelated-resource cleanup.
