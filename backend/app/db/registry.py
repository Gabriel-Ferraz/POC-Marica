from app.db.base import Base  # noqa — must be first

from app.models.user import User, Role, Permission, Department, UserDepartment  # noqa
from app.models.workflow import (  # noqa
    Workflow, WorkflowStep, WorkflowForm, WorkflowFormField,
    WorkflowStarter, WorkflowManager, WorkflowStepResponsible, WorkflowSLA,
)
from app.models.process import ProcessInstance, ProcessActivity, ProcessAttachment, ProcessSignature  # noqa
from app.models.dlt import (  # noqa
    DLTNetwork, DLTServer, SmartContract, SmartContractField,
    DLTCredential, DLTRecord, DLTEndpointPermission,
)
from app.models.chatbot import Chatbot, Conversation, ConversationMessage, ConversationSummary  # noqa
from app.models.voice import (  # noqa
    VoiceBot, VoiceCall, VoiceCallTranscript,
    VoiceCampaign, VoiceCampaignTarget, VoiceCampaignScript, VoiceCampaignRule,
)
from app.models.idp import IDPDocument, IDPProcessingJob, IDPResult, IDPExtractedField  # noqa
from app.models.automation import (  # noqa
    AutomationPackage, AutomationRun, AutomationRunLog, AutomationSecurityValidation,
)
from app.models.notification import Notification  # noqa
