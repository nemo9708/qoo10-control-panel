import sys
from PyQt5.QtWidgets import (
    QApplication, QMainWindow, QWidget,
    QHBoxLayout, QVBoxLayout, QFormLayout,
    QLabel, QLineEdit, QPushButton, QPlainTextEdit,
    QGroupBox, QComboBox, QMessageBox, QSizePolicy
)
from PyQt5.QtCore import Qt

from config_loader import load_config
from github_client import GitHubClient
from scheduler_client import SchedulerClient

# scheduler_client는 다음 단계에서 구현 예정
# from scheduler_client import SchedulerClient


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()

        self.setWindowTitle("Qoo10 Scraper Control Panel")
        self.resize(900, 500)

        # ---- config.json 로딩 ----
        try:
            cfg = load_config("config.json")
        except Exception:
            QMessageBox.critical(self, "오류", "config.json 파일을 찾을 수 없습니다.")
            sys.exit(1)

        # ---- GitHub Client 생성 ----
        self.github_client = GitHubClient(
            cfg["github"]["token"],
            cfg["github"]["owner"],
            cfg["github"]["repo"]
        )

        # ---- Scheduler Client 생성 ----
        self.scheduler_client = SchedulerClient(
            cfg["gcp"]["service_account_file"],
            cfg["gcp"]["project_id"],
            cfg["gcp"]["location"],
            cfg["gcp"]["job_name"]
        )

        # ---- UI 구성 ----
        self._init_ui()

    # ====================================================
    # UI 초기화
    # ====================================================
    def _init_ui(self):
        central = QWidget(self)
        main_layout = QHBoxLayout()
        central.setLayout(main_layout)
        self.setCentralWidget(central)

        # ----- 왼쪽: 설정 패널 -----
        left_panel = QGroupBox("설정")
        left_layout = QVBoxLayout()
        left_panel.setLayout(left_layout)

        form = QFormLayout()

        self.txt_highlight_name = QLineEdit()
        self.txt_url = QLineEdit()

        self.cmb_scheduler_state = QComboBox()
        self.cmb_scheduler_state.addItems(["ON", "OFF"])

        form.addRow("강조 할 제품 명 :", self.txt_highlight_name)
        form.addRow("메가 와리 URL :", self.txt_url)
        form.addRow("스케줄러 상태 :", self.cmb_scheduler_state)

        left_layout.addLayout(form)

        # 버튼 영역
        btn_layout = QVBoxLayout()

        self.btn_save_secret = QPushButton("시크릿 저장 (GitHub)")
        self.btn_apply_scheduler = QPushButton("스케줄러 적용 (GCP)")
        self.btn_run_action = QPushButton("스크래퍼 테스트 실행")
        self.btn_fetch_log = QPushButton("GitHub 로그 불러오기")

        btn_layout.addWidget(self.btn_save_secret)
        btn_layout.addWidget(self.btn_apply_scheduler)
        btn_layout.addWidget(self.btn_run_action)
        btn_layout.addWidget(self.btn_fetch_log)
        btn_layout.addStretch()

        left_layout.addLayout(btn_layout)

        # ----- 오른쪽: 로그 패널 -----
        right_panel = QGroupBox("시스템 로그")
        right_layout = QVBoxLayout()
        right_panel.setLayout(right_layout)

        self.txt_log = QPlainTextEdit()
        self.txt_log.setReadOnly(True)
        self.txt_log.setLineWrapMode(QPlainTextEdit.NoWrap)
        self.txt_log.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)

        right_layout.addWidget(self.txt_log)

        main_layout.addWidget(left_panel, 2)
        main_layout.addWidget(right_panel, 3)

        # 시그널 연결
        self.btn_save_secret.clicked.connect(self.on_save_secret_clicked)
        self.btn_apply_scheduler.clicked.connect(self.on_apply_scheduler_clicked)
        self.btn_run_action.clicked.connect(self.on_run_action_clicked)
        self.btn_fetch_log.clicked.connect(self.on_fetch_log_clicked)

    # ====================================================
    # 공용 로그 출력 함수
    # ====================================================
    def log(self, message: str):
        self.txt_log.appendPlainText(message)

    # ====================================================
    # 버튼 핸들러
    # ====================================================
    def on_save_secret_clicked(self):
        highlight = self.txt_highlight_name.text().strip()
        url = self.txt_url.text().strip()

        if not highlight or not url:
            QMessageBox.warning(self, "입력 오류", "상품명과 URL을 모두 입력하세요.")
            return

        try:
            self.github_client.update_secrets(highlight, url)
            self.log("[시크릿 저장 완료] GitHub Secrets 업데이트 성공")
            QMessageBox.information(self, "완료", "GitHub Secrets 업데이트 완료")
        except Exception as e:
            error_msg = f"시크릿 저장 실패: {str(e)}"
            self.log("[시크릿 저장 오류] " + error_msg)
            QMessageBox.critical(self, "오류", error_msg)

    def on_apply_scheduler_clicked(self):
        state = self.cmb_scheduler_state.currentText()  # ON 또는 OFF

        try:
            self.scheduler_client.set_state(state)
            self.log(f"[스케줄러 적용 성공] 상태가 '{state}' 로 변경됨")
            QMessageBox.information(self, "완료", f"GCP 스케줄러가 '{state}' 상태로 변경되었습니다.")
        except Exception as e:
            err = f"[스케줄러 오류] {str(e)}"
            self.log(err)
            QMessageBox.critical(self, "오류", err)

        def on_run_action_clicked(self):
        # GitHub workflow 파일명 (너의 레포에 있는 YAML 파일 이름)
        workflow_file = "qoo10.yml"   # 반드시 실제 이름으로 수정해야 함!

        try:
            self.github_client.run_workflow(workflow_file)
            self.log(f"[액션 실행 완료] GitHub Actions '{workflow_file}' 실행됨")
            QMessageBox.information(self, "완료", "GitHub Actions 실행이 요청되었습니다.")
        except Exception as e:
            err = f"[액션 실행 오류] {str(e)}"
            self.log(err)
            QMessageBox.critical(self, "오류", err)

    def on_fetch_log_clicked(self):
        # TODO: GitHub 로그 다운로드 기능 연결 예정
        self.log("[로그 조회 요청] (미구현 기능)")
        QMessageBox.information(self, "로그 조회", "GitHub Actions 로그 불러오기 기능은 아직 미구현입니다.")


def main():
    app = QApplication(sys.argv)
    win = MainWindow()
    win.show()
    sys.exit(app.exec_())


if __name__ == "__main__":
    main()
