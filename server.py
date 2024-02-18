from flask import Flask, request, jsonify, Response
from flask_cors import CORS
from scraping.class_reuters_com import ReutersComScraper
from scraping.class_investing_com import InvestingComScraper
from api.oanda_api import OandaApi
from infrastructure.log_wrapper import LogWrapper

app = Flask(__name__)
CORS(app)
logger = LogWrapper(name="server_flask")

reuters_scraper = ReutersComScraper()
investing_scraper = InvestingComScraper()
o_api = OandaApi()

class CustomError(Exception):
    pass

@app.route('/api/test')
def test():
    return jsonify({'message': 'Hello, World!'})

@app.route('/api/headlines')
def headlines():
    try:
        headlines_data = reuters_scraper.scrape_reuters()
        if headlines_data is None:
            raise CustomError('No data found.')
        return jsonify(headlines_data)
    except CustomError as e:
        logger.error(f"Error in retrieving headlines: {str(e)}")
        return jsonify({'error': str(e)}), 500
    except Exception as e:
        logger.exception("An unexpected error occurred:")
        return jsonify({'error': 'An unexpected error occurred.'}), 500

@app.route('/api/technical/<pair>/<time_frame>')
def investing_data(pair, time_frame):
    try:
        technical_data = investing_scraper.scrape_data(pair=pair, time_frame=time_frame)
        if technical_data is None:
            raise CustomError('No data found.')
        json_data = technical_data.to_json(orient='records', indent=4)
        return Response(json_data, mimetype='application/json')
    except CustomError as e:
        logger.error(f"Error in retrieving technical data: {str(e)}")
        return jsonify({'error': str(e)}), 500
    except Exception as e:
        logger.exception("An unexpected error occurred:")
        return jsonify({'error': 'An unexpected error occurred.'}), 500

@app.route('/api/prices/<pair_name>/<granularity>/<count>')
def instruments(pair_name, granularity, count):
    try:
        instruments_data = o_api.web_api_candles(pair_name, granularity, count)
        return jsonify(instruments_data)
    except Exception as e:
        logger.exception("An unexpected error occurred:")
        return jsonify({'error': 'An unexpected error occurred.'}), 500

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)
