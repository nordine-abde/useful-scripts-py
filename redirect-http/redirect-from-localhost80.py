from flask import Flask, request, redirect
from urllib.parse import urlencode

app = Flask(__name__)

TARGET_URL = '#INSERT_TARGET_URL_HERE#'  # Replace with the target URL you want to redirect to

@app.route('/')
def proxy():
    # Collect original query parameters
    params = request.args.to_dict()

    redirect_url = TARGET_URL
    # Append query parameters to the target URL
    query_string = urlencode(params)
    if query_string:
        redirect_url += f"?{query_string}"

    return redirect(redirect_url)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=80)
