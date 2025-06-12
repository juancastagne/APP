import os
from src.ui.app import StreamViewerApp

if __name__ == "__main__":
    port = int(os.getenv("PORT", 8080))
    app = StreamViewerApp()
    app.start(port=port) 