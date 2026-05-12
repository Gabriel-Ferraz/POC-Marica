export interface User {
  id: string;
  email: string;
  full_name: string;
  is_active: boolean;
  is_superuser: boolean;
  created_at: string;
}

export interface Department {
  id: string;
  name: string;
  description?: string;
  is_active: boolean;
  created_at: string;
}

export interface Workflow {
  id: string;
  name: string;
  description?: string;
  is_active: boolean;
  created_by?: string;
  created_at: string;
}

export interface WorkflowStep {
  id: string;
  workflow_id: string;
  name: string;
  description?: string;
  order: number;
  is_final: boolean;
}

export interface ProcessInstance {
  id: string;
  workflow_id: string;
  current_step_id?: string;
  started_by: string;
  title: string;
  status: string;
  form_data: Record<string, unknown>;
  created_at: string;
}

export interface ProcessActivity {
  id: string;
  process_id: string;
  user_id: string;
  action: string;
  from_step_id?: string;
  to_step_id?: string;
  comment?: string;
  dlt_hash?: string;
  created_at: string;
}

export interface DLTNetwork {
  id: string;
  name: string;
  description?: string;
  is_active: boolean;
  created_at: string;
}

export interface SmartContract {
  id: string;
  network_id: string;
  name: string;
  description?: string;
  is_active: boolean;
  created_at: string;
}

export interface DLTRecord {
  id: string;
  network_id?: string;
  contract_id?: string;
  event_type: string;
  payload: Record<string, unknown>;
  record_hash: string;
  created_at: string;
}

export interface DLTCredential {
  id: string;
  network_id: string;
  name: string;
  access_key: string;
  allowed_routes: string[];
  is_active: boolean;
  created_at: string;
  secret_key?: string;
}

export interface Chatbot {
  id: string;
  name: string;
  description?: string;
  is_active: boolean;
  created_at: string;
}

export interface AutomationPackage {
  id: string;
  name: string;
  description?: string;
  language: string;
  source_code?: string;
  is_active: boolean;
  created_at: string;
}

export interface AutomationRun {
  id: string;
  package_id: string;
  status: string;
  exit_code?: string;
  started_at?: string;
  completed_at?: string;
}

export interface IDPDocument {
  id: string;
  filename: string;
  mime_type?: string;
  created_at: string;
}

export interface IDPResult {
  id: string;
  document_id: string;
  document_type?: string;
  confidence: number;
  raw_text?: string;
  has_handwriting: boolean;
  json_export: Record<string, unknown>;
  created_at: string;
}

export interface VoiceCampaign {
  id: string;
  name: string;
  description?: string;
  status: string;
  ideal_hours: number[];
  created_at: string;
}

export interface KanbanColumn {
  step: { id: string; name: string; order: number; is_final: boolean };
  processes: { id: string; title: string; status: string; created_at: string }[];
}
