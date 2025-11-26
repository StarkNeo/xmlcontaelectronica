import threading
import webview
import os
from app import app

#def run_flask():
 #   app.run(debug=False)

    
if __name__ == '__main__':
    app.run(debug=True)
    #threading.Thread(target=run_flask).start()
    #webview.create_window("XML Creator", "http://127.0.0.1:5000")