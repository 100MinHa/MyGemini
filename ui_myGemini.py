import os
import sys
# PySide6 라이브러리 임포트
from PySide6.QtCore import (QCoreApplication, QDate, QDateTime, QLocale,
                            QMetaObject, QObject, QPoint, QRect,
                            QSize, QTime, QUrl, Qt)
from PySide6.QtGui import (QBrush, QColor, QConicalGradient, QCursor,
                           QFont, QFontDatabase, QGradient, QIcon,
                           QImage, QKeySequence, QLinearGradient, QPainter,
                           QPalette, QPixmap, QRadialGradient, QTransform)
from PySide6.QtWidgets import (QApplication, QHBoxLayout, QLabel, QLineEdit,
                               QMainWindow, QPushButton, QScrollArea, QSizePolicy,
                               QSpacerItem, QVBoxLayout, QWidget, QMessageBox)

# Google GenAI SDK
from google import genai

# ----------------------------------------------------
# 1. Qt Designer에서 변환된 UI 클래스 (Ui_MainWindow)
#    - 단일 파일 구성을 위해 여기에 직접 포함
# ----------------------------------------------------
class Ui_MainWindow(object):
    def setupUi(self, MainWindow):
        if not MainWindow.objectName():
            MainWindow.setObjectName(u"MainWindow")
        MainWindow.resize(600, 500)
        self.centralwidget = QWidget(MainWindow)
        self.centralwidget.setObjectName(u"centralwidget")
        self.centralwidget.setStyleSheet(u"background-color: #f0f0f0;")
        
        self.verticalLayout = QVBoxLayout(self.centralwidget)
        self.verticalLayout.setSpacing(10)
        self.verticalLayout.setObjectName(u"verticalLayout")
        self.verticalLayout.setContentsMargins(15, 15, 15, 15)
        
        self.scrollArea = QScrollArea(self.centralwidget)
        self.scrollArea.setObjectName(u"scrollArea")
        self.scrollArea.setWidgetResizable(True)
        self.scrollArea.setStyleSheet(u"QScrollArea { border: 1px solid #d0d0d0; border-radius: 8px; background-color: white; }")
        
        self.scrollAreaWidgetContents = QWidget()
        self.scrollAreaWidgetContents.setObjectName(u"scrollAreaWidgetContents")
        
        self.verticalLayout_2 = QVBoxLayout(self.scrollAreaWidgetContents)
        self.verticalLayout_2.setObjectName(u"verticalLayout_2")
        self.verticalLayout_2.setContentsMargins(15, 15, 15, 15)
        
        self.lblAnswer = QLabel(self.scrollAreaWidgetContents)
        self.lblAnswer.setObjectName(u"lblAnswer")
        # QLabel이 HTML을 렌더링하도록 설정
        self.lblAnswer.setTextFormat(Qt.RichText)
        self.lblAnswer.setAlignment(Qt.AlignLeading | Qt.AlignLeft | Qt.AlignTop)
        self.lblAnswer.setWordWrap(True)
        self.lblAnswer.setStyleSheet(u"font-size: 14px; color: #333; padding: 0;") 

        self.verticalLayout_2.addWidget(self.lblAnswer)

        self.verticalSpacer = QSpacerItem(20, 40, QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Expanding)
        self.verticalLayout_2.addItem(self.verticalSpacer)

        self.scrollArea.setWidget(self.scrollAreaWidgetContents)
        self.verticalLayout.addWidget(self.scrollArea)

        # Input and Send Button Layout
        self.horizontalLayout = QHBoxLayout()
        self.horizontalLayout.setSpacing(10)
        self.horizontalLayout.setObjectName(u"horizontalLayout")
        
        self.lineEditMyQuestion = QLineEdit(self.centralwidget)
        self.lineEditMyQuestion.setObjectName(u"lineEditMyQuestion")
        self.lineEditMyQuestion.setMinimumSize(QSize(0, 45))
        self.lineEditMyQuestion.setStyleSheet(u"padding: 10px; border: 1px solid #aaa; border-radius: 22px; background-color: white;")

        self.horizontalLayout.addWidget(self.lineEditMyQuestion)

        self.btnSend = QPushButton(self.centralwidget)
        self.btnSend.setObjectName(u"btnSend")
        self.btnSend.setMinimumSize(QSize(80, 45))
        self.btnSend.setToolTip(QCoreApplication.translate("MainWindow", u"\uc9c8\ubb38 \uc804\uc1a1", None))
        self.btnSend.setStyleSheet(u"QPushButton {background-color: #1a73e8; color: white; border-radius: 22px; font-weight: bold; font-size: 14px;} QPushButton:hover {background-color: #185abc;} QPushButton:disabled {background-color: #999999;}")
        self.btnSend.setText(QCoreApplication.translate("MainWindow", u"\uc804\uc1a1", None))

        self.horizontalLayout.addWidget(self.btnSend)
        self.verticalLayout.addLayout(self.horizontalLayout)

        MainWindow.setCentralWidget(self.centralwidget)
        self.retranslateUi(MainWindow)
        QMetaObject.connectSlotsByName(MainWindow)
    # setupUi

    def retranslateUi(self, MainWindow):
        MainWindow.setWindowTitle(QCoreApplication.translate("MainWindow", u"Gemini Chat (Qt6/PySide6)", None))
        # 초기 텍스트는 코드에서 설정할 예정입니다.
        self.lineEditMyQuestion.setPlaceholderText(QCoreApplication.translate("MainWindow", u"\uc5ec\uae30\uc5d0 \uc9c8\ubb38\uc744 \uc785\ub825\ud558\uc138\uc694...", None))
        # retranslateUi

# ----------------------------------------------------
# 2. 메인 애플리케이션 로직 (UI 클래스 상속)
# ----------------------------------------------------
class GeminiChatApp(QMainWindow, Ui_MainWindow):
    def __init__(self):
        super().__init__()
        
        self.setupUi(self)
        self.setWindowTitle("Gemini Chat (PySide6 - Complete)")
        
        # --- [변경/추가] 대화 기록 및 API 설정 ---
        # HTML 태그를 사용하여 대화 내용을 저장할 변수
        self.display_history = ""
        self.initial_message = "새로운 Gemini 챗 세션입니다. 궁금한 점을 편하게 질문해 주세요."

        # ----------------------------------------------------
        # 🚨 사용자 지정 API 키 설정 (여기를 수정하세요)
        # ----------------------------------------------------
        API_KEY = "AIzaSyDgH_zdvWNm_b3fF9TgA7Fz4qiLzj0MC9g"
        PLACEHOLDER_KEY = "YOUR_API_KEY_HERE"
        
        # Gemini API 클라이언트 설정
        try:
            if API_KEY == PLACEHOLDER_KEY and "GEMINI_API_KEY" not in os.environ:
                 raise ValueError("API 키가 설정되지 않았습니다. API_KEY 변수를 실제 키로 수정하거나 환경 변수를 설정하세요.")
            
            if API_KEY != PLACEHOLDER_KEY:
                 self.client = genai.Client(api_key=API_KEY)
            else:
                 self.client = genai.Client()
                 
            self.api_key_set = True

        except Exception as e:
            error_msg = f"API 클라이언트 초기화 오류: {e}"
            QMessageBox.critical(self, "API 오류", error_msg)
            self.lblAnswer.setText(f"❌ {error_msg}")
            self.btnSend.setEnabled(False)
            self.api_key_set = False
            return
        
        # 초기 메시지 설정 및 대화 기록 초기화
        self.display_history = self._format_gemini_response(self.initial_message, is_initial=True)
        self.lblAnswer.setText(self.display_history)

        # 이벤트 연결
        self.btnSend.clicked.connect(self.send_question)
        self.lineEditMyQuestion.returnPressed.connect(self.send_question)
        
    def _format_user_message(self, text):
        """사용자 메시지를 HTML로 포맷합니다."""
        # 텍스트 내의 <, > 기호를 HTML 엔티티로 변환하여 안전하게 표시
        safe_text = text.replace('<', '&lt;').replace('>', '&gt;')
        return f"""
        <div style="background-color: #e3f2fd; padding: 12px; border-radius: 8px; margin-bottom: 15px; border-left: 5px solid #2196F3; color: #1565C0;">
            <strong>🙋‍♂️ 나:</strong>
            <p style="margin-top: 5px; margin-bottom: 0;">{safe_text}</p>
        </div>
        """

    def _format_gemini_response(self, text, is_initial=False):
        """Gemini 응답을 HTML로 포맷합니다."""
        # 기본 텍스트에 줄바꿈을 적용하기 위해 \n을 <br>로 변환
        formatted_text = text.replace('\n', '<br>') 
        
        # 초기 메시지인 경우 스타일을 다르게 적용
        if is_initial:
            return f"""
            <div style="background-color: #f9f9f9; padding: 12px; border-radius: 8px; margin-bottom: 15px; border-left: 5px solid #4CAF50; color: #333;">
                <strong>✨ Gemini:</strong>
                <p style="margin-top: 5px; margin-bottom: 0;">{formatted_text}</p>
            </div>
            """
        
        return f"""
        <div style="background-color: #f3e5f5; padding: 12px; border-radius: 8px; margin-bottom: 15px; border-left: 5px solid #9C27B0; color: #6A1B9A;">
            <strong>✨ Gemini:</strong>
            <p style="margin-top: 5px; margin-bottom: 0;">{formatted_text}</p>
        </div>
        """

    def send_question(self):
        """질문 입력란의 내용을 가져와 Gemini API에 전송하고, 응답을 QLabel에 표시합니다."""
        
        if not hasattr(self, 'client') or not self.api_key_set:
             self.lblAnswer.setText("API 키 설정이 올바르지 않아 질문을 보낼 수 없습니다. 키를 확인하세요.")
             return

        user_question = self.lineEditMyQuestion.text().strip()
        
        if not user_question:
            return

        # 1. 사용자 질문을 기록에 추가하고 임시 로딩 메시지와 함께 UI 업데이트
        self.display_history += self._format_user_message(user_question)
        
        # 로딩 메시지를 포함한 전체 기록을 표시
        temp_loading_html = self.display_history + self._format_gemini_response("... Gemini가 생각 중입니다 ...")
        self.lblAnswer.setText(temp_loading_html) 
        
        self.btnSend.setEnabled(False) 
        self.lineEditMyQuestion.setEnabled(False)
        QApplication.processEvents()

        try:
            # Gemini API 호출 (대화 기록을 보여주기만 할 뿐, 문맥 유지를 위해서는 별도 chat session 관리가 필요)
            # 현재는 display history만 누적
            response = self.client.models.generate_content(
                model="gemini-2.5-flash",
                contents=user_question
            )
            
            # 2. Gemini 응답을 기록에 추가하고 UI 최종 업데이트
            self.display_history = self.display_history + self._format_gemini_response(response.text)
            self.lblAnswer.setText(self.display_history)

        except Exception as e:
            error_message = f"Gemini API 호출 중 오류 발생: {e}"
            QMessageBox.critical(self, "API 호출 오류", f"Gemini API 호출 중 오류가 발생했습니다: {e}")
            
            # 오류 메시지를 기록에 추가하여 로딩 메시지를 대체
            error_html = self._format_gemini_response(f"❌ 오류: {error_message}")
            self.display_history = self.display_history.rsplit(self._format_gemini_response("... Gemini가 생각 중입니다 ..."), 1)[0] + error_html
            self.lblAnswer.setText(self.display_history)
            
        finally:
            # 입력창 초기화 및 버튼 다시 활성화
            self.lineEditMyQuestion.clear()
            self.btnSend.setEnabled(True)
            self.lineEditMyQuestion.setEnabled(True)
            
            # 스크롤 영역을 가장 아래로 이동 (가장 최근 대화가 보이도록)
            QApplication.processEvents() # 레이아웃 업데이트 대기
            self.scrollArea.verticalScrollBar().setValue(self.scrollArea.verticalScrollBar().maximum())

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = GeminiChatApp()
    window.show()
    sys.exit(app.exec())