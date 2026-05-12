from app.workers.celery_app import celery_app


@celery_app.task(name="idp.process_document")
def process_document_task(document_id: str):
    from app.db.session import SessionLocal
    from app.models.idp import IDPDocument, IDPProcessingJob, IDPResult, IDPExtractedField
    from app.services import idp_service
    import uuid

    db = SessionLocal()
    try:
        doc = db.query(IDPDocument).filter(IDPDocument.id == uuid.UUID(document_id)).first()
        if not doc:
            return {"error": "Document not found"}

        job = IDPProcessingJob(document_id=doc.id, status="processing")
        db.add(job)
        db.flush()

        with open(doc.file_path, "rb") as f:
            file_bytes = f.read()

        result_data = idp_service.process_document(file_bytes, doc.mime_type or "image/png")

        result = IDPResult(
            document_id=doc.id,
            document_type=result_data["document_type"],
            confidence=result_data["confidence"],
            raw_text=result_data["raw_text"],
            has_handwriting=result_data.get("has_handwriting", False),
            json_export=result_data["json_export"],
        )
        db.add(result)
        db.flush()

        for field_name, field_value in result_data.get("fields", {}).items():
            db.add(IDPExtractedField(result_id=result.id, field_name=field_name, field_value=str(field_value), confidence=result_data["confidence"]))

        job.status = "completed"
        db.commit()
        return {"status": "completed", "document_type": result_data["document_type"]}
    except Exception as e:
        db.rollback()
        return {"error": str(e)}
    finally:
        db.close()
