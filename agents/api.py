"""
FastAPI REST API Server for Imdc Metastatic Renal Risk.
"""
from typing import Dict, Any, List
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from .base import AuditLogger, PHIGuard
from .models import SystemTaskPayload, ConsensusDossier
from .supervisor import SystemSupervisor

supervisor = SystemSupervisor(model_provider="mock")

app = FastAPI(
    title="Imdc Metastatic Renal Risk API",
    description="Enterprise Distributed Component Platform (Clinical & Biomedical AI)",
    version="3.0.0-ENTERPRISE",
)


class ChatRequest(BaseModel):
    query: str


@app.get("/health")
def health():
    return {"status": "HEALTHY", "service": "imdc-metastatic-renal-risk", "domain": "Clinical & Biomedical AI", "standard": "CAP / CLSI / ISO Standards", "version": "3.0.0-ENTERPRISE"}


@app.get("/metrics")
def metrics():
    return {
        "dossiers_processed_total": len(supervisor.dossier_registry),
        "audit_blocks_total": len(AuditLogger.get_trail()),
        "system_status": "NOMINAL_OPTIMAL"
    }


@app.post("/api/audit")
def api_audit(payload: SystemTaskPayload):
    dossier = supervisor.process_task(payload)
    return dossier.to_dict()


@app.post("/api/chat")
def api_chat(req: ChatRequest):
    try:
        ans = supervisor.query_supervisory_chat(req.query)
        return {"response": ans}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@app.get("/api/audit/logs")
def api_audit_logs():
    return {"audit_trail": AuditLogger.get_trail(), "verified": AuditLogger.verify_integrity()}


# Published six-factor IMDC prognostic score, distinct from generic audit workers.
from pydantic import ConfigDict, StrictBool
from imdc_risk import calculate_metrics


class IMDCRiskRequest(BaseModel):
    model_config = ConfigDict(extra="forbid")
    kps_below_80: StrictBool
    diagnosis_to_treatment_lt_1yr: StrictBool
    hemoglobin_below_lln: StrictBool
    corrected_calcium_above_uln: StrictBool
    neutrophils_above_uln: StrictBool
    platelets_above_uln: StrictBool


@app.post("/api/imdc")
def api_imdc(payload: IMDCRiskRequest):
    """Compute published six-factor IMDC prognostic classification."""
    return calculate_metrics(**payload.model_dump())
