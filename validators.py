# forms.py
from urllib.parse import urlparse
from flask import flash
from wtforms import Form, StringField, TextAreaField, BooleanField, DateField, TimeField, ValidationError
from wtforms.validators import DataRequired, Optional, Length, Regexp, Email
from flask_wtf.file import FileAllowed

import re


class FormValidators:

    SQL_KEYWORDS = [
        "select", "insert", "update", "delete", "drop", "alter",
        "create", "truncate", "union", "exec", "execute", "grant",
        "revoke", "commit", "rollback", "merge", "call", "declare"
    ]

    SQL_PATTERNS = [
        r"--", r";", r"/\*", r"\*/", r"@@", r"char\(", r"nchar\(",
        r"varchar\(", r"nvarchar\(", r"cast\(", r"convert\(",
        r" or ", r" and ", r"=.+="
    ]

    @staticmethod
    def contains_sql(value: str) -> bool:
        if value is None:
            return False
        val = value.lower()
        for kw in FormValidators.SQL_KEYWORDS:
            if re.search(rf"\b{kw}\b", val):
                return True
        for pat in FormValidators.SQL_PATTERNS:
            if re.search(pat, val):
                return True
        return False

    @staticmethod
    def no_sql(form, field):
        if FormValidators.contains_sql(field.data):
            raise ValidationError("SQL code is not allowed")

    @staticmethod
    def contains_html(value) -> bool:
        if value is None:
            return False
        return bool(re.search(r'<[^>]+>', str(value)))

    @staticmethod
    def no_html(form, field):
        if FormValidators.contains_html(field.data):
            flash("HTML tags are not allowed", "error")
            raise ValidationError("HTML tags are not allowed")

    @staticmethod
    def validate_url(value, field_name: str, allowed_domains=None):
        if not value:
            raise ValidationError(f"{field_name} cannot be empty")
        if FormValidators.contains_html(value) or FormValidators.contains_sql(value):
            raise ValidationError(f"{field_name} cannot contain HTML or SQL")
        parsed = urlparse(value)
        if parsed.scheme not in ('http', 'https'):
            raise ValidationError(f"{field_name} must start with http:// or https://")
        if allowed_domains:
            if isinstance(allowed_domains, str):
                allowed_domains = [allowed_domains]
            if not any(d in parsed.netloc for d in allowed_domains):
                raise ValidationError(f"{field_name} must belong to allowed domains: {', '.join(allowed_domains)}")

    @staticmethod
    def url_validator_factory(field_name: str, allowed_domains=None):
        def _validator(form, field):
            FormValidators.validate_url(field.data, field_name or field.label.text, allowed_domains)
        return _validator

    @staticmethod
    def validate_cap(value: str):
        if not value.isdigit() or len(value) != 5:
            flash("CAP must be exactly 5 digits", "error")
            return False
        return True

    @staticmethod
    def validate_nr(value: str):
        if len(value) > 10 or not any(c.isdigit() for c in value):
            flash("Nr must be max 10 characters and contain at least one digit", "error")
            return False
        return True
    

    @staticmethod
    def validate_board_message(value: str, field_name: str = "Board Message"):
        if not isinstance(value, str):
            raise ValidationError(f"{field_name} must be a string")
        if FormValidators.contains_html(value) or FormValidators.contains_sql(value):
            raise ValidationError(f"{field_name} cannot contain HTML or SQL")
        length = len(value.strip()) if value else 0
        if length <= 0:
            raise ValidationError(f"{field_name} cannot be empty")
        if length > 500:
            raise ValidationError(f"{field_name} cannot exceed 500 characters")

    @staticmethod
    def validate_page_description(value: str, field_name: str = "Page Description"):
        if not isinstance(value, str):
            raise ValidationError(f"{field_name} must be a string")
        if FormValidators.contains_html(value) or FormValidators.contains_sql(value):
            raise ValidationError(f"{field_name} cannot contain HTML or SQL")
        length = len(value.strip()) if value else 0
        if length <= 0:
            raise ValidationError(f"{field_name} cannot be empty")
        if length > 500:
            raise ValidationError(f"{field_name} cannot exceed 500 characters")

    @staticmethod
    def validate_album_name(value: str, field_name: str = "Album Name"):
        if not isinstance(value, str):
            raise ValidationError(f"{field_name} must be a string")
        if FormValidators.contains_html(value) or FormValidators.contains_sql(value):
            raise ValidationError(f"{field_name} cannot contain HTML or SQL")
        length = len(value.strip()) if value else 0
        if length <= 0:
            raise ValidationError(f"{field_name} cannot be empty")
        if length > 100:
            raise ValidationError(f"{field_name} cannot exceed 50 characters")
        
    @staticmethod
    def validate_album_description(value: str, field_name: str = "Album Description"):
        if not isinstance(value, str):
            raise ValidationError(f"{field_name} must be a string")
        if FormValidators.contains_html(value) or FormValidators.contains_sql(value):
            raise ValidationError(f"{field_name} cannot contain HTML or SQL")
        length = len(value.strip()) if value else 0
        # Qui 0 è accettato → campo opzionale
        if length > 500:
            raise ValidationError(f"{field_name} cannot exceed 250 characters")