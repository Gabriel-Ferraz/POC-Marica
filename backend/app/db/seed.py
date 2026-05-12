"""Seed initial data — idempotent (checks before inserting)."""
import sys
from app.db.session import SessionLocal
from app.core.security import hash_password


def seed():
    db = SessionLocal()
    try:
        from app.models.user import User, Department, Role

        # Admin user
        if not db.query(User).filter(User.email == "admin@poc.com").first():
            admin = User(
                email="admin@poc.com",
                full_name="Administrador",
                hashed_password=hash_password("admin123"),
                is_active=True,
                is_superuser=True,
            )
            db.add(admin)
            db.flush()
            print("✔ Admin user created: admin@poc.com / admin123")
        else:
            admin = db.query(User).filter(User.email == "admin@poc.com").first()
            print("✔ Admin user already exists")

        # Departments
        if not db.query(Department).filter(Department.name == "Administração").first():
            dept1 = Department(name="Administração", description="Departamento administrativo")
            dept2 = Department(name="Jurídico", description="Departamento jurídico")
            db.add_all([dept1, dept2])
            print("✔ Departments created")

        # Demo workflow
        from app.models.workflow import Workflow, WorkflowStep, WorkflowSLA
        if not db.query(Workflow).filter(Workflow.name == "Processo Administrativo Demo").first():
            wf = Workflow(
                name="Processo Administrativo Demo",
                description="Fluxo de demonstração da POC",
                created_by=admin.id,
            )
            db.add(wf)
            db.flush()
            step1 = WorkflowStep(workflow_id=wf.id, name="Análise Inicial", order=0)
            step2 = WorkflowStep(workflow_id=wf.id, name="Revisão Jurídica", order=1)
            step3 = WorkflowStep(workflow_id=wf.id, name="Assinatura", order=2)
            step4 = WorkflowStep(workflow_id=wf.id, name="Concluído", order=3, is_final=True)
            db.add_all([step1, step2, step3, step4])
            db.flush()
            db.add(WorkflowSLA(step_id=step1.id, deadline_hours=24, warning_hours=8))
            db.add(WorkflowSLA(step_id=step2.id, deadline_hours=48, warning_hours=12))
            print("✔ Demo workflow created")

        # DLT Network
        from app.models.dlt import DLTNetwork, DLTServer, SmartContract, SmartContractField, DLTCredential
        from app.core.security import generate_api_key_pair, hash_secret_key
        if not db.query(DLTNetwork).filter(DLTNetwork.name == "Rede Principal").first():
            net = DLTNetwork(name="Rede Principal", description="Rede DLT permissionada da POC")
            db.add(net)
            db.flush()
            db.add(DLTServer(network_id=net.id, name="Nó 1", endpoint="http://dlt-node-1:7050"))
            contract = SmartContract(network_id=net.id, name="Contrato Administrativo", description="Contrato para processos administrativos")
            db.add(contract)
            db.flush()
            db.add(SmartContractField(contract_id=contract.id, name="protocolo", field_type="text", required=True))
            db.add(SmartContractField(contract_id=contract.id, name="valor", field_type="number"))
            db.add(SmartContractField(contract_id=contract.id, name="ativo", field_type="boolean"))
            db.add(SmartContractField(contract_id=contract.id, name="data_abertura", field_type="date"))
            db.add(SmartContractField(contract_id=contract.id, name="hora_abertura", field_type="time"))
            access_key, secret_key = generate_api_key_pair()
            cred = DLTCredential(
                network_id=net.id,
                name="Chave Demo",
                access_key=access_key,
                secret_key_hash=hash_secret_key(secret_key),
                allowed_routes=["/api/dlt/records"],
            )
            db.add(cred)
            print(f"✔ DLT Network created | accessKey: {access_key} | secretKey: {secret_key}")

        # Chatbot
        from app.models.chatbot import Chatbot
        if not db.query(Chatbot).filter(Chatbot.name == "Assistente POC").first():
            bot = Chatbot(name="Assistente POC", description="Chatbot NLP da demonstração")
            db.add(bot)
            print("✔ Demo chatbot created")

        db.commit()
        print("✔ Seed completed successfully")
    except Exception as e:
        db.rollback()
        print(f"✗ Seed error: {e}", file=sys.stderr)
        raise
    finally:
        db.close()


if __name__ == "__main__":
    seed()
