# -*- coding: utf-8 -*-
from __future__ import unicode_literals
import os
import sys
import uuid
import pytest
from lxml import etree
import namespaces as ns

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
    SIP,
)


THIS_DIR = os.path.dirname(os.path.abspath(__file__))
sys.path.append(os.path.abspath(os.path.join(THIS_DIR, "../lib/clientScripts")))

from create_mets_v2 import createDMDIDsFromCSVMetadata
from md_writer import create_md_object
from create_mets_v2 import createEvent


@pytest.fixture()
def subdir_path(tmp_path):
    subdir = tmp_path / "subdir1"
    subdir.mkdir()

    return subdir


@pytest.fixture()
def sip(db):
    sip = SIP.objects.create(
        uuid="ae8d4290-fe52-4954-b72a-0f591bee2e2f",
    )
    return sip


@pytest.fixture()
def empty_subdir_path(tmp_path):
    empty_subdir = tmp_path / "subdir2-empty"
    empty_subdir.mkdir()

    return empty_subdir


@pytest.fixture()
def transfer(db):
    return Transfer.objects.create(
        uuid=uuid.uuid4(), currentlocation=r"%transferDirectory%", description= "nicer Transfer"
    )


@pytest.fixture()
def file_path(subdir_path):
    file_path = subdir_path / "file1"
    file_path.write_text("Hello world")

    return file_path


@pytest.fixture()
def file_path2(subdir_path):
    file_path = subdir_path / "file2"
    file_path.write_text("Hello world")

    return file_path


@pytest.fixture()
def file_obj(db, transfer, tmp_path, file_path, sip):
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


def test_create_md_object(file_obj):
    """
    assert that the create_digiprovMD function returns digiprovMD data
    """
    file_list = None
    file_list = create_md_object(file_obj)
    print(file_list)
    assert file_list is not None
