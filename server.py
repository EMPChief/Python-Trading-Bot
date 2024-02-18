from flask import Flask, request, jsonify, Response
from flask_cors import CORS
from scraping.class_reuters_com import ReutersComScraper
from scraping.class_investing_com import InvestingComScraper
from api.oanda_api import OandaApi
app = Flask(__name__)
CORS(app)
reuters_scraper = ReutersComScraper()
investing_scraper = InvestingComScraper()
o_api = OandaApi()
@app.route('/api/test')
def test():
    return jsonify({'message': 'Hello, World!'})

@app.route('/api/headlines')
def headlines():
    headlines_data = reuters_scraper.scrape_reuters()
    if headlines_data is None:
        return jsonify({'message': 'No data found.'})
    else:
        return jsonify(headlines_data)

@app.route('/api/technical/<pair>/<time_frame>')
def investing_data(pair, time_frame):
    technical_data = investing_scraper.scrape_data(pair=pair, time_frame=time_frame)
    json_data = technical_data.to_json(orient='records', indent=4)
    if technical_data is None:
        return jsonify({'message': 'No data found.'})
    else:
        return Response(json_data, mimetype='application/json')

@app.route('/api/prices/<pair_name>/<granularity>/<count>')
def instruments(pair_name, granularity, count):
    instruments_data = o_api.web_api_candles(pair_name, granularity, count)
    return jsonify(instruments_data)


if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)
