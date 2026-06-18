# Python

Canadian address validator.

## Usage

Run the validator with address fields as command-line arguments:

```bash
python -m src.address_validator --line1 "111 Wellington St" --city "Ottawa" --province "ON" --postal-code "K1A 0A9"
```

`--line2` is optional. If a value is not provided on the command line, the program will prompt for it.

The province lookup is stored in `src/province_codes.json` and can be edited if the list changes.
The postal-prefix lookup is stored in `src/postal_prefixes.json` and enforces the Canadian postal-code first-letter by province or territory.

## Flask API

Install dependencies and run the API:

```bash
pip install -r requirements.txt
python -m src.flask_api
```

POST JSON to `/validate` with `line1`, `line2`, `city`, `province`, and `postal_code`.

Example request:

```bash
curl -X POST http://127.0.0.1:5000/validate \
	-H "Content-Type: application/json" \
	-d "{\"line1\":\"111 Wellington St\",\"city\":\"Ottawa\",\"province\":\"ON\",\"postal_code\":\"K1A 0A9\"}"
```