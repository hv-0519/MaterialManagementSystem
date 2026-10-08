from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from database import get_db_connection

app = FastAPI(
    title="Material Management System API",
    version="1.0.0"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173",
        "http://127.0.0.1:5173"
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# ============================================================
# Health
# ============================================================

@app.get("/")
def home():
    return {
        "message": "Material Management System API is running"
    }


# ============================================================
# Material Requests
# ============================================================

@app.get("/api/material-requests")
def get_material_requests():

    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)

    try:
        query = """
            SELECT
                mr.id,
                mr.request_no,
                mr.material_id,
                m.material_name,
                m.unit,
                mr.quantity,
                mr.request_type,
                mr.required_date,
                mr.remarks,
                mr.status,
                mr.created_by,
                u.username AS created_by_username,
                mr.verified_by,
                vu.username AS verified_by_username,
                mr.created_at,
                mr.verified_at
            FROM material_requests mr

            JOIN materials m
                ON mr.material_id = m.id

            JOIN users u
                ON mr.created_by = u.id

            LEFT JOIN users vu
                ON mr.verified_by = vu.id

            ORDER BY mr.id DESC
        """

        cursor.execute(query)

        return cursor.fetchall()

    finally:
        cursor.close()
        conn.close()


# ============================================================
# Verify Material Request
# ============================================================

@app.put("/api/material-requests/{request_id}/verify")
def verify_material_request(request_id: int):

    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)

    try:

        cursor.execute(
            """
            SELECT
                id,
                request_no,
                status
            FROM material_requests
            WHERE id = %s
            """,
            (request_id,)
        )

        request = cursor.fetchone()

        if not request:
            raise HTTPException(
                status_code=404,
                detail="Material request not found"
            )

        if request["status"] != "PENDING_VERIFICATION":
            raise HTTPException(
                status_code=400,
                detail="Only pending requests can be verified"
            )

        cursor.execute(
            """
            UPDATE material_requests
            SET
                status = 'VERIFIED',
                verified_by = 1,
                verified_at = CURRENT_TIMESTAMP
            WHERE id = %s
            """,
            (request_id,)
        )

        conn.commit()

        return {
            "message": "Material request verified successfully",
            "request_id": request_id,
            "request_no": request["request_no"],
            "status": "VERIFIED"
        }

    finally:
        cursor.close()
        conn.close()


# ============================================================
# Dashboard Summary
# ============================================================

@app.get("/api/dashboard/summary")
def get_dashboard_summary():

    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)

    try:

        # ----------------------------------------------------
        # Request counts
        # ----------------------------------------------------

        cursor.execute(
            """
            SELECT
                COUNT(*) AS total,

                SUM(
                    CASE
                        WHEN status = 'PENDING_VERIFICATION'
                        THEN 1 ELSE 0
                    END
                ) AS pending_verification,

                SUM(
                    CASE
                        WHEN status = 'VERIFIED'
                        THEN 1 ELSE 0
                    END
                ) AS verified,

                SUM(
                    CASE
                        WHEN status = 'REJECTED'
                        THEN 1 ELSE 0
                    END
                ) AS rejected

            FROM material_requests
            """
        )

        counts = cursor.fetchone()

        pending_verification = int(
            counts["pending_verification"] or 0
        )

        verified = int(
            counts["verified"] or 0
        )

        rejected = int(
            counts["rejected"] or 0
        )

        # ----------------------------------------------------
        # Material / Inventory base count
        # ----------------------------------------------------

        cursor.execute(
            """
            SELECT COUNT(*) AS total
            FROM materials
            """
        )

        material_count = cursor.fetchone()["total"] or 0

        # ----------------------------------------------------
        # Requests requiring attention
        # ----------------------------------------------------

        cursor.execute(
            """
            SELECT
                mr.request_no AS id,
                m.material_name AS material,
                CONCAT(
                    mr.quantity,
                    ' ',
                    m.unit
                ) AS qty,
                mr.request_type AS type,
                mr.status,
                CASE
                    WHEN mr.status = 'PENDING_VERIFICATION'
                    THEN 'Waiting for receiver verification'

                    WHEN mr.status = 'VERIFIED'
                    THEN 'Verified · awaiting purchase review'

                    ELSE mr.status
                END AS note
            FROM material_requests mr

            JOIN materials m
                ON mr.material_id = m.id

            WHERE mr.status IN (
                'PENDING_VERIFICATION',
                'VERIFIED'
            )

            ORDER BY mr.id DESC
            LIMIT 5
            """
        )

        attention_rows = cursor.fetchall()

        attention = []

        for row in attention_rows:

            tone = "warning"

            if row["status"] == "VERIFIED":
                tone = "violet"

            attention.append({
                "id": row["id"],
                "material": row["material"],
                "qty": row["qty"],
                "type": row["type"],
                "note": row["note"],
                "tone": tone
            })

        # ----------------------------------------------------
        # Recent activity
        # ----------------------------------------------------

        cursor.execute(
            """
            SELECT
                mr.request_no,
                mr.status,
                mr.created_at,
                u.username
            FROM material_requests mr

            JOIN users u
                ON mr.created_by = u.id

            ORDER BY mr.created_at DESC
            LIMIT 5
            """
        )

        activity_rows = cursor.fetchall()

        activity = []

        for row in activity_rows:

            status = row["status"]

            if status == "VERIFIED":
                action = "verified"
                tone = "success"

            elif status == "REJECTED":
                action = "rejected"
                tone = "danger"

            else:
                action = "created"
                tone = "primary"

            activity.append({
                "who": row["username"],
                "action": action,
                "target": row["request_no"],
                "when": row["created_at"].strftime("%d %b %Y %H:%M"),
                "tone": tone
            })

        # ----------------------------------------------------
        # Dashboard response
        # ----------------------------------------------------

        return {
            "counts": {
                "pendingVerification": pending_verification,
                "verified": verified,

                # Purchase approval workflow will be connected
                # when its DB fields/table are implemented.
                "pendingApproval": verified,

                "approved": 0,
                "poCreated": 0,
                "received": 0,
                "rejected": rejected
            },

            "trend": {
                "pendingVerification": [],
                "approved": [],
                "purchaseOrders": [],
                "received": []
            },

            "inventory": {
                "skus": int(material_count),
                "healthy": int(material_count),
                "low": 0,
                "out": 0
            },

            "attention": attention,

            "activity": activity
        }

    finally:
        cursor.close()
        conn.close()

# ============================================================
# Materials
# ============================================================

@app.get("/api/materials")
def get_materials():

    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)

    try:
        cursor.execute(
            """
            SELECT
                id,
                material_name,
                unit
            FROM materials
            ORDER BY material_name
            """
        )

        return cursor.fetchall()

    finally:
        cursor.close()
        conn.close()


# ============================================================
# Create Material Request
# ============================================================

@app.post("/api/material-requests")
def create_material_request(request_data: dict):

    material_id = request_data.get("material_id")
    quantity = request_data.get("quantity")
    request_type = request_data.get("request_type")
    required_date = request_data.get("required_date")
    remarks = request_data.get("remarks")

    # --------------------------------------------------------
    # Validation
    # --------------------------------------------------------

    if not material_id:
        raise HTTPException(
            status_code=400,
            detail="Material is required"
        )

    if not quantity or float(quantity) <= 0:
        raise HTTPException(
            status_code=400,
            detail="Quantity must be greater than zero"
        )

    if request_type not in ["NEW", "ADVANCE"]:
        raise HTTPException(
            status_code=400,
            detail="Request type must be NEW or ADVANCE"
        )

    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)

    try:

        # ----------------------------------------------------
        # Verify material exists
        # ----------------------------------------------------

        cursor.execute(
            """
            SELECT
                id,
                material_name,
                unit
            FROM materials
            WHERE id = %s
            """,
            (material_id,)
        )

        material = cursor.fetchone()

        if not material:
            raise HTTPException(
                status_code=404,
                detail="Material not found"
            )

        # ----------------------------------------------------
        # Generate next request number
        # ----------------------------------------------------

        cursor.execute(
            """
            SELECT
                COALESCE(
                    MAX(
                        CAST(
                            SUBSTRING(request_no, 4)
                            AS UNSIGNED
                        )
                    ),
                    0
                ) + 1 AS next_number
            FROM material_requests
            WHERE request_no LIKE 'MR-%'
            """
        )

        next_number = cursor.fetchone()["next_number"]

        request_no = f"MR-{int(next_number):03d}"

        # ----------------------------------------------------
        # Create request
        # ----------------------------------------------------

        cursor.execute(
            """
            INSERT INTO material_requests
            (
                request_no,
                material_id,
                quantity,
                request_type,
                required_date,
                remarks,
                status,
                created_by
            )
            VALUES
            (
                %s,
                %s,
                %s,
                %s,
                %s,
                %s,
                'PENDING_VERIFICATION',
                1
            )
            """,
            (
                request_no,
                material_id,
                quantity,
                request_type,
                required_date if required_date else None,
                remarks if remarks else None
            )
        )

        conn.commit()

        return {
            "message": "Material request created successfully",
            "request_id": cursor.lastrowid,
            "request_no": request_no,
            "status": "PENDING_VERIFICATION"
        }

    except HTTPException:
        conn.rollback()
        raise

    except Exception:
        conn.rollback()
        raise

    finally:
        cursor.close()
        conn.close()

