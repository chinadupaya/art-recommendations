from hsfs.feature import Feature

### Post ingestion format.###

customer_feature_descriptions = [
    {"name": "user_id", "description": "Unique identifier for each user."},
    {"name": "age", "description": "Age of the user."},
    {"name": "preference", "description": "Preference of the user."},
    {
        "name": "gender",
        "description": "User gender",
    },
    {"name": "age_group", "description": "Categorized age group of the customer."},
]

transactions_feature_descriptions = [
    {"name": "t_dat", "description": "Timestamp of the data record."},
    {"name": "user_id", "description": "Unique identifier for each customer."},
    {"name": "artwork_id", "description": "Identifier for the liked artwork."},
    {"name": "year", "description": "Year of the transaction."},
    {"name": "month", "description": "Month of the transaction."},
    {"name": "day", "description": "Day of the transaction."},
    {"name": "day_of_week", "description": "Day of the week of the transaction."},
]

interactions_feature_descriptions = [
    {"name": "t_dat", "description": "Timestamp of the interaction."},
    {"name": "user_id", "description": "Unique identifier for each customer."},
    {
        "name": "artwork_id",
        "description": "Identifier for the artwork that was interacted with.",
    },
    {
        "name": "interaction_score",
        "description": "Type of interaction: 0 = ignore, 1 = click, 2 = like.",
    },
    {
        "name": "prev_artwork_id",
        "description": "Previous artwork that the customer interacted with, useful for sequential recommendation patterns.",
    },
]

ranking_feature_descriptions = [
    {"name": "customer_id", "description": "Unique identifier for each customer."},
    {"name": "artwork_id", "description": "Identifier for the liked artwork."},
    {"name": "age", "description": "Age of the customer."},
    {"name": "product_type_name", "description": "Name of the product type."},
    {"name": "product_group_name", "description": "Name of the product group."},
    {
        "name": "graphical_appearance_name",
        "description": "Name of the graphical appearance.",
    },
    {"name": "colour_group_name", "description": "Name of the colour group."},
    {
        "name": "perceived_colour_value_name",
        "description": "Name of the perceived colour value.",
    },
    {
        "name": "perceived_colour_master_name",
        "description": "Name of the perceived colour master.",
    },
    {"name": "department_name", "description": "Name of the department."},
    {"name": "index_name", "description": "Name of the index."},
    {"name": "index_group_name", "description": "Name of the index group."},
    {"name": "section_name", "description": "Name of the section."},
    {"name": "garment_group_name", "description": "Name of the garment group."},
    {
        "name": "label",
        "description": "Label indicating whether the artwork was liked (1) or not (0).",
    },
]

### Pre ingestion format. ###

artwork_feature_description = [
    Feature(
        name="artwork_id", type="string", description="Identifier for the artwork."
    ),
    Feature(name="title", type="string", description="Name of the artwork."),
    Feature(
        name="category",
        type="string",
        description="Type of artwork",
    ),
    Feature(
        name="thumbnail_link", type="string", description="URL of the artwork."
    ),
    Feature(
        name="description",
        type="string",
        description="Description of the artwork.",
    ),
    Feature(
        name="embeddings",
        type="array<double>",
        description="Vector embeddings of the artwork description.",
    )
]