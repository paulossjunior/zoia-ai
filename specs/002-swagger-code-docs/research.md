# Research: Swagger and Code Documentation

## Decision: Use existing interactive API documentation support

**Rationale**: The service already uses a web framework that exposes interactive API documentation and generated API schema from route and model metadata. Enhancing route descriptions, schema examples, tags, and response definitions keeps documentation close to the actual API contract.

**Alternatives considered**: A separate static documentation site was rejected because it would duplicate the API contract and increase drift risk. A standalone hand-written OpenAPI file was rejected for the same reason.

## Decision: Add concise docstrings at architectural boundaries

**Rationale**: The constitution emphasizes domain/application/infrastructure separation and handler extensibility. Docstrings on public classes/functions at those boundaries help maintainers understand responsibilities without noisy line-by-line comments.

**Alternatives considered**: Commenting every function line-by-line was rejected because it obscures code. Generating full API reference docs was deferred because the user asked to document code, not build a documentation portal.

## Decision: Validate documentation through tests

**Rationale**: Documentation must remain aligned with runtime behavior. Tests should verify the docs page is reachable, the generated schema includes `POST /commands`, examples and responses are present, and source modules include boundary docstrings.

**Alternatives considered**: Manual README-only validation was rejected because it cannot prevent future documentation regressions.

## Decision: Keep infrastructure details out of external documentation

**Rationale**: The constitution requires external contracts to be explicit while keeping infrastructure replaceable. Public API documentation should describe command submission behavior and asynchronous processing outcomes, not require clients to know Redis or repository internals.

**Alternatives considered**: Documenting Redis queue details in the external API contract was rejected because it leaks implementation detail and weakens replaceability.
