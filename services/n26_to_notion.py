import os
import csv
from openai import OpenAI

import json
from abc import ABC, abstractmethod

client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
# Set your OpenAI API key

class Extractor:
    """Class responsible for extracting data from the input CSV file."""
    def __init__(self, input_file):
        self.input_file = input_file

    def extract(self):
        """Extracts data from the CSV file."""
        with open(self.input_file, mode='r', newline='', encoding='utf-8') as infile:
            reader = csv.DictReader(infile)
            data = [row for row in reader]
        return data

class Transformer:
    """Class responsible for validating and transforming the extracted data."""
    def __init__(self, data):
        self.data = data

    def list_available_models(self):
        try:
            models = client.Model.list()
            model_ids = [model.id for model in models.data]
            return model_ids
        except Exception as e:
            print(f"Error retrieving models: {e}")
            return []

    def predict_categories(self, transactions: list[dict[str, str]]):
        """Predicts categories for a list of transactions using OpenAI's GPT model with Structured Outputs."""
        allowed_categories = ["Food", "Transportation", "Utilities", "Entertainment", "Healthcare", "Other"]
        json_schema = {
            "type": "object",
            "properties": {
                "transactions": {
                    "type": "array",
                    "items": {
                        "type": "object",
                        "properties": {
                            "description": {"type": "string"},
                            "category": {"type": "string", "enum": allowed_categories}
                        },
                        "required": ["description", "category"]
                    }
                }
            },
            "required": ["transactions"]
        }

        transaction_data = json.dumps(transactions, indent=4)
        prompt = (
            "Categorize the following transaction descriptions into one of the predefined categories:\n\n"
            "Transactions raw data:\n" + transaction_data + "\n\n"
            f"Categories: {', '.join(allowed_categories)}\n\n"
            f"Respond with a JSON object containing the descriptions and their corresponding categories."
        )

        try:
            response = client.chat.completions.create(
                model="gpt-4o-2024-11-20",
                messages=[{"role": "user", "content": prompt}],
                functions=[
                    {
                        "name": "categorize_transactions",
                        "parameters": json_schema,
                    },
                ],
                function_call={"name": "categorize_transactions"}
            )

            categorized_transactions = response.choices[0].message.function_call.arguments
            return json.loads(categorized_transactions)
        except Exception as e:
            print(f"Error in OpenAI API call: {e}")
            import ipdb; ipdb.set_trace()
            return [{"description": txn['description'], "category": "Uncategorized"} for txn in transactions]

    def get_category(self, transaction: dict[str, str], transaction_category_map: dict[str, str]):
        """Get the category for a single transaction."""
        json_transaction = json.dumps(transaction)
        for description, category in transaction_category_map.items():
            if description in json_transaction:
                return category
        return "Uncategorized"

    def transform(self):
        """Transforms the data into the intermediate representation."""
        transformed_data = []
        predicted_category = self.predict_categories(self.data)
        transactions_predicted = predicted_category.get("transactions")
        transaction_category_map = {trx['description']: trx['category'] for trx in transactions_predicted}
        for i, transaction in enumerate(self.data):
            new_row = {
                'Date': transaction['Value Date'],
                'Name': transaction['Partner Name'],
                'Amount': transaction['Amount (EUR)'],
                'Category': self.get_category(transaction, transaction_category_map),
                'Comments': transaction['Payment Reference']
            }
            transformed_data.append(new_row)

        return transformed_data

class BaseLoader(ABC):
    """Abstract base class for loading data into the desired output format."""
    @abstractmethod
    def load(self, data):
        pass

class CSVLoader(BaseLoader):
    """Concrete class for loading data into a CSV file."""
    def __init__(self, output_file):
        self.output_file = output_file

    def load(self, data):
        """Loads data into a CSV file."""
        output_header = ['Date', 'Name', 'Amount', 'Category', 'Comments']
        with open(self.output_file, mode='w', newline='', encoding='utf-8') as outfile:
            writer = csv.DictWriter(outfile, fieldnames=output_header)
            writer.writeheader()
            for row in data:
                writer.writerow(row)

class ETLProcess:
    """Class that orchestrates the ETL process using the Extractor, Transformer, and CSVLoader."""
    def __init__(self, input_file, output_file):
        self.input_file = input_file
        self.output_file = output_file

    def run(self):
        # Extract
        extractor = Extractor(self.input_file)
        raw_data = extractor.extract()

        # Transform
        transformer = Transformer(raw_data)
        transformed_data = transformer.transform()

        # Load
        loader = CSVLoader(self.output_file)
        loader.load(transformed_data)

# Usage
if __name__ == "__main__":
    input_file = 'csv_input/01-to-12-set-gabi.csv'  # Replace with your input file path
    output_file = 'output.csv'  # Replace with your desired output file path
    etl_process = ETLProcess(input_file, output_file)
    etl_process.run()