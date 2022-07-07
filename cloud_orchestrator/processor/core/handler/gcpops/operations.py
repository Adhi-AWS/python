from google.oauth2 import service_account
from util.core.app.audit_log_transaction import insert_audit_log
from util.core.app.constants import TASK_STATUS
from util.core.app.terraform_resource import TerraformClass
from resource_adapters.providers.gcp.vmoperations import *
from resource_adapters.providers.gcp.diskoperations import *
from resource_adapters.providers.gcp.commonoperations import *
from resource_adapters.providers.gcp.networkoperations import *

from util.core.app.logger import get_logger_func
LOG = get_logger_func(__file__)

class Operations:
    def __init__(self, session, task_id, config, env_vars):
        self.session = session
        self.task_id = task_id
        self.config = config
        self.env_vars = env_vars
        LOG.debug("GCP Operations init method:%s" % config,
                  {'task_id': self.task_id})

    def add_audit_log(self, source, event, trace, status):
        payload = {
            "task_id": self.task_id,
            "source": source,
            "event": event,
            "trace": trace,
            "status": status
        }
        LOG.debug("Insert audit logs:%s" % payload, {'task_id': self.task_id})
        insert_audit_log(payload, session_factory=self.session._session_factory)

    def __call__(self, operation_name, parameters: dict):
        LOG.debug("GCP Operation call:%s" % parameters, {'task_id': self.task_id})
        try:
            self.add_audit_log("GCP Operation", operation_name,
                               "Started", TASK_STATUS.COMPLETED)
            eval(operation_name)(parameters, self.session,
                                 config=self.config,
                                 env_vars=self.env_vars)
            self.add_audit_log("GCP Operation", operation_name,
                               "Success", TASK_STATUS.COMPLETED)
        except Exception as ex:
            raise Exception("Failed operation:%s" % str(ex))