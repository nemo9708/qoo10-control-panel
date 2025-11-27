from google.oauth2 import service_account
from googleapiclient.discovery import build


class SchedulerClient:
    def __init__(self, service_account_file: str, project_id: str, location: str, job_name: str):
        """
        GCP 스케줄러 제어를 위한 클라이언트
        """
        self.service_account_file = service_account_file
        self.project_id = project_id
        self.location = location
        self.job_name = job_name

        # 서비스 계정 파일로 인증
        scopes = ["https://www.googleapis.com/auth/cloud-platform"]
        self.credentials = service_account.Credentials.from_service_account_file(
            service_account_file,
            scopes=scopes
        )

        # Cloud Scheduler API 초기화
        self.service = build("cloudscheduler", "v1", credentials=self.credentials)

        # API 호출용 job 경로
        self.job_path = f"projects/{project_id}/locations/{location}/jobs/{job_name}"

    def set_state(self, state: str):
        """
        state = "ON"  → resume()
        state = "OFF" → pause()
        """
        if state == "ON":
            return self._resume()
        elif state == "OFF":
            return self._pause()
        else:
            raise ValueError("state must be ON or OFF")

    def _pause(self):
        """
        스케줄러 정지 (pause)
        """
        request = self.service.projects().locations().jobs().pause(name=self.job_path)
        return request.execute()

    def _resume(self):
        """
        스케줄러 재개 (resume)
        """
        request = self.service.projects().locations().jobs().resume(name=self.job_path)
        return request.execute()

    def get_state(self):
        """
        현재 Job 상태 조회
        """
        request = self.service.projects().locations().jobs().get(name=self.job_path)
        return request.execute()
