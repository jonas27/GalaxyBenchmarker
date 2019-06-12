"""
Definition of different workflow-types.
"""
import planemo_bridge
import os
import logging
from galaxy_bridge import Galaxy
from destination import BaseDestination, PulsarMQDestination

log = logging.getLogger("GalaxyBenchmarker")


class BaseWorkflow:
    description = ""

    def __init__(self, name, path):
        if not os.path.isfile(path):
            raise IOError("Workflow-File at '{path}' in workflow '{wf_name}' could not be found".format(path=path,
                                                                                                        wf_name=name))
        self.path = path
        self.name = name

    def run(self, dest: BaseDestination):
        """
        Starts workflow
        """
        raise NotImplementedError


class GalaxyWorkflow(BaseWorkflow):
    def __init__(self, name, path):
        super().__init__(name, path)

    def run(self, dest: PulsarMQDestination, glx: Galaxy):
        log.info("Running workflow '{wf_name}' using Planemo".format(wf_name=self.name))
        return planemo_bridge.run_planemo(glx, dest, self.path)


class CondorWorkflow(BaseWorkflow):
    def __init__(self, name, path):
        super().__init__(name, path)

    def deploy_to_condor_manager(self):
        # Use ansible-playbook to upload *.job-file to Condor-Manager
        raise NotImplementedError

    def run(self, dest: BaseDestination):
        # TODO: Prepare Shell-Script, upload it to Condor-Manager and run it
        raise NotImplementedError


def configure_workflow(wf_config):
    if wf_config["type"] not in ["Galaxy"]:
        raise ValueError("Workflow-Type '{type}' not valid".format(type=wf_config["type"]))

    if wf_config["type"] == "Galaxy":
        workflow = GalaxyWorkflow(wf_config["name"], wf_config["path"])
        if "description" in wf_config:
            workflow.description = wf_config["description"]

    return workflow
