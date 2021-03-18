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

THIS_DIR = os.path.dirname(os.path.abspath(__file__))
sys.path.append(os.path.abspath(os.path.join(THIS_DIR, "../lib/clientScripts")))
sys.path.append(
    os.path.abspath(os.path.join(THIS_DIR, "../../archivematicaCommon/lib"))
)


def create_md_object(file_object):
    file_list = []
    files_as_dict = []
    for file_object in File.objects.filter(uuid=file_object.uuid):
        print(file_object.checksum, file_object.currentlocation, file_object.transfer, file_object.size)
        # file_object.transfer gives back the transfer object which is related
        # to the file object which means I could use the dot notation to get
        # information of the transfer
        file_list.append(file_object)
        files_as_dict.append(vars(file_object))
    return files_as_dict



