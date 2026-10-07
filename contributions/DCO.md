# Jefferson Nascimento — reusable DCO reference

Prepared at Jefferson's request on 2026-10-07. Reuse this identity and sign-off
format for contributions covered by the [Developer Certificate of Origin 1.1](dco/DCO-1.1.txt).
The complete certificate is retained verbatim from the
[Eclipse Foundation's published copy](https://www.eclipse.org/legal/dco/dco.html).

| Field | Value |
| --- | --- |
| Author | Jefferson Nascimento |
| Email | jnsagai@gmail.com |
| Eclipse account | jnascimento6p0 |

Reusable commit trailer:

```text
Signed-off-by: Jefferson Nascimento <jnsagai@gmail.com>
```

For each contribution, Jefferson certifies that the DCO applies to the actual
work before this trailer is attached. Keep the certification and exact revision
in that contribution's records. This reusable reference supplies the certificate
and signing identity; contribution-specific certification remains with Jefferson.

After reviewing the staged changes and certifying them, create the commit in the
receiving project's checkout with this identity:

```bash
git -c user.name='Jefferson Nascimento' \
    -c user.email='jnsagai@gmail.com' \
    commit --signoff --author='Jefferson Nascimento <jnsagai@gmail.com>'
```

Confirm the resulting author, committer and trailer:

```bash
git show --no-patch --format=full HEAD
```

Git's [`--signoff` option](https://git-scm.com/docs/git-commit#Documentation/git-commit.txt---signoff)
adds the committer's `Signed-off-by` trailer. Use the receiving project's commit
message format and contribution process along with this reference.

Assisted-by: OpenAI Codex (reference preparation)
