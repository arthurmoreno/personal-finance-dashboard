import re


class TransactionProcessor:
    def __init__(self, config):
        self.config = config

    def map_categories(self, data, first_time=True):
        """Maps transaction descriptions to predefined categories and subcategories based on matching rules from the YAML file."""
        if first_time:
            data = data.assign(
                SUBCATEGORY="UNKNOWN",
                CATEGORY="UNKNOWN",
            )
        data = data.assign(
            SUBCATEGORY_COUNT=0,
            CATEGORY_COUNT=0,
        )

        subcategories = self.config["SUBCATEGORIES"]
        for subcategory, matches in subcategories.items():
            pattern = "|".join(re.escape(match) for match in matches)
            cond = (data["DESCRIPTION"].str.contains(pattern, na=False)) & (
                data["SUBCATEGORY"] == "UNKNOWN"
            )
            data.loc[
                cond,
                "SUBCATEGORY_COUNT",
            ] += 1
            data.loc[
                cond,
                "SUBCATEGORY",
            ] = subcategory

        categories = self.config["CATEGORIES"]
        for category, matches in categories.items():
            cond = data["SUBCATEGORY"].apply(lambda x: x in matches)
            data.loc[
                cond,
                "CATEGORY_COUNT",
            ] += 1
            data.loc[
                cond,
                "CATEGORY",
            ] = category
        return data

    def validate_data(self, data):
        """Validates the processed data to ensure there are no duplicate categories or subcategories and all transactions are categorized correctly."""

        try:
            assert data[data["SUBCATEGORY_COUNT"] > 1].shape[0] == 0
        except AssertionError as e:
            e.args += (
                "Some of your transactions have multiple subcategories assigned to them. Please ensure that each transaction is assigned to one category only.",
            )
            raise
        try:
            assert data[data["CATEGORY_COUNT"] > 1].shape[0] == 0
        except AssertionError as e:
            e.args += (
                "Some of your transactions have multiple categories assigned to them. Please ensure that each transaction is assigned to one category only.",
            )
            raise

        unknown_filter = (
            (data["CATEGORY"] == "UNKNOWN")
            & (data["SUBCATEGORY"] == "UNKNOWN")
            & (data["SUBCATEGORY_COUNT"] == 0)
            & (data["CATEGORY_COUNT"] == 0)
        )
        try:
            assert (
                data[data["SUBCATEGORY_COUNT"] > data["CATEGORY_COUNT"]].shape[0] == 0
            )
        except AssertionError as e:
            e.args += (
                "Some of your subcategories have not been assigned to a category in the config file.",
            )
            raise

        assert (
            data[unknown_filter].shape[0]
            == data[data["CATEGORY"] == "UNKNOWN"].shape[0]
        )

        if "TRANSACTION_ID" in data.columns:
            assert (  # this still has to be tested -- can also remove
                data.groupby("TRANSACTION_ID")
                .size()
                .reset_index(name="count")
                .query("count > 1")
                .shape[0]
                == 0
            )

    def remove_columns(self, data):
        """Removes columns that are not needed for the analysis."""
        return data.drop(["SUBCATEGORY_COUNT", "CATEGORY_COUNT"], axis=1)

    def write_data(self, data, filename):
        """Writes the processed transaction data to an Excel file with the specified filename."""
        data = data.select(self.select_columns)
        data.to_excel(filename, index=False)

    def map_and_validate_categories(self, org_data):
        categorized_data = self.map_categories(org_data)
        self.validate_data(categorized_data)
        categorized_data = self.remove_columns(categorized_data)
        return categorized_data
