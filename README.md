# Personal Finance Dashboard 👋

**Take Control of Your Finances.**

This is a Streamlit application that provides a comprehensive dashboard for visualizing and analyzing personal finance data. The application allows users to upload their transaction data (e.g., from a bank statement) and generates interactive visualizations and insights based on the data.

## Pages

### Categorizer
The Categorizer allows users to categorize their financial transactions by uploading transaction data and a configuration file. It automatically assigns categories and subcategories based on the provided rules, displays the categorized transactions in an interactive grid, and enables users to manually edit or download the categorized data.

### Dashboard
The Dashboard lets users upload transaction data from excel files. It displays balance trends over time for different sources such as bank accounts and credit cards using graphs and tiles. It also provides insights into spending per category using bar graphs. Additionally, users can set financial goals, like limiting travel expenses, and track their progress with a heatmap.

The application's behavior and settings can be customized the dasboard settings.

## Folder Structure
```
personal-finance-dashboard/
├── app_pages/                          # Directory for all the pages
├── static/                             # Static files (examples, css and config)
├── utils/                              # Utility functions for all plots and calculations
├── .gitignore
├── .pre-commit-config.yaml
├── app.py                              # Main Streamlit application file
├── README.md
├── requirements.txt
```

## Getting Started

Use it hosted on streamlit cloud https://personalfinancedashboard.streamlit.app/ or run it locally:

1. Clone the repository:
```
$ git clone https://github.com/NarekAra/personal-finance-dashboard.git
```
2. Install the required dependencies:
```
$ pip install -r requirements.txt
```
3. Run the Streamlit application:
```
$ streamlit run app.py
```

## Contributing

Contributions to this project are welcome. If you find any issues or have suggestions for improvements, please open an issue or submit a pull request.

## Changelog
- 01/07/2024: First version. Added the dashboard
- 02/07/2024: Added the transaction categorizer
- 05/07/2024: Added support for financial goals
- 15/08/2024: Allow changing the dashboardconfig in the UI
- 23/08/2024: Allow users to log in
- 11/09/2024: Many bugfixes
- 11/09/2024: Added the ability to query data & bugfix firebase
- 28/09/2024: Allow changing the categorization config in the UI
- 24/11/2024: Removed logging in posibility and made open source

## To-do
- Allow removing financial goals
- dashboard_utils might still contain a bug if 2 categories have a subcategory with the same name and you change between these 2 categories
- calculate_income_outcome: remove TRANSFERS as a constant
- merge display_get_configuration_file and display_get_transactions_file
- check that subcategory is always on 1 categoy
- categorize gives datetime instead of date
- order categorizer is not correct
- the reload button is not working