import flask
from flask import request

from slivka.server.forms import FormLoader
from slivka.db import database


bp = flask.Blueprint('webapp', __name__, url_prefix='/webapp', template_folder='templates')


@bp.route('/<service>', methods=['GET', 'POST'])
def form(service):
  Form = FormLoader.instance[service]
  if request.method == 'GET':
    form = Form()
    return flask.render_template('form.jinja2', form=form)
  elif request.method == 'POST':
    form = Form(data=request.form, files=request.files)
    if form.is_valid():
      job_request = form.save(database)
      url = flask.url_for('webapp.status', uuid=job_request.uuid)
      return flask.redirect(url)
    else:
      return flask.render_template('form.jinja2', form=form)


@bp.route('/job/<uuid>', methods=['GET'])
def status(uuid):
  return flask.render_template('status.jinja2', job_id=uuid)
