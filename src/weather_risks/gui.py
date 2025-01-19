from datetime import datetime

from nicegui import ui

from weather_risks.api import geocode, get_precipitation_amounts


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

        self.build_ui()

    def build_ui(self):
        self.main_card = ui.card().classes('w-full mx-auto mt-8')
        with self.main_card:
            ui.label('Weather Data Viewer').classes('text-2xl mb-4')

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

            self.fetch_button = ui.button('Get Precipitation Data')
            self.fetch_button.disable()
            self.fetch_button.on('click', self.fetch_precipitation_data)

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

    def fetch_precipitation_data(self):
        if not self.selected_location or not self.location_dropdown.value:
            ui.notify('Please select a location', color='red')
            return

        try:
            index = self.location_dropdown.options.index(self.location_dropdown.value)
            loc = self.selected_location[index]
            year = int(self.year_input.value)

            data = get_precipitation_amounts(loc.latitude, loc.longitude, year)

            # Update the chart with new data
            self.update_chart(loc.name, year, data.days, data.values)
        except Exception as e:
            ui.notify(f'Error: {e}', color='red')

    def update_chart(self, location_name, year, days, values):
        # the documentation states that data can be changed by changing the options property,
        # but options is a read-only property so we have to use _props instead
        # noinspection PyProtectedMember
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


def main():
    WeatherApp()
    ui.run()


if __name__ == "__main__":
    main()
