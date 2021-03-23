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
import json
import datetime

import django
import scandir
from django.forms.models import model_to_dict

from job import Job
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
    Transfer,
)

THIS_DIR = os.path.dirname(os.path.abspath(__file__))
sys.path.append(os.path.abspath(os.path.join(THIS_DIR, "../lib/clientScripts")))
sys.path.append(
    os.path.abspath(os.path.join(THIS_DIR, "../../archivematicaCommon/lib"))
)


def convert_date_format_values(file_as_dict):
    """
    convert datetime values into Strings to use and access the information
    e.g. in a json object.
    """
    for k, v in file_as_dict.items():
        if isinstance(v, datetime.datetime):
            file_as_dict.update({k: v.strftime("%m/%d/%Y, %H:%M:%S %z, %Z")})
    return file_as_dict


def get_file_obj_as_json(sip_uuid):
    files_as_json = []
    # Get the files that have the sip.uuid xyz
    for file_object in File.objects.filter(sip=sip_uuid).values():
        # file_object.transfer gives back the transfer object which is related
        # to the file object which means I could use the dot notation to get
        # information of the transfer
        # file_as_dict = file_object.__dict__
        file_as_dict = convert_date_format_values(file_object)
        files_as_json.append(json.dumps(file_as_dict))
    return files_as_json


def get_event_obj_as_json(event_object):
    events_as_json = []
    for event_object in Event.objects.filter(id=event_object.id).values():
        event_as_dict = convert_date_format_values(event_object)
        events_as_json.append(event_as_dict)
    return events_as_json


def get_agents_obj_as_json(file_object_id):
    agents_as_json = []
    for agent in Agent.objects.filter(event__file_uuid_id=file_object_id).distinct():
        agents_as_json.append(agent)
    return agents_as_json


def get_job_obj_as_json(job):
    jobs_as_json = []
    for job in Job.objects.filter(uuid=job.uuid):
        jobs_as_json.append(job)
    return jobs_as_json


# TODO: Return list of files which are modified through a certain event like:
# The file x was modified through the event y
# for agent in event_record.agents.all():

# TODO: Maybe think about calling single files and returning single json file objects
# rather than a list.

