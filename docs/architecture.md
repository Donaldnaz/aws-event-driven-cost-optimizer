# Architecture

## High-quality diagram (recommended)

### Option A — Editable draw.io (official AWS icons)

Open in **[diagrams.net](https://app.diagrams.net)**:

```
docs/aws-cost-optimizer-architecture.drawio
```

Uses the **AWS Architecture Icons (aws4)** shape library built into draw.io. Export as PNG or SVG at 2x scale for LinkedIn/README.

### Option B — Ready-made PNG

![High-quality AWS architecture](aws-cost-optimizer-hq.png)

File: `docs/aws-cost-optimizer-hq.png`

---

## Logical architecture (AWS-style)

This is the recommended view for documentation, LinkedIn, and interviews. It groups services the way AWS Well-Architected diagrams do: **schedule → compute → read APIs → outputs**.

```mermaid
flowchart TB
  subgraph external [External]
    UserEmail["Email subscriber"]
  end

  subgraph account [AWS Account - us-east-1 deployment region]
    subgraph eventing [Application Integration]
      EB["Amazon EventBridge<br/>Schedule: cron 0 2 * * ? *"]
    end

    subgraph compute [Compute]
      Lambda["AWS Lambda<br/>cost-optimizer-analyzer<br/>Python 3.12 · 256 MB · 600s"]
      CW["Amazon CloudWatch Logs"]
      IAM["IAM execution role<br/>least-privilege read + S3 Put + SNS Publish"]
    end

    subgraph billing [AWS Billing and Cost Management]
      CE["AWS Cost Explorer API<br/>GetCostAndUsage<br/>account-wide spend"]
    end

    subgraph multiregion [All enabled regions - read only]
      EC2["Amazon EC2 API<br/>DescribeRegions · Volumes · EIPs<br/>Instances · Snapshots"]
      RDS["Amazon RDS API<br/>DescribeDBInstances"]
    end

    subgraph storage [Storage and Messaging]
      S3["Amazon S3<br/>cost-optimizer-cost-reports-*<br/>reports/ prefix · SSE · 90d lifecycle"]
      SNS["Amazon SNS<br/>cost-optimizer-cost-alerts"]
    end
  end

  EB -->|"InvokeFunction"| Lambda
  Lambda --> CW
  Lambda -.-> IAM

  Lambda -->|"read spend"| CE
  Lambda -->|"discover + scan"| EC2
  Lambda -->|"scan stopped DBs"| RDS

  Lambda -->|"PutObject JSON report"| S3
  Lambda -->|"Publish summary"| SNS
  SNS -->|"email protocol"| UserEmail
```

## Data flow

| Step | From | To | What happens |
|------|------|-----|--------------|
| 1 | EventBridge | Lambda | Nightly trigger at 02:00 UTC |
| 2 | Lambda | Cost Explorer | Yesterday, MTD, 7-day trend, top services |
| 3 | Lambda | EC2 `DescribeRegions` | List enabled regions |
| 4 | Lambda | EC2 + RDS (per region) | Waste checks with per-region error isolation |
| 5 | Lambda | S3 | Upload `reports/YYYY/MM/DD/cost-report-*.json` |
| 6 | Lambda | SNS | Email with spend headline + top 5 findings + S3 URI |

## Terraform infrastructure map

```mermaid
flowchart LR
  subgraph tf [terraform/environments/prod]
    Prod[main.tf]
  end

  Prod --> ModS3[module.s3]
  Prod --> ModSNS[module.sns]
  Prod --> ModLambda[module.lambda]
  Prod --> ModEB[module.eventbridge]

  ModEB -->|"schedule target"| ModLambda
  ModLambda -->|"PutObject"| ModS3
  ModLambda -->|"Publish"| ModSNS
```

## Build a professional diagram (official AWS icons)

For portfolio posts, README hero images, or slide decks, use **official AWS Architecture Icons** — not generic clip art.

### Official resources

| Resource | URL | Best for |
|----------|-----|----------|
| **AWS Architecture Icons** (official, free) | https://aws.amazon.com/architecture/icons/ | PowerPoint, draw.io, Figma, Lucidchart |
| **AWS Well-Architected Framework** | https://aws.amazon.com/architecture/well-architected/ | Design principles + lens for cost optimization |
| **AWS Serverless patterns** | https://serverlessland.com/patterns | Similar EventBridge → Lambda reference patterns |
| **AWS Prescriptive Guidance – diagrams** | https://docs.aws.amazon.com/prescriptive-guidance/latest/architecture-diagrams/introduction.html | How AWS expects diagrams to be structured |

### Recommended free tools

| Tool | URL | Notes |
|------|-----|-------|
| **draw.io (diagrams.net)** | https://app.diagrams.net | Import AWS 4/5 icon packs; most common for GitHub projects |
| **Lucidchart AWS shapes** | https://www.lucidchart.com | Polished exports; AWS shape library built in |
| **Cloudcraft** | https://www.cloudcraft.co | 3D isometric AWS diagrams from live or manual layout |
| **AWS Application Composer** | https://docs.aws.amazon.com/serverless-application-model/latest/developerguide/what-is-application-composer.html | Visual serverless editor (SAM); good for Lambda-centric apps |

### Suggested layout (for draw.io)

Place icons left → right:

1. **EventBridge** (scheduler icon)
2. Arrow → **Lambda** (with small **IAM role** and **CloudWatch** underneath)
3. From Lambda, upward arrows to:
   - **Cost Explorer** (Billing category)
   - **EC2** + **RDS** (group label: “All enabled regions”)
4. From Lambda, downward arrows to:
   - **S3** (report bucket)
   - **SNS** → **Email** (external/user icon)

Use one dashed **AWS Account** boundary around everything except the email subscriber.

### Icon names to search in the AWS icon set

- Amazon EventBridge
- AWS Lambda
- AWS Identity and Access Management (IAM)
- Amazon CloudWatch
- AWS Cost Explorer
- Amazon EC2
- Amazon RDS
- Amazon Simple Storage Service (S3)
- Amazon Simple Notification Service (SNS)
- Email / User (generic or AWS User icon)

## Simple diagram (quick reference)

![Generated overview](architecture.png)

*The PNG above is a quick visual. For a production-quality diagram, rebuild using the official icon pack and layout above.*
