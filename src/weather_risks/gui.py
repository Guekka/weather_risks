from datetime import datetime

from nicegui import ui
from weather_risks.api import geocode, get_precipitation_amounts
from weather_risks.pricing import PricingParameters, price_insurance_yearly_premium


class WeatherApp:
    def __init__(self):
        self.main_card = None
        self.selected_location = None
        self.prev_year = datetime.now().year - 1
        self.location_dropdown = None
        self.fetch_button = None
        self.chart_area = None
        self.location_input = None
        self.search_button = None
        self.year_input = None
        self.pivot_input = None
        self.turnover_input = None
        self.fixed_costs_input = None
        self.calculate_button = None
        self.results_area = None

        self.build_ui()

    def build_ui(self):
        self.main_card = ui.card().classes('w-full mx-auto mt-8')
        with self.main_card:
            # Section 1: Recherche de la localisation
            ui.label('Weather Data Viewer & Insurance Calculator').classes('text-2xl mb-4')

            self.location_input = ui.input(
                label='Enter a location', placeholder='E.g., Paris, Tokyo'
            ).classes('mb-2')

            self.search_button = ui.button('Search for Location')
            self.search_button.on('click', self.fetch_locations)

            self.location_dropdown = ui.select(
                label='Select Location', options=[]
            ).classes('mb-2')

            self.year_input = ui.number(
                label='Enter a Year', value=self.prev_year, min=1980, max=self.prev_year
            ).classes('mb-2')

            self.fetch_button = ui.button('Get Data & Update Chart')
            self.fetch_button.disable()
            self.fetch_button.on('click', self.fetch_data)

            # Section 2: Paramètres pour le calcul de la prime
            ui.separator()
            ui.label('Insurance Pricing Parameters').classes('text-xl mb-4')

            self.pivot_input = ui.number(label='Pivot Precipitation Amount (mm)').classes('mb-2')
            self.turnover_input = ui.number(label='Max Daily Turnover (€)').classes('mb-2')
            self.fixed_costs_input = ui.number(label='Fixed Daily Costs (€)').classes('mb-2')

            self.calculate_button = ui.button('Calculate Yearly Premium')
            self.calculate_button.on('click', self.calculate_premium)

            # Section 3: Résultats détaillés
            ui.separator()
            ui.label('Detailed Results').classes('text-xl mb-4')

            self.results_area = ui.card().classes('w-full mb-4')

            # Section 4: Graphique
            ui.separator()
            self.chart_area = ui.echart({
                "title": {"text": "No Data Available"},
                "xAxis": {"categories": []},
                "series": [{"data": []}],
            })

    def fetch_locations(self):
        self.search_button.disable()
        try:
            search_query = self.location_input.value
            if not search_query:
                ui.notify('Please enter a location.', color='red')
                return

            results = geocode(search_query)
            if results:
                options = [
                    f"{loc.name}, {loc.country} (Lat: {loc.latitude}, Lon: {loc.longitude})"
                    for loc in results
                ]
                self.location_dropdown.set_options(options, value=options[0])
                self.selected_location = results
                self.fetch_button.enable()
            else:
                ui.notify('No locations found', color='red')
        except Exception as e:
            ui.notify(f'Error: {e}', color='red')
        finally:
            self.search_button.enable()

    def fetch_data(self):
        if not self.selected_location or not self.location_dropdown.value:
            ui.notify('Please select a location', color='red')
            return

        try:
            index = self.location_dropdown.options.index(self.location_dropdown.value)
            loc = self.selected_location[index]
            year = int(self.year_input.value)

            data = get_precipitation_amounts(loc.latitude, loc.longitude, year)

            # Mise à jour du graphique
            self.update_chart(loc.name, year, data.days, data.values)

            # Stocker les données pour le calcul de la prime
            self.current_precipitation_data = data
            self.current_location = loc

            ui.notify(f'Data loaded for {loc.name} ({year}).', color='green')
        except Exception as e:
            ui.notify(f'Error: {e}', color='red')

    def update_chart(self, location_name, year, days, values):
        self.chart_area._props['options'] = {
            "title": {"text": f"Daily Precipitation for {location_name} ({year})"},
            "xAxis": {"type": "category", "data": days},
            "yAxis": {"type": "value"},
            "series": [
                {
                    "data": values,
                    "type": "line",
                    "smooth": True,
                    "areaStyle": {},
                }
            ],
        }

        self.chart_area.update()
        self.main_card.update()

    def calculate_premium(self):
        if not hasattr(self, 'current_precipitation_data') or not hasattr(self, 'current_location'):
            ui.notify('Please fetch weather data first.', color='red')
            return

        try:
            # Construire les paramètres pour la prime
            parameters = PricingParameters(
                pivot_precipitation_amount=self.pivot_input.value,
                max_daily_turnover=self.turnover_input.value,
                fixed_daily_costs=self.fixed_costs_input.value,
                subscription_date=f"{self.year_input.value}-01-01",
                location=self.current_location
            )

            # Calculer la prime et récupérer les détails
            pricing_details = price_insurance_yearly_premium(parameters)

            # Afficher les résultats détaillés
            self.display_results(pricing_details)

            ui.notify(f'Calculated Yearly Premium: €{pricing_details.yearly_premium:.2f}', color='green')
        except Exception as e:
            ui.notify(f'Error: {e}', color='red')

    def display_results(self, pricing_details):
        self.results_area.clear()

        with self.results_area:
            ui.label(f"Total Losses: €{pricing_details.total_losses:.2f}").classes('mb-2')
            ui.label(f"Yearly Premium (with Margin): €{pricing_details.yearly_premium:.2f}").classes('mb-2')

            ui.label("Daily Turnover and Results:").classes('text-lg mt-4')

            # Créer les colonnes et lignes pour le tableau
            columns = [
                {"header": "Day", "field": "day"},
                {"header": "Daily Turnover (€)", "field": "turnover"},
                {"header": "Daily Result (€)", "field": "result"},
            ]
            rows = [
                {"day": str(day), "turnover": f"{ca:.2f}", "result": f"{result:.2f}"}
                for day, ca, result in zip(
                    range(1, len(pricing_details.daily_ca) + 1),
                    pricing_details.daily_ca,
                    pricing_details.daily_results
                )
            ]

            # Créer un tableau dynamique avec pagination
            ui.table(columns=columns, rows=rows).classes('w-full mt-4')


def main():
    WeatherApp()
    ui.run(reload=False)