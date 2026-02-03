# Jalankan pengujian backend
cd backend
pytest -v --cov=app --cov-report=html:cov_html_backend

# Jalankan pengujian scanner
cd ../scanner
pytest -v --cov=app --cov-report=html:cov_html_scanner

# Jalankan pengujian khusus
cd tests
python stress_concurrency.py
python memory_profile.py
