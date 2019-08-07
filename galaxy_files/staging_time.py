"""The module describes the ``uname`` job metrics plugin."""
from . import InstrumentPlugin
from .. import formatting
import os.path
import logging

log = logging.getLogger(__name__)


class StagingTimeFormatter(formatting.JobMetricFormatter):

    def format(self, key, value):
        return key, value


class StagingTimePlugin(InstrumentPlugin):
    """ Use uname to gather operating system information about remote system
    job is running on. Linux only.
    """
    plugin_type = "staging_time"
    formatter = StagingTimeFormatter()

    def __init__(self, **kwargs):
        pass

    def job_properties(self, job_id, job_directory):
        result = {}

        preprocess_time_path = self._instrument_file_path(job_directory, "preprocessing_time")
        if os.path.isfile(preprocess_time_path):
            with open(preprocess_time_path) as f:
                result["preprocessing_time"] = f.read()

        return result


__all__ = ('StagingTimePlugin', )