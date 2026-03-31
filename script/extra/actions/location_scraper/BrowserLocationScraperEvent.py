from script.extra.helper import go_to_page
from script.models.Country import Country
from script.models.City import City
from script.models.Location import Location
import requests
import random

# Configuration
TARGET_COUNTRY_CODE = 'US'
TARGET_COUNTRY_NAME = 'United States'
TARGET_COUNTRY_SLUG = 'united-states'


class BrowserLocationScraperEvent:
    ig = None
    session = None
    countries_collected = 0
    cities_collected = 0
    locations_collected = 0

    def __init__(self, ig):
        self.ig = ig

    def init(self):
        go_to_page(self.ig, "https://www.instagram.com/explore/locations/", 'Locations')
        self.ig.pause(7000, 8000)
        go_to_page(
            self.ig,
            f"https://www.instagram.com/explore/locations/{TARGET_COUNTRY_CODE}/{TARGET_COUNTRY_SLUG}/",
            'Country'
        )
        self.ig.pause(7000, 8000)

        if not self._validate_graphql_data():
            self.ig.account.add_cli('GraphQL data not available, skipping')
            return

        self.session = self._create_proxied_session()
        if not self.session:
            self.ig.account.add_cli('Cannot proceed without proxy')
            return

        # Phase 0: Collect countries
        self._phase_countries()

        # Get or create target country in DB
        country = self._get_target_country()
        if not country:
            self.ig.account.add_cli('Target country not found in DB, stopping')
            return

        # Phase 1: Collect cities for target country
        self._phase_cities(country)

        # Phase 2: Collect locations for each city
        self._phase_locations(country)

        self.ig.account.add_cli(
            f'Done. Countries: {self.countries_collected}, '
            f'Cities: {self.cities_collected}, '
            f'Locations: {self.locations_collected}'
        )

        if self.session:
            self.session.close()

    # Phase 1: Countries

    def _phase_countries(self):
        existing = Country.select().count()
        if existing > 0:
            self.ig.account.add_cli(f'Countries already collected ({existing}), skipping')
            return

        self.ig.account.add_cli('Collecting countries ...')
        page = 1

        while True:
            self.ig.account.add_cli(f'Fetching countries page {page} ...')

            try:
                data = self._fetch_api_page(
                    'https://www.instagram.com/api/v1/web/explore/locations/',
                    'https://www.instagram.com/explore/locations/',
                    page
                )
            except Exception as e:
                self.ig.account.add_cli(f'Failed to fetch countries page {page}: {str(e)}')
                break

            country_list = data.get('country_list', [])

            if not country_list:
                break

            for c in country_list:
                code = c.get('id', '')
                name = c.get('name', '')
                slug = c.get('slug', '')

                if not code or not name:
                    continue

                try:
                    Country.get_or_create(
                        country_code=code,
                        defaults={'name': name, 'slug': slug}
                    )
                    self.countries_collected += 1
                except Exception:
                    pass

            next_page = data.get('next_page')
            if not next_page:
                break

            page = next_page
            self.ig.pause(4000, 8000)

        # Make sure target country exists even if API didn't return it
        Country.get_or_create(
            country_code=TARGET_COUNTRY_CODE,
            defaults={'name': TARGET_COUNTRY_NAME, 'slug': TARGET_COUNTRY_SLUG}
        )

        self.ig.account.add_cli(f'Countries collected: {self.countries_collected}')

    # Phase 2: Cities

    def _phase_cities(self, country):
        existing = City.select().where(City.country == country.id).count()
        if existing > 0:
            self.ig.account.add_cli(f'Cities already collected for {country.name} ({existing}), skipping')
            return

        self.ig.account.add_cli(f'Collecting cities for {country.name} ...')
        page = 1

        while True:
            self.ig.account.add_cli(f'Fetching cities page {page} ...')

            try:
                data = self._fetch_api_page(
                    f'https://www.instagram.com/api/v1/web/explore/locations/{TARGET_COUNTRY_CODE}/',
                    f'https://www.instagram.com/explore/locations/{TARGET_COUNTRY_CODE}/{TARGET_COUNTRY_SLUG}/',
                    page
                )
            except Exception as e:
                self.ig.account.add_cli(f'Failed to fetch cities page {page}: {str(e)}')
                break

            city_list = data.get('city_list', [])

            if not city_list:
                break

            for c in city_list:
                city_id = c.get('id', '')
                name = c.get('name', '')
                slug = c.get('slug', '')

                if not city_id or not name:
                    continue

                try:
                    City.get_or_create(
                        city_id=city_id,
                        defaults={
                            'name': name,
                            'slug': slug,
                            'country': country.id,
                        }
                    )
                    self.cities_collected += 1
                except Exception as e:
                    self.ig.account.add_cli(f'Failed to save city {name}: {str(e)}')

            next_page = data.get('next_page')
            if not next_page:
                break

            page = next_page
            self.ig.pause(4000, 8000)

        self.ig.account.add_cli(f'Cities collected: {self.cities_collected}')

    # Phase 3: Locations

    def _phase_locations(self, country):
        cities = list(
            City
            .select()
            .where(City.country == country.id)
            .order_by(City.id)
        )

        self.ig.account.add_cli(f'Collecting locations for {len(cities)} cities ...')

        for city in cities:
            existing = Location.select().where(Location.city == city.id).count()
            if existing > 0:
                self.ig.account.add_cli(f'Locations for {city.name} already collected ({existing}), skipping')
                continue

            try:
                self._collect_locations_for_city(city)
                self.ig.pause(6000, 10000)
            except Exception as e:
                self.ig.account.add_cli(f'Failed for {city.name}: {str(e)}')

        self.ig.account.add_cli(f'Locations collected: {self.locations_collected}')

    def _collect_locations_for_city(self, city):
        page = 1

        while True:
            self.ig.account.add_cli(f'  Fetching locations page {page} for {city.name} ...')

            try:
                data = self._fetch_api_page(
                    f'https://www.instagram.com/api/v1/web/explore/locations/{city.city_id}/',
                    f'https://www.instagram.com/explore/locations/{city.city_id}/{city.slug}/',
                    page
                )
            except Exception as e:
                self.ig.account.add_cli(f'  Failed to fetch locations page {page}: {str(e)}')
                break

            location_list = data.get('location_list', [])

            if not location_list:
                break

            for loc in location_list:
                location_id = loc.get('id', '')
                name = loc.get('name', '')
                slug = loc.get('slug', '')

                if not location_id or not name:
                    continue

                try:
                    Location.get_or_create(
                        location_id=location_id,
                        defaults={
                            'name': name,
                            'slug': slug,
                            'city': city.id,
                        }
                    )
                    self.locations_collected += 1
                except Exception:
                    pass

            next_page = data.get('next_page')
            if not next_page:
                break

            page = next_page
            self.ig.pause(4000, 8000)


    def _fetch_api_page(self, url, referer, page):
        headers = self.ig.graphql_data['headers'].copy()
        headers['referer'] = referer

        payload = {
            'page': str(page),
            'jazoest': str(random.randint(20000, 29999)),
        }

        response = self.session.post(url, headers=headers, data=payload, timeout=30)

        if response.status_code != 200:
            self.ig.account.add_cli(
                f'[API] status={response.status_code}, '
                f'content_type={response.headers.get("content-type", "unknown")}, '
                f'body={response.text[:500]}'
            )
            response.raise_for_status()

        if not response.text.strip():
            self.ig.account.add_cli('[API] Empty response body')
            raise Exception('Empty response body')

        try:
            return response.json()
        except Exception:
            self.ig.account.add_cli(
                f'[API] Invalid JSON, '
                f'content_type={response.headers.get("content-type", "unknown")}, '
                f'length={len(response.text)}, '
                f'body={response.text[:500]}'
            )
            raise

    def _get_target_country(self):
        try:
            return Country.get(Country.country_code == TARGET_COUNTRY_CODE)
        except Country.DoesNotExist:
            return None

    def _validate_graphql_data(self):
        if not hasattr(self.ig, 'graphql_data') or not self.ig.graphql_data:
            return False

        if 'headers' not in self.ig.graphql_data:
            return False

        return True

    def _create_proxied_session(self):
        session = requests.Session()

        try:
            proxy = self.ig.proxy
            if not proxy:
                self.ig.account.add_cli('[PROXY] No proxy found')
                return None

            session.proxies = proxy.to_requests_proxy()

            if not self._verify_proxy_ip(session, proxy):
                return None

        except Exception as e:
            self.ig.account.add_cli(f'[PROXY] Setup error: {str(e)}')
            return None

        return session

    def _verify_proxy_ip(self, session, proxy):
        stored_ip = proxy.real_ip or 'unknown'

        try:
            response = session.get('https://api.ipify.org?format=json', timeout=10)
            if response.status_code == 200:
                current_ip = response.json().get('ip', 'unknown')

                if current_ip == stored_ip:
                    self.ig.account.add_cli(f'[PROXY] {current_ip} -> OK')
                    return True
                else:
                    self.ig.account.add_cli(f'[PROXY] {current_ip} vs {stored_ip} -> MISMATCH')
                    return False

            self.ig.account.add_cli(f'[PROXY] {stored_ip} -> verify skipped')
            return True

        except Exception:
            self.ig.account.add_cli(f'[PROXY] {stored_ip} -> verify skipped')
            return True