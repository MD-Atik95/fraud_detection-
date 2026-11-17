# Credit Card Fraud Detection System (Python)

Real-time CNP fraud scoring gateway following the SRS slides: ML ensemble (XGBoost + LightGBM + Random Forest)
with SMOTE + undersampling, hybrid rule override, SHAP explanations, automated block / MFA, Twilio + SendGrid
alerts, Celery/Redis, PostgreSQL, Streamlit dashboard, Docker.

## Desktop app (double-click)
**Windows:** double-click `Start_App.bat`. First run installs packages (a few minutes), then the Fraud Monitor opens in its own
app window. **Mac/Linux:** `./start_app.sh`. Or run `python run_app.py` from VS Code.
If the native window cannot open, it opens in your browser instead. Windows 10/11 already include the required WebView2.
The included model uses the synthetic data (best for demos). To use the real Kaggle data run
`python -m fraud.train --csv data/creditcard.csv` once, then start the app again.

## Web app
Start the API, then open **http://localhost:8000/** - the HTML/CSS/JS frontend is served by FastAPI itself
(login admin / admin123): live overview, scoring with SHAP, case queue, editable rules, model metrics.
The Streamlit dashboard is optional.

## Run locally
```bash
pip install -r requirements.txt
python -m fraud.train                 # trains on synthetic data, saves models/fraud_model.joblib
uvicorn fraud.api:app --reload        # API docs: http://localhost:8000/docs
streamlit run fraud/dashboard.py      # dashboard (login: admin / admin123)
pytest -q tests                       # tests
```
## Docker
`docker compose up --build`  (API :8000, dashboard :8501, Redis, PostgreSQL, Celery worker)

## Score a transaction
```bash
TOKEN=$(curl -s -X POST localhost:8000/token -d "username=admin&password=admin123" | python -c "import sys,json;print(json.load(sys.stdin)['access_token'])")
curl -X POST localhost:8000/score -H "Authorization: Bearer $TOKEN" -H "Content-Type: application/json" \
  -d '{"txn_id":"T1","card_id":"4111111111111111","amount":900,"mcc":7995,"ip":"10.0.0.1","ip_country":"RU","device_new":true}'
```
## Using the real Kaggle dataset (creditcard.csv)
1. `creditcard.csv` is already included in the `data/` folder.
2. Train on it:  `python -m fraud.train --csv data/creditcard.csv`  (about 2-5 minutes)
3. Start the API (`uvicorn fraud.api:app --reload`). `/health` now shows `"mode": "csv"`.
4. Send real rows through the API:  `python -m fraud.replay --csv data/creditcard.csv --legit 30 --fraud 10`
5. Open the dashboard: the transactions and case queue fill up with the replayed rows.

In CSV mode use `POST /score/raw` (body: `txn_id`, optional `card_id`, `ip`, `mcc`, and `features` = the CSV columns
Time, V1..V28, Amount). `/score` is only for the synthetic model. Blacklisted-IP and high-risk-MCC rules still work
if you send `ip` / `mcc`; impossible-travel needs location data, which this dataset does not have.
To go back to the synthetic model run `python -m fraud.train` again.

Measured on a 25% hold-out of the Kaggle data: accuracy 99.90%, recall 85.4%, precision 67.7%, ROC-AUC 0.983.
Recall is below the 92% target in the slides, and lowering the threshold only helps a little (see report notes).

## Decision logic
| Final score | Action |
|---|---|
| blacklisted IP or >= 0.95 | BLOCK (card blocked) |
| > 0.85 | MFA (step-up verification) |
| 0.50 - 0.85 | REVIEW (investigator case queue) |
| < 0.50 | APPROVE |

Hard rules (`rules.json`: blacklisted IPs, impossible travel, high-risk MCC) can only raise the ML score.
Reload them without restart: `POST /rules/reload`.

## Notes
* Training data is synthetic (`fraud/data.py`). For real use, replace `generate()` with your bank's labelled data
  and keep the same feature columns (or edit `FEATURES` in `fraud/config.py` + `Scorer.build_features`).
* Alerts are only logged until you set `TWILIO_*`, `SENDGRID_KEY`, `INVESTIGATOR_EMAIL`.
* Change `JWT_SECRET`, `ADMIN_USER`, `ADMIN_PASS` before any real deployment.
* Kubernetes manifests are not included; the Docker images are ready to be deployed there.
