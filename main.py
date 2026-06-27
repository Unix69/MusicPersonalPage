from app_core import App

try:
    web_app = App.create_app()
    configuration = web_app.configure()
    web_app.init()
    application = web_app.get_flask_app()
except Exception as e:
    # questo stampa subito eventuali errori all’avvio
    import traceback, sys
    traceback.print_exc(file=sys.stderr)
    raise
