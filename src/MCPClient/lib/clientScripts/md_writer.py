import collections
import copy
from glob import glob
from itertools import chain
import lxml.etree as etree
import os
from pprint import pprint
import re
import sys
import traceback
from uuid import uuid4
import json
import datetime
import decimal

import django
import scandir
from django.forms.models import model_to_dict

from job import Job

from itertools import groupby
from operator import itemgetter


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
    Job
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
        if isinstance(v, decimal.Decimal):
            file_as_dict.update({k: str(v)})
    return file_as_dict


def get_files_in_sip(sip_uuid):
    """
    Get all files related to the package and return them as json files
    """
    files_in_sip = []
    for file_object in File.objects.filter(sip=sip_uuid).values():
        files_in_sip.append(file_object)
    return files_in_sip


def transform_to_json(dict_list):
    """
    transform list of dictionaries into a list of json
    """
    # files_as_json = []
    # for file_as_dict in dict_list:
    converted_dict = convert_date_format_values(dict_list)
    #     files_as_json.append(json.dumps(converted_dict))
    dict_as_json = json.dumps(converted_dict)
    return dict_as_json


# def get_file_objs_as_json(sip_uuid):
#     """
#     get a list of all files from a sip as json
#     TODO: Problem with this approach is, that its running one superficial
#     iteration, due to seperation of concerns. It would also be possible to
#     transform the files into dicts and json objects in one iteration instead
#     of saving them as dicts in a list first and transforming them to json later.
#     This can be changed if we are sure which format we want to use.
#     """
#     files_as_json = transform_to_json(get_files_in_sip(sip_uuid))
#     return files_as_json


# TODO: Get all file objs in a sip and calc the file sizes
#  to get the size of the sip
# def get_file_obj_as_json(sip_uuid):
#     """
#     Get all files related to the package and return them as json files
#     """
#     files_as_json = []
#     for file_object in File.objects.filter(sip=sip_uuid).values():
#         # file_object.transfer gives back the transfer object which is related
#         # to the file object which means I could use the dot notation to get
#         # information of the transfer
#
#         file_as_dict = convert_date_format_values(file_object)
#         files_as_json.append(json.dumps(file_as_dict))
#     return files_as_json


def get_event_objs(sip_uuid):
    event_list = []
    for event in Event.objects.filter(file_uuid__sip__uuid=sip_uuid).values():
        event_list.append(convert_date_format_values(event))
    return event_list


def get_sip_objs(sip_uuid):
    list_of_sips = []
    for sip in SIP.objects.filter(uuid=sip_uuid).values():
        list_of_sips.append(sip)
    return list_of_sips


def get_agents_objs(sip_uuid):
    agents_as_json = []
    for agent in Agent.objects.filter(
            event__file_uuid__sip__uuid=sip_uuid).distinct().values():
        agents_as_json.append(agent)
    return agents_as_json


# def get_job_obj_as_json(sip_uuid):
#     jobs_as_json = []
#     for job in Job.objects.filter(sipuuid=sip_uuid).values():
#         jobs_as_json.append(job)
#     return jobs_as_json


def get_file_size_of_sip(list_of_files):
    """
    Sum up the size values of the files to get the size of the sip.
    """
    sip_size = 0
    for f in list_of_files:
        sip_size += f.get("size")
    return sip_size


def metadata_writer(sip_uuid):
    """
    'Main'function which writes the MD
    """
    sip_files = get_sip_objs(sip_uuid)
    agents = get_agents_objs(sip_uuid)
    event_list = get_event_objs(sip_uuid)
    sip_file = sip_files[0]
    list_of_files = get_files_in_sip(sip_uuid)
    #sip_size = get_file_size_of_sip(list_of_files)
    #amount_of_files = len(list_of_files)
    metadata_info = {
        "collection_name": sip_file.get("aip_filename"),
        "accession_id": sip_file.get("uuid"),
        #"sip_size": sip_size,
        "aip_creation_date": sip_file.get("createdtime").strftime("%m/%d/%Y, %H:%M:%S %z, %Z"),
        "sip_path": sip_file.get("currentpath"),
        "number_of_files": len(list_of_files),
        "files": list_of_files,
        "events_agents": agents,
        #"events": event_list,
        # Cant I use the jobs getting called for jobs in job and save them as a counter?
    }
    metadata_info_json = json.dumps(metadata_info)
    pprint(metadata_info_json)
    return metadata_info_json


def get_md_info(sip_uuid):
    """
    Get all files related to the package and return them as dict
    """
    sip_files = get_sip_objs(sip_uuid)
    list_of_files = []
    """TODO: This has to be optimised. I want to get all the events where the 
    file_uuid_id is = the uuid of the file_object and add them to the respective
    file_object events key. 
    To avoid the for loop inside the for loop its maybe better to pull a list
    of events through the get_events function and merge the file list and event
    list to match file_uuid_id of an event with uuid of a file and add the event
    to the file dict"""
    md_info = {
        "Collection name": sip_files[0].get("aip_filename"),
        "Accession ID": sip_uuid,
        "AIP creation date": sip_files[0].get("createdtime").strftime(
            "%m/%d/%Y, %H:%M:%S %z, %Z"),
    }
    for file_object in File.objects.filter(sip=sip_uuid).values():
        file_object_info = {}
        file_object_info.update(
            {"Current file path": file_object.get("currentlocation"),
             "Original file path": file_object.get("originallocation"),
             "Last modified": file_object.get("modificationtime"),
             "Checksum Type": file_object.get("checksumtype"),
             "Checksum": file_object.get("checksum"),
             "Object ID": file_object.get("uuid"),
             "File Size": file_object.get("size"), })
        list_of_files.append(file_object_info)
        event_list = []
        for event in Event.objects.filter(
                file_uuid_id=file_object.get("uuid")).values():
            if event.get("event_type") == "validation":
                file_object_info.update(
                    {"File Format": event.get("event_outcome_detail")})
            event_info = {}
            event_info.update({"Event ID": event.get("event_id")})
            event_list.append(convert_date_format_values(event_info))
        file_object_info.update({"events": event_list})
        list_of_files.append(convert_date_format_values(file_object_info))
    md_info.update({"files": list_of_files})
    metadata_info_json = json.dumps(md_info)
    pprint(metadata_info_json)
    return metadata_info_json

