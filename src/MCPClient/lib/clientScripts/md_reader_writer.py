import collections
import copy
from glob import glob
from itertools import chain
import lxml.etree as etree
import os
import pprint
import re
import sys
import traceback
from uuid import uuid4

from __future__ import unicode_literals

import argparse
import logging
import os
import uuid

import django
import scandir
from lxml import etree
from django.db.models import Prefetch

import django
import scandir

django.setup()
# dashboard
from django.utils import timezone
from main.models import (
    Agent,
    Derivation,
    Directory,
    DublinCore,
    Event,
    File,
    FileID,
    FPCommandOutput,
    SIP,
    SIPArrange,
    Transfer
)


def get_transfer(transfer_id):
    transfer = Transfer.objects.get(uuid=transfer_id)
    return transfer


def get_file(file_id):
    file = File.objects.get(uuid=file_id)
    return file