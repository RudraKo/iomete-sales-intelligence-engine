"""Authoritative Ground Truth and Living Ledger Seed Data for IOMETE.

Every fact here is verified against IOMETE's core architecture:
- Sovereign Deployment (Data plane in customer VPC/infrastructure)
- Apache Spark Compute Engine (Distributed, auto-scaling, serverless & interactive)
- Apache Iceberg Open Table Format (ACID, time-travel, zero vendor lock-in)
- Kubernetes Native Orchestration (EKS, GKE, AKS, OpenShift, On-Prem)
"""

from typing import List
from app.core.models import KnowledgeSnippet

SEED_SNIPPETS: List[KnowledgeSnippet] = [
    # ARCHITECTURE & SOVEREIGN DEPLOYMENT
    KnowledgeSnippet(
        id="arch-001",
        title="Sovereign Deployment Architecture: Control Plane vs Data Plane",
        category="architecture",
        content=(
            "IOMETE uses a hybrid sovereign architecture that strictly isolates the control plane from the data plane. "
            "The Data Plane runs 100% inside the customer's own cloud account (AWS, GCP, Azure) or private on-premise Kubernetes cluster. "
            "Customer data NEVER leaves the customer's boundary. No queries, data records, or raw bytes are transmitted to IOMETE servers. "
            "The IOMETE Control Plane solely manages cluster orchestration, metadata synchronization, and platform health. "
            "This provides absolute data sovereignty, zero egress costs between vendor and client, and strict regulatory compliance."
        ),
        tags=["sovereignty", "architecture", "vpc", "security", "data-plane", "control-plane"],
        source="IOMETE Core Architecture Whitepaper v3.2 [arch#data-plane-isolation]",
        verified=True
    ),
    KnowledgeSnippet(
        id="arch-002",
        title="Apache Iceberg Open Table Format & Storage Layer",
        category="compute_storage",
        content=(
            "IOMETE's storage engine is built on Apache Iceberg open table specification stored in customer-owned object storage "
            "(AWS S3, Google Cloud Storage, Azure Data Lake Gen2, MinIO, or Ceph). "
            "Features include ACID transactions, schema evolution without rewriting data, partition evolution, hidden partitioning, "
            "time-travel queries, and snapshot rollback. "
            "Because tables are stored in 100% standard Iceberg format, there is ZERO vendor lock-in: if a customer ever uninstalls IOMETE, "
            "their data remains immediately queryable by any engine supporting Apache Iceberg (Spark, Trino, DuckDB, Snowflake, Athena)."
        ),
        tags=["iceberg", "storage", "acid", "vendor-lockin", "open-source", "s3", "gcs"],
        source="IOMETE Technical Reference: Storage Subsystem [storage#apache-iceberg]",
        verified=True
    ),
    KnowledgeSnippet(
        id="arch-003",
        title="Apache Spark Compute Engine & Elastic Scaling",
        category="compute_storage",
        content=(
            "IOMETE provides managed, enterprise-grade Apache Spark compute. It supports both long-running interactive BI clusters "
            "and ephemeral, serverless scheduled batch/ETL jobs. "
            "Compute instances autoscale dynamically from zero based on workload queue depth and CPU/memory pressure. "
            "Includes IOMETE Spark optimizations such as intelligent metadata caching, columnar vectorization, and adaptive query execution (AQE). "
            "Exposes standard Thrift Server JDBC/ODBC endpoints allowing direct connection from SQL and BI tools."
        ),
        tags=["spark", "compute", "autoscaling", "aqe", "jdbc", "odbc", "thrift"],
        source="IOMETE Compute Engine Documentation [compute#spark-runtime]",
        verified=True
    ),
    KnowledgeSnippet(
        id="arch-004",
        title="Kubernetes-Native Orchestration & Deployment Targets",
        category="architecture",
        content=(
            "IOMETE deploys as a Kubernetes-native platform using custom Kubernetes Operators. "
            "Supported environments include: AWS EKS, GCP GKE, Azure AKS, Red Hat OpenShift, and standard on-premises bare-metal K8s clusters. "
            "Operators manage Spark driver and executor pod lifecycles, handle node failure recovery, auto-healing, and support "
            "cost-efficient spot/preemptible instances with graceful decommissioning."
        ),
        tags=["kubernetes", "k8s", "eks", "gke", "aks", "openshift", "on-prem"],
        source="IOMETE Infrastructure Guide [k8s#operator-architecture]",
        verified=True
    ),

    # TCO & PRICING
    KnowledgeSnippet(
        id="tco-001",
        title="TCO Advantage: Direct Cloud Infrastructure Pricing vs SaaS Warehouses",
        category="tco_pricing",
        content=(
            "IOMETE eliminates the predatory compute and storage markups typical of SaaS data warehouses (Snowflake, Databricks). "
            "Customers purchase their underlying cloud compute (AWS EC2, GCP Compute Engine, Azure VMs) and storage directly at cloud cost, "
            "leveraging their existing Enterprise Discount Programs (EDP), Savings Plans, and Spot instances. "
            "IOMETE charges a transparent, predictable software subscription fee without per-query billing or credit multipliers. "
            "Enterprise customers typically achieve 70% to 80% total cost of ownership (TCO) savings compared to Snowflake."
        ),
        tags=["tco", "pricing", "cost-savings", "snowflake", "databricks", "cloud-spend"],
        source="IOMETE Enterprise Economic Analysis [pricing#tco-model-2024]",
        verified=True
    ),

    # COMPETITOR COMPARISONS
    KnowledgeSnippet(
        id="comp-001",
        title="Competitive Teardown: IOMETE vs Snowflake",
        category="competitor_comparison",
        content=(
            "Snowflake locks customer data in proprietary micro-partition storage (FDN format) within Snowflake's own VPCs. "
            "Snowflake charges massive compute markups (3x to 5x over raw cloud compute) via proprietary credits that escalate during peak hours. "
            "In contrast, IOMETE stores 100% open Apache Iceberg tables in YOUR storage bucket inside YOUR VPC. "
            "Compute runs on your own K8s nodes at direct cloud cost with no markup. "
            "If you leave Snowflake, extracting data incurs huge egress and transformation costs; with IOMETE, you already own the Parquet/Iceberg files."
        ),
        tags=["snowflake", "competitor", "lockin", "tco", "micro-partition"],
        source="IOMETE Sales Competitive Matrix: Snowflake [battlecard#snowflake-q3]",
        verified=True
    ),
    KnowledgeSnippet(
        id="comp-002",
        title="Competitive Teardown: IOMETE vs Databricks",
        category="competitor_comparison",
        content=(
            "While Databricks supports open Delta Lake, Databricks charges high Databricks Units (DBU) consumption fees layered on top of cloud bills. "
            "Additionally, Databricks Unity Catalog and proprietary platform services create strong ecosystem stickiness and architectural complexity. "
            "IOMETE offers pure Apache Iceberg natively (industry-standard open table format adopted by AWS, Snowflake, and Google Cloud) "
            "with a lightweight, focused Lakehouse experience, predictable non-DBU pricing, and zero proprietary lock-in."
        ),
        tags=["databricks", "competitor", "dbu", "iceberg", "delta-lake"],
        source="IOMETE Sales Competitive Matrix: Databricks [battlecard#databricks-q3]",
        verified=True
    ),
    KnowledgeSnippet(
        id="comp-003",
        title="Competitive Teardown: IOMETE vs DIY Self-Managed Open Source on K8s",
        category="competitor_comparison",
        content=(
            "Building a self-managed lakehouse from raw open-source Spark and Iceberg requires 3-5 dedicated full-time platform engineers ($600k+/year in salary). "
            "Teams struggle with: cluster autoscaling lag, spot instance termination, Thrift JDBC server concurrency bottlenecks, "
            "manual Iceberg compaction and snapshot expiration jobs, and lack of unified RBAC/governance UI. "
            "IOMETE delivers a turn-key enterprise control plane with built-in fine-grained security, automated Iceberg table maintenance, "
            "a collaborative SQL editor, and enterprise support for a fraction of an engineer's salary, while preserving 100% sovereignty."
        ),
        tags=["diy", "open-source", "engineering-overhead", "spark", "k8s-overhead"],
        source="IOMETE Platform Value Whitepaper [battlecard#diy-vs-iomete]",
        verified=True
    ),

    # SECURITY & GOVERNANCE
    KnowledgeSnippet(
        id="sec-001",
        title="Enterprise Security, RBAC & Data Masking",
        category="security",
        content=(
            "IOMETE provides enterprise-grade data governance built directly into the Lakehouse: "
            "1. Role-Based Access Control (RBAC) at database, table, column, and row levels. "
            "2. Dynamic Data Masking (hashing, nulling, partial redaction) based on user role and group membership. "
            "3. Row-level filtering based on tenant ID or geographical region attributes. "
            "4. Comprehensive immutable audit logging recording every SQL query, user identity, IP address, and execution duration. "
            "5. Works within private subnets without public internet ingress required."
        ),
        tags=["security", "rbac", "data-masking", "row-level-security", "audit", "compliance"],
        source="IOMETE Security & Governance Architecture v2.4 [sec#governance-rbac]",
        verified=True
    ),

    # ECOSYSTEM & INTEGRATIONS
    KnowledgeSnippet(
        id="eco-001",
        title="BI & Data Ecosystem Integrations",
        category="compute_storage",
        content=(
            "IOMETE integrates seamlessly with the existing modern data stack: "
            "1. BI Tools: Tableau, Power BI, Apache Superset, Metabase, and Looker via standard JDBC and ODBC drivers. "
            "2. Transformation: Official dbt-iomete adapter for declarative SQL and Iceberg table transformations. "
            "3. Orchestration: Native Apache Airflow and Dagster operators. "
            "4. Streaming: Native Apache Spark Structured Streaming connecting to Apache Kafka, AWS Kinesis, and Azure Event Hubs."
        ),
        tags=["integrations", "bi", "tableau", "powerbi", "dbt", "airflow", "jdbc"],
        source="IOMETE Ecosystem & Partner Integration Guide [eco#modern-data-stack]",
        verified=True
    ),

    # WINNING CALL RESOLUTIONS (PAST DEALS & VERIFIED PLAYBOOKS)
    KnowledgeSnippet(
        id="win-001",
        title="Winning Call Playbook: Healthcare FinTech Sovereignty & Cost Reduction",
        category="winning_call",
        content=(
            "Case: 500TB customer data migration from Snowflake to IOMETE. "
            "Objection Raised by CSO: 'We handle protected health information (PHI) and financial transaction logs; multi-tenant cloud warehouses fail our audit.' "
            "Winning Talk Track: Proved that with IOMETE's sovereign deployment, all compute pods run in their private AWS VPC subnet, "
            "and all Iceberg data is encrypted with their AWS KMS customer-managed key. Zero data leaves their boundary. "
            "Outcome: Full SOC2 / HIPAA audit passed; monthly data warehouse spend decreased from $85,000/mo on Snowflake to $17,500/mo on IOMETE + EC2."
        ),
        tags=["case-study", "healthcare", "fintech", "snowflake-migration", "cso-objection"],
        source="IOMETE Winning Deal Retrospective: HealthFin Deal #104 [sales#deal-healthfin]",
        verified=True
    ),
    KnowledgeSnippet(
        id="win-002",
        title="Winning Call Playbook: Enterprise SaaS Replacing High-Maintenance EMR",
        category="winning_call",
        content=(
            "Case: Global B2B SaaS processing 4TB daily logs on custom AWS EMR Spark. "
            "Objection Raised by VP Data: 'We looked at Databricks, but the DBU cost markup is absurd. Can IOMETE run our Spark jobs faster without manual babysitting?' "
            "Winning Talk Track: Demonstrated IOMETE Kubernetes Spark Operator with automated spot instance draining and adaptive query execution. "
            "ETL pipelines completed 2.2x faster due to metadata caching and vectorized reader. "
            "Outcome: Slashed maintenance overhead from 3 platform engineers to under 0.5 FTE, saving $420k annually in team time and cloud compute."
        ),
        tags=["case-study", "emr-replacement", "databricks-objection", "spot-instances", "vp-data"],
        source="IOMETE Winning Deal Retrospective: LogFlow SaaS Deal #118 [sales#deal-logflow]",
        verified=True
    ),
    KnowledgeSnippet(
        id="win-003",
        title="Winning Call Playbook: Reversing the 'Why Not Raw Open Source?' Objection",
        category="winning_call",
        content=(
            "Case: Tech unicorn evaluating self-hosting Apache Iceberg and Spark on their existing EKS cluster. "
            "Objection: 'We have strong DevOps engineers. Why pay IOMETE when Spark and Iceberg are both free Apache software?' "
            "Winning Inversion: 'You can definitely run raw Spark and Iceberg yourself. The hidden trap isn't day-1 deployment; "
            "it's day-90 operations: writing manual Spark compaction jobs to prevent small-file syndrome in Iceberg, "
            "building an enterprise RBAC proxy for BI analysts, debugging Thrift server OOM crashes under concurrency, and handling multi-tenant isolation. "
            "IOMETE gives your team all those enterprise operational features out-of-the-box so your engineers build business data products rather than plumbing.' "
            "Outcome: Customer signed 2-year enterprise agreement within 3 weeks."
        ),
        tags=["objection-inversion", "diy-spark", "iceberg-maintenance", "compaction", "sales-script"],
        source="IOMETE Executive Sales Playbook: Handling the DIY Objection [playbook#diy-inversion]",
        verified=True
    ),
]

