import os
from datetime import datetime, timedelta
from flask import Blueprint, render_template, jsonify
from flask_jwt_extended import jwt_required
from sqlalchemy import func
from application.auth.controllers import JWTUtilities
from application.config import ADMIN_ROLE_TYPE
from application.user.models import UserSearchData
from application.app import db
from application.exceptions import InvalidAPIRequest

admin_blueprint = Blueprint('admin', __name__,
                            template_folder=os.path.join('templates', 'admin'),
                            url_prefix='/admin'
                            )


@admin_blueprint.route("/", methods=["GET"])
@jwt_required
@JWTUtilities.user_role_required(ADMIN_ROLE_TYPE)
def admin_dashboard():
    return render_template("index.html")


@admin_blueprint.route("/statistics/search/<start_date>/<time_group_by>")
@jwt_required
@JWTUtilities.user_role_required(ADMIN_ROLE_TYPE)
def user_search_statistics(start_date, time_group_by):
    """
    Returns the total search requests made from the start date
    :param start_date: the earliest date to calculate from
    :param time_group_by: the time period to group by (daily or monthly)
    :return:
    """
    start_date, time_group_by = _parse_input_args(start_date, time_group_by)
    time_group_by = time_group_by if time_group_by else 'DAY'
    if time_group_by.upper() == 'DAY':
        aggregate_searches = db.session.query(
            func.to_date(UserSearchData.created_at), func.count(UserSearchData.pk)).\
            filter(func.to_date(UserSearchData.created_at) <= start_date).\
            group_by(func.to_date(UserSearchData.created_at)).\
            order_by(func.to_date(UserSearchData.created_at))
    elif time_group_by.upper() == 'MONTH':
        aggregate_searches = db.session.query(
            func.month(UserSearchData.created_at), func.count(UserSearchData.user.pk)).\
            filter(func.to_date(UserSearchData.created_at) <= start_date).\
            group_by(func.month(UserSearchData.created_at)).\
            order_by(func.year(UserSearchData.created_at)).\
            order_by(func.month(UserSearchData.created_at))
    else:
        raise InvalidAPIRequest("Could not group by: {0}. not valid. Only DAY and MONTH supported".format(
            time_group_by))
    return jsonify(aggregate_searches)


@admin_blueprint.route("/statistics/search/unique-users/<start_date>/<time_group_by>")
@jwt_required
@JWTUtilities.user_role_required(ADMIN_ROLE_TYPE)
def unique_search_users(start_date, time_group_by):
    """
        Returns the total search requests made from the start date by distinct users
        :param start_date: the earliest date to calculate from
        :param time_group_by: the time period to group by (daily or monthly)
        :return:
        """
    start_date, time_group_by = _parse_input_args(start_date, time_group_by)
    if time_group_by.upper() == 'DAY':
        aggregate_searches = db.session.query(
            func.to_date(UserSearchData.created_at), func.count(func.distinct(UserSearchData.user.pk))).\
            filter(func.to_date(UserSearchData.created_at) <= start_date).\
            group_by(func.to_date(UserSearchData.created_at)).\
            order_by(func.to_date(UserSearchData.created_at))
    elif time_group_by.upper() == 'MONTH':
        aggregate_searches = db.session.query(
            func.month(UserSearchData.created_at), func.count(func.distinct(UserSearchData.user.pk))).\
            filter(func.to_date(UserSearchData.created_at) <= start_date).\
            group_by(func.month(UserSearchData.created_at)).\
            order_by(func.year(UserSearchData.created_at)).\
            order_by(func.month(UserSearchData.created_at))
    else:
        raise InvalidAPIRequest("Could not group by: {0}. not valid. Only DAY and MONTH supported".format(
            time_group_by))
    return jsonify(aggregate_searches)


def _parse_input_args(start_date, time_group_by):
    start_date = datetime.strptime(start_date, '%Y-%m-%d') \
        if start_date else (datetime.now() - timedelta(days=30)).date()
    time_group_by = time_group_by if time_group_by else 'DAY'
    return start_date, time_group_by
