import sys

from PyQt5.QtCore import *
from PyQt5.QtGui import QDesktopServices, QIcon
from PyQt5.QtWebEngineWidgets import *
from PyQt5.QtWidgets import *


class ProtonDesktopApp(QMainWindow):
    def __init__(self):
        super().__init__()

        self.proton_services = {
            'mail': 'https://mail.proton.me',
            'calendar': 'https://calendar.proton.me',
            'drive': 'https://drive.proton.me'
        }
        self.internal_urls = [url.split('://')[1] for url in self.proton_services.values()]
        self.internal_urls.append('account.proton.me')

        self.setWindowTitle('Proton Desktop')

        # window size and position
        screen_geometry = QApplication.desktop().availableGeometry()
        screen_width, screen_height = screen_geometry.width(), screen_geometry.height()
        self.setGeometry(0, 0, screen_width, screen_height)

        self.central_widget = QWidget(self)
        self.main_layout = QHBoxLayout(self.central_widget)
        self.main_layout.setContentsMargins(0, 0, 0, 0)
        self.main_layout.setSpacing(0)
        self.setCentralWidget(self.central_widget)

        # sidebar
        self.sidebar = QWidget(self)
        self.sidebar_layout = QVBoxLayout(self.sidebar)
        self.sidebar.setFixedWidth(60)
        self.sidebar.setSizePolicy(QSizePolicy.Fixed, QSizePolicy.Expanding)
        self.sidebar.setStyleSheet('background-color: #505264;')

        # sidebar buttons: mail, calendar, drive, vpn
        self.add_button('mail', 'Mail', 'assets/mail.svg')
        self.add_button('calendar', 'Calendar', 'assets/calendar.svg')
        self.add_button('drive', 'Drive', 'assets/drive.svg')
        self.sidebar_layout.addStretch()
        self.add_button('support', 'Support', 'assets/donate.svg')
        self.add_button('about', 'About', 'assets/about.svg')

        self.main_layout.addWidget(self.sidebar, alignment=Qt.AlignLeft)

        # webview
        self.web = QWebEngineView(self)
        self.web.urlChanged.connect(self.on_link_clicked)
        self.main_layout.addWidget(self.web)
        self.web.load(QUrl('https://mail.proton.me'))

        self.main_layout.setStretchFactor(self.web, 1)

    def on_link_clicked(self, url: QUrl):
        print(f'{url.host()} has been clicked!!!')
        if url.host() not in self.internal_urls:
            print(url.host())
            QDesktopServices.openUrl(url)

    def add_button(self, service_name, tooltip, icon_path, on_clicked=None):
        btn = QPushButton(self)
        btn.setIcon(QIcon(icon_path))
        btn.setIconSize(QSize(32, 32))
        btn.setStyleSheet("border: none; margin: 2px;")
        btn.setToolTip(tooltip)

        btn.clicked.connect(lambda: self.load_proton_service(service_name))

        self.sidebar_layout.addWidget(btn)

    def load_proton_service(self, service_name):
        destination_url = self.proton_services.get(service_name, 'mail')
        self.web.load(QUrl(destination_url))

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = ProtonDesktopApp()
    window.show()
    sys.exit(app.exec_())
