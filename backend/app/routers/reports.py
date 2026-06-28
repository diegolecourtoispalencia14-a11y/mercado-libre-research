from __future__ import annotations

import csv
import io
from typing import List

from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import StreamingResponse
from sqlalchemy.orm import Session

from app.database import get_db
from app.models.analysis import SavedReport, Analysis
from app.schemas.analysis import SaveReportRequest, SavedReportResponse

router = APIRouter()


@router.get("/reports", response_model=List[SavedReportResponse])
def list_reports(db: Session = Depends(get_db)):
    reports = db.query(SavedReport).order_by(SavedReport.id.desc()).all()
    return [
        SavedReportResponse(
            id=r.id,
            analysis_id=r.analysis_id,
            name=r.name,
            notes=r.notes,
            created_at=r.analysis.created_at,
        )
        for r in reports
    ]


@router.post("/reports", response_model=SavedReportResponse)
def save_report(body: SaveReportRequest, db: Session = Depends(get_db)):
    analysis = db.query(Analysis).filter(Analysis.id == body.analysis_id).first()
    if not analysis:
        raise HTTPException(status_code=404, detail="Analysis not found")

    report = SavedReport(
        analysis_id=body.analysis_id,
        name=body.name,
        notes=body.notes,
    )
    db.add(report)
    db.commit()
    db.refresh(report)

    return SavedReportResponse(
        id=report.id,
        analysis_id=report.analysis_id,
        name=report.name,
        notes=report.notes,
        created_at=analysis.created_at,
    )


@router.get("/reports/{report_id}/export")
def export_report(report_id: int, format: str = "csv", db: Session = Depends(get_db)):
    report = db.query(SavedReport).filter(SavedReport.id == report_id).first()
    if not report:
        raise HTTPException(status_code=404, detail="Report not found")

    analysis = report.analysis
    products = list(analysis.products)

    if format == "csv":
        output = io.StringIO()
        writer = csv.writer(output)
        writer.writerow(["rank", "product_id", "estimated_monthly_sales"])
        for ap in products:
            writer.writerow([ap.rank, ap.product_id, ap.estimated_monthly_sales])
        output.seek(0)
        return StreamingResponse(
            iter([output.getvalue()]),
            media_type="text/csv",
            headers={"Content-Disposition": f"attachment; filename=report_{report_id}.csv"},
        )

    if format == "pdf":
        from reportlab.lib.pagesizes import A4
        from reportlab.platypus import SimpleDocTemplate, Table

        buf = io.BytesIO()
        doc = SimpleDocTemplate(buf, pagesize=A4)
        data = [["Rank", "Product ID", "Est. Monthly Sales"]]
        for ap in products:
            data.append([str(ap.rank), str(ap.product_id), str(ap.estimated_monthly_sales)])
        doc.build([Table(data)])
        buf.seek(0)
        return StreamingResponse(
            buf,
            media_type="application/pdf",
            headers={"Content-Disposition": f"attachment; filename=report_{report_id}.pdf"},
        )

    raise HTTPException(status_code=400, detail="format must be csv or pdf")
