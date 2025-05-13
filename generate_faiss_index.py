from langchain_community.vectorstores import FAISS
from langchain_openai import OpenAIEmbeddings
from langchain.docstore.document import Document
import os

from dotenv import load_dotenv
load_dotenv()

docs = [
    # Tech
    Document(page_content="Developed a machine learning pipeline that reduced prediction error by 25%.", metadata={"industry": "tech"}),
    Document(page_content="Led a team of 5 developers to launch a SaaS product used by 10,000+ users.", metadata={"industry": "tech"}),
    Document(page_content="Migrated legacy systems to AWS, improving infrastructure reliability by 40%.", metadata={"industry": "tech"}),
    Document(page_content="Implemented CI/CD pipelines that reduced deployment time by 80%.", metadata={"industry": "tech"}),
    Document(page_content="Built a RESTful API for internal tools, improving data access for analysts.", metadata={"industry": "tech"}),
    Document(page_content="Refactored legacy codebase, reducing technical debt by 60%.", metadata={"industry": "tech"}),

    # Marketing
    Document(page_content="Designed and executed email campaigns, increasing open rates by 32%.", metadata={"industry": "marketing"}),
    Document(page_content="Managed $500K ad budget, generating a 4.5x ROAS.", metadata={"industry": "marketing"}),
    Document(page_content="Rebranded product line, leading to 20% YoY growth.", metadata={"industry": "marketing"}),
    Document(page_content="Led SEO strategy that improved organic traffic by 75% in six months.", metadata={"industry": "marketing"}),
    Document(page_content="Created influencer partnerships that resulted in a 3x engagement lift.", metadata={"industry": "marketing"}),
    Document(page_content="Optimized Google Ads campaigns, reducing CPA by 35%.", metadata={"industry": "marketing"}),

    # Finance
    Document(page_content="Analyzed quarterly performance reports, identifying cost savings of $200K.", metadata={"industry": "finance"}),
    Document(page_content="Improved financial forecasting accuracy by implementing variance analysis.", metadata={"industry": "finance"}),
    Document(page_content="Audited internal controls, reducing compliance risks by 60%.", metadata={"industry": "finance"}),
    Document(page_content="Created financial models to evaluate M&A opportunities.", metadata={"industry": "finance"}),
    Document(page_content="Automated monthly reporting process, saving 40 staff hours per cycle.", metadata={"industry": "finance"}),
    Document(page_content="Collaborated with CFO on annual budget planning and forecasting.", metadata={"industry": "finance"}),

    # Healthcare
    Document(page_content="Administered medication and monitored recovery of post-op patients.", metadata={"industry": "healthcare"}),
    Document(page_content="Implemented patient tracking system, reducing missed follow-ups by 35%.", metadata={"industry": "healthcare"}),
    Document(page_content="Trained new nurses in hospital protocols and patient care documentation.", metadata={"industry": "healthcare"}),
    Document(page_content="Reduced hospital readmissions by 15% through proactive care coordination.", metadata={"industry": "healthcare"}),
    Document(page_content="Led infection control audits, improving compliance to 98%.", metadata={"industry": "healthcare"}),
    Document(page_content="Developed telehealth procedures adopted by over 300 patients.", metadata={"industry": "healthcare"}),

    # Education
    Document(page_content="Developed interdisciplinary curriculum increasing student test scores by 18%.", metadata={"industry": "education"}),
    Document(page_content="Incorporated interactive tech tools that boosted classroom engagement by 40%.", metadata={"industry": "education"}),
    Document(page_content="Organized and led faculty development workshops for 50+ educators.", metadata={"industry": "education"}),
    Document(page_content="Established a peer mentoring program improving student retention by 22%.", metadata={"industry": "education"}),
    Document(page_content="Adapted remote learning tools during COVID-19, ensuring 100% attendance.", metadata={"industry": "education"}),
    Document(page_content="Published academic paper on instructional design used by national network.", metadata={"industry": "education"}),

    # Tech
    Document(page_content="Engineered a scalable microservices architecture reducing downtime by 90%.", metadata={"industry": "tech"}),
    Document(page_content="Deployed a containerized solution with Docker and Kubernetes.", metadata={"industry": "tech"}),
    Document(page_content="Monitored system performance using Prometheus and Grafana dashboards.", metadata={"industry": "tech"}),
    Document(page_content="Created automated test suites that reduced regression bugs by 50%.", metadata={"industry": "tech"}),
    Document(page_content="Developed an internal tool in React, saving 200+ dev hours per quarter.", metadata={"industry": "tech"}),

    # Marketing
    Document(page_content="Ran A/B tests on landing pages, improving conversion rate by 28%.", metadata={"industry": "marketing"}),
    Document(page_content="Created quarterly marketing reports to track campaign effectiveness.", metadata={"industry": "marketing"}),
    Document(page_content="Increased Instagram following by 80% through daily engagement strategy.", metadata={"industry": "marketing"}),
    Document(page_content="Developed a brand style guide to ensure consistency across channels.", metadata={"industry": "marketing"}),
    Document(page_content="Collaborated with designers and developers on multimedia content projects.", metadata={"industry": "marketing"}),

    # Finance
    Document(page_content="Reduced overdue receivables by 45% through improved collections workflow.", metadata={"industry": "finance"}),
    Document(page_content="Prepared variance reports and budget vs actuals for quarterly reviews.", metadata={"industry": "finance"}),
    Document(page_content="Implemented a cash flow forecasting model for weekly treasury updates.", metadata={"industry": "finance"}),
    Document(page_content="Consolidated multi-entity financials using NetSuite ERP system.", metadata={"industry": "finance"}),
    Document(page_content="Provided financial insights to executive team for strategic decisions.", metadata={"industry": "finance"}),

    # Healthcare
    Document(page_content="Provided compassionate care to 20+ patients per shift in a fast-paced ER.", metadata={"industry": "healthcare"}),
    Document(page_content="Assisted physicians with diagnostic procedures and patient triage.", metadata={"industry": "healthcare"}),
    Document(page_content="Documented patient records using EHR with 99% accuracy.", metadata={"industry": "healthcare"}),
    Document(page_content="Coordinated patient discharge planning with social services team.", metadata={"industry": "healthcare"}),
    Document(page_content="Maintained infection control standards per CDC guidelines.", metadata={"industry": "healthcare"}),

    # Education
    Document(page_content="Led parent-teacher conferences with 100% attendance rate.", metadata={"industry": "education"}),
    Document(page_content="Implemented project-based learning modules for 4th grade curriculum.", metadata={"industry": "education"}),
    Document(page_content="Tutored ESL students after hours, improving comprehension scores by 22%.", metadata={"industry": "education"}),
    Document(page_content="Managed classroom of 30 students, maintaining positive behavioral outcomes.", metadata={"industry": "education"}),
    Document(page_content="Used student data analytics to personalize lesson plans effectively.", metadata={"industry": "education"}),

    # Tech
    Document(page_content="Wrote unit and integration tests using PyTest, improving code coverage to 95%.", metadata={"industry": "tech"}),
    Document(page_content="Led security audit across backend services, patching 12 vulnerabilities.", metadata={"industry": "tech"}),
    Document(page_content="Improved frontend load speed by 40% through lazy loading and code splitting.", metadata={"industry": "tech"}),
    Document(page_content="Mentored junior developers during biweekly code reviews and workshops.", metadata={"industry": "tech"}),
    Document(page_content="Integrated payment gateways (Stripe, PayPal) to support global customers.", metadata={"industry": "tech"}),

    # Marketing
    Document(page_content="Researched competitor positioning to refine brand messaging.", metadata={"industry": "marketing"}),
    Document(page_content="Built and managed CRM segmentation lists for targeted email flows.", metadata={"industry": "marketing"}),
    Document(page_content="Produced product explainer videos, increasing landing page dwell time by 45%.", metadata={"industry": "marketing"}),
    Document(page_content="Tracked influencer ROI with UTM codes and affiliate dashboards.", metadata={"industry": "marketing"}),
    Document(page_content="Managed content calendar for blog and social media, maintaining weekly publishing cadence.", metadata={"industry": "marketing"}),

    # Finance
    Document(page_content="Closed monthly books in under five days for three business units.", metadata={"industry": "finance"}),
    Document(page_content="Assisted external auditors during year-end financial audits.", metadata={"industry": "finance"}),
    Document(page_content="Created SOPs for finance team onboarding and recurring tasks.", metadata={"industry": "finance"}),
    Document(page_content="Processed payroll for 300+ employees using ADP and Gusto.", metadata={"industry": "finance"}),
    Document(page_content="Evaluated cost-benefit analysis for major vendor renegotiations.", metadata={"industry": "finance"}),

    # Healthcare
    Document(page_content="Scheduled appointments and coordinated referrals with specialty clinics.", metadata={"industry": "healthcare"}),
    Document(page_content="Supported mental health patients with daily counseling check-ins.", metadata={"industry": "healthcare"}),
    Document(page_content="Monitored vital signs and reported changes to attending physician.", metadata={"industry": "healthcare"}),
    Document(page_content="Created training materials for new patient intake protocols.", metadata={"industry": "healthcare"}),
    Document(page_content="Assisted with vaccine administration and community health events.", metadata={"industry": "healthcare"}),

    # Education
    Document(page_content="Championed inclusive teaching strategies for students with IEPs.", metadata={"industry": "education"}),
    Document(page_content="Maintained detailed progress reports aligned with national standards.", metadata={"industry": "education"}),
    Document(page_content="Coordinated after-school STEM club with weekly hands-on projects.", metadata={"industry": "education"}),
    Document(page_content="Hosted virtual learning sessions during school closures with full attendance.", metadata={"industry": "education"}),
    Document(page_content="Helped design school-wide literacy improvement initiative.", metadata={"industry": "education"}),

    # Tech
    Document(page_content="Reduced memory usage in backend services by optimizing data structures.", metadata={"industry": "tech"}),
    Document(page_content="Collaborated with product managers to define technical scope and timelines.", metadata={"industry": "tech"}),
    Document(page_content="Wrote GraphQL resolvers to support new frontend dashboard features.", metadata={"industry": "tech"}),
    Document(page_content="Deployed monitoring alerts with Datadog to catch system anomalies early.", metadata={"industry": "tech"}),
    Document(page_content="Participated in hackathons and shipped two internal tools now in production.", metadata={"industry": "tech"}),

    # Marketing
    Document(page_content="Drafted PR campaigns that led to coverage in Forbes and TechCrunch.", metadata={"industry": "marketing"}),
    Document(page_content="Created and maintained a brand partnership database for outreach tracking.", metadata={"industry": "marketing"}),
    Document(page_content="Analyzed user behavior via Hotjar and Google Analytics to guide UX strategy.", metadata={"industry": "marketing"}),
    Document(page_content="Led market segmentation project to redefine customer personas.", metadata={"industry": "marketing"}),
    Document(page_content="Tested pricing models through email surveys and landing page conversions.", metadata={"industry": "marketing"}),

    # Finance
    Document(page_content="Managed vendor invoices and reconciliations with NetSuite integration.", metadata={"industry": "finance"}),
    Document(page_content="Tracked depreciation schedules and ensured accurate fixed asset accounting.", metadata={"industry": "finance"}),
    Document(page_content="Reviewed corporate credit card expenses and flagged inconsistencies.", metadata={"industry": "finance"}),
    Document(page_content="Built dashboards to visualize financial KPIs for leadership.", metadata={"industry": "finance"}),
    Document(page_content="Collaborated with procurement to improve cost tracking and approvals.", metadata={"industry": "finance"}),

    # Healthcare
    Document(page_content="Taught CPR and first aid courses as part of staff development program.", metadata={"industry": "healthcare"}),
    Document(page_content="Assessed nutritional needs and designed patient meal plans.", metadata={"industry": "healthcare"}),
    Document(page_content="Managed medical supply inventory, reducing shortages by 25%.", metadata={"industry": "healthcare"}),
    Document(page_content="Provided translation services for Spanish-speaking patients and families.", metadata={"industry": "healthcare"}),
    Document(page_content="Led peer training sessions on trauma-informed care.", metadata={"industry": "healthcare"}),

    # Education
    Document(page_content="Piloted a flipped classroom model, improving homework completion rates.", metadata={"industry": "education"}),
    Document(page_content="Collaborated with special education staff to co-teach inclusive classrooms.", metadata={"industry": "education"}),
    Document(page_content="Created assessment rubrics aligned with core learning standards.", metadata={"industry": "education"}),
    Document(page_content="Facilitated peer mediation programs to improve school climate.", metadata={"industry": "education"}),
    Document(page_content="Organized field trips and parent volunteer days with 100% satisfaction.", metadata={"industry": "education"}),

    # Tech
    Document(page_content="Reverse engineered legacy software to migrate key functionality to a new platform.", metadata={"industry": "tech"}),
    Document(page_content="Created a CLI tool that reduced manual server checks by 80%.", metadata={"industry": "tech"}),
    Document(page_content="Optimized image delivery by implementing lazy loading and CDN caching.", metadata={"industry": "tech"}),
    Document(page_content="Assisted in SOC 2 Type II compliance through secure code practices.", metadata={"industry": "tech"}),
    Document(page_content="Architected real-time data ingestion pipeline using Kafka and Spark.", metadata={"industry": "tech"}),

    # Marketing
    Document(page_content="Surveyed customer satisfaction and implemented feedback loops to increase NPS by 12 points.", metadata={"industry": "marketing"}),
    Document(page_content="Wrote blog content that ranked on page 1 for 20+ keywords.", metadata={"industry": "marketing"}),
    Document(page_content="Automated reporting dashboards using Google Data Studio.", metadata={"industry": "marketing"}),
    Document(page_content="Managed CRM campaign for win-back customers, recovering $100K in revenue.", metadata={"industry": "marketing"}),
    Document(page_content="Revamped webinar strategy, doubling average attendee engagement.", metadata={"industry": "marketing"}),

    # Finance
    Document(page_content="Introduced zero-based budgeting approach for cost control.", metadata={"industry": "finance"}),
    Document(page_content="Performed scenario analysis for investment planning across three economic models.", metadata={"industry": "finance"}),
    Document(page_content="Filed quarterly tax estimates and ensured 100% IRS compliance.", metadata={"industry": "finance"}),
    Document(page_content="Conducted sensitivity analysis on pricing assumptions in financial models.", metadata={"industry": "finance"}),
    Document(page_content="Prepared executive briefing books for quarterly board meetings.", metadata={"industry": "finance"}),

    # Healthcare
    Document(page_content="Reduced appointment no-show rate by 22% through patient reminder system.", metadata={"industry": "healthcare"}),
    Document(page_content="Triaged incoming ER patients and prioritized urgent cases effectively.", metadata={"industry": "healthcare"}),
    Document(page_content="Provided bereavement support for families in hospice care.", metadata={"industry": "healthcare"}),
    Document(page_content="Facilitated telehealth visits and resolved tech issues for elderly patients.", metadata={"industry": "healthcare"}),
    Document(page_content="Led response team during emergency drills and real incidents.", metadata={"industry": "healthcare"}),

    # Education
    Document(page_content="Established classroom norms using restorative justice principles.", metadata={"industry": "education"}),
    Document(page_content="Developed bilingual resources for English learners and their families.", metadata={"industry": "education"}),
    Document(page_content="Evaluated curriculum effectiveness through student learning outcomes.", metadata={"industry": "education"}),
    Document(page_content="Provided 1-on-1 reading interventions that closed performance gaps by 30%.", metadata={"industry": "education"}),
    Document(page_content="Collaborated with IT to integrate LMS tools into daily instruction.", metadata={"industry": "education"}),

    # Tech
    Document(page_content="Performed codebase audit and removed deprecated dependencies.", metadata={"industry": "tech"}),
    Document(page_content="Ran performance benchmarks and tuned SQL queries for high-volume datasets.", metadata={"industry": "tech"}),
    Document(page_content="Built integrations with third-party logistics APIs for automated order fulfillment.", metadata={"industry": "tech"}),
    Document(page_content="Created reusable UI component library in Vue.js for product consistency.", metadata={"industry": "tech"}),
    Document(page_content="Wrote scripts to automate internal compliance reports generation.", metadata={"industry": "tech"}),

    # Marketing
    Document(page_content="Launched quarterly brand awareness survey to inform campaign planning.", metadata={"industry": "marketing"}),
    Document(page_content="Reduced bounce rate on product pages by 25% through improved layout and CTAs.", metadata={"industry": "marketing"}),
    Document(page_content="Managed agency partners for PPC and creative asset production.", metadata={"industry": "marketing"}),
    Document(page_content="Developed annual marketing plan tied to company OKRs and tracked progress.", metadata={"industry": "marketing"}),
    Document(page_content="Facilitated monthly content brainstorm sessions across departments.", metadata={"industry": "marketing"}),

    # Finance
    Document(page_content="Trained junior analysts on Excel modeling and internal systems.", metadata={"industry": "finance"}),
    Document(page_content="Monitored capital expenditures and reconciled project spend.", metadata={"industry": "finance"}),
    Document(page_content="Prepared equity grant paperwork in coordination with legal and HR teams.", metadata={"industry": "finance"}),
    Document(page_content="Built profitability models for new service lines with break-even analysis.", metadata={"industry": "finance"}),
    Document(page_content="Generated variance commentary for monthly financial review deck.", metadata={"industry": "finance"}),

    # Healthcare
    Document(page_content="Oversaw intake assessments and created care plans for chronic conditions.", metadata={"industry": "healthcare"}),
    Document(page_content="Tracked patient satisfaction metrics and initiated service improvements.", metadata={"industry": "healthcare"}),
    Document(page_content="Provided lactation consultation and postpartum support.", metadata={"industry": "healthcare"}),
    Document(page_content="Reviewed medication adherence trends and coordinated pharmacist follow-ups.", metadata={"industry": "healthcare"}),
    Document(page_content="Documented patient education outcomes in EMR.", metadata={"industry": "healthcare"}),

    # Education
    Document(page_content="Taught interdisciplinary environmental science course with outdoor labs.", metadata={"industry": "education"}),
    Document(page_content="Partnered with nonprofit orgs to bring mentorship programs to school.", metadata={"industry": "education"}),
    Document(page_content="Chaired curriculum committee to align cross-grade learning objectives.", metadata={"industry": "education"}),
    Document(page_content="Created flipped lesson plans for hybrid learning environments.", metadata={"industry": "education"}),
    Document(page_content="Guided 5th graders through national science fair submissions.", metadata={"industry": "education"}),

    # Tech
    Document(page_content="Migrated application state management to Redux Toolkit for cleaner architecture.", metadata={"industry": "tech"}),
    Document(page_content="Built serverless functions using AWS Lambda to handle dynamic form submissions.", metadata={"industry": "tech"}),
    Document(page_content="Redesigned data model to eliminate redundancy and improve relational mapping.", metadata={"industry": "tech"}),
    Document(page_content="Implemented multi-factor authentication (MFA) across all user accounts.", metadata={"industry": "tech"}),
    Document(page_content="Created a Slack bot that auto-reports CI build failures to relevant teams.", metadata={"industry": "tech"}),

    # Marketing
    Document(page_content="Launched multilingual ad campaigns targeting Latin American markets.", metadata={"industry": "marketing"}),
    Document(page_content="Created social listening reports using Brandwatch to monitor brand sentiment.", metadata={"industry": "marketing"}),
    Document(page_content="Designed onboarding drip sequence that improved free-to-paid conversion by 14%.", metadata={"industry": "marketing"}),
    Document(page_content="Produced quarterly webinars featuring guest experts to boost engagement.", metadata={"industry": "marketing"}),
    Document(page_content="Maintained editorial calendar across 5 content channels and tracked performance.", metadata={"industry": "marketing"}),

    # Finance
    Document(page_content="Negotiated payment terms with vendors to extend AP cycle by 10 days.", metadata={"industry": "finance"}),
    Document(page_content="Supported quarterly investor reporting and KPI summaries.", metadata={"industry": "finance"}),
    Document(page_content="Reconciled intercompany transactions across three entities.", metadata={"industry": "finance"}),
    Document(page_content="Worked with legal to structure client contracts with milestone-based billing.", metadata={"industry": "finance"}),
    Document(page_content="Oversaw implementation of expense tracking software, reducing fraud incidents.", metadata={"industry": "finance"}),

    # Healthcare
    Document(page_content="Collaborated with physical therapists on rehab plan adjustments.", metadata={"industry": "healthcare"}),
    Document(page_content="Screened patients for clinical trials based on eligibility criteria.", metadata={"industry": "healthcare"}),
    Document(page_content="Digitized intake process, reducing paperwork handling by 90%.", metadata={"industry": "healthcare"}),
    Document(page_content="Provided end-of-life care with compassion and dignity.", metadata={"industry": "healthcare"}),
    Document(page_content="Trained administrative staff on HIPAA-compliant scheduling software.", metadata={"industry": "healthcare"}),

    # Education
    Document(page_content="Designed elective course on digital citizenship and online safety.", metadata={"industry": "education"}),
    Document(page_content="Led school-wide literacy night with activities for 200+ families.", metadata={"industry": "education"}),
    Document(page_content="Introduced coding curriculum using Scratch and block-based logic.", metadata={"industry": "education"}),
    Document(page_content="Mentored new teachers during their first academic year.", metadata={"industry": "education"}),
    Document(page_content="Wrote grant proposal that secured $15K for STEM classroom materials.", metadata={"industry": "education"}),

    # Tech
    Document(page_content="Integrated error tracking with Sentry and set up alerting for key exceptions.", metadata={"industry": "tech"}),
    Document(page_content="Deployed versioned APIs to support backward compatibility for enterprise clients.", metadata={"industry": "tech"}),
    Document(page_content="Refined CI/CD pipeline to include staging smoke tests and rollback plans.", metadata={"industry": "tech"}),
    Document(page_content="Configured infrastructure-as-code using Terraform for multi-region deployment.", metadata={"industry": "tech"}),
    Document(page_content="Built internal analytics dashboard with React and D3.js.", metadata={"industry": "tech"}),

    # Marketing
    Document(page_content="Produced testimonial video series to increase trust with prospects.", metadata={"industry": "marketing"}),
    Document(page_content="Ran retargeting ad campaign across Facebook and LinkedIn, increasing ROI by 50%.", metadata={"industry": "marketing"}),
    Document(page_content="Managed email segmentation based on customer lifecycle stages.", metadata={"industry": "marketing"}),
    Document(page_content="Audited website copy for clarity, improving average session duration by 22%.", metadata={"industry": "marketing"}),
    Document(page_content="Initiated affiliate program that added 12% to monthly revenue.", metadata={"industry": "marketing"}),

    # Finance
    Document(page_content="Implemented dual approval process for large vendor payments.", metadata={"industry": "finance"}),
    Document(page_content="Led budget review meetings with department heads to identify cost-saving opportunities.", metadata={"industry": "finance"}),
    Document(page_content="Created waterfall revenue recognition schedules for SaaS contracts.", metadata={"industry": "finance"}),
    Document(page_content="Analyzed loan portfolio performance using internal credit risk models.", metadata={"industry": "finance"}),
    Document(page_content="Oversaw internal controls testing in preparation for SOX audit.", metadata={"industry": "finance"}),

    # Healthcare
    Document(page_content="Helped launch patient feedback portal to gather care experience insights.", metadata={"industry": "healthcare"}),
    Document(page_content="Developed post-surgical care guides to reduce readmission rates.", metadata={"industry": "healthcare"}),
    Document(page_content="Participated in weekly interdisciplinary rounds to coordinate care plans.", metadata={"industry": "healthcare"}),
    Document(page_content="Oversaw new employee health onboarding, including vaccination tracking.", metadata={"industry": "healthcare"}),
    Document(page_content="Trained nursing assistants on mobility support and fall prevention.", metadata={"industry": "healthcare"}),

    # Education
    Document(page_content="Created scaffolded writing units for ELA curriculum.", metadata={"industry": "education"}),
    Document(page_content="Redesigned classroom layout to promote collaboration and reduce distractions.", metadata={"industry": "education"}),
    Document(page_content="Incorporated AI tools into lesson planning and assessment creation.", metadata={"industry": "education"}),
    Document(page_content="Facilitated peer-led Socratic seminars to deepen comprehension.", metadata={"industry": "education"}),
    Document(page_content="Organized regional professional development conference for 100+ educators.", metadata={"industry": "education"}),

    # Tech
    Document(page_content="Built mobile-first UI components to enhance accessibility across devices.", metadata={"industry": "tech"}),
    Document(page_content="Implemented feature flag system to support gradual rollout of new services.", metadata={"industry": "tech"}),
    Document(page_content="Wrote cron jobs for scheduled data sync between internal systems.", metadata={"industry": "tech"}),
    Document(page_content="Upgraded legacy JavaScript to TypeScript, reducing runtime errors by 40%.", metadata={"industry": "tech"}),
    Document(page_content="Conducted root cause analysis on production incidents to prevent recurrence.", metadata={"industry": "tech"}),

    # Marketing
    Document(page_content="Directed seasonal campaign planning to align with product release cycle.", metadata={"industry": "marketing"}),
    Document(page_content="Developed and tested call-to-action copy variations for ad campaigns.", metadata={"industry": "marketing"}),
    Document(page_content="Created visual content strategy across Instagram and TikTok.", metadata={"industry": "marketing"}),
    Document(page_content="Mapped customer journey to identify key conversion friction points.", metadata={"industry": "marketing"}),
    Document(page_content="Published bi-weekly marketing newsletter for 10,000+ subscribers.", metadata={"industry": "marketing"}),

    # Finance
    Document(page_content="Tracked financial KPIs and compiled reports for board review.", metadata={"industry": "finance"}),
    Document(page_content="Reviewed billing accuracy across enterprise customer contracts.", metadata={"industry": "finance"}),
    Document(page_content="Liaised with external tax consultants during annual filing season.", metadata={"industry": "finance"}),
    Document(page_content="Oversaw bank reconciliations across multiple domestic and international accounts.", metadata={"industry": "finance"}),
    Document(page_content="Implemented credit check process for onboarding new clients.", metadata={"industry": "finance"}),

    # Healthcare
    Document(page_content="Created monthly patient education series on chronic disease management.", metadata={"industry": "healthcare"}),
    Document(page_content="Assessed pain levels and adjusted care protocols in consultation with physicians.", metadata={"industry": "healthcare"}),
    Document(page_content="Participated in vaccine rollout strategy and storage compliance audits.", metadata={"industry": "healthcare"}),
    Document(page_content="Maintained detailed nursing logs per state and federal regulations.", metadata={"industry": "healthcare"}),
    Document(page_content="Provided emotional support and advocacy for end-of-life patients.", metadata={"industry": "healthcare"}),

    # Education
    Document(page_content="Facilitated student-led conferences that built goal-setting skills.", metadata={"industry": "education"}),
    Document(page_content="Created unit assessments aligned with Common Core standards.", metadata={"industry": "education"}),
    Document(page_content="Supervised student teachers and provided formal observation feedback.", metadata={"industry": "education"}),
    Document(page_content="Redesigned course materials to accommodate visual and auditory learners.", metadata={"industry": "education"}),
    Document(page_content="Led virtual open house to engage families during remote learning.", metadata={"industry": "education"}),

    # Tech
    Document(page_content="Led cross-platform app migration from Ionic to React Native.", metadata={"industry": "tech"}),
    Document(page_content="Configured cloud storage lifecycle policies to reduce costs by 30%.", metadata={"industry": "tech"}),
    Document(page_content="Performed penetration testing and remediated all critical findings.", metadata={"industry": "tech"}),
    Document(page_content="Developed chatbot integration for customer support using Dialogflow.", metadata={"industry": "tech"}),
    Document(page_content="Contributed to open-source libraries adopted by internal teams.", metadata={"industry": "tech"}),

    # Marketing
    Document(page_content="Spearheaded brand refresh including logo, typography, and tone guidelines.", metadata={"industry": "marketing"}),
    Document(page_content="Collaborated with design team to improve site UX for lead gen forms.", metadata={"industry": "marketing"}),
    Document(page_content="Increased blog subscriber rate by 40% through gated content strategy.", metadata={"industry": "marketing"}),
    Document(page_content="Launched LinkedIn Ads campaign targeting B2B SaaS decision makers.", metadata={"industry": "marketing"}),
    Document(page_content="Created SEO content hub targeting long-tail queries in niche vertical.", metadata={"industry": "marketing"}),

    # Finance
    Document(page_content="Prepared investor pitch decks with financial projections and unit economics.", metadata={"industry": "finance"}),
    Document(page_content="Automated payroll reporting for cross-border teams with variable pay.", metadata={"industry": "finance"}),
    Document(page_content="Created benchmark analysis comparing competitors' financial performance.", metadata={"industry": "finance"}),
    Document(page_content="Standardized chart of accounts during accounting system transition.", metadata={"industry": "finance"}),
    Document(page_content="Reviewed expense claims against travel policy, reducing policy violations.", metadata={"industry": "finance"}),

    # Healthcare
    Document(page_content="Shadowed attending physician to support diagnosis documentation workflow.", metadata={"industry": "healthcare"}),
    Document(page_content="Set up telehealth hardware for patients with limited tech literacy.", metadata={"industry": "healthcare"}),
    Document(page_content="Participated in community vaccination drives in underserved areas.", metadata={"industry": "healthcare"}),
    Document(page_content="Performed wound care and updated recovery notes daily.", metadata={"industry": "healthcare"}),
    Document(page_content="Coordinated discharge planning with home health and case management.", metadata={"industry": "healthcare"}),

    # Education
    Document(page_content="Led school coding club and helped students publish apps to app stores.", metadata={"industry": "education"}),
    Document(page_content="Wrote differentiated learning objectives based on pre-assessment results.", metadata={"industry": "education"}),
    Document(page_content="Held weekly office hours for student support and parent communication.", metadata={"industry": "education"}),
    Document(page_content="Partnered with counselors to integrate SEL into homeroom sessions.", metadata={"industry": "education"}),
    Document(page_content="Used project-based learning to teach inquiry and collaboration skills.", metadata={"industry": "education"}),

    # Tech
    Document(page_content="Designed secure user authentication with JWT and refresh token handling.", metadata={"industry": "tech"}),
    Document(page_content="Wrote documentation for API endpoints and data contracts using Swagger.", metadata={"industry": "tech"}),
    Document(page_content="Implemented data anonymization protocols for GDPR compliance.", metadata={"industry": "tech"}),
    Document(page_content="Created sandbox environments for dev team feature experimentation.", metadata={"industry": "tech"}),
    Document(page_content="Set up Git hooks to enforce linting and pre-commit checks.", metadata={"industry": "tech"}),

    # Marketing
    Document(page_content="Built UTM tracking dashboard to monitor multi-channel attribution.", metadata={"industry": "marketing"}),
    Document(page_content="Launched first brand podcast, reaching 15K listeners in 60 days.", metadata={"industry": "marketing"}),
    Document(page_content="Managed international translation vendors for campaign localization.", metadata={"industry": "marketing"}),
    Document(page_content="Created swipe file of top-performing ads to inspire new creatives.", metadata={"industry": "marketing"}),
    Document(page_content="Ran sentiment analysis on product reviews to identify brand advocates.", metadata={"industry": "marketing"}),

    # Finance
    Document(page_content="Audited 12 months of vendor payments to recover $30K in overbilling.", metadata={"industry": "finance"}),
    Document(page_content="Created treasury policy for short-term investment of idle cash.", metadata={"industry": "finance"}),
    Document(page_content="Drafted financial due diligence memos for two acquisition targets.", metadata={"industry": "finance"}),
    Document(page_content="Automated invoice matching and approval workflow with OCR tech.", metadata={"industry": "finance"}),
    Document(page_content="Established reporting cadence with C-suite for cash runway updates.", metadata={"industry": "finance"}),

    # Healthcare
    Document(page_content="Supported mobile clinic operations for rural health access program.", metadata={"industry": "healthcare"}),
    Document(page_content="Maintained sterile environments according to JCAHO standards.", metadata={"industry": "healthcare"}),
    Document(page_content="Documented daily vitals and symptoms for patients in isolation units.", metadata={"industry": "healthcare"}),
    Document(page_content="Counseled diabetic patients on dietary management and medication adherence.", metadata={"industry": "healthcare"}),
    Document(page_content="Performed quality checks on EMR entries for accuracy and completeness.", metadata={"industry": "healthcare"}),

    # Education
    Document(page_content="Created independent study projects for gifted students in STEM.", metadata={"industry": "education"}),
    Document(page_content="Facilitated book circles to enhance reading fluency and critical thinking.", metadata={"industry": "education"}),
    Document(page_content="Led outdoor education program to promote environmental literacy.", metadata={"industry": "education"}),
    Document(page_content="Built digital library of annotated resources for teacher collaboration.", metadata={"industry": "education"}),
    Document(page_content="Trained staff on trauma-sensitive teaching practices and classroom routines.", metadata={"industry": "education"}),

    # Tech
    Document(page_content="Conducted spike analysis to evaluate feasibility of blockchain integration.", metadata={"industry": "tech"}),
    Document(page_content="Developed cross-browser testing suite for responsive design verification.", metadata={"industry": "tech"}),
    Document(page_content="Implemented caching layer with Redis to boost API response time by 70%.", metadata={"industry": "tech"}),
    Document(page_content="Built command-line tools for internal dev workflows and configuration.", metadata={"industry": "tech"}),
    Document(page_content="Reviewed PRs daily to ensure adherence to style guides and architecture rules.", metadata={"industry": "tech"}),

    # Marketing
    Document(page_content="Generated monthly competitor landscape analysis for GTM team.", metadata={"industry": "marketing"}),
    Document(page_content="Set up real-time analytics with GA4 to track conversion events.", metadata={"industry": "marketing"}),
    Document(page_content="Created product explainer carousel for use in paid social campaigns.", metadata={"industry": "marketing"}),
    Document(page_content="Managed creative testing backlog to optimize ad visuals and copy.", metadata={"industry": "marketing"}),
    Document(page_content="Built KPI dashboards for executive team using Looker Studio.", metadata={"industry": "marketing"}),

    # Finance
    Document(page_content="Modeled customer LTV and CAC to support fundraising narrative.", metadata={"industry": "finance"}),
    Document(page_content="Reviewed historical burn rate trends to recommend cost containment strategies.", metadata={"industry": "finance"}),
    Document(page_content="Prepared compliance docs for financial institution licensing process.", metadata={"industry": "finance"}),
    Document(page_content="Conducted internal audit on credit card spend for policy adherence.", metadata={"industry": "finance"}),
    Document(page_content="Collaborated with HR to structure employee bonus and equity programs.", metadata={"industry": "finance"}),

    # Healthcare
    Document(page_content="Provided grief counseling resources to families during hospital stays.", metadata={"industry": "healthcare"}),
    Document(page_content="Supervised CNA team and delegated responsibilities by patient acuity.", metadata={"industry": "healthcare"}),
    Document(page_content="Escorted patients to diagnostics and ensured safety during transport.", metadata={"industry": "healthcare"}),
    Document(page_content="Updated care team on overnight patient events during shift handoff.", metadata={"industry": "healthcare"}),
    Document(page_content="Assisted with wound vac dressing changes and monitored healing.", metadata={"industry": "healthcare"}),

    # Education
    Document(page_content="Designed graphic organizers to support language learners in history class.", metadata={"industry": "education"}),
    Document(page_content="Participated in IEP meetings as classroom teacher and provided accommodations data.", metadata={"industry": "education"}),
    Document(page_content="Recorded instructional videos for asynchronous learning modules.", metadata={"industry": "education"}),
    Document(page_content="Co-led teacher book study on inclusive curriculum practices.", metadata={"industry": "education"}),
    Document(page_content="Piloted gamified learning units to improve student motivation and participation.", metadata={"industry": "education"}),

    # Tech
    Document(page_content="Benchmarked internal services to identify CPU bottlenecks under load.", metadata={"industry": "tech"}),
    Document(page_content="Migrated monolith to service-oriented architecture using gRPC.", metadata={"industry": "tech"}),
    Document(page_content="Built CLI-based scaffolding tool for new microservice setup.", metadata={"industry": "tech"}),
    Document(page_content="Integrated Firebase authentication for real-time sync features.", metadata={"industry": "tech"}),
    Document(page_content="Documented API versioning standards and legacy endpoint migration plan.", metadata={"industry": "tech"}),

    # Marketing
    Document(page_content="Crafted positioning framework used across pitch decks and onboarding.", metadata={"industry": "marketing"}),
    Document(page_content="Implemented lead scoring to prioritize MQLs and accelerate conversion.", metadata={"industry": "marketing"}),
    Document(page_content="Analyzed campaign CTRs to optimize subject lines and banner placement.", metadata={"industry": "marketing"}),
    Document(page_content="Launched PR outreach sequence that resulted in five media placements.", metadata={"industry": "marketing"}),
    Document(page_content="Built swipe file library for campaign inspiration and creative testing.", metadata={"industry": "marketing"}),

    # Finance
    Document(page_content="Closed books for year-end in compliance with IFRS standards.", metadata={"industry": "finance"}),
    Document(page_content="Led budgeting process for three business units across five markets.", metadata={"industry": "finance"}),
    Document(page_content="Developed and rolled out policy for non-PO invoice exceptions.", metadata={"industry": "finance"}),
    Document(page_content="Analyzed FX exposure and recommended hedging strategy for global payments.", metadata={"industry": "finance"}),
    Document(page_content="Ran quarterly cost review meetings with operations and procurement teams.", metadata={"industry": "finance"}),

    # Healthcare
    Document(page_content="Created visual handouts for patients with limited literacy.", metadata={"industry": "healthcare"}),
    Document(page_content="Implemented hourly rounding protocol that improved HCAHPS scores.", metadata={"industry": "healthcare"}),
    Document(page_content="Maintained isolation precautions and signage per infection control guidelines.", metadata={"industry": "healthcare"}),
    Document(page_content="Mentored nursing students during clinical rotations on med-surg unit.", metadata={"industry": "healthcare"}),
    Document(page_content="Coordinated interpreter services for multilingual patient care.", metadata={"industry": "healthcare"}),

    # Education
    Document(page_content="Created data tracker for formative assessments by learning standard.", metadata={"industry": "education"}),
    Document(page_content="Planned and led interdisciplinary unit on sustainability and climate.", metadata={"industry": "education"}),
    Document(page_content="Redesigned substitute teacher guides to include SEL guidance.", metadata={"industry": "education"}),
    Document(page_content="Facilitated lunch bunch sessions to support student friendships and wellbeing.", metadata={"industry": "education"}),
    Document(page_content="Helped students publish digital portfolios of semester-long projects.", metadata={"industry": "education"}),

    # Tech
    Document(page_content="Developed dark mode toggle and user preferences using local storage.", metadata={"industry": "tech"}),
    Document(page_content="Wrote shell scripts to automate CI build triggers for each branch.", metadata={"industry": "tech"}),
    Document(page_content="Debugged persistent memory leaks in real-time WebSocket application.", metadata={"industry": "tech"}),
    Document(page_content="Optimized CSS loading strategy by splitting critical and non-critical styles.", metadata={"industry": "tech"}),
    Document(page_content="Built GraphQL federation layer for microservice communication.", metadata={"industry": "tech"}),

    # Marketing
    Document(page_content="Established creative review process to streamline approvals across departments.", metadata={"industry": "marketing"}),
    Document(page_content="Published interactive quizzes to boost social engagement and data capture.", metadata={"industry": "marketing"}),
    Document(page_content="Implemented behavioral triggers for abandoned cart emails.", metadata={"industry": "marketing"}),
    Document(page_content="Revamped nurture campaigns based on sales feedback and lifecycle stage.", metadata={"industry": "marketing"}),
    Document(page_content="Led rebranding of newsletter format to improve open and click-through rates.", metadata={"industry": "marketing"}),

    # Finance
    Document(page_content="Presented revenue recognition updates in all-hands financial meeting.", metadata={"industry": "finance"}),
    Document(page_content="Reviewed lease agreements for compliance with ASC 842 standards.", metadata={"industry": "finance"}),
    Document(page_content="Conducted cost allocation analysis for shared services teams.", metadata={"industry": "finance"}),
    Document(page_content="Created templates for monthly departmental forecasting submission.", metadata={"industry": "finance"}),
    Document(page_content="Ran stress test models on company cash flow projections.", metadata={"industry": "finance"}),

    # Healthcare
    Document(page_content="Escorted pediatric patients and parents through surgical prep process.", metadata={"industry": "healthcare"}),
    Document(page_content="Monitored post-op patients for signs of surgical complications.", metadata={"industry": "healthcare"}),
    Document(page_content="Developed emergency codes cheat sheets for cross-functional staff.", metadata={"industry": "healthcare"}),
    Document(page_content="Assisted patients with discharge paperwork and transport coordination.", metadata={"industry": "healthcare"}),
    Document(page_content="Initiated pain scale communication protocol with non-verbal patients.", metadata={"industry": "healthcare"}),

    # Education
    Document(page_content="Created classroom jobs system to promote responsibility and collaboration.", metadata={"industry": "education"}),
    Document(page_content="Designed quarterly progress reports with narrative feedback.", metadata={"industry": "education"}),
    Document(page_content="Held virtual parent Q&A sessions to support remote learning transitions.", metadata={"industry": "education"}),
    Document(page_content="Introduced financial literacy mini-unit in middle school advisory program.", metadata={"industry": "education"}),
    Document(page_content="Supported peer mediation training to build student conflict resolution skills.", metadata={"industry": "education"}),

    # Tech
    Document(page_content="Created internal developer wiki with setup guides and architecture diagrams.", metadata={"industry": "tech"}),
    Document(page_content="Integrated analytics SDKs to track feature usage in production.", metadata={"industry": "tech"}),
    Document(page_content="Developed reusable web components with Stencil.js for design consistency.", metadata={"industry": "tech"}),
    Document(page_content="Audited access permissions across cloud services to ensure least-privilege.", metadata={"industry": "tech"}),
    Document(page_content="Ran retrospective sessions after major deployments to identify process improvements.", metadata={"industry": "tech"}),

    # Marketing
    Document(page_content="Mapped customer lifecycle journeys and aligned touchpoints with campaign goals.", metadata={"industry": "marketing"}),
    Document(page_content="Built media kits and spec sheets for partners and publishers.", metadata={"industry": "marketing"}),
    Document(page_content="Created multi-touch attribution model to assess true campaign impact.", metadata={"industry": "marketing"}),
    Document(page_content="Redesigned onboarding emails for brand tone consistency and retention.", metadata={"industry": "marketing"}),
    Document(page_content="Ran post-campaign debriefs and compiled learnings into best practices playbook.", metadata={"industry": "marketing"}),

    # Finance
    Document(page_content="Built variance bridges explaining delta between forecast and actuals.", metadata={"industry": "finance"}),
    Document(page_content="Facilitated cross-functional planning cycle for annual headcount strategy.", metadata={"industry": "finance"}),
    Document(page_content="Automated bank feed reconciliation and approval routing workflows.", metadata={"industry": "finance"}),
    Document(page_content="Benchmarked SaaS metrics (ARR, NRR) against public comps for board updates.", metadata={"industry": "finance"}),
    Document(page_content="Created monthly compliance checklist and tracked resolution statuses.", metadata={"industry": "finance"}),

    # Healthcare
    Document(page_content="Hosted patient education sessions on medication safety and adherence.", metadata={"industry": "healthcare"}),
    Document(page_content="Collected intake histories and documented in EHR under physician supervision.", metadata={"industry": "healthcare"}),
    Document(page_content="Trained on-site interns in basic patient care and medical charting.", metadata={"industry": "healthcare"}),
    Document(page_content="Ran simulation-based training scenarios for emergency response preparedness.", metadata={"industry": "healthcare"}),
    Document(page_content="Updated incident logs and submitted safety reports in compliance portal.", metadata={"industry": "healthcare"}),

    # Education
    Document(page_content="Chaired after-school tech club to promote STEM interest among underserved students.", metadata={"industry": "education"}),
    Document(page_content="Created differentiated lesson plans for students with diverse IEP goals.", metadata={"industry": "education"}),
    Document(page_content="Maintained classroom website to keep families informed of homework and events.", metadata={"industry": "education"}),
    Document(page_content="Implemented flexible seating plan to support attention and engagement.", metadata={"industry": "education"}),
    Document(page_content="Developed student survey to gather feedback on learning preferences and needs.", metadata={"industry": "education"}),
]

embedding_model = OpenAIEmbeddings()
vectorstore = FAISS.from_documents(docs, embedding_model)
vectorstore.save_local("resume_lines_faiss_index")
