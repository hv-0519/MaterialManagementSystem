from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from database import get_db_connection

app = FastAPI(
    title="Material Management System API",
    version="1.0.0"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=False,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/")
def home():
    return {"message": "Material Management System API is running"}


class RejectionRequest(BaseModel):
    reason: str


class ReceiveRequest(BaseModel):
    quantity: float


from pydantic import Field, field_validator
from mysql.connector import Error as MySQLError


class BomComponentIn(BaseModel):
    output_material_id: int
    component_material_id: int
    qty_per_unit: float = Field(gt=0, description="Must be greater than zero")

    @field_validator("component_material_id")
    @classmethod
    def no_self_reference(cls, v, info):
        if info.data.get("output_material_id") == v:
            raise ValueError("A material cannot be a component of itself")
        return v


class PackingRuleIn(BaseModel):
    output_material_id: int
    package_material_id: int
    units_per_package: int = Field(gt=0, description="Must be greater than zero")

    @field_validator("package_material_id")
    @classmethod
    def no_self_reference(cls, v, info):
        if info.data.get("output_material_id") == v:
            raise ValueError("A material cannot be its own package")
        return v


class ConversionIn(BaseModel):
    output_material_id: int
    output_qty: float = Field(gt=0, description="Must be greater than zero")


@app.get("/api/material-requests")
def get_material_requests():
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    try:
        cursor.execute("""
            SELECT
                mr.id, mr.request_no, mr.material_id, m.material_name, m.unit,
                mr.quantity, mr.request_type, mr.required_date, mr.remarks,
                mr.status, mr.created_by, u.username AS created_by_username,
                mr.verified_by, vu.username AS verified_by_username,
                mr.created_at, mr.verified_at
            FROM material_requests mr
            JOIN materials m ON mr.material_id = m.id
            JOIN users u ON mr.created_by = u.id
            LEFT JOIN users vu ON mr.verified_by = vu.id
            ORDER BY mr.id DESC
        """)
        return cursor.fetchall()
    finally:
        cursor.close()
        conn.close()


@app.post("/api/material-requests")
def create_material_request(request_data: dict):
    material_id = request_data.get("material_id")
    quantity = request_data.get("quantity")
    request_type = request_data.get("request_type")
    required_date = request_data.get("required_date")
    remarks = request_data.get("remarks")

    if not material_id:
        raise HTTPException(status_code=400, detail="Material is required")
    if not quantity or float(quantity) <= 0:
        raise HTTPException(status_code=400, detail="Quantity must be greater than zero")
    if request_type not in ["NEW", "ADVANCE"]:
        raise HTTPException(status_code=400, detail="Request type must be NEW or ADVANCE")

    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    try:
        cursor.execute(
            "SELECT id, material_name, unit FROM materials WHERE id = %s",
            (material_id,)
        )
        material = cursor.fetchone()
        if not material:
            raise HTTPException(status_code=404, detail="Material not found")

        cursor.execute("""
            SELECT COALESCE(
                MAX(CAST(SUBSTRING(request_no, 4) AS UNSIGNED)), 0
            ) + 1 AS next_number
            FROM material_requests
            WHERE request_no LIKE 'MR-%'
        """)
        next_number = cursor.fetchone()["next_number"]
        request_no = f"MR-{int(next_number):03d}"

        cursor.execute("""
            INSERT INTO material_requests
                (request_no, material_id, quantity, request_type,
                 required_date, remarks, status, created_by)
            VALUES (%s, %s, %s, %s, %s, %s, 'PENDING_VERIFICATION', 1)
        """, (
            request_no, material_id, quantity, request_type,
            required_date if required_date else None,
            remarks if remarks else None
        ))
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


@app.put("/api/material-requests/{request_id}/verify")
def verify_material_request(request_id: int):
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    try:
        cursor.execute(
            "SELECT id, request_no, status FROM material_requests WHERE id = %s",
            (request_id,)
        )
        request = cursor.fetchone()
        if not request:
            raise HTTPException(status_code=404, detail="Material request not found")
        if request["status"] != "PENDING_VERIFICATION":
            raise HTTPException(status_code=400, detail="Only pending requests can be verified")

        cursor.execute("""
            UPDATE material_requests
            SET status = 'VERIFIED', verified_by = 1, verified_at = CURRENT_TIMESTAMP
            WHERE id = %s
        """, (request_id,))
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


@app.get("/api/materials")
def get_materials():
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    try:
        cursor.execute("SELECT id, material_name, unit FROM materials ORDER BY material_name")
        return cursor.fetchall()
    finally:
        cursor.close()
        conn.close()


@app.get("/api/purchase-approval/queue")
def get_purchase_approval_queue():
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    try:
        cursor.execute("""
            SELECT
                mr.id, mr.request_no, m.material_name, m.unit, mr.quantity,
                mr.request_type, mr.required_date, mr.remarks, mr.created_at,
                u.username AS created_by_username,
                vu.username AS verified_by_username, mr.verified_at
            FROM material_requests mr
            JOIN materials m ON mr.material_id = m.id
            JOIN users u ON mr.created_by = u.id
            LEFT JOIN users vu ON mr.verified_by = vu.id
            WHERE mr.status = 'VERIFIED' AND mr.approval_status = 'PENDING'
            ORDER BY mr.id DESC
        """)
        rows = cursor.fetchall()
        for row in rows:
            row["quantity"] = float(row["quantity"]) if row["quantity"] is not None else 0
            for field in ("required_date", "created_at", "verified_at"):
                if row.get(field):
                    row[field] = row[field].isoformat()

        cursor.execute("""
            SELECT COUNT(*) AS total FROM material_requests
            WHERE approval_status = 'APPROVED' AND DATE(approved_at) = CURDATE()
        """)
        approved_today = cursor.fetchone()["total"] or 0

        return {"queue": rows, "approved_today": int(approved_today)}
    finally:
        cursor.close()
        conn.close()


@app.post("/api/material-requests/{request_id}/approve")
def approve_material_request(request_id: int):
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    try:
        cursor.execute("""
            SELECT id, request_no, status, approval_status
            FROM material_requests WHERE id = %s
        """, (request_id,))
        request = cursor.fetchone()
        if not request:
            raise HTTPException(status_code=404, detail="Material request not found")
        if request["status"] != "VERIFIED" or request["approval_status"] != "PENDING":
            raise HTTPException(
                status_code=400,
                detail="Only verified requests awaiting approval can be approved"
            )

        cursor.execute("""
            UPDATE material_requests
            SET approval_status = 'APPROVED', approved_by = 1,
                approved_at = CURRENT_TIMESTAMP, approval_reason = NULL
            WHERE id = %s
        """, (request_id,))

        cursor.execute(
            "SELECT material_id, quantity FROM material_requests WHERE id = %s",
            (request_id,)
        )
        mr = cursor.fetchone()

        po_number = f"PO-{request_id:04d}"
        cursor.execute(
            "INSERT INTO purchase_orders (po_number, request_id, status) VALUES (%s, %s, 'PO_CREATED')",
            (po_number, request_id)
        )
        po_id = cursor.lastrowid

        cursor.execute(
            "INSERT INTO material_receiving (po_id, ordered_quantity, received_quantity, status) "
            "VALUES (%s, %s, 0, 'PENDING')",
            (po_id, mr["quantity"])
        )

        cursor.execute("SELECT id FROM inventory WHERE material_id = %s", (mr["material_id"],))
        inv = cursor.fetchone()
        if inv:
            cursor.execute(
                "UPDATE inventory SET incoming_quantity = incoming_quantity + %s WHERE material_id = %s",
                (mr["quantity"], mr["material_id"])
            )
        else:
            cursor.execute(
                "INSERT INTO inventory (material_id, available_quantity, incoming_quantity) "
                "VALUES (%s, 0, %s)",
                (mr["material_id"], mr["quantity"])
            )

        cursor.execute(
            "UPDATE material_requests SET status = 'PO_CREATED' WHERE id = %s",
            (request_id,)
        )

        conn.commit()
        return {
            "message": "Material request approved successfully",
            "request_id": request_id,
            "request_no": request["request_no"],
            "approval_status": "APPROVED"
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


@app.post("/api/material-requests/{request_id}/reject")
def reject_material_request(request_id: int, data: RejectionRequest):
    reason = data.reason.strip()
    if not reason:
        raise HTTPException(status_code=400, detail="Rejection reason is required")

    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    try:
        cursor.execute("""
            SELECT id, request_no, status, approval_status
            FROM material_requests WHERE id = %s
        """, (request_id,))
        request = cursor.fetchone()
        if not request:
            raise HTTPException(status_code=404, detail="Material request not found")
        if request["status"] != "VERIFIED" or request["approval_status"] != "PENDING":
            raise HTTPException(
                status_code=400,
                detail="Only verified requests awaiting approval can be rejected"
            )

        cursor.execute("""
            UPDATE material_requests
            SET approval_status = 'REJECTED', approval_reason = %s
            WHERE id = %s
        """, (reason, request_id))
        conn.commit()

        return {
            "message": "Material request rejected successfully",
            "request_id": request_id,
            "request_no": request["request_no"],
            "approval_status": "REJECTED",
            "reason": reason
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


@app.get("/api/purchase-orders")
def get_purchase_orders():
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    try:
        cursor.execute("""
            SELECT po.id, po.po_number, po.status, po.expected_receiving_date, po.created_at,
                   mr.request_no, mr.quantity, m.material_name, m.unit,
                   u.username AS approved_by_username
            FROM purchase_orders po
            JOIN material_requests mr ON po.request_id = mr.id
            JOIN materials m ON mr.material_id = m.id
            LEFT JOIN users u ON mr.approved_by = u.id
            ORDER BY po.created_at DESC
        """)
        return cursor.fetchall()
    finally:
        cursor.close()
        conn.close()


@app.get("/api/material-receiving")
def get_material_receiving():
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    try:
        cursor.execute("""
            SELECT mrv.id, mrv.ordered_quantity, mrv.received_quantity, mrv.status, mrv.receiving_date,
                   po.po_number, m.material_name, m.unit
            FROM material_receiving mrv
            JOIN purchase_orders po ON mrv.po_id = po.id
            JOIN material_requests mr ON po.request_id = mr.id
            JOIN materials m ON mr.material_id = m.id
            WHERE mrv.status != 'RECEIVED'
            ORDER BY mrv.id DESC
        """)
        return cursor.fetchall()
    finally:
        cursor.close()
        conn.close()


@app.post("/api/material-receiving/{receiving_id}/receive")
def record_receipt(receiving_id: int, data: ReceiveRequest):
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    try:
        cursor.execute("SELECT * FROM material_receiving WHERE id = %s", (receiving_id,))
        rec = cursor.fetchone()
        if not rec:
            raise HTTPException(status_code=404, detail="Receiving record not found")

        new_received = float(rec["received_quantity"]) + data.quantity
        if new_received > float(rec["ordered_quantity"]):
            raise HTTPException(status_code=400, detail="Received quantity exceeds ordered quantity")
        new_status = "RECEIVED" if new_received >= float(rec["ordered_quantity"]) else "PARTIAL"

        cursor.execute(
            "UPDATE material_receiving SET received_quantity = %s, status = %s, "
            "receiving_date = CURRENT_TIMESTAMP WHERE id = %s",
            (new_received, new_status, receiving_id)
        )

        cursor.execute("SELECT request_id FROM purchase_orders WHERE id = %s", (rec["po_id"],))
        request_id = cursor.fetchone()["request_id"]
        cursor.execute("SELECT material_id FROM material_requests WHERE id = %s", (request_id,))
        material_id = cursor.fetchone()["material_id"]

        cursor.execute(
            "UPDATE inventory SET available_quantity = available_quantity + %s, "
            "incoming_quantity = GREATEST(incoming_quantity - %s, 0) WHERE material_id = %s",
            (data.quantity, data.quantity, material_id)
        )

        if new_status == "RECEIVED":
            cursor.execute("UPDATE purchase_orders SET status = 'RECEIVED' WHERE id = %s", (rec["po_id"],))
            cursor.execute("UPDATE material_requests SET status = 'RECEIVED' WHERE id = %s", (request_id,))

        conn.commit()
        return {"message": "Receipt recorded", "received_quantity": new_received, "status": new_status}
    except HTTPException:
        conn.rollback()
        raise
    except Exception:
        conn.rollback()
        raise
    finally:
        cursor.close()
        conn.close()


@app.get("/api/inventory")
def get_inventory():
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    try:
        cursor.execute("""
            SELECT inv.id, inv.material_id, inv.available_quantity, inv.incoming_quantity,
                   inv.low_stock_threshold, m.material_name, m.unit
            FROM inventory inv
            JOIN materials m ON inv.material_id = m.id
            ORDER BY m.material_name
        """)
        return cursor.fetchall()
    finally:
        cursor.close()
        conn.close()


@app.get("/api/dashboard/summary")
def get_dashboard_summary():
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    try:
        cursor.execute("""
            SELECT
                COUNT(*) AS total,
                SUM(CASE WHEN status = 'PENDING_VERIFICATION' THEN 1 ELSE 0 END) AS pending_verification,
                SUM(CASE WHEN status = 'VERIFIED' THEN 1 ELSE 0 END) AS verified,
                SUM(CASE WHEN status = 'REJECTED' THEN 1 ELSE 0 END) AS rejected
            FROM material_requests
        """)
        counts = cursor.fetchone()
        pending_verification = int(counts["pending_verification"] or 0)
        verified = int(counts["verified"] or 0)
        rejected = int(counts["rejected"] or 0)

        cursor.execute("SELECT COUNT(*) AS total FROM materials")
        material_count = cursor.fetchone()["total"] or 0

        cursor.execute("SELECT COUNT(*) AS c FROM material_requests WHERE approval_status = 'APPROVED'")
        approved_count = cursor.fetchone()["c"] or 0

        cursor.execute("SELECT COUNT(*) AS c FROM purchase_orders WHERE status = 'PO_CREATED'")
        po_created_count = cursor.fetchone()["c"] or 0

        cursor.execute("SELECT COUNT(*) AS c FROM material_receiving WHERE status = 'RECEIVED'")
        received_count = cursor.fetchone()["c"] or 0

        cursor.execute("""
            SELECT
                SUM(CASE WHEN available_quantity <= 0 THEN 1 ELSE 0 END) AS out_c,
                SUM(CASE WHEN available_quantity > 0 AND available_quantity <= low_stock_threshold THEN 1 ELSE 0 END) AS low_c,
                SUM(CASE WHEN available_quantity > low_stock_threshold THEN 1 ELSE 0 END) AS healthy_c
            FROM inventory
        """)
        inv_row = cursor.fetchone()
        out_count = int(inv_row["out_c"] or 0)
        low_count = int(inv_row["low_c"] or 0)
        healthy_count = int(inv_row["healthy_c"] or 0)

        cursor.execute("""
            SELECT
                mr.request_no AS id, m.material_name AS material,
                CONCAT(mr.quantity, ' ', m.unit) AS qty,
                mr.request_type AS type, mr.status,
                CASE
                    WHEN mr.status = 'PENDING_VERIFICATION' THEN 'Waiting for receiver verification'
                    WHEN mr.status = 'VERIFIED' THEN 'Verified Â· awaiting purchase review'
                    ELSE mr.status
                END AS note
            FROM material_requests mr
            JOIN materials m ON mr.material_id = m.id
            WHERE mr.status IN ('PENDING_VERIFICATION', 'VERIFIED')
            ORDER BY mr.id DESC
            LIMIT 5
        """)
        attention = []
        for row in cursor.fetchall():
            attention.append({
                "id": row["id"], "material": row["material"], "qty": row["qty"],
                "type": row["type"], "note": row["note"],
                "tone": "violet" if row["status"] == "VERIFIED" else "warning"
            })

        cursor.execute("""
            SELECT mr.request_no, mr.status, mr.created_at, u.username
            FROM material_requests mr
            JOIN users u ON mr.created_by = u.id
            ORDER BY mr.created_at DESC
            LIMIT 5
        """)
        activity = []
        for row in cursor.fetchall():
            status = row["status"]
            if status == "VERIFIED":
                action, tone = "verified", "success"
            elif status == "REJECTED":
                action, tone = "rejected", "danger"
            else:
                action, tone = "created", "primary"
            activity.append({
                "who": row["username"], "action": action, "target": row["request_no"],
                "when": row["created_at"].strftime("%d %b %Y %H:%M"), "tone": tone
            })

        return {
            "counts": {
                "pendingVerification": pending_verification,
                "verified": verified,
                "pendingApproval": verified,
                "approved": approved_count,
                "poCreated": po_created_count,
                "received": received_count,
                "rejected": rejected
            },
            "trend": {
                "pendingVerification": [], "approved": [],
                "purchaseOrders": [], "received": []
            },
            "inventory": {
                "skus": int(material_count),
                "healthy": healthy_count, "low": low_count, "out": out_count
            },
            "attention": attention,
            "activity": activity
        }
    finally:
        cursor.close()
        conn.close()


@app.post("/api/bom-components")
def add_bom_component(data: BomComponentIn):
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    try:
        for mat_id in (data.output_material_id, data.component_material_id):
            cursor.execute("SELECT id FROM materials WHERE id = %s", (mat_id,))
            if not cursor.fetchone():
                raise HTTPException(status_code=404, detail=f"Material {mat_id} does not exist")

        try:
            cursor.execute(
                "INSERT INTO bom_components (output_material_id, component_material_id, qty_per_unit) "
                "VALUES (%s, %s, %s)",
                (data.output_material_id, data.component_material_id, data.qty_per_unit)
            )
        except MySQLError as err:
            if err.errno == 1062:
                raise HTTPException(status_code=400, detail="This component is already part of the BOM for this material")
            raise

        conn.commit()
        return {"id": cursor.lastrowid}
    except HTTPException:
        conn.rollback()
        raise
    finally:
        cursor.close()
        conn.close()


@app.get("/api/bom-components/{output_material_id}")
def get_bom_components(output_material_id: int):
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    try:
        cursor.execute("""
            SELECT bc.id, bc.component_material_id, m.material_name, m.unit, bc.qty_per_unit
            FROM bom_components bc
            JOIN materials m ON bc.component_material_id = m.id
            WHERE bc.output_material_id = %s
        """, (output_material_id,))
        return cursor.fetchall()
    finally:
        cursor.close()
        conn.close()


@app.post("/api/packing-rules")
def add_packing_rule(data: PackingRuleIn):
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    try:
        for mat_id in (data.output_material_id, data.package_material_id):
            cursor.execute("SELECT id FROM materials WHERE id = %s", (mat_id,))
            if not cursor.fetchone():
                raise HTTPException(status_code=404, detail=f"Material {mat_id} does not exist")

        try:
            cursor.execute(
                "INSERT INTO packing_rules (output_material_id, package_material_id, units_per_package) "
                "VALUES (%s, %s, %s)",
                (data.output_material_id, data.package_material_id, data.units_per_package)
            )
        except MySQLError as err:
            if err.errno == 1062:
                raise HTTPException(status_code=400, detail="A packing rule for this material/package pair already exists")
            raise

        conn.commit()
        return {"id": cursor.lastrowid}
    except HTTPException:
        conn.rollback()
        raise
    finally:
        cursor.close()
        conn.close()


@app.get("/api/packing-rules/{output_material_id}")
def get_packing_rules(output_material_id: int):
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    try:
        cursor.execute("""
            SELECT pr.id, pr.package_material_id, m.material_name, m.unit, pr.units_per_package
            FROM packing_rules pr
            JOIN materials m ON pr.package_material_id = m.id
            WHERE pr.output_material_id = %s
        """, (output_material_id,))
        return cursor.fetchall()
    finally:
        cursor.close()
        conn.close()


def execute_conversion(output_material_id: int, output_qty: float, user_id: int):
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    try:
        cursor.execute("SELECT id FROM materials WHERE id = %s", (output_material_id,))
        if not cursor.fetchone():
            raise HTTPException(status_code=404, detail=f"Material {output_material_id} does not exist")

        cursor.execute(
            "SELECT component_material_id, qty_per_unit FROM bom_components WHERE output_material_id = %s",
            (output_material_id,)
        )
        bom_rows = cursor.fetchall()
        if not bom_rows:
            raise HTTPException(status_code=400, detail="No BOM defined for this material")

        required = {row["component_material_id"]: float(row["qty_per_unit"]) * output_qty for row in bom_rows}

        cursor.execute(
            "SELECT package_material_id, units_per_package FROM packing_rules WHERE output_material_id = %s",
            (output_material_id,)
        )
        packing_rows = cursor.fetchall()
        packages_needed = {}
        for p in packing_rows:
            qty = int(output_qty // int(p["units_per_package"]))
            if qty > 0:
                packages_needed[p["package_material_id"]] = qty

        all_needed = dict(required)
        for mat_id, qty in packages_needed.items():
            all_needed[mat_id] = all_needed.get(mat_id, 0) + qty

        shortages = []
        for mat_id, needed_qty in all_needed.items():
            cursor.execute("SELECT available_quantity FROM inventory WHERE material_id = %s", (mat_id,))
            row = cursor.fetchone()
            available = float(row["available_quantity"]) if row else 0
            if available < needed_qty:
                cursor.execute("SELECT material_name, unit FROM materials WHERE id = %s", (mat_id,))
                mat = cursor.fetchone()
                mat_label = f"{mat['material_name']} ({mat['unit']})" if mat else f"material_id {mat_id}"
                shortages.append(f"{mat_label} â€” need {needed_qty}, have {available}")

        if shortages:
            raise HTTPException(status_code=400, detail="Insufficient stock: " + "; ".join(shortages))

        cursor.execute(
            "INSERT INTO conversion_transactions (output_material_id, output_qty, created_by) "
            "VALUES (%s, %s, %s)",
            (output_material_id, output_qty, user_id)
        )
        txn_id = cursor.lastrowid

        for mat_id, qty in required.items():
            cursor.execute(
                "UPDATE inventory SET available_quantity = available_quantity - %s WHERE material_id = %s",
                (qty, mat_id)
            )
            cursor.execute(
                "INSERT INTO conversion_transaction_lines (transaction_id, material_id, qty_change, line_type) "
                "VALUES (%s, %s, %s, 'BOM_COMPONENT')",
                (txn_id, mat_id, -qty)
            )

        for mat_id, qty in packages_needed.items():
            cursor.execute(
                "UPDATE inventory SET available_quantity = available_quantity - %s WHERE material_id = %s",
                (qty, mat_id)
            )
            cursor.execute(
                "INSERT INTO conversion_transaction_lines (transaction_id, material_id, qty_change, line_type) "
                "VALUES (%s, %s, %s, 'PACKAGING')",
                (txn_id, mat_id, -qty)
            )

        cursor.execute(
            "INSERT INTO inventory (material_id, available_quantity) VALUES (%s, %s) "
            "ON DUPLICATE KEY UPDATE available_quantity = available_quantity + %s",
            (output_material_id, output_qty, output_qty)
        )
        cursor.execute(
            "INSERT INTO conversion_transaction_lines (transaction_id, material_id, qty_change, line_type) "
            "VALUES (%s, %s, %s, 'OUTPUT')",
            (txn_id, output_material_id, output_qty)
        )

        conn.commit()
        return {"transaction_id": txn_id, "output_qty": output_qty, "packages_used": packages_needed}
    except HTTPException:
        conn.rollback()
        raise
    except Exception:
        conn.rollback()
        raise
    finally:
        cursor.close()
        conn.close()


@app.post("/api/conversions")
def create_conversion(data: ConversionIn):
    return execute_conversion(data.output_material_id, data.output_qty, user_id=1)


@app.get("/api/conversions")
def list_conversions():
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    try:
        cursor.execute("""
            SELECT ct.id, ct.output_qty, ct.created_at,
                   m.material_name AS output_material, u.username AS created_by_username
            FROM conversion_transactions ct
            JOIN materials m ON ct.output_material_id = m.id
            JOIN users u ON ct.created_by = u.id
            ORDER BY ct.created_at DESC
        """)
        return cursor.fetchall()
    finally:
        cursor.close()
        conn.close()


@app.get("/api/conversions/{transaction_id}")
def get_conversion_detail(transaction_id: int):
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    try:
        cursor.execute("""
            SELECT ctl.material_id, m.material_name, m.unit, ctl.qty_change, ctl.line_type
            FROM conversion_transaction_lines ctl
            JOIN materials m ON ctl.material_id = m.id
            WHERE ctl.transaction_id = %s
        """, (transaction_id,))
        lines = cursor.fetchall()
        if not lines:
            raise HTTPException(status_code=404, detail="Transaction not found")
        return {"transaction_id": transaction_id, "lines": lines}
    finally:
        cursor.close()
        conn.close()
