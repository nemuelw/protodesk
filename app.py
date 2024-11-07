import os
import sys
import webbrowser

from PyQt5.QtCore import pyqtSlot, QSize, QUrl, Qt
from PyQt5.QtGui import QIcon
from PyQt5.QtWebEngineWidgets import QWebEnginePage, QWebEngineDownloadItem, QWebEngineView
from PyQt5.QtWidgets import (QApplication, QDialog, QFileDialog, QHBoxLayout, QLabel, QMainWindow,
                             QPushButton, QSizePolicy, QVBoxLayout, QWidget)
from pyqt_toast import Toast


def asset_path(asset_name):
    """
    Construct correct path for the asset file
    """
    return os.path.join(os.path.dirname(__file__), "assets", asset_name)


class TempPage(QWebEnginePage):
    """
    Temporary page to facilitate capturing the URLs of any clicked links
    """
    def __init__(self, webview, parent=None):
        super().__init__(parent)
        self.web = webview
        self.urlChanged.connect(self.handle_url_changed)
        self.allowlist = [
            'mail.proton.me', 'calendar.proton.me', 'drive.proton.me', 'account.proton.me']

    @pyqtSlot(QUrl)
    def handle_url_changed(self, url: QUrl):
        if url.host() not in self.allowlist:
            webbrowser.open(url.toString())
        else:
            self.web.load(url)
        self.deleteLater()


class ProtonWebPage(QWebEnginePage):
    """
    Custom web page for loading Proton services
    """
    def __init__(self, parent=None):
        super().__init__(parent)

    def createWindow(self, _):
        return TempPage(self, self.view())


class ProtonWebView(QWebEngineView):
    """
    Custom QWebEngineView for Proton Desktop
    """
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setPage(ProtonWebPage(self))
        profile = self.page().profile()
        profile.downloadRequested.connect(self.handle_download)

        # load initial page: Proton Mail
        self.page().setUrl(QUrl('https://mail.proton.me'))

    def handle_download(self, download):
        """
        Handle a file download request
        """
        suggested_filename = download.suggestedFileName()
        save_path, _ = QFileDialog.getSaveFileName(self, 'Save File', suggested_filename)
        if save_path:
            download.setPath(save_path)
            download.accept()
            download.finished.connect(self.handle_download_finished)
        else:
            download.cancel()

    def handle_download_finished(self):
        """
        Check if a download has completed successfully and show a toast notification.
        """
        download = self.sender()
        if download.state() == QWebEngineDownloadItem.DownloadState.DownloadCompleted:
            toast = Toast('Download completed successfully!', duration=5, parent=self)
            toast.show()
        else:
            error_message = f'Download failed: {download.errorString()}'
            toast = Toast(error_message, duration=5, parent=self)
            toast.show()


class DonateDialog(QDialog):
    """
    Dialog for donating to the project
    """
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle('Donate')
        self.setFixedSize(300, 300)
        self.setWindowFlags(Qt.Popup)

        self.setStyleSheet("""
            QDialog {
                background-color: #2D2D2D;
                border-radius: 10px;
            }
            QLabel {
                font-family: 'Arial';
                font-size: 12pt;
                color: white;
            }
            QLabel#title_label {
                font-size: 16pt;
                font-weight: bold;
                color: #0076D1;
            }
            QPushButton {
                font-family: 'Arial';
                font-size: 12pt;
                background-color: white;
                color: #000000;
                border-radius: 5px;
            }
        """)

        layout = QVBoxLayout()

        title_label = QLabel('Donate')
        title_label.setObjectName("title_label")
        title_label.setAlignment(Qt.AlignCenter)
        layout.addWidget(title_label)

        info_label = QLabel("Support the development of \nProton Desktop.")
        info_label.setAlignment(Qt.AlignCenter)
        layout.addWidget(info_label)

        paypal_btn = QPushButton()
        paypal_btn.setIcon(QIcon(asset_path('paypal.svg')))
        paypal_btn.setIconSize(QSize(150, 80))
        paypal_btn.clicked.connect(self.open_paypal)
        layout.addWidget(paypal_btn)

        kofi_btn = QPushButton()
        kofi_btn.setIcon(QIcon(asset_path('kofi.svg')))
        kofi_btn.setIconSize(QSize(150, 80))
        kofi_btn.clicked.connect(self.open_kofi)
        layout.addWidget(kofi_btn)

        self.setLayout(layout)

    def open_paypal(self):
        paypal_url = 'https://www.paypal.com/donate/?hosted_button_id=8KU8MDWA86SNJ'
        webbrowser.open(paypal_url)

    def open_kofi(self):
        kofi_url = 'https://ko-fi.com/nemuelw'
        webbrowser.open(kofi_url)


class AboutDialog(QDialog):
    """
    Dialog for info on the application: version, description, author, and contact information.
    """
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle('About Proton Desktop')
        self.setFixedSize(300, 230)
        self.setWindowFlags(Qt.Popup)

        self.setStyleSheet("""
            QDialog {
                background-color: #2D2D2D;
                border-radius: 10px;
                padding: 10px;
            }
            QLabel {
                font-family: 'Arial';
                font-size: 12pt;
                color: white;
            }
            QLabel#title_label {
                font-size: 14pt;
                font-weight: bold;
                color: #0076D1;
            }
            QPushButton {
                font-family: 'Arial';
                font-size: 12pt;
                background-color: #0076D1;
                color: white;
                padding: 10px;
                border: none;
                border-radius: 10px;
                width: 100%;
            }
            QPushButton:hover {
                background-color: #005BB5;
            }
        """)

        layout = QVBoxLayout()

        title_label = QLabel('Proton Desktop')
        title_label.setObjectName("title_label")
        title_label.setAlignment(Qt.AlignCenter)
        layout.addWidget(title_label)

        info_label = QLabel('Version 0.1.0\nUnofficial desktop app for Proton.')
        info_label.setAlignment(Qt.AlignCenter)
        layout.addWidget(info_label)

        dev_label = QLabel('Author: Nemuel Wainaina\nContact: nemuelwainaina@proton.me')
        dev_label.setAlignment(Qt.AlignCenter)
        layout.addWidget(dev_label)

        ok_button = QPushButton("Ok")
        ok_button.clicked.connect(self.accept)
        layout.addWidget(ok_button)

        self.setLayout(layout)


class ProtonDesktopApp(QMainWindow):
    """
    Main application window for Proton Desktop
    """
    def __init__(self):
        super().__init__()

        self.proton_services = {
            'mail': 'https://mail.proton.me',
            'calendar': 'https://calendar.proton.me',
            'drive': 'https://drive.proton.me'
        }

        self.setWindowTitle('Proton Desktop')

        # window size and position
        screen_geometry = QApplication.desktop().availableGeometry()
        screen_width, screen_height = screen_geometry.width(), screen_geometry.width()
        self.setGeometry(0, 0, screen_width, screen_height)

        self.central_widget = QWidget(self)
        self.main_layout = QHBoxLayout(self.central_widget)
        self.main_layout.setContentsMargins(0, 0, 0, 0)
        self.main_layout.setSpacing(0)
        self.setCentralWidget(self.central_widget)

        # styles for tooltips
        self.setStyleSheet('''
            QToolTip {
                background-color: #333333;
                color: #ffffff;
                font: 14px;
                border: 1px solid #888888;
                padding: 5px;
                opacity: 200;
            }
        ''')

        # sidebar
        self.sidebar = QWidget(self)
        self.sidebar_layout = QVBoxLayout(self.sidebar)
        self.sidebar.setFixedWidth(60)
        self.sidebar.setSizePolicy(QSizePolicy.Fixed, QSizePolicy.Expanding)
        self.sidebar.setStyleSheet('background-color: #505264;')

        # sidebar buttons: mail, calendar, drive, donate, about
        self.add_button('mail', 'Mail', 'mail.svg')
        self.add_button('calendar', 'Calendar', 'calendar.svg')
        self.add_button('drive', 'Drive', 'drive.svg')
        self.sidebar_layout.addStretch()
        self.add_button('donate', 'Donate', 'donate.svg', self.show_donate_dialog)
        self.add_button('about', 'About', 'about.svg', self.show_about_dialog)

        self.main_layout.addWidget(self.sidebar, alignment=Qt.AlignLeft)

        # webview
        self.web = ProtonWebView(self)
        self.main_layout.addWidget(self.web)

        self.main_layout.setStretchFactor(self.web, 1)

    def add_button(self, service_name, tooltip, icon_path, on_clicked=None):
        """
        Add a button to the sidebar with the specified service name, tooltip, and icon.

        Args:
            service_name (str): The name of the Proton service being represented by the button.
            tooltip (str): The tooltip for the button.
            icon_path (str): The path to the icon file to use for the button.
            on_clicked (function): An optional callback function to be executed when the button is clicked.
        """
        btn = QPushButton(self)
        btn.setIcon(QIcon(asset_path(icon_path)))
        btn.setIconSize(QSize(32, 32))
        btn.setStyleSheet("border: none; margin: 2px;")
        btn.setToolTip(tooltip)

        btn.clicked.connect(lambda:
                            on_clicked() if on_clicked else self.load_proton_service(service_name))

        self.sidebar_layout.addWidget(btn)

    def load_proton_service(self, service_name):
        """
        Load the page for the specified Proton service inside the webview.

        Args:
            service_name (str): The name of the Proton service to load.
        """
        destination_url = self.proton_services.get(service_name, 'mail')
        self.web.load(QUrl(destination_url))

    def show_donate_dialog(self):
        """
        Show the 'Donate' dialog
        """
        DonateDialog(self).show()

    def show_about_dialog(self):
        """
        Show the 'About' dialog
        """
        AboutDialog(self).show()


if __name__ == "__main__":
    app = QApplication(sys.argv)
    app.setWindowIcon(QIcon(asset_path('logo.ico')))
    window = ProtonDesktopApp()
    window.show()
    sys.exit(app.exec_())
