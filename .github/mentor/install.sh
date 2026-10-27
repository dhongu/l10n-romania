# What test.yml installs besides test-requirements.txt, for Mentor's screenshots job
# (sourced by terrabit-solutions/ci-agents, after the private clones, without credentials).
# Keep in step with test.yml.
pip install "requests>=2.27.0"
# Keep the cryptography of the image (see test.yml): pdfminer.six would upgrade it and
# break pyOpenSSL, so Odoo no longer starts.
pip freeze | grep -i '^cryptography==' >> test-requirements.txt
if [ -f requirements.txt ]; then pip install -r requirements.txt; fi
