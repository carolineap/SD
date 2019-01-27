from flask import Flask

my_awesome_app = Flask(__name__)


@sd-cloud-broker.route('/')
def hello_world():
	return 'Hello World!'


if __name__ == '__main__':
	sd-cloud-broker.run()