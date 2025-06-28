from shiny import App
from modules.dashboard import dashboard_ui, dashboard_server
from modules.alerts import AlertSystem
from utils.database import DatabaseConnection

# Initialize components
db = DatabaseConnection()
alert_system = AlertSystem()

app = App(
    ui=dashboard_ui,
    server=dashboard_server
)

if __name__ == "__main__":
    app.run()
