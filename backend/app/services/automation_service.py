import subprocess
import tempfile
import os
from datetime import datetime, timezone

from sqlalchemy.orm import Session

from app.models.automation import AutomationRun, AutomationRunLog, AutomationSecurityValidation, AutomationPackage
from app.core.config import settings


SECURITY_RISK_PATTERNS = [
    ("os.system", "high", "Direct OS command execution detected"),
    ("subprocess.Popen", "medium", "Subprocess creation detected — verify intent"),
    ("eval(", "high", "Use of eval() is dangerous"),
    ("exec(", "high", "Use of exec() is dangerous"),
    ("__import__", "medium", "Dynamic import detected"),
    ("open(", "low", "File I/O detected"),
    ("requests.get", "low", "HTTP request detected"),
    ("socket", "medium", "Network socket usage detected"),
]


def analyze_security(source_code: str) -> dict:
    issues = []
    risk_level = "low"

    for pattern, severity, message in SECURITY_RISK_PATTERNS:
        if pattern in source_code:
            issues.append({"pattern": pattern, "severity": severity, "message": message})
            if severity == "high":
                risk_level = "high"
            elif severity == "medium" and risk_level != "high":
                risk_level = "medium"

    return {"risk_level": risk_level, "issues": issues}


def run_python_script(source_code: str, timeout: int = 30) -> tuple[int, str, str]:
    with tempfile.NamedTemporaryFile(mode="w", suffix=".py", delete=False) as f:
        f.write(source_code)
        tmp_path = f.name

    try:
        result = subprocess.run(
            ["python", tmp_path],
            capture_output=True,
            text=True,
            timeout=timeout,
        )
        return result.returncode, result.stdout, result.stderr
    except subprocess.TimeoutExpired:
        return -1, "", "Execution timed out after 30 seconds"
    except Exception as e:
        return -1, "", str(e)
    finally:
        os.unlink(tmp_path)


def execute_automation(db: Session, run: AutomationRun) -> AutomationRun:
    package: AutomationPackage = run.package
    run.status = "running"
    run.started_at = datetime.now(timezone.utc)
    db.commit()

    if package.language == "python" and package.source_code:
        exit_code, stdout, stderr = run_python_script(package.source_code)
    else:
        exit_code, stdout, stderr = 0, f"[{package.language.upper()} runtime registered — execution simulated]", ""

    run.exit_code = str(exit_code)
    run.status = "completed" if exit_code == 0 else "failed"
    run.completed_at = datetime.now(timezone.utc)

    for line in (stdout + stderr).splitlines():
        if line.strip():
            log = AutomationRunLog(
                run_id=run.id,
                level="info" if exit_code == 0 else "error",
                message=line,
            )
            db.add(log)

    db.commit()
    db.refresh(run)
    return run
