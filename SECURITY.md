# Security and Disclosure Policy

## Repository Purpose

This repository is a sanitized professional case study of an independently developed prediction-market execution and quantitative research platform.

It is not the production trading repository and is not intended to contain live credentials, private account information, complete proprietary strategy logic, or confidential third-party information.

## Sensitive Information Policy

The following material must never be committed to this repository:

* API keys, access tokens, passwords, or private keys
* `.env` files or unredacted configuration files
* Authentication certificates or signing credentials
* Kalshi account identifiers or private account information
* Bank, brokerage, payment, or personal financial information
* Raw production order, execution, position, or account records
* Live trading logs containing sensitive identifiers
* Personally identifiable information
* Confidential legal, client, employer, or third-party information
* Materials related to confidential litigation consulting
* Complete proprietary production strategy logic
* Private infrastructure addresses or server credentials
* Data or source code that Ryan Eblen does not have the right to distribute

## Public Case-Study Standards

Material may be included only after it has been reviewed and sanitized.

Approved public content may include:

* High-level system architecture
* Sanitized and simplified Python examples
* Synthetic or anonymized sample data
* Aggregate research counts and results
* Selected charts and tables
* Testing and validation examples
* General debugging methodology
* Non-sensitive research findings
* Documented limitations
* Educational examples that do not enable access to a live account or private system

All example files should be understandable independently of the private production platform.

## Credential Handling

Credentials must be stored outside the repository using secure environment variables, credential-management tools, or another appropriate private storage method.

Placeholder values may be used in examples, such as:

```text
KALSHI_API_KEY=YOUR_API_KEY_HERE
KALSHI_PRIVATE_KEY_PATH=/secure/path/to/private-key
```

Placeholders must never contain fragments of real credentials.

## Accidental Disclosure Response

If a credential, token, password, private key, or other secret is committed:

1. Revoke or rotate the exposed credential immediately.
2. Remove the sensitive material from the repository.
3. Review the repository history and affected files.
4. Inspect related systems for unauthorized access.
5. Replace the credential wherever it was used.
6. Document the incident and corrective action privately.

Deleting the visible file alone should not be treated as sufficient because earlier versions may remain in repository history.

## Data Sanitization

Before publishing a dataset, log excerpt, screenshot, or output file:

* Remove names, account identifiers, order identifiers, and transaction identifiers.
* Remove exact balances, private positions, and private trading history.
* Remove credentials, hostnames, file paths, and infrastructure details.
* Replace production values with synthetic or aggregated examples where practical.
* Confirm that the material cannot be combined with another public source to reveal private information.
* Confirm that publication does not violate an agreement, duty, or third-party right.

## Code Sanitization

Before publishing code:

* Remove credentials and hard-coded secrets.
* Remove private endpoints and infrastructure details.
* Remove account-specific identifiers.
* Remove proprietary strategy thresholds when disclosure is unnecessary.
* Replace private dependencies with documented interfaces or simplified examples.
* Confirm that the code does not expose an exploitable production-system weakness.
* Confirm that Ryan Eblen has the right to publish all included material.

## Reporting a Security Concern

Do not open a public GitHub issue containing sensitive information.

Security concerns relating to this case-study repository may be reported privately to:

**Ryan Eblen**
[ryan.eblen.work@gmail.com](mailto:ryan.eblen.work@gmail.com)

Include a concise description of the concern and the affected file or section. Do not include active credentials or unnecessary private information in the initial message.

## Scope

This policy applies to the public case-study repository and its supporting documentation.

It does not provide access to the private production platform, trading accounts, live infrastructure, complete source code, or confidential research materials.

## Current Status

This repository is currently under private construction and review. Files will be considered for public release only after security, confidentiality, ownership, and presentation checks are complete.
