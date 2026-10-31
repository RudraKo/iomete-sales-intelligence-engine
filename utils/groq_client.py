"""Groq API client wrapper for IOMETE Sales Intelligence Engine.

Enforces zero-hallucination accuracy and strict grounding in IOMETE's core facts:
- Sovereign deployment (Control plane vs Data plane separation; data stays in customer VPC)
- Apache Spark compute engine (Autoscaling, serverless & interactive, AQE)
- Apache Iceberg open table format (ACID transactions, zero lock-in)
- Kubernetes native orchestration (EKS, GKE, AKS, OpenShift)
"""

import os
import logging
from typing import Optional, Dict, Any, List
try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    pass

logger = logging.getLogger(__name__)

# Default model as specified for Phase 1
DEFAULT_MODEL = os.getenv("GROQ_MODEL", "llama-3.3-70b-versatile")
DEFAULT_TEMPERATURE = float(os.getenv("TEMPERATURE", "0.1"))
DEFAULT_MAX_TOKENS = int(os.getenv("MAX_TOKENS", "4096"))

# Non-negotiable system prompt enforcing Zero Hallucination and IOMETE technical reality
STRICT_IOMETE_SYSTEM_PROMPT = """You are the Lead Sales Intelligence Engine for IOMETE.
Your role is to assist enterprise sales teams, solutions architects, and technical sales reps with call preparation, objection inversion, and executive proposals.

CORE IOMETE ARCHITECTURAL PILLARS (GROUND TRUTH):
1. SOVEREIGN DEPLOYMENT: IOMETE uses a hybrid sovereign architecture. The Data Plane runs 100% inside the customer's private cloud VPC (AWS, GCP, Azure) or on-premise Kubernetes cluster. Customer data NEVER leaves the customer's boundary. No queries, data records, or raw bytes are transmitted to IOMETE servers. The IOMETE Control Plane solely manages cluster orchestration and metadata synchronization.
2. APACHE SPARK COMPUTE: Enterprise-grade Apache Spark compute engine with autoscaling executors, Adaptive Query Execution (AQE), vectorized Parquet reader, and Thrift Server JDBC/ODBC endpoints for BI tools (Tableau, Power BI, Superset).
3. APACHE ICEBERG STORAGE: 100% open table format with ACID transactions, schema/partition evolution, time-travel, and snapshot rollbacks. ZERO vendor lock-in: data in customer S3/GCS/ADLS buckets remains immediately queryable by any open-source engine (Trino, DuckDB, Spark).
4. KUBERNETES-NATIVE: Deployed via Kubernetes Operators across AWS EKS, GCP GKE, Azure AKS, Red Hat OpenShift, and bare-metal K8s.
5. DIRECT TCO PRICING: Customers purchase cloud compute directly at cost (leveraging EDP/commitments/spot instances) without predatory compute credit markups (70-80% savings vs Snowflake/Databricks).

CRITICAL ZERO-HALLUCINATION RULE (NON-NEGOTIABLE):
- Every statement, claim, and technical metric must be strictly supported by the provided context or the core facts above.
- If a user asks about unsupported platforms (e.g., Windows 95, mainframes), unverified proprietary hardware, or features not documented in the provided context, you MUST explicitly respond with:
  "Unknown / Requires Engineering Verification"
- NEVER invent, speculate, extrapolate, or hallucinate architecture features or benchmark numbers.
"""


class GroqLLMClient:
    """Wrapper client for Groq API with zero-hallucination guardrails."""

    def __init__(
        self,
        api_key: Optional[str] = None,
        model: str = DEFAULT_MODEL,
        default_temperature: float = DEFAULT_TEMPERATURE,
        default_max_tokens: int = DEFAULT_MAX_TOKENS,
    ):
        self.api_key = api_key or os.getenv("GROQ_API_KEY")
        self.model = model
        self.default_temperature = default_temperature
        self.default_max_tokens = default_max_tokens
        self._client = None

    def _get_client(self):
        """Lazy initialization of Groq client."""
        if self._client is None:
            if not self.api_key or self.api_key == "your_groq_api_key_here":
                raise ValueError(
                    "GROQ_API_KEY is not set. Please set GROQ_API_KEY in your environment or .env file."
                )
            try:
                from groq import Groq
                self._client = Groq(api_key=self.api_key)
            except ImportError:
                raise ImportError(
                    "The 'groq' package is not installed. Please install it with 'pip install groq>=0.4.0'."
                )
        return self._client

    def generate(
        self,
        prompt: str,
        context: Optional[str] = None,
        system_prompt: Optional[str] = None,
        temperature: Optional[float] = None,
        max_tokens: Optional[int] = None,
    ) -> str:
        """
        Generates text using Groq's llama-3.3-70b-versatile with strict IOMETE grounding.

        Args:
            prompt: User or task prompt.
            context: Verified technical documentation or living ledger context.
            system_prompt: Optional override for the strict system prompt.
            temperature: Sampling temperature (defaults to 0.1 for high determinism).
            max_tokens: Maximum tokens in completion.

        Returns:
            The generated response string.
        """
        client = self._get_client()

        sys_instruction = system_prompt or STRICT_IOMETE_SYSTEM_PROMPT

        # Compose user message with grounding context if provided
        if context:
            user_content = (
                f"### VERIFIED IOMETE CONTEXT:\n{context}\n\n"
                f"### TASK INSTRUCTION:\n{prompt}\n\n"
                f"Remember: If the requested information is not substantiated by the context or core facts, "
                f"respond strictly with 'Unknown / Requires Engineering Verification'."
            )
        else:
            user_content = prompt

        messages: List[Dict[str, str]] = [
            {"role": "system", "content": sys_instruction},
            {"role": "user", "content": user_content},
        ]

        try:
            response = client.chat.completions.create(
                model=self.model,
                messages=messages,
                temperature=temperature if temperature is not None else self.default_temperature,
                max_tokens=max_tokens or self.default_max_tokens,
            )
            return response.choices[0].message.content.strip()
        except Exception as e:
            logger.error(f"Groq API text generation error: {str(e)}")
            raise RuntimeError(f"Groq Generation Failed: {str(e)}")


def generate_grounded_response(
    prompt: str,
    context: Optional[str] = None,
    model: str = DEFAULT_MODEL,
    temperature: float = DEFAULT_TEMPERATURE,
) -> str:
    """Convenience helper function for generating grounded responses."""
    client = GroqLLMClient(model=model, default_temperature=temperature)
    return client.generate(prompt=prompt, context=context)
