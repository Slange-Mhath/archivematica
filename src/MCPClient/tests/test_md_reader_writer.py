from __future__ import unicode_literals
import collections
import csv
import os
import random
import shutil
import sys
import tempfile
import unittest
import uuid

import scandir
from django.test import TestCase

from lxml import etree

THIS_DIR = os.path.dirname(os.path.abspath(__file__))
sys.path.append(os.path.abspath(os.path.join(THIS_DIR, "../lib/clientScripts")))
sys.path.append(
    os.path.abspath(os.path.join(THIS_DIR, "../../archivematicaCommon/lib"))
)

import pytest
from lxml import etree

import metsrw
from metsrw.plugins.premisrw import PREMIS_3_0_NAMESPACES

from fpr.models import FPRule
from main.models import (
    Agent,
    DashboardSetting,
    Directory,
    Event,
    File,
    FPCommandOutput,
    RightsStatement,
    Transfer,
)


@pytest.fixture()
def transfer(db):
    return Transfer.objects.create(
        uuid=uuid.uuid4(), currentlocation=r"%transferDirectory%"
    )
