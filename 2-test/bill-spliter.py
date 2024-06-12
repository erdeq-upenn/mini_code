from flask import Flask, request, jsonify

app = Flask(__name__)

@app.route('/split-bill', methods=['POST'])
def split_bill():
    data = request.get_json()
    total_amount = data.get('totalAmount')
    num_people = data.get('numPeople')

    if not total_amount or not num_people:
        return jsonify({'error': 'Total amount and number of people are required'}), 400

    amount_per_person = total_amount / num_people
    individual_amounts = [amount_per_person] * num_people

    return jsonify({'individualAmounts': individual_amounts})

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)