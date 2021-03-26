# -*- coding: utf-8 -*-
from __future__ import unicode_literals
import os
import sys
import uuid
import pytest
from lxml import etree
import namespaces as ns
from pprint import pprint
import create_mets_v2
import json
import metsrw
from metsrw.plugins.premisrw import PREMIS_3_0_NAMESPACES

from job import Job
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
    SIP,
    Job
)


THIS_DIR = os.path.dirname(os.path.abspath(__file__))
sys.path.append(os.path.abspath(os.path.join(THIS_DIR, "../lib/clientScripts")))

from create_mets_v2 import createDMDIDsFromCSVMetadata
from md_writer import get_event_objs
from md_writer import get_agents_objs
from md_writer import get_files_in_sip
from create_mets_v2 import createEvent
from create_mets_v2 import write_md_file
from md_writer import get_file_size_of_sip
from md_writer import metadata_writer
from md_writer import get_md_info


@pytest.fixture()
def subdir_path(tmp_path):
    subdir = tmp_path / "subdir1"
    subdir.mkdir()

    return subdir


@pytest.fixture()
def state():
    state = create_mets_v2.MetsState()
    return state


@pytest.fixture()
def sip(db, file_path):
    sip = SIP.objects.create(
        uuid="ae8d4290-fe52-4954-b72a-0f591bee2e2f",
        aip_filename="Thats my APE"
    )
    return sip


@pytest.fixture()
def empty_subdir_path(tmp_path):
    empty_subdir = tmp_path / "subdir2-empty"
    empty_subdir.mkdir()

    return empty_subdir


@pytest.fixture()
def transfer(db):
    transfer = Transfer.objects.create(
        uuid="eee15993-af4b-484c-992f-c5b3edebd127",
        currentlocation=r"%transferDirectory%",
        description= "nicer Transfer",
    )
    return transfer


@pytest.fixture()
def file_path(subdir_path):
    file_path = subdir_path / "file"
    file_path.write_text("Hello world")

    return file_path


@pytest.fixture()
def file_path2(subdir_path):
    file_path = subdir_path / "file2"
    file_path.write_text("Hello world")

    return file_path


@pytest.fixture()
def file_obj(db, state, transfer, tmp_path, file_path, sip):
    file_obj_path = "".join(
        [transfer.currentlocation, str(file_path.relative_to(tmp_path))]
    )
    file_obj = File.objects.create(
        uuid="f3c747f0-2e60-48b7-b113-1dc2ebd6eeaf",
        transfer=transfer,
        originallocation=file_obj_path,
        currentlocation=file_obj_path,
        removedtime=None,
        size=113318,
        checksum="35e0cc683d75704fc5b04fc3633f6c654e10cd3af57471271f370309c7ff9dba",
        checksumtype="sha256",
        sip=sip,
        label="my_crazy_filo"
    )
    file_obj.identifiers.create(type="TEST FILE", value="12345")

    return file_obj


@pytest.fixture()
def file_obj2(db, transfer, tmp_path, file_path2, sip):
    file_obj_path = "".join(
        [transfer.currentlocation, str(file_path2.relative_to(tmp_path))]
    )
    return File.objects.create(
        uuid="b85ff1cd-0b6d-4de6-b91a-f60be71b3e1e",
        transfer=transfer,
        originallocation=file_obj_path,
        currentlocation=file_obj_path,
        removedtime=None,
        size=113318,
        checksum="35e0cc683d75704fc5b04fc3633f6c654e10cd3af57471271f370309c7ff9dba",
        checksumtype="sha256",
        sip=sip,
    )


@pytest.fixture()
def event(request, db, file_obj):
    event = Event.objects.create(
        event_id="c985a8cc-fb77-46ff-8063-9a2dda29348c",
        file_uuid=file_obj,
        event_type="message digest calculation",
        event_detail='program="python"; module="hashlib.sha256()"',
        event_outcome_detail="d10bbb2cddc343cd50a304c21e67cb9d5937a93bcff5e717de2df65e0a6309d6",
    )
    event_agent = Agent.objects.create(
        identifiertype="preservation system", identifiervalue="Archivematica-1.9"
    )
    event.agents.add(event_agent)

    return event


@pytest.fixture()
def event2(request, db, file_obj):
    event = Event.objects.create(
        event_id="15f71683-4aae-4723-be31-eec0ba15c63d",
        file_uuid=file_obj,
        event_type="virus check",
        event_detail='program="python"; module="hashlib.sha256()"',
        event_outcome_detail="d10bbb2cddc343cd50a304c21e67cb9d5937a93bcff5e717de2df65e0a6309d6",
    )
    event_agent = Agent.objects.create(
        identifiertype="preservation system", identifiervalue="Archivematica-1.9"
    )
    event.agents.add(event_agent)

    return event


# @pytest.fixture()
# def job(db, sip):
#     job = Job.objects.create(
#         uuid="0b2c7f3c-c73a-4e7d-8334-c547062face8",
#         job_type="Virus scan",
#     )
#     return job


# def test_get_event_obj_as_json(event):
#     event_list = get_event_obj_as_json(event)
#     for e in event_list:
#         print(e)
#     assert event_list is not None


# def test_get_agents_obj_as_json(file_obj, event):
#     agents_list = get_agents_obj_as_json(file_obj.uuid)
#     for a in agents_list:
#         print(a)
#     assert agents_list is not None


def test_write_md_file(file_obj):
    empty = write_md_file("Testname", file_obj.uuid)
    assert empty is not None


def test_get_files_in_sip(file_obj, file_obj2, sip, event, event2):
    files_in_sip = get_files_in_sip(sip.uuid)
    assert len(files_in_sip) == 2


# def test_get_files_objs_in_json(file_obj, file_obj2, sip):
#     json_files = get_file_objs_as_json(sip.uuid)
#     for jf in json_files:
#         pprint(jf)
#     assert len(json_files) == 3


def test_get_file_size_of_sip(file_obj, file_obj2, sip):
    file_size = get_file_size_of_sip(sip.uuid)
    print(file_size)
    assert file_size > file_obj.size


def test_metadata_writer(sip, file_obj, file_obj2, event, event2):
    infos = metadata_writer(sip.uuid)
    assert infos is not None


def test_md_info(sip, file_obj, file_obj2, event, event2):
    infos = get_md_info(sip.uuid)
    assert infos is not None
#
# def test_get_job_obj_as_json(job):
#     jobs_list = get_job_obj_as_json(job.uuid)
#     for j in jobs_list:
#         print(j)
#     assert jobs_list is not None

