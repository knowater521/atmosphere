"""
  Boot script model for atmosphere.
"""
import time
import requests
from hashlib import md5
import pytz

from django.db import models
from django.db.models import Q
from django.utils import timezone
from django.utils.text import slugify

from threepio import logger
from uuid import uuid4
from core.models.instance import Instance
from core.models.application import Application


class ScriptType(models.Model):

    """
    ScriptType objects are created by developers,
    they should NOT be added/removed unless there
    are corresponding logic-choices in core code.
    """
    name = models.CharField(max_length=128)
    description = models.TextField(null=True, blank=True)

    class Meta:
        db_table = 'script_type'
        app_label = 'core'

    def __unicode__(self):
        return self.name


class BootScript(models.Model):

    """
    BootScripts can be created as an isolated unit, before they are associated
    with a specific application or instance.
    """
    uuid = models.UUIDField(default=uuid4, unique=True, editable=False)
    title = models.CharField(max_length=128)
    created_by = models.ForeignKey("AtmosphereUser")
    script_type = models.ForeignKey(ScriptType)
    script_text = models.TextField()
    # If True: run on resume, start, restart, and Initial Launch
    # If False: run on Initial Launch ONLY
    run_every_deploy = models.BooleanField(default=False)
    wait_for_deploy = models.BooleanField(default=True)

    applications = models.ManyToManyField(Application, related_name='scripts')
    instances = models.ManyToManyField(Instance, related_name='scripts')

    def get_title_slug(self):
        """
        Return a slug,
        But replace all hyphens(-) with underscores(_)
        """
        return slugify(self.title).replace('-', '_')

    def get_text(self, clean=True):
        raw_text = ""
        if self.script_type.name == 'Raw Text':
            raw_text = self.script_text.strip()  # Remove whitespace
        elif self.script_type.name == 'URL':
            raw_text = self._text_from_url()
        if clean:
            return BootScript._clean_script_text(raw_text)
        return raw_text

    @classmethod
    def _clean_script_text(self, raw_text):
        """
        Remove special characters from boot-scripts to avoid ansible failures.
        """
        if not raw_text:
            return ""
        elif type(raw_text) == unicode:
            return raw_text.encode('ascii', 'ignore')
        elif type(raw_text) == str:
            return raw_text.decode('unicode_escape').encode('ascii', 'ignore')
        else:
            raise TypeError("Expected type of 'raw_text' to be unicode/str. Found: %s" % type(raw_text))

    def _text_from_url(self):
        """
        """
        req = requests.get(self.script_text)
        content = req.content
        return content

    def __unicode__(self):
        return "%s <%s>" % (self.title, self.script_type)

    class Meta:
        db_table = 'boot_script'
        app_label = 'core'


class ApplicationVersionBootScript(models.Model):
    """
    Represents the M2M table auto-created by 'applicationversion.bootscripts'
    """
    image_version = models.ForeignKey("ApplicationVersion",
                                      db_column='applicationversion_id')
    boot_script = models.ForeignKey(BootScript,
                                    db_column="bootscript_id")

    def __unicode__(self):
        return "(ApplicationVersion:%s - BootScript:%s) " %\
            (self.image_version, self.boot_script.title)

    class Meta:
        db_table = 'application_version_boot_scripts'
        app_label = 'core'
        managed = False


# Useful
def get_scripts_for_user(username):
    return BootScript.objects.filter(
        created_by__username=username)


def get_scripts_for_application(application_uuid):
    return BootScript.objects.filter(
        applications__uuid=application_uuid)


def _save_scripts_to_application(application, boot_script_list):
    # Empty when new, otherwise over-write all changes
    old_scripts = application.scripts.all()
    if old_scripts:
        for old_script in old_scripts:
            application.scripts.remove(old_script)
    # Add all new scripts
    for script_id in boot_script_list:
        script = BootScript.objects.get(id=script_id)
        script.applications.add(application)


def _save_scripts_to_instance(instance, boot_script_list):
    # Empty when new, otherwise over-write all changes
    old_scripts = instance.scripts.all()
    if old_scripts:
        for old_script in old_scripts:
            instance.scripts.remove(old_script)
    # Add all new scripts
    for script_id in boot_script_list:
        try:
            if type(script_id) == int:
                query=Q(id=script_id)
            else:
                query=Q(uuid=script_id)
            script = BootScript.objects.get(query)
        except BootScript.DoesNotExist:
            # This 2nd-attempt can be removed when API v1 is removed
            try:
                script = BootScript.objects.get(id=script_id)
            except BootScript.DoesNotExist:
                continue

        script.instances.add(instance)
