from flask import Flask, render_template, request
from .database import db, migrate
from app.Table.models import User, Group, Schedule, Notice, Register_Info, InviteCode, MoneyList

import config


def create_app():
    app = Flask(__name__)
    app.config.from_object(config)

    # ORM
    db.init_app(app)
    migrate.init_app(app, db)
    return app