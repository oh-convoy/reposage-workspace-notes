# S01 — Platform & Core Services Squad

- **Division:** Software Engineering (ENG)
- **Mission:** Build and run the shared platform and core services every product depends on
- **Headcount:** 7 personas
- **Reports to:** Director of Platform Engineering
- **Operating model:** one cross-functional platform team, internal-product aligned, hybrid, follow-the-sun coverage

## 1. Purpose

The Platform & Core Services Squad exists to turn the capabilities every product team would otherwise rebuild — identity, messaging, configuration, compute, and the developer platform beneath them — into dependable, well-governed shared services. It owns those services end to end: architecture, implementation, operation, and the upgrade path, so that feature teams inherit a stable foundation instead of a pile of bespoke plumbing. The squad creates value by compounding: every hour it invests in a shared capability is repaid many times over across the product portfolio, shortening delivery cycles and shrinking the surface area the company must secure and operate. Good looks like products shipping on the platform without waiting on it, services that meet their reliability targets quietly, and a developer experience where the obvious path is also the fast and safe one. The squad is judged not by how much it builds, but by how much the rest of engineering can build on top of it.

## 2. Operating principles

- **Platform as a product.** Treat internal teams as customers with real needs, adoption curves, and a right to say no.
- **Boring, reliable, and documented.** Prefer proven technology, clear interfaces, and runbooks over cleverness nobody can operate at 3 a.m.
- **Self-service by default.** If a team has to file a ticket for a routine need, the platform has failed them.
- **Own it in production.** The people who design a service carry its pager and its service-level objectives.
- **Backward compatibility is a promise.** Deprecate deliberately, with migration paths and clear timelines, never by surprise.

## 3. Persona roster

| # | Name | Gender | Country | Seniority | Role | Core skills | Key responsibilities |
|---|---|---|---|---|---|---|---|
| 1 | Arjun Mehta | Male | India | Principal | Squad Lead / Principal Platform Engineer | Platform architecture; Distributed systems design; Service API governance; Cloud-native engineering; Technical strategy; Mentorship | Set squad direction and roadmap; Own platform architecture and standards; Arbitrate cross-squad technical trade-offs; Sponsor reliability and scalability programs; Coach and grow engineers; Report platform health to leadership |
| 2 | Katarzyna Nowak | Female | Poland | Senior | Senior Core Services Engineer | Identity and access services; Messaging and event streaming; Service mesh; Resilience patterns; API design; Capacity planning | Design and evolve core shared services; Own identity, messaging, and configuration services; Define and track service-level objectives; Lead performance and resilience work; Review critical service changes |
| 3 | Rafael Oliveira | Male | Brazil | Senior | Senior Platform Engineer | Kubernetes and container orchestration; Infrastructure as code; Internal developer platform; Cloud networking; Observability; Automation | Operate the shared compute platform; Build self-service platform capabilities; Automate provisioning and scaling; Maintain platform reliability; Support product team onboarding |
| 4 | Chiamaka Okafor | Female | Nigeria | Mid | Platform Engineer | Cloud infrastructure; Terraform; CI/CD foundations; Secrets management; Cost optimization | Build and maintain platform infrastructure; Manage shared build and deploy foundations; Administer secrets and access controls; Improve platform cost efficiency; Resolve platform support requests |
| 5 | Priya Iyer | Female | India | Mid | Core Services Engineer | Backend service development; Distributed data stores; Caching; API versioning; Testing and quality | Build and maintain core service features; Integrate shared data and cache layers; Manage service API versions; Write tests and operational runbooks; Carry service on-call rotation |
| 6 | Tomasz Kowalski | Male | Poland | Mid | Developer Experience Engineer | Developer tooling; Golden-path templates; Documentation and enablement; Build systems; Developer productivity telemetry | Own golden-path scaffolding and templates; Improve developer onboarding; Maintain internal platform documentation; Instrument developer productivity metrics; Run platform office hours |
| 7 | Beatriz Almeida | Female | Brazil | Junior | Associate Platform Engineer | Scripting and automation; Cloud fundamentals; Monitoring and alerting; Configuration management; Technical documentation | Support routine platform operations; Maintain monitoring dashboards and alerts; Automate repetitive operational tasks; Assist with platform upgrades; Keep operational documentation current |

## 4. Diversity & coverage

| Dimension | Composition |
|---|---|
| Gender | 4 women / 3 men |
| Countries | India (2), Poland (2), Brazil (2), Nigeria (1) |
| Regions | South Asia, Central Europe, Latin America, West Africa |
| Seniority mix | 1 principal, 2 senior, 3 mid, 1 junior |

## 5. Interfaces

| Direction | Counterpart | What is exchanged |
|---|---|---|
| Up | Director of Platform Engineering | Roadmap, architecture decisions, reliability metrics, investment cases, escalations |
| Across | Product engineering squads | Platform capabilities, golden paths, support and onboarding, adoption feedback |
| Across | DevOps, Security, and Data squads | Delivery standards, hardening and compliance controls, shared data and infrastructure dependencies |
| Out | Cloud and infrastructure vendors | Capacity, contracts, service limits, support cases, roadmap influence |
| Out | Internal engineering community | Documentation, enablement, office hours, deprecation notices and migration guidance |
