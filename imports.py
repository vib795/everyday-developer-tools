from flask import Flask, render_template, request, make_response, jsonify, send_file, session
from markupsafe import escape
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
import concurrent.futures

import difflib  # For Diff viewer
import re  # For Regex checking
from jsonschema import validate
from jsonschema.exceptions import ValidationError  # For JSON validation
import json
import logging 
import base64
from helper import generate_basic_pattern, generate_json_schema, generate_sample_data, generate_sample, generate_fake_data
from datetime import datetime
import pytz
import os
import yaml
import string
import random
from collections import Counter
import jwt
from io import StringIO
import csv

import tempfile

from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import letter
from PyPDF2 import PdfReader
import markdown
import io
from dotenv import load_dotenv


from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, ListFlowable, ListItem
from reportlab.lib import colors
