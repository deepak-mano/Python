from __future__ import annotations

import argparse
import json
import re
from dataclasses import dataclass
from pathlib import Path


PROVINCE_LOOKUP_FILE = Path(__file__).with_name("province_codes.json")
POSTAL_PREFIX_LOOKUP_FILE = Path(__file__).with_name("postal_prefixes.json")
POSTAL_CODE_PATTERN = re.compile(r"^[A-CEGHJ-NPR-TV-Z]\d[A-CEGHJ-NPR-TV-Z]\d[A-CEGHJ-NPR-TV-Z]\d$", re.IGNORECASE)


@dataclass(slots=True)
class ValidationResult:
    is_valid: bool
    errors: list[str]
    normalized_address: dict[str, str]


def load_province_codes(lookup_file: Path = PROVINCE_LOOKUP_FILE) -> dict[str, str]:
    data = json.loads(lookup_file.read_text(encoding="utf-8"))
    if not isinstance(data, dict):
        raise ValueError("Province lookup file must contain a JSON object of province codes.")

    province_codes: dict[str, str] = {}
    for code, name in data.items():
        if not isinstance(code, str) or not isinstance(name, str):
            raise ValueError("Province lookup entries must use string keys and values.")
        province_codes[code.strip().upper()] = name.strip()

    return province_codes


def load_postal_prefixes(lookup_file: Path = POSTAL_PREFIX_LOOKUP_FILE) -> dict[str, set[str]]:
    data = json.loads(lookup_file.read_text(encoding="utf-8"))
    if not isinstance(data, dict):
        raise ValueError("Postal prefix lookup file must contain a JSON object of province codes.")

    postal_prefixes: dict[str, set[str]] = {}
    for code, prefixes in data.items():
        if not isinstance(code, str) or not isinstance(prefixes, list):
            raise ValueError("Postal prefix lookup entries must use string keys and list values.")

        normalized_prefixes: set[str] = set()
        for prefix in prefixes:
            if not isinstance(prefix, str) or len(prefix.strip()) != 1:
                raise ValueError("Postal prefix values must be single-character strings.")
            normalized_prefixes.add(prefix.strip().upper())

        postal_prefixes[code.strip().upper()] = normalized_prefixes

    return postal_prefixes


def normalize_postal_code(postal_code: str) -> str:
    compact_code = re.sub(r"\s+", "", postal_code).upper()
    if len(compact_code) != 6:
        return compact_code
    return f"{compact_code[:3]} {compact_code[3:]}"


def validate_canadian_address(
    line1: str,
    line2: str,
    city: str,
    province: str,
    postal_code: str,
    lookup_file: Path = PROVINCE_LOOKUP_FILE,
) -> ValidationResult:
    errors: list[str] = []
    province_codes = load_province_codes(lookup_file)
    postal_prefixes = load_postal_prefixes()

    normalized_line1 = line1.strip()
    normalized_line2 = line2.strip()
    normalized_city = city.strip()
    normalized_province = province.strip().upper()
    normalized_postal = normalize_postal_code(postal_code)
    postal_prefix = normalized_postal[:1]

    if not normalized_line1:
        errors.append("Address line 1 is required.")
    if not normalized_city:
        errors.append("City is required.")
    if not normalized_province:
        errors.append("Province code is required.")
    elif normalized_province not in province_codes:
        errors.append(f"Province code '{normalized_province}' is not a valid Canadian province or territory code.")

    if not postal_code.strip():
        errors.append("Postal code is required.")
    elif not POSTAL_CODE_PATTERN.fullmatch(normalized_postal.replace(" ", "")):
        errors.append("Postal code must match the Canadian format A1A 1A1 and use valid postal characters.")
    elif normalized_province in postal_prefixes and postal_prefix not in postal_prefixes[normalized_province]:
        allowed_prefixes = ", ".join(sorted(postal_prefixes[normalized_province]))
        errors.append(
            f"Postal code prefix '{postal_prefix}' is not valid for province code '{normalized_province}'. "
            f"Expected one of: {allowed_prefixes}."
        )

    normalized_address = {
        "line1": normalized_line1,
        "line2": normalized_line2,
        "city": normalized_city,
        "province": normalized_province,
        "postal_code": normalized_postal,
    }

    return ValidationResult(is_valid=not errors, errors=errors, normalized_address=normalized_address)


def _prompt_if_missing(value: str | None, label: str, required: bool = True) -> str:
    if value is not None:
        return value

    while True:
        entered_value = input(f"Enter {label}: ").strip()
        if entered_value or not required:
            return entered_value
        print(f"{label} is required.")


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Validate a Canadian address.")
    parser.add_argument("--line1", help="Address line 1")
    parser.add_argument("--line2", help="Address line 2", default="")
    parser.add_argument("--city", help="City")
    parser.add_argument("--province", help="Two-letter province or territory code")
    parser.add_argument("--postal-code", help="Canadian postal code")
    return parser


def format_result(result: ValidationResult) -> str:
    if result.is_valid:
        return "Address is valid."

    error_text = "\n".join(f"- {error}" for error in result.errors)
    return f"Address is invalid:\n{error_text}"


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)

    line1 = _prompt_if_missing(args.line1, "address line 1")
    line2 = args.line2 if args.line2 is not None else ""
    city = _prompt_if_missing(args.city, "city")
    province = _prompt_if_missing(args.province, "province code")
    postal_code = _prompt_if_missing(args.postal_code, "postal code")

    result = validate_canadian_address(line1, line2, city, province, postal_code)
    print(format_result(result))

    if result.is_valid:
        print(f"Normalized postal code: {result.normalized_address['postal_code']}")
        return 0

    return 1


if __name__ == "__main__":
    raise SystemExit(main())
