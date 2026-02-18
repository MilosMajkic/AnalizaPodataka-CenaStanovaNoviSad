# Real Estate Price Prediction & Analytics Engine (Novi Sad)

## Project Overview
This repository hosts an end-to-end data pipeline designed to analyze the real estate market in Novi Sad, Serbia. The system automates the extraction of property data, enriches it with geospatial coordinates, utilizes machine learning algorithms to predict property market values, and visualizes the results on an interactive map.

The project demonstrates a full Data Science lifecycle: Data Acquisition (ETL), Preprocessing, Feature Engineering, Predictive Modeling, and Geospatial Visualization.

## System Architecture

The workflow consists of four distinct stages:

1.  **Data Acquisition:** A custom web scraper collects real-time data from local real estate listings.
2.  **Geospatial Enrichment:** Addresses are converted into latitude/longitude coordinates using OpenStreetMap (Nominatim API).
3.  **Predictive Modeling:** A Random Forest Regressor is trained to estimate property prices based on location and structural features.
4.  **Visualization:** An interactive HTML map displays property distribution with price-based color coding.

## Technology Stack

* **Language:** Python 3.x
* **Data Manipulation:** Pandas, NumPy
* **Web Scraping:** BeautifulSoup4, Requests
* **Geospatial Analysis:** Geopy, Folium
* **Machine Learning:** Scikit-learn (Random Forest Regressor)

## Installation & Setup

Clone the repository and install the required dependencies:

```bash
git clone [https://github.com/your-username/real-estate-prediction-ns.git](https://github.com/your-username/real-estate-prediction-ns.git)
cd real-estate-prediction-ns
pip install pandas requests beautifulsoup4 geopy scikit-learn matplotlib seaborn folium
Usage Pipeline
Execute the scripts in the following order to replicate the analysis:

1. Data Extraction
Runs the scraping bot to fetch raw listing data.

Bash
python scraper.py
Output: nekretnine_ns_final.csv (Raw dataset containing location, price, and area).

2. Geocoding (Feature Enrichment)
Converts textual addresses (e.g., "Grbavica, Novi Sad") into geospatial coordinates (Latitude/Longitude).

Bash
python geocoder.py
Output: nekretnine_ns_geo.csv (Enriched dataset ready for ML).

3. Model Training & Evaluation
Trains the Random Forest model, performs train/test splitting, and outputs performance metrics.

Bash
python ml_model.py
Output: Console logs with MAE, R2 scores, and feature importance analysis.

4. Visualization
Generates an interactive map of Novi Sad with pinned property locations. Markers are color-coded based on price per m² (Green < 1800€, Orange < 2500€, Red > 2500€).

Bash
python map_viz.py
Output: mapa_nekretnina_ns.html (Open this file in your web browser).

Model Performance
The current implementation utilizes a Random Forest Regressor (n_estimators=100). The model has been evaluated on a hold-out test set (20% split) with the following results:

R² Score: 0.92 (Explains 92% of price variance)

Mean Absolute Error (MAE): ~8,570 EUR

Key Drivers of Price (Feature Importance)
The model identified the following features as the most significant determinants of property value:

Square Footage (m²): Primary driver (~55% importance).

Neighborhood (Categorical): High impact specific locations (e.g., Novo Naselje).

Geospatial Coordinates: Fine-tuning based on exact latitude/longitude.

Future Improvements
Web Interface: Developing a Flask/Django dashboard to serve the model via API.

Hyperparameter Tuning: GridSearch implementation to further reduce MAE.

Data Expansion: Integration of additional scraping sources to increase dataset size.

License
This project is open-source and available under the MIT License.
