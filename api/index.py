# Vercel serverless entry — exposes the Flask `app` (WSGI) from server.py.
# Vercel's @vercel/python runtime serves the `app` object below.
import os, sys
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from server import app  # noqa: F401  (`app` is the WSGI application Vercel serves)
