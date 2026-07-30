# Public-release checklist

## Completed in the current cleanup

- [x] Remove the committed Python virtual environment.
- [x] Remove vendored Obsidian plugin code and local workspace state.
- [x] Remove local AI-tool plans and operating-system metadata.
- [x] Remove plaintext credentials from the current tree.
- [x] Replace downloaded third-party papers with citations to original sources.
- [x] Simplify repository metadata and remove generated/local tooling.
- [x] Document the scope and current reproducibility boundary.

## Release blockers

- [ ] Rotate the exposed campus and lab credentials immediately.
- [ ] Rewrite all branches and tags to remove the credentials from Git history,
  then force-push in coordination with every collaborator.
- [ ] Ask owners of forks and old clones to delete or re-clone them; assume old
  credentials remain recoverable from caches.
- [ ] Confirm that the testbed photographs may be published and that visible
  lab screens/topology labels disclose nothing restricted.
- [ ] Confirm the copyright holder and choose a license for documentation,
  scripts, and original images.
- [ ] Add author and affiliation information, then create `CITATION.cff`.

## Reproducibility work still required

- [ ] Publish or link the deployment repository and sanitized configurations.
- [ ] Record the exact OAI commit and public patch series.
- [ ] Publish a hardware/software manifest and machine-readable experiment data.
- [ ] Repeat comparative runs under a frozen protocol and report distributions.
- [ ] Attach packet-path evidence to wireless-backhaul claims.
- [ ] Replace user-confirmed peak values with repeatable evidence bundles.
- [ ] Verify all paper-ready claims and citations with the research supervisor.

## Final GitHub settings

- [ ] Add a concise repository description and topics.
- [ ] Enable private vulnerability reporting and secret scanning.
- [ ] Protect `main` against accidental force-pushes and deletions.
- [ ] Review the repository from a fresh, unauthenticated clone.
- [ ] Create a signed release only after the history rewrite and license choice.
