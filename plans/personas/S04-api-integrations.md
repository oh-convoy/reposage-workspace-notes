# S04 — API & Integrations Squad

- **Division:** Software Engineering (ENG)
- **Mission:** Design, expose, and integrate the public and partner APIs
- **Headcount:** 6 personas
- **Reports to:** VP of Engineering

## 1. Purpose

The API & Integrations Squad owns the company's contract surface: the public and
partner APIs through which external systems and third parties interact with our
products. It defines API standards, lifecycle, and versioning, and builds the
integration layer that connects internal services to outside platforms. The
squad is accountable for the reliability, consistency, and developer experience
of every API the company exposes.

## 2. Personas

| # | Name | Gender | Country | Role | Skills | Responsibilities |
|---|---|---|---|---|---|---|
| 1 | Katharina Braun | Female | Germany | Principal API Architect (Squad Lead) | API strategy; distributed systems; platform architecture; standards and governance; technical leadership; stakeholder alignment | Set the API architecture and roadmap; own API standards and lifecycle policy; lead and mentor the squad; align with platform and product strategy; represent the squad to leadership |
| 2 | Rafael Domingo | Male | Philippines | Senior API Engineer | API design; service implementation; authentication and authorization; performance tuning; observability | Design and build public APIs; implement auth and rate limiting; harden services for scale; support API observability; review peer designs |
| 3 | Camila Fernández | Female | Argentina | Senior Integration Engineer | Third-party integrations; event-driven messaging; data mapping and transformation; partner onboarding; error handling and resilience | Build and maintain partner integrations; own connector and webhook pipelines; onboard external partners; ensure integration reliability |
| 4 | Jonas Keller | Male | Germany | Senior Developer Experience Engineer | API documentation; SDKs and client libraries; developer portals; sandbox tooling; developer advocacy | Own the developer portal and docs; build and maintain SDKs; run sandbox and self-service tooling; improve developer onboarding |
| 5 | Brian Otieno | Male | Kenya | API Engineer | REST and GraphQL implementation; schema modeling; automated testing; versioning and deprecation | Implement API endpoints and schemas; write contract and integration tests; manage versioning and deprecation; support incident resolution |
| 6 | Alexis Bautista | Non-binary | Philippines | API Engineer | Service integration; middleware and gateways; CI/CD for services; monitoring and alerting | Implement integrations and gateway routes; maintain service pipelines; monitor API health; document interfaces and changes |

## 3. Diversity

| Dimension | Composition |
|---|---|
| Gender | 2F / 3M / 1NB |
| Countries | Germany, Philippines, Argentina, Kenya |
| Regions | Europe, Southeast Asia, South America, Africa |
| Seniority mix | 1 principal, 3 senior, 2 mid |

## 4. Interfaces

| Direction | Counterpart | What is exchanged |
|---|---|---|
| Up | VP of Engineering | API strategy, roadmap, standards, and delivery status |
| Across | Platform & Core Services, Web Frontend, Mobile Engineering, Security Engineering | Service contracts, schemas, integration requirements, and security constraints |
| Out | External developers and partner organizations | Public and partner APIs, SDKs, documentation, and support |
