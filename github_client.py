import base64
import json
import requests
from nacl import encoding, public


class GitHubClient:
    def __init__(self, token: str, owner: str, repo: str):
        self.token = token
        self.owner = owner
        self.repo = repo
        self.api_base = f"https://api.github.com/repos/{owner}/{repo}"

        self.headers = {
            "Authorization": f"Bearer {token}",
            "Accept": "application/vnd.github+json"
        }

    # ------------------------------
    # 내부용: GitHub Secret Public Key 가져오기
    # ------------------------------
    def _get_public_key(self):
        url = f"{self.api_base}/actions/secrets/public-key"
        r = requests.get(url, headers=self.headers)
        r.raise_for_status()
        return r.json()  # {key, key_id}

    # ------------------------------
    # 내부용: 값 암호화
    # ------------------------------
    def _encrypt(self, public_key: str, value: str) -> str:
        public_key = public.PublicKey(public_key.encode("utf-8"), encoding.Base64Encoder())
        sealed_box = public.SealedBox(public_key)
        encrypted = sealed_box.encrypt(value.encode("utf-8"))
        return base64.b64encode(encrypted).decode("utf-8")

    # ------------------------------
    # Secret 저장 함수
    # ------------------------------
    def update_secret(self, name: str, value: str):
        key_info = self._get_public_key()
        encrypted_value = self._encrypt(key_info["key"], value)

        url = f"{self.api_base}/actions/secrets/{name}"
        payload = {
            "encrypted_value": encrypted_value,
            "key_id": key_info["key_id"]
        }

        r = requests.put(url, headers=self.headers, json=payload)
        r.raise_for_status()
        return True

    # ------------------------------
    # 복수 Secret 한번에 저장
    # ------------------------------
    def update_secrets(self, highlight_name: str, url: str):
        self.update_secret("HIGHLIGHT_NAME", highlight_name)
        self.update_secret("QOO10_URL", url)
        return True
    
    # ------------------------------
    # GitHub Actions workflow 실행
    # ------------------------------
    def run_workflow(self, workflow_filename: str, ref: str = "main"):
        """
        workflow_filename 예: 'scraper.yml'
        ref: 보통 main 브랜치
        """
        url = f"{self.api_base}/actions/workflows/{workflow_filename}/dispatches"
        payload = {
            "ref": ref
        }

        r = requests.post(url, headers=self.headers, json=payload)
        r.raise_for_status()
        return True

