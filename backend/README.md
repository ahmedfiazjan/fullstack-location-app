# Location API Backend

A Django REST API for managing geographical data including countries, states, cities, and zip codes.

## Features
- REST API endpoints for countries, states, cities, and zip codes
- Advanced search functionality with prioritized results
- Pagination and filtering
- Bulk data import functionality
- Optimized database queries

## Prerequisites
- Python 3.8 or higher
- pip (Python package installer)
- SQLite database with location data

## Setup Instructions

1. Create and activate virtual environment:
```bash
# Create virtual environment
python -m venv venv

# Activate virtual environment
# On Windows:
venv\Scripts\activate
# On Unix/MacOS:
source venv/bin/activate
```

2. Install required packages:
```bash
pip install -r requirements.txt
```

3. Set up the database:
```bash
# Create database tables
python manage.py makemigrations
python manage.py migrate
```

4. Import location data:
```bash
# Make sure your SQLite database file is in the correct location (which is in the root of the backendproject)
python manage.py import_locations
```

5. Run the development server:
```bash
python manage.py runserver
```

## API Endpoints

### Countries
- List/Search: `GET /api/countries/`
- Search parameters: `?search=term`
- Example: `http://localhost:8000/api/countries/?search=united`

### States
- List/Search: `GET /api/states/`
- Filter by country: `?country=country_id`
- Search: `?search=term`
- Example: `http://localhost:8000/api/states/?country=1&search=new`

### Cities
- List/Search: `GET /api/cities/`
- Filter by state: `?state=state_id`
- Search with prioritization: `?search=term`
- Example: `http://localhost:8000/api/cities/?state=1387&search=york`

### Locations/Zip Codes
- List/Search: `GET /api/locations/` or `GET /api/zipcodes/`
- Filter by city: `?city=city_id`
- Search: `?search=term`
- Example: `http://localhost:8000/api/zipcodes/?city=10224`

## Search Features
- Partial matching
- Case-insensitive search
- Prioritized results (exact matches, starts with, contains)
- Combined filters (e.g., search within a state)

## Database Schema
- Countries: id, name, alpha2, alpha3
- States: id, name, country(FK), abbreviation
- Cities: id, name, state(FK)
- Locations: city(FK), state(FK), country(FK), zip_code, latitude, longitude

## Development

### Running Tests
```bash
python manage.py test
```

### Code Style
Follow PEP 8 guidelines for Python code style.

### Debug Mode
Set `DEBUG = True` in settings.py for development.

## Troubleshooting

### Common Issues

1. Database Import Fails:
   - Verify database file exists
   - Check file permissions
   - Ensure correct table structure

2. Search Not Working:
   - Verify database contains data
   - Check search parameters
   - Look for exact spelling

3. No Results:
   - Verify pagination parameters
   - Check filter combinations
   - Ensure data exists for criteria

## Contributing
1. Fork the repository
2. Create a feature branch
3. Commit changes
4. Push to the branch
5. Create a Pull Request

## License
This project is licensed under the MIT License.
