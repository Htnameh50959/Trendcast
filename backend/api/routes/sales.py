import os
import pandas as pd
import io
from fastapi import APIRouter, UploadFile, File, HTTPException, Response, Request
from pydantic import BaseModel
from api.firebase_admin_init import get_db, verify_token

router = APIRouter()


class AddRecordRequest(BaseModel):
    record: dict


class DeleteRecordRequest(BaseModel):
    record: dict


def get_user_id_from_request(request: Request) -> str:
    token = getattr(request.state, "token", None)
    if not token:
        raise HTTPException(status_code=401, detail="No authentication token provided")
    try:
        return verify_token(token)
    except Exception:
        raise HTTPException(status_code=401, detail="Unauthorized")


def get_latest_doc(user_id: str):
    db = get_db()
    docs = (
        db.collection("sales_data")
        .where("user_id", "==", user_id)
        .order_by("created_at", direction="DESCENDING")
        .limit(1)
        .stream()
    )
    results = list(docs)
    return results[0] if results else None


@router.post("/upload")
async def upload_file(request: Request, file: UploadFile = File(...)):
    if not file.filename:
        raise HTTPException(status_code=400, detail="No selected file")

    contents = await file.read()

    if file.filename.endswith(".csv"):
        df = pd.read_csv(io.BytesIO(contents))
    elif file.filename.endswith((".xlsx", ".xls")):
        df = pd.read_excel(io.BytesIO(contents))
    else:
        raise HTTPException(status_code=400, detail="Invalid file type")

    data = df.to_dict(orient="records")

    try:
        user_id = get_user_id_from_request(request)
        from datetime import datetime, timezone
        db = get_db()
        db.collection("sales_data").add({
            "data": data,
            "filename": file.filename,
            "record_count": len(data),
            "user_id": user_id,
            "created_at": datetime.now(timezone.utc).isoformat(),
        })
    except Exception as e:
        print(f"Upload failed: {e}")
        raise HTTPException(status_code=500, detail=f"Upload failed: {str(e)}")

    return {
        "message": "File uploaded successfully",
        "filename": file.filename,
        "records": len(data),
    }


@router.get("/salesdata")
async def get_sales_data(request: Request):
    try:
        user_id = get_user_id_from_request(request)
        doc = get_latest_doc(user_id)
        if not doc:
            raise HTTPException(status_code=404, detail="No data found")
        return doc.to_dict()
    except HTTPException:
        raise
    except Exception as e:
        print(f"Error fetching sales data: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/delete")
async def delete_data(request: Request):
    try:
        user_id = get_user_id_from_request(request)
        doc = get_latest_doc(user_id)
        if doc:
            doc.reference.delete()
    except HTTPException:
        raise
    except Exception as e:
        print(f"Error deleting data: {e}")
        raise HTTPException(status_code=500, detail="Delete failed")

    return {"message": "Deleted successfully", "type": "success"}


@router.post("/addrecord")
async def add_record(data: AddRecordRequest, request: Request):
    try:
        user_id = get_user_id_from_request(request)
        doc = get_latest_doc(user_id)
        if not doc:
            raise HTTPException(status_code=404, detail="No data found")

        doc_data = doc.to_dict()
        updated_data = doc_data.get("data", [])
        updated_data.append(data.record)

        doc.reference.update({
            "data": updated_data,
            "record_count": len(updated_data),
        })
    except HTTPException:
        raise
    except Exception as e:
        print(f"Error adding record: {e}")
        raise HTTPException(status_code=500, detail="Failed to add record")

    return {"message": "Record added successfully"}


@router.post("/deleterecord")
async def delete_record(data: DeleteRecordRequest, request: Request):
    try:
        user_id = get_user_id_from_request(request)
        doc = get_latest_doc(user_id)
        if not doc:
            raise HTTPException(status_code=404, detail="No data found")

        doc_data = doc.to_dict()
        updated_data = [r for r in doc_data.get("data", []) if r != data.record]

        doc.reference.update({
            "data": updated_data,
            "record_count": len(updated_data),
        })
    except HTTPException:
        raise
    except Exception as e:
        print(f"Error deleting record: {e}")
        raise HTTPException(status_code=500, detail="Failed to delete record")

    return {"message": "Record deleted successfully"}


@router.get("/export")
async def export_data(request: Request):
    try:
        user_id = get_user_id_from_request(request)
        doc = get_latest_doc(user_id)
        if not doc:
            raise HTTPException(status_code=404, detail="No data found")

        df = pd.DataFrame(doc.to_dict().get("data", []))
        output = io.StringIO()
        df.to_csv(output, index=False)

        return Response(
            content=output.getvalue(),
            media_type="text/csv",
            headers={"Content-Disposition": "attachment; filename=sales_data.csv"},
        )
    except HTTPException:
        raise
    except Exception as e:
        print(f"Error exporting data: {e}")
        raise HTTPException(status_code=500, detail="Export failed")
