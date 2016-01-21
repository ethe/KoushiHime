from flask import Flask,request
from MU_weibo import GetCode
app = Flask(__name__)

@app.route('/')
def index():
    code=request.args.get('code')
    GetCode(code)
    return code

if __name__=='__main__':
    app.run(debug=True)