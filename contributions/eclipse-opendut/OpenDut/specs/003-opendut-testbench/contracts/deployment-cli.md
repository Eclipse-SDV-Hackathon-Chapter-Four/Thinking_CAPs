# Deployment contract
OpenDut/scripts/opendut_testbench.py prepare|up|status|down --state PRIVATE_PATH --output NEW_PATH
prepare retrieves digest-checked CLEO, builds pinned peer image, creates private PKI.
up preflights overlap and resources, creates owned network/containers, enrolls two peers,
deploys one cluster, and exports redacted interface/status results. Bounded command deadlines.
status reads actual peer/cluster/interface state. down undeploys/removes exact owned resources.
Exit0 assertions passed; exit1 failed; exit2 dependency blocked. Existing evidence is immutable.
Private state includes generated UUIDs, setup files, PKI and owned resource names.
