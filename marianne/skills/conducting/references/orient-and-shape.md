# Orient and Shape

Use this before committing the orchestra or whenever the world model is no
longer trustworthy.

## Build the world model

Establish:

1. **Composer** — desired end state, intended meaning, non-negotiables,
   acceptance concerns, and longer-term direction.
2. **Venue libretto** — standards, conventions, existing design, safety rules,
   ownership boundaries, and local ways of working.
3. **Reality** — current artifacts, runtime state, technical constraints,
   available capabilities, active performances, scarce resources, and known
   failures.
4. **Future** — what later work this performance should enable, what contracts
   it must preserve, and which short-term choices would make the future harder.

Learn through direct reading, reversible probes, composer dialogue,
reconnaissance musicians, domain experts, and concise briefs. Technical fluency
lets the conductor ask better questions and judge reports; it is not authority
to perform the specialist's work.

If vision and libretto appear to conflict, recover intended meaning rather than
obeying the first literal formulation. Ask the composer when available. If not,
continue reversible work, preserve existing design, record assumptions, and
hold any irreversible choice that could damage the long-term vision.

## Shape the performance graph

For every end state, record:

- outcome and relation to the vision;
- owner, supporters, and decision authority;
- inputs, where context lands, and missing information;
- dependencies and timing;
- artifacts and behavioral evidence required;
- shared files, services, interfaces, compute, credentials, rate limits, and
  human attention;
- downstream consumers and future contracts;
- effects on every other end state.

Classify each interaction:

- **beneficial** — one result strengthens or validates another;
- **neutral** — coexistence is safe and requires no coordination;
- **dangerous** — collision, contradiction, resource contention, hidden order,
  or incompatible assumptions require direction.

Sequence, isolate, merge, or commission an integration owner for dangerous
interactions. Do not infer safety because individual jobs are green.

## Cast for the end state

Choose the smallest orchestra that covers the required expertise, independence,
and throughput. Assign authorship and validation to different musicians when
bias or correctness matters. Add principals, alignment analysts, adversarial
users, dogfooders, or co-conductors when they improve trajectory visibility or
management scale.

One musician with one strong proof may be enough. A fleet is justified by the
work, not by the availability of agents.
