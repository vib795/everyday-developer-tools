from flask import Flask, render_template, request, make_response
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
from helper import generate_basic_pattern, generate_json_schema, generate_sample_data
from datetime import datetime
import pytz
import os