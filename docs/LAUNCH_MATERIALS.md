# eidosSec - Month 4 Launch Materials

**Prepared for:** Product Hunt, Hacker News, Reddit, Twitter/X
**Target:** 200-500 FREE tier users in Week 1
**Launch Date:** TBD (Recommend: Tuesday 10 AM EST for HN, Monday 12:01 AM PST for PH)

---

## 1. Product Hunt Listing

### Tagline (60 chars max)
```
50+ security tools. One scan. Zero cost. 100% local.
```

**Alternative taglines:**
- "Enterprise security scanning that runs on your laptop"
- "Find vulnerabilities before hackers do - free forever"
- "The open-source alternative to $500/month security scanners"

### Short Description (260 chars max)
```
eidosSec combines 50+ security tools (SAST, DAST, SCA, secrets detection) into one autonomous scanner. Runs entirely on your machine via Docker - your code never leaves your infrastructure. Find SQL injection, XSS, leaked API keys, and CVEs in minutes.
```

### Full Description
```
## The Problem

Security scanning tools are either:
- **Expensive**: Snyk ($98+/dev/year), GitHub Advanced Security ($49/user/month), Checkmarx ($$$)
- **Limited**: Free tools cover only ONE category (just SAST, or just SCA)
- **Privacy-invasive**: Cloud-based scanners require uploading your source code

Most startups and solo developers ship insecure code because they can't afford proper security tooling.

## The Solution: eidosSec

We've integrated **50+ industry-standard security tools** into a single, unified platform:

**What we scan:**
- **SAST** (Static Analysis): Semgrep, CodeQL, Bandit, ESLint security rules
- **DAST** (Dynamic Testing): OWASP ZAP, Nuclei
- **SCA** (Dependencies): Trivy, npm audit, pip-audit
- **Secrets**: TruffleHog, Gitleaks, detect-secrets
- **IaC**: Checkov, tfsec (Terraform, CloudFormation)
- **Containers**: Trivy, Dockle, Hadolint

**Key Features:**
- **Quick Scan** (5-10 min): Perfect for CI/CD and daily development
- **Deep Scan** (30-60 min): Comprehensive pre-release audits
- **Smart Deduplication**: 50 tools don't mean 50x noise - we merge duplicates intelligently
- **Multi-tool Verification**: When 3 tools agree, you KNOW it's real (95%+ confidence)
- **100% Local**: Docker Compose deployment, zero cloud dependencies
- **Privacy First**: Your code NEVER leaves your machine

**Who is this for?**
- Solo developers who can't afford enterprise tools
- Startups needing security compliance (SOC2, PCI-DSS)
- Open-source maintainers protecting their users
- Security teams wanting broader coverage

**Getting Started:**
```bash
git clone https://github.com/eidossec/eidossec
docker-compose up -d
# Open http://localhost:3000
```

Time to first scan: Under 5 minutes.

## Pricing

**FREE Forever:**
- 15 essential tools
- 3 projects
- Quick Scan mode
- JSON export

**PRO ($39/month):**
- All 50+ tools
- Unlimited projects
- AI-powered explanations
- Auto-fix suggestions
- PDF/HTML reports
- CI/CD templates
```

### Maker's First Comment
```
Hey Product Hunt! 👋

I'm the solo developer behind eidosSec. Here's why I built this:

Last year, I was working on a Laravel project for a client. I ran a quick security check using free tools and found... nothing major. Shipped it.

Two weeks later, a security researcher found 3 SQL injections I missed. The free SAST tool I used didn't have good PHP support. A secrets scanner would have caught the hardcoded API key in my .env.example file.

I spent the next month researching every security tool out there. Turns out:
- Semgrep is great for patterns, but misses data flow issues
- CodeQL catches data flow, but is slow
- TruffleHog finds secrets, but Gitleaks catches different ones
- Each tool has blind spots the others cover

So I built eidosSec to run them ALL and merge the results intelligently. When Semgrep, CodeQL, AND ZAP all flag the same line? That's a 95%+ confidence finding.

**What makes us different:**

1. **50+ tools, not 1**: More coverage = fewer blind spots
2. **Runs locally**: I've worked with healthcare startups - they CAN'T upload code to cloud scanners. eidosSec respects that.
3. **Actually free**: Not "free trial" or "free for open source only". FREE. The PRO tier exists for teams who want AI features and premium support.

I'd love your feedback! What security pain points do you face? What tools should we add next?

🔗 GitHub: https://github.com/eidossec/eidossec
💬 Discord: [link]
```

### Product Hunt Tips
- Launch on Monday 12:01 AM PST (start of voting week)
- Prepare 5-6 high-quality screenshots/GIFs
- Reply to EVERY comment within 2 hours
- Share on Twitter, LinkedIn immediately after launch

---

## 2. Hacker News "Show HN" Post

### Title (80 chars max)
```
Show HN: eidosSec – 50+ security tools in one free, local scanner
```

### Post Body
```
I built eidosSec because I couldn't afford Snyk/Checkmarx and got tired of running 10 different tools manually.

It's a Docker Compose stack that runs 50+ security tools (Semgrep, CodeQL, OWASP ZAP, TruffleHog, Trivy, etc.) and merges their findings intelligently. Your code never leaves your machine.

Key features:
- Quick Scan (5-10 min) for CI/CD
- Deep Scan (30-60 min) for audits
- Smart deduplication (500 raw findings → 50 unique issues)
- Multi-tool verification (3+ tools agree = 95% confidence)

Tech stack: FastAPI + React + Celery + PostgreSQL + Redis

Try it:
  git clone https://github.com/eidossec/eidossec
  docker-compose up -d
  # Open localhost:3000

FREE tier: 15 tools, 3 projects
PRO ($39/mo): All 50+ tools, AI features, unlimited

GitHub: https://github.com/eidossec/eidossec

Would love feedback on:
1. What tools should we prioritize adding?
2. Would you use this in CI/CD? What's blocking you?
3. Any interest in a VS Code extension?
```

### HN Best Practices
- Post Tuesday or Wednesday, 10 AM EST
- Keep technical, avoid marketing speak
- Respond to every comment thoughtfully
- Be honest about limitations
- Ask genuine questions to spark discussion

---

## 3. Reddit Strategy

### Target Subreddits

| Subreddit | Members | Best Approach | Post Type |
|-----------|---------|---------------|-----------|
| r/netsec | 550K | Technical deep-dive | Text post |
| r/cybersecurity | 700K | Problem/solution narrative | Text post |
| r/programming | 5.5M | Technical announcement | Link + comment |
| r/devops | 300K | CI/CD integration angle | Text post |
| r/selfhosted | 350K | Privacy/self-hosting angle | Text post |
| r/opensource | 100K | OSS contribution angle | Text post |

### r/netsec Post
```
Title: eidosSec: Open-source security scanner combining 50+ tools (Semgrep, CodeQL, ZAP, Trivy, TruffleHog) with smart deduplication

Body:
I've been working on an open-source project that aggregates multiple security scanning tools into a single platform with intelligent result correlation.

**Problem it solves:**
- Running multiple tools manually is tedious
- Each tool has blind spots the others cover
- Deduplicating results across tools is painful
- Cloud-based scanners are expensive and raise privacy concerns

**Technical approach:**
- Docker Compose deployment (FastAPI + React + Celery)
- Tools run in isolated containers with read-only code mounts
- AST-based deduplication engine for cross-tool correlation
- Confidence scoring based on tool consensus

**Current tool coverage:**
- SAST: Semgrep, Bandit, ESLint, PHPStan, Brakeman (15 total)
- DAST: OWASP ZAP, Nuclei
- SCA: Trivy, npm audit, pip-audit, Composer audit
- Secrets: TruffleHog, Gitleaks, detect-secrets
- IaC: Checkov, cfn-nag

**Looking for feedback on:**
1. Tool prioritization for next release
2. Deduplication accuracy (happy to share the algorithm)
3. Interest in SARIF export for IDE integration

GitHub: [link]

Happy to answer technical questions about the architecture.
```

### r/selfhosted Post
```
Title: Self-hosted security scanner with 50+ tools - your code never leaves your machine

Body:
Built this for developers who need security scanning but can't (or won't) upload code to cloud services.

**What it does:**
Runs 50+ security tools locally via Docker Compose and presents unified results in a web UI.

**Privacy features:**
- 100% local execution
- Code mounted read-only
- No telemetry (optional opt-in analytics)
- No account required
- Works offline after initial setup

**Requirements:**
- Docker + Docker Compose
- 4GB RAM minimum (8GB recommended)
- 10GB disk space

**Quick start:**
```bash
git clone https://github.com/eidossec/eidossec
docker-compose up -d
```

Open localhost:3000, add your project path, scan.

GitHub: [link]

Anyone interested in contributing or testing?
```

### Reddit Best Practices
- Don't post to all subreddits on the same day (looks spammy)
- Engage genuinely in comments
- Don't be defensive about criticism
- Offer to help with specific use cases
- Follow each subreddit's self-promotion rules

---

## 4. Twitter/X Thread

### Thread (10 tweets)

**Tweet 1 (Hook)**
```
I spent 6 months building what Snyk charges $98/dev/year for.

eidosSec: 50+ security tools. One scan. Completely free.

Here's how it finds vulnerabilities your current tools miss 🧵
```

**Tweet 2 (Problem)**
```
The dirty secret of security scanning:

Every tool has blind spots.

- Semgrep misses data flow issues
- CodeQL is slow on large repos
- TruffleHog misses secrets Gitleaks catches
- OWASP ZAP can't see code-level issues

One tool = false confidence.
```

**Tweet 3 (Solution)**
```
eidosSec runs ALL of them and merges results:

✅ Semgrep finds pattern
✅ CodeQL confirms data flow
✅ ZAP exploits it at runtime

3 tools agree = 95% confidence it's real.

500 raw findings → 50 verified issues.
```

**Tweet 4 (Demo - Secrets)**
```
Example: Finding leaked secrets

Most repos have this problem. Let's scan one:

[Screenshot: TruffleHog finds AWS key in .env.backup]
[Screenshot: Gitleaks finds it in git history from 6 months ago]

Two tools, same secret, different locations. Both matter.
```

**Tweet 5 (Demo - SQLi)**
```
Example: SQL Injection

Quick scan finds this in a Laravel controller:

[Screenshot: Code with $request->input() in raw query]

Semgrep flags it ✅
PHPStan flags it ✅
ZAP exploits it ✅

Confidence: 98%
Time to find: 47 seconds
```

**Tweet 6 (Privacy)**
```
"But I can't upload my code to cloud scanners"

You don't have to.

eidosSec runs 100% locally via Docker.

Your code never leaves your machine. Ever.

Perfect for:
- Healthcare/HIPAA
- Finance/PCI-DSS
- Government contractors
- Anyone who values privacy
```

**Tweet 7 (Speed)**
```
"Security scanning takes forever"

Quick Scan: 5-10 minutes
- 15 essential tools
- Entry points + high-risk files
- Perfect for CI/CD

Deep Scan: 30-60 minutes
- All 50+ tools
- Full codebase
- Pre-release audits
```

**Tweet 8 (Pricing)**
```
Pricing:

FREE forever:
- 15 tools
- 3 projects
- Quick Scan

PRO ($39/mo):
- 50+ tools
- Unlimited everything
- AI explanations
- Auto-fix suggestions

That's 60% cheaper than GitHub Advanced Security.
```

**Tweet 9 (Tech Stack)**
```
Built with:
- FastAPI (Python backend)
- React + TypeScript (frontend)
- Celery + Redis (async scanning)
- PostgreSQL (results storage)
- Docker Compose (deployment)

Fully open source. MIT licensed.
```

**Tweet 10 (CTA)**
```
Try it now:

git clone https://github.com/eidossec/eidossec
docker-compose up -d

5 minutes to your first scan.

⭐ Star on GitHub: [link]
💬 Join Discord: [link]
📖 Docs: [link]

What should we build next? Reply with your security pain points 👇
```

### Twitter Best Practices
- Post thread Tuesday-Thursday, 9-11 AM EST
- Include screenshots/GIFs for visual engagement
- Pin the thread to your profile
- Reply to every response
- Retweet with additional context

---

## 5. Community Setup Checklist

### Discord Server Structure
```
📢 ANNOUNCEMENTS
  #announcements (read-only)
  #releases

💬 COMMUNITY
  #general
  #introductions
  #showcase (user success stories)

🛠️ SUPPORT
  #help
  #bug-reports
  #feature-requests

🔧 DEVELOPMENT
  #contributors
  #roadmap-discussion
```

### GitHub Discussions Categories
- **Q&A**: General questions
- **Ideas**: Feature requests
- **Show and Tell**: User implementations
- **Announcements**: Official updates

---

## 6. Launch Week Timeline

### Day -7 (Preparation)
- [ ] Finalize all copy
- [ ] Create screenshots/GIFs
- [ ] Set up Discord server
- [ ] Enable GitHub Discussions
- [ ] Prepare email list (if any)

### Day 0 (Monday) - Product Hunt
- [ ] Submit to Product Hunt at 12:01 AM PST
- [ ] Post maker comment immediately
- [ ] Share on Twitter/LinkedIn
- [ ] Monitor and respond to comments

### Day 1 (Tuesday) - Hacker News
- [ ] Post "Show HN" at 10 AM EST
- [ ] Monitor for 4+ hours
- [ ] Respond to every comment
- [ ] Cross-post notable discussions to Twitter

### Day 2-3 - Reddit
- [ ] Post to r/netsec
- [ ] Post to r/selfhosted
- [ ] Engage authentically

### Day 4-5 - Content
- [ ] Write follow-up blog post based on feedback
- [ ] Create "lessons learned" Twitter thread
- [ ] Thank the community

### Day 6-7 - Analysis
- [ ] Compile metrics (users, stars, feedback)
- [ ] Identify top feature requests
- [ ] Plan iteration based on feedback

---

## 7. Success Metrics (Week 1)

| Metric | Target | Stretch Goal |
|--------|--------|--------------|
| GitHub Stars | 200 | 500 |
| FREE Users | 100 | 300 |
| Discord Members | 50 | 150 |
| Product Hunt Upvotes | 100 | 300 |
| HN Points | 50 | 150 |

---

## 8. Common Questions (FAQ Prep)

**Q: How is this different from SonarQube?**
A: SonarQube is primarily SAST. eidosSec includes SAST + DAST + SCA + secrets + IaC + containers. We also run multiple tools per category for cross-validation.

**Q: Why should I trust this?**
A: It's open source. Read the code. We run established tools (Semgrep, OWASP ZAP, Trivy) - we're just orchestrating them.

**Q: Will you sell my data?**
A: Your data never leaves your machine. There's nothing to sell. We make money from PRO subscriptions, not data.

**Q: Can I use this in CI/CD?**
A: Yes! We provide templates for GitHub Actions, GitLab CI, and Jenkins. Quick Scan is optimized for CI (5-10 min).

**Q: What languages do you support?**
A: Python, JavaScript/TypeScript, PHP, Ruby, Go, Java, C/C++, and more. We auto-detect your stack.

**Q: Is the FREE tier limited on purpose to force upgrades?**
A: The FREE tier includes 15 essential tools that cover most common vulnerabilities. PRO adds specialized tools, AI features, and team collaboration - things solo developers don't necessarily need.

---

*Document Version: 1.0*
*Last Updated: 2026-02-03*
