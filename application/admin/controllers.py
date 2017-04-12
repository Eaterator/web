import os
import json
from datetime import datetime, timedelta
from collections import Counter
from itertools import chain
from flask import Blueprint, jsonify, render_template, abort, send_from_directory
from flask_jwt_extended import jwt_required
from sqlalchemy import func
from application.auth.controllers import JWTUtilities
from application.config import ADMIN_ROLE_TYPE
from application.user.models import UserSearchData
from application.auth.models import User
from application.app import app, db, cache
from application.exceptions import InvalidAPIRequest
from application.redis_cache_utlits import RedisUtilities

admin_blueprint = Blueprint('admin', __name__,
                            template_folder=os.path.join('templates', 'admin'),
                            url_prefix='/admin'
                            )


@admin_blueprint.route("/<page>", methods=["GET"])
@jwt_required
@JWTUtilities.user_role_required([ADMIN_ROLE_TYPE])
# @cache.cached(timeout=int(60*60/2), key_prefix=RedisUtilities.cache_by_static_page)
def admin_dashboard(page):
    try:
        return render_template("admin/{0}.html".format(page.split('.')[0]))
    except Exception as e:
        import traceback
        app.logger.error("ADMIN | static error: {0}".format(traceback.format_exc()))
        app.logger.error("ADMIN | error logging admin template, check format. Error: {0}".format(str(e)))
        abort(404)


@admin_blueprint.route("/statistics/search/<start_date>/<time_group_by>")
@jwt_required
@JWTUtilities.user_role_required(ADMIN_ROLE_TYPE)
@cache.cached(timeout=60*60)
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
                func.date(UserSearchData.created_at).label('date'),
                func.count(UserSearchData.pk).label('value')
            ).\
            filter(func.date(UserSearchData.created_at) >= start_date).\
            group_by(func.date(UserSearchData.created_at)).\
            order_by(func.date(UserSearchData.created_at)).all()
    elif time_group_by.upper() == 'MONTH':
        aggregate_searches = db.session.query(
                func.max(func.date(UserSearchData.created_at)),
                func.count(UserSearchData.pk)
            ).\
            filter(func.date(UserSearchData.created_at) >= start_date).\
            group_by(
                func.date_trunc('year', UserSearchData.created_at),
                func.date_trunc('month', UserSearchData.created_at)
            ).\
            order_by(
                func.date_trunc('year', UserSearchData.created_at),
                func.date_trunc('month', UserSearchData.created_at)
            ).all()
    else:
        raise InvalidAPIRequest("Could not group by: {0}. not valid. Only DAY and MONTH supported".format(
            time_group_by))
    return AdminFormattingUtilities.jsonify_datetime_query(aggregate_searches, type_="all_user_searches")


@admin_blueprint.route("/statistics/search/unique-users/<start_date>/<time_group_by>")
@jwt_required
@JWTUtilities.user_role_required(ADMIN_ROLE_TYPE)
@cache.cached(timeout=60*60)
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
                func.date(UserSearchData.created_at).label('date'),
                func.count(func.distinct(UserSearchData.user)).label('value')
            ).\
            filter(func.date(UserSearchData.created_at) >= start_date).\
            group_by(
                func.date(UserSearchData.created_at),
                UserSearchData.user
            ).\
            order_by(func.date(UserSearchData.created_at)).all()
    elif time_group_by.upper() == 'MONTH':
        aggregate_searches = db.session.query(
                func.max(func.date(UserSearchData.created_at)).label('date'),
                func.count(func.distinct(UserSearchData.user)).label('value')
            ).\
            filter(func.date(UserSearchData.created_at) <= start_date). \
            group_by(
                func.date_trunc('year', UserSearchData.created_at),
                func.date_trunc('month', UserSearchData.created_at)
            ). \
            order_by(
                func.date_trunc('year', UserSearchData.created_at),
                func.date_trunc('month', UserSearchData.created_at)
            ).all()
    else:
        raise InvalidAPIRequest("Could not group by: {0}. not valid. Only DAY and MONTH supported".format(
            time_group_by))
    return AdminFormattingUtilities.jsonify_datetime_query(aggregate_searches, type_='distinct_search_users')


@admin_blueprint.route("/statistics/search/new-users/<start_date>/<time_group_by>")
@jwt_required
@JWTUtilities.user_role_required(ADMIN_ROLE_TYPE)
@cache.cached(timeout=60*60)
def new_users(start_date, time_group_by):
    """
    Returns the new users that have signed up for accounts
    :param start_date: the first
    :param time_group_by:
    :return:
    """
    start_date, time_group_by = _parse_input_args(start_date, time_group_by)
    if time_group_by.upper() == 'DAY':
        aggregate_searches = db.session.query(
                func.date(User.created_at).label('date'),
                func.count(func.distinct(User.pk)).label('value')
            ).\
            filter(func.date(User.created_at) <= start_date).\
            group_by(func.date(User.created_at)).\
            order_by(func.date(User.created_at))
    elif time_group_by.upper() == 'MONTH':
        aggregate_searches = db.session.query(
                func.max(func.date(User.created_at)).label('value'),
                func.count(func.distinct(User.pk)).date('date')
            ).\
            filter(func.date(User.created_at) <= start_date). \
            group_by(
                func.date_trunc('year', User.created_at),
                func.date_trunc('month', User.created_at)
            ). \
            order_by(
                func.date_trunc('year', User.created_at),
                func.date_trunc('month', User.created_at)
            ).all
    else:
        raise InvalidAPIRequest("Could not group by: {0}. not valid. Only DAY and MONTH supported".format(
            time_group_by))
    return AdminFormattingUtilities.jsonify_datetime_query(aggregate_searches, type_='new_users')


@admin_blueprint.route("/statistics/search/popular-ingredients")
@jwt_required
@JWTUtilities.user_role_required(ADMIN_ROLE_TYPE)
@cache.cached(timeout=60*60)
def popular_ingredients():
    searches = UserSearchData.query\
        .filter(UserSearchData.search.isnot(None)).\
        order_by(UserSearchData.created_at.desc()).limit(5000)
    cleaner = lambda s: s.strip().rstrip('s')
    most_popular = sorted(
        Counter(
            chain(*[map(cleaner, json.loads(s.search)['ingredients']) if isinstance(s.search, str)
                    else map(cleaner, s.search['ingredients']) for s in searches])
        ).most_common(25),
        reverse=True, key=lambda i: i[1]
    )
    return AdminFormattingUtilities.jsonify_top_ingredients(most_popular)


def _parse_input_args(start_date, time_group_by):
    try:
        start_date = datetime.strptime(start_date, '%Y-%m-%d') \
            if start_date else (datetime.now() - timedelta(days=30)).date()
    except (ValueError, TypeError):
        start_date = (datetime.now() - timedelta(days=30)).date()
    time_group_by = time_group_by if time_group_by else 'DAY'
    return start_date, time_group_by


class AdminFormattingUtilities:

    @staticmethod
    def jsonify_datetime_query(query, type_="unspecified"):
        return jsonify(
            {
                'type': type_,
                'statistics': [{'date': i[0].strftime('%y-%m-%d'), 'value': i[1]} for i in query]
            }
        )

    @staticmethod
    def jsonify_top_ingredients(most_common):
        return jsonify(
            {
                'most_popular': [{'name': i[0], 'value': i[1]} for i in most_common]
            }
        )
