# Payment Reconciliation Service 💳

A high-performance backend service designed to ingest payment lifecycle events and identify reconciliation discrepancies. This solution focuses on data integrity, idempotency, and query optimization for high-volume financial data.

🎥 **[Link to Video Walkthrough](https://drive.google.com/file/d/1nk5gqyiI-3n1aRm9bp8e-hHUJaDI13f2/view?usp=drive_link)**
---

## 🏗 Architecture Overview
The service is built using a layered architectural pattern to ensure separation of concerns:

* **API Layer (FastAPI):** Manages HTTP routing, Pydantic data validation, and automated OpenAPI (Swagger) documentation.
* **Service Layer:** Contains the logic for identifying discrepancies using optimized SQL set-based logic rather than memory-heavy Python loops.
* **Persistence Layer (SQLAlchemy + SQLite):** Handles structured storage and enforces data constraints at the database level.

---

## 🛠 Local Setup & Testing
I have prioritized a **"zero-config"** local setup to ensure reviewers can run and verify the service instantly.

### 1. Clone & Navigate
```bash
git clone [https://github.com/AbinayaVairamuthu/setu-reconciliation-service.git](https://github.com/AbinayaVairamuthu/setu-reconciliation-service.git)
cd setu-reconciliation-service
```
### 2. Install Dependencies
```bash
pip install -r requirements.txt
```
### 3. Data Ingestion (Seed the DB)
Run this script to process the 10,000+ sample events. It handles initial cleaning and prepares the local SQLite database.

```bash
python ingest_actual_data.py
```
### 4. Run the API
Launch the local server to start testing the endpoints.
```bash
uvicorn main:app --reload
```
### 5. Interactive Docs
Access the interactive Swagger UI to test the API directly from your browser:
[http://127.0.0.1:8000/docs](http://127.0.0.1:8000/docs)

---

## 📖 API Documentation & Key Features

### 1. Robust Event Ingestion (`POST /events`)
* **Feature:** Database-Level Idempotency.
* **Logic:** By enforcing a **Unique Constraint** on the `event_id`, the system ensures that retried requests from partners do not create duplicate records, maintaining 100% ledger accuracy.

### 2. Reconciliation Engine (`GET /reconciliation/discrepancies`)
* **Feature:** Set-Based Inconsistency Detection.
* **Logic:** The system identifies transactions that have both a `payment_failed` and a `payment_settled` status.
* **Result:** Identified **95 discrepancies** in the provided dataset.

---

## 🧪 Testing with Postman
I have included a pre-configured Postman collection to simplify the review process.

1. **Import:** Open Postman and import `Setu_Collection.json` from the root folder.
2. **Endpoints:**
   * `POST /events`: Test the ingestion logic and idempotency.
   * `GET /reconciliation/discrepancies`: Retrieve the list of 95 identified discrepancies.
3. **Environment:** The collection is configured to point to `http://127.0.0.1:8000` by default.

---

## ⚖️ Assumptions & Tradeoffs
* **Database Choice:** SQLite was used for portability and ease of review. For a production environment, I would recommend PostgreSQL.
* **Reconciliation:** A discrepancy is defined as any `transaction_id` having conflicting "Success" and "Failure" states within the payment lifecycle.

---

## 🤖 AI Disclosure & Development Methodology
I utilized **Gemini (Google AI)** as a collaborative development assistant during this assignment to ensure the solution followed industry best practices.

### ⚙️ How AI Was Used:
* **Architectural Guidance:** Used to explore the most efficient ways to handle 10,000+ events using high-performance SQL-driven reconciliation logic.
* **Code Generation:** Assisted with FastAPI boilerplate, SQLAlchemy models, and endpoint structures.
* **Documentation Support:** Used to refine README quality and improve the clarity of the Postman collection.

### ✅ Human Ownership & Validation
Despite using AI for acceleration, I maintain full ownership of the logic. I personally:
* **Verified** all reconciliation logic to ensure accuracy.
* **Tested** the full ingestion flow from scratch.
* **Confirmed** the final count of **95 discrepancies**.
* **Ensured** that every specific requirement of the Setu assignment was fully satisfied.
  
---

Thank you for providing such an interesting challenge and for taking the time to review my submission. I really enjoyed building this service, started immediately after getting this mail at evening and completed early morning. Looking forward to hearing your thoughts. Have a great day!
