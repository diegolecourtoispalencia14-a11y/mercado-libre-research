from __future__ import annotations

from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, BackgroundTasks
from sqlalchemy.orm import Session
from sqlalchemy import desc

from app.database import get_db
from app.models.opportunity import MarketOpportunity
from app.schemas.radar import (
    OpportunityResponse,
    RadarStatusResponse,
    UpdateOpportunityStatusRequest,
    TriggerScanResponse,
)
from app.services.opportunity_scanner import scanner_service

router = APIRouter(prefix="/radar", tags=["radar"])


@router.get("", response_model=List[OpportunityResponse])
def get_opportunities(
    status: Optional[str] = "active",
    limit: int = 50,
    db: Session = Depends(get_db),
):
    """
    Returns high-yield e-commerce opportunities filtered by status.
    Ordered by Score (descending) and detection timestamp.
    """
    query = db.query(MarketOpportunity)
    if status and status != "all":
        query = query.filter(MarketOpportunity.status == status)

    return query.order_by(
        desc(MarketOpportunity.score), desc(MarketOpportunity.detected_at)
    ).limit(limit).all()


@router.get("/status", response_model=RadarStatusResponse)
def get_radar_status(db: Session = Depends(get_db)):
    """Returns current health, scan status and opportunity statistics."""
    total = db.query(MarketOpportunity).count()
    active = db.query(MarketOpportunity).filter(MarketOpportunity.status == "active").count()

    return RadarStatusResponse(
        is_running=scanner_service.is_scanning,
        last_scan_at=scanner_service.last_scan_at,
        total_opportunities=total,
        active_opportunities=active,
        categories_monitored=scanner_service.categories,
    )


@router.post("/scan", response_model=TriggerScanResponse)
def trigger_radar_scan(background_tasks: BackgroundTasks):
    """Triggers an autonomous market scan in the background."""
    if scanner_service.is_scanning:
        return TriggerScanResponse(
            status="running",
            message="El radar ya está ejecutando un escaneo en segundo plano.",
            new_opportunities_found=0,
        )

    background_tasks.add_task(scanner_service.run_scan)
    return TriggerScanResponse(
        status="started",
        message="Escaneo 24/7 iniciado en segundo plano a través de las categorías diana.",
        new_opportunities_found=0,
    )


@router.patch("/{opportunity_id}", response_model=OpportunityResponse)
def update_opportunity_status(
    opportunity_id: int,
    req: UpdateOpportunityStatusRequest,
    db: Session = Depends(get_db),
):
    """Updates opportunity lifecycle (active, dismissed, contacted) and notes."""
    opp = db.query(MarketOpportunity).filter(MarketOpportunity.id == opportunity_id).first()
    if not opp:
        raise HTTPException(status_code=404, detail="Oportunidad no encontrada")

    opp.status = req.status
    if req.notes is not None:
        opp.notes = req.notes

    db.commit()
    db.refresh(opp)
    return opp
