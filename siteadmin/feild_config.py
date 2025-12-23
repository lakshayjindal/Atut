# operator/operator_fields.py

"""
Field configuration for operator-driven data entry.

This defines:
- Which fields operators can enter
- Which fields are mandatory
- How fields should be rendered in UI
- Which model they belong to
"""

OPERATOR_FIELDS = [
    # --------------------
    # REQUIRED CORE FIELDS
    # --------------------

    {
        "key": "full_name",
        "label": "Full Name",
        "model": "profile",
        "required": True,
        "type": "text",
    },
    {
        "key": "gender",
        "label": "Gender",
        "model": "profile",
        "required": True,
        "type": "select",
        "choices": ["Male", "Female", "Other"],
    },
    {
        "key": "phone1",
        "label": "Primary Phone",
        "model": "profile",
        "required": True,
        "type": "text",
    },
    {
        "key": "city",
        "label": "City",
        "model": "profile",
        "required": True,
        "type": "text",
    },

    # --------------------
    # OPTIONAL BASIC FIELDS
    # --------------------

    {
        "key": "phone2",
        "label": "Alternate Phone",
        "model": "profile",
        "required": False,
        "type": "text",
    },
    {
        "key": "date_of_birth",
        "label": "Date of Birth",
        "model": "profile",
        "required": False,
        "type": "date",
    },
    {
        "key": "age",
        "label": "Age",
        "model": "profile",
        "required": False,
        "type": "number",
    },
    {
        "key": "height",
        "label": "Height",
        "model": "profile",
        "required": False,
        "type": "text",
    },

    # --------------------
    # CULTURAL BACKGROUND
    # --------------------

    {
        "key": "religion",
        "label": "Religion",
        "model": "profile",
        "required": False,
        "type": "select",
        "choices": ["Hindu", "Muslim", "Christian", "Sikh", "Other"],
    },
    {
        "key": "caste",
        "label": "Caste",
        "model": "profile",
        "required": False,
        "type": "text",
    },
    {
        "key": "gotra",
        "label": "Gotra",
        "model": "profile",
        "required": False,
        "type": "text",
    },
    {
        "key": "mother_tongue",
        "label": "Mother Tongue",
        "model": "profile",
        "required": False,
        "type": "text",
    },

    # --------------------
    # EDUCATION & WORK
    # --------------------

    {
        "key": "education",
        "label": "Education",
        "model": "profile",
        "required": False,
        "type": "text",
    },
    {
        "key": "profession",
        "label": "Profession",
        "model": "profile",
        "required": False,
        "type": "text",
    },
    {
        "key": "occupation",
        "label": "Occupation",
        "model": "profile",
        "required": False,
        "type": "text",
    },
    {
        "key": "income",
        "label": "Income",
        "model": "profile",
        "required": False,
        "type": "text",
    },

    # --------------------
    # PREFERENCES & NOTES
    # --------------------

    {
        "key": "marital_status",
        "label": "Marital Status",
        "model": "profile",
        "required": False,
        "type": "select",
        "choices": ["Single", "Married"],
    },
    {
        "key": "looking_for",
        "label": "Looking For",
        "model": "profile",
        "required": True,
        "type": "select",
        "choices": ["Bride", "Groom", "Other"],
    },
    {
        "key": "bio",
        "label": "Bio",
        "model": "profile",
        "required": False,
        "type": "textarea",
    },
    {
        "key": "notes",
        "label": "Internal Notes",
        "model": "profile",
        "required": False,
        "type": "textarea",
    },

    # --------------------
    # MEDIA (SPECIAL CASE)
    # --------------------

    {
        "key": "pictures",
        "label": "Photos",
        "model": "picture",
        "required": False,
        "type": "media",
        "multiple": True,
        "note": "Handled separately after user creation",
    },
]
