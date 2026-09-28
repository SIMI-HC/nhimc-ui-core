from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
import hashlib
import json
import os
from pathlib import Path
import re
import tempfile

from scripts.build_single_html import build_single_html, inspect_completion_manifest
from scripts.run_browser_tests import run_exact_browser_verification


RECEIPT_KEYS = {
    "schemaVersion",
    "artifactSha256",
    "artifactBytes",
    "runtimeToken",
    "browserProduct",
    "browserVersion",
    "verifiedAt",
}


@dataclass(frozen=True)
class ArtifactReceipt:
    schema_version: int
    artifact_sha256: str
    artifact_bytes: int
    runtime_token: str
    browser_product: str
    browser_version: str
    verified_at: str


@dataclass(frozen=True)
class VerifiedArtifact:
    html_path: Path
    receipt_path: Path
    sha256: str
    bytes: int
    manifest: dict[str, object]


def _runtime_token(html: str) -> str:
    match = re.search(
        r'<meta\s+name="nhimc-runtime-token"\s+content="([0-9a-f]{64})">',
        html,
        re.I,
    )
    if not match:
        raise ValueError("completed artifact runtime token is missing")
    return match.group(1)


def _read_receipt(path: Path) -> ArtifactReceipt:
    if not path.is_file():
        raise ValueError("browser receipt is missing")
    try:
        raw = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as error:
        raise ValueError("browser receipt is not valid JSON") from error
    if not isinstance(raw, dict) or set(raw) != RECEIPT_KEYS:
        raise ValueError("browser receipt has an invalid schema")
    if raw["schemaVersion"] != 1:
        raise ValueError("browser receipt has an unsupported schema version")
    for field in ("artifactSha256", "runtimeToken"):
        if not isinstance(raw[field], str) or not re.fullmatch(r"[0-9a-f]{64}", raw[field]):
            raise ValueError(f"browser receipt has an invalid {field}")
    if not isinstance(raw["artifactBytes"], int) or raw["artifactBytes"] <= 0:
        raise ValueError("browser receipt has an invalid artifactBytes")
    for field in ("browserProduct", "browserVersion", "verifiedAt"):
        if not isinstance(raw[field], str) or not raw[field]:
            raise ValueError(f"browser receipt has an invalid {field}")
    try:
        verified_at = datetime.fromisoformat(raw["verifiedAt"].replace("Z", "+00:00"))
    except ValueError as error:
        raise ValueError("browser receipt verifiedAt is not ISO-8601") from error
    if verified_at.utcoffset() is None or verified_at.utcoffset().total_seconds() != 0:
        raise ValueError("browser receipt verifiedAt must be UTC")
    return ArtifactReceipt(
        raw["schemaVersion"], raw["artifactSha256"], raw["artifactBytes"],
        raw["runtimeToken"], raw["browserProduct"], raw["browserVersion"],
        raw["verifiedAt"],
    )


def load_matching_receipt(artifact: Path, receipt: Path) -> ArtifactReceipt:
    artifact = artifact.resolve()
    receipt = receipt.resolve()
    if not artifact.is_file():
        raise ValueError("completed artifact is missing")
    payload = artifact.read_bytes()
    html = payload.decode("utf-8")
    manifest = inspect_completion_manifest(html)
    if re.search(r"<nhimc-frame\b", html, re.I):
        raise ValueError("completed artifact still contains authoring source")
    if manifest["verificationRequired"] is not True or manifest["sidecarCount"] != 0:
        raise ValueError("completed artifact is not eligible for verified delivery")
    proof = _read_receipt(receipt)
    digest = hashlib.sha256(payload).hexdigest()
    if proof.artifact_sha256 != digest:
        raise ValueError("artifact digest does not match browser receipt")
    if proof.artifact_bytes != len(payload):
        raise ValueError("artifact byte count does not match browser receipt")
    if proof.runtime_token != _runtime_token(html):
        raise ValueError("runtime token does not match browser receipt")
    return proof


def _delivery_path(destination: Path) -> Path:
    if destination.exists() and destination.is_dir():
        return destination / "index.html"
    if destination.name.lower() != "index.html":
        return (destination if not destination.suffix else destination.parent) / "index.html"
    return destination


def deliver_verified_artifact(
    verified: VerifiedArtifact, destination: Path
) -> Path:
    proof = load_matching_receipt(verified.html_path, verified.receipt_path)
    payload = verified.html_path.read_bytes()
    if hashlib.sha256(payload).hexdigest() != proof.artifact_sha256:
        raise ValueError("artifact digest does not match browser receipt")
    if len(payload) != proof.artifact_bytes:
        raise ValueError("artifact byte count does not match browser receipt")
    html = payload.decode("utf-8")
    manifest = inspect_completion_manifest(html)
    if proof.artifact_sha256 != verified.sha256 or proof.artifact_bytes != verified.bytes:
        raise ValueError("verified artifact metadata no longer matches its browser receipt")
    if manifest != verified.manifest:
        raise ValueError("verified artifact manifest changed before delivery")

    target = _delivery_path(destination.resolve())
    target.parent.mkdir(parents=True, exist_ok=True)
    temporary_name: str | None = None
    try:
        with tempfile.NamedTemporaryFile(
            mode="wb", delete=False, dir=target.parent,
            prefix=f".{target.name}.", suffix=".tmp",
        ) as temporary:
            temporary.write(payload)
            temporary.flush()
            temporary_name = temporary.name
        os.replace(temporary_name, target)
        temporary_name = None
    finally:
        if temporary_name is not None:
            Path(temporary_name).unlink(missing_ok=True)
    return target


def build_and_verify(root: Path, source: Path, work_dir: Path) -> VerifiedArtifact:
    root = root.resolve()
    work_dir = work_dir.resolve()
    work_dir.mkdir(parents=True, exist_ok=True)
    artifact = work_dir / "index.html"
    receipt = work_dir / "index.receipt.json"
    build_single_html(root, source, artifact)
    run_exact_browser_verification(root, artifact, receipt)
    proof = load_matching_receipt(artifact, receipt)
    manifest = inspect_completion_manifest(artifact.read_text(encoding="utf-8"))
    return VerifiedArtifact(
        artifact, receipt, proof.artifact_sha256, proof.artifact_bytes, manifest
    )
