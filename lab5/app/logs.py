from functools import wraps
from check_rights import CheckRights
from flask_login import LoginManager, UserMixin, login_user, logout_user, current_user, login_required
from flask import Blueprint, render_template, redirect, send_file, url_for, request,flash, abort
from app import db
from math import ceil
import io
bp = Blueprint('logs', __name__, url_prefix='/logs')

PER_PAGE = 5

@bp.route("/visits")
@login_required
def show_user_logs():
    logs=None
    page = int(request.args.get('page',1))
    user_id=getattr(current_user,"id",None)
    with db.connect().cursor(named_tuple=True) as cursor:
        if current_user.is_admin():
            query = ('SELECT logs.*, users.first_name as first_name, users.middle_name as second_name,users.last_name as last_name  FROM logs left join users on logs.user_id=users.id order by logs.created_at DESC LIMIT %s OFFSET %s ')
            cursor.execute(query, (PER_PAGE, (page-1) * PER_PAGE))
        else:
            query = ('SELECT logs.*, users.first_name as first_name, users.middle_name as second_name,users.last_name as last_name  FROM logs left join users on logs.user_id=users.id where logs.user_id=%s order by logs.created_at DESC LIMIT %s OFFSET %s ')
            cursor.execute(query, (user_id,PER_PAGE, (page-1) * PER_PAGE))
        logs=cursor.fetchall()
    with db.connect().cursor(named_tuple=True) as cursor:
        if current_user.is_admin():
            query = ('SELECT count(*) as count FROM logs')
            cursor.execute(query)
            count=cursor.fetchone().count
        else:
            query = ('SELECT count(*) as count FROM logs where user_id=%s')
            cursor.execute(query,[user_id])
            count=cursor.fetchone().count
    return render_template("log/visits.html",logs=logs, count=ceil(count/PER_PAGE), page=page)

@bp.route("/users")
@login_required
def show_count_logs():
    if current_user.is_admin():
        logs=None
        with db.connect().cursor(named_tuple=True) as cursor:
            query = ('SELECT user_id,count(*) as count, users.first_name as first_name, users.middle_name as second_name,users.last_name as last_name  FROM logs left join users on logs.user_id=users.id group by user_id ')
            cursor.execute(query)
            logs=cursor.fetchall()
        return render_template("log/users.html",logs=logs)
    else:
        abort(404)

@bp.route("/page")
@login_required
def show_page_logs():
    print(current_user.role_id)
    print(current_user.is_admin())
    if current_user.is_admin():
        logs=None
        with db.connect().cursor(named_tuple=True) as cursor:
            query = ('SELECT path,count(*) as count FROM logs group by path order by count DESC')
            cursor.execute(query)
            logs=cursor.fetchall()
        return render_template("log/page.html", logs=logs)
    else:
        abort(404)

@bp.route("/export_csv")
@login_required
def export_csv():
    ref=request.referrer
    if ref!=None:
        with db.connect().cursor(named_tuple=True) as cursor:
            if current_user.is_admin():
                if 'visits' in ref:
                    query = ('SELECT * FROM logs order by logs.created_at DESC')
                elif 'page' in ref:
                    query = ('SELECT user_id,count(*) as count FROM logs group by user_id ')
                elif 'users' in ref:
                    query = ('SELECT path,count(*) as count FROM logs group by path order by count DESC ')
                cursor.execute(query)
            else:
                if 'visits' in ref:
                    user_id=current_user.id
                    query = ('SELECT * FROM logs where user_id=%s order by logs.created_at DESC')
                    cursor.execute(query,[user_id])
                else:
                    abort(404)
            logs=cursor.fetchall()
        if 'visits' in ref:
            data = load_data(logs, ['user_id','path', 'created_at'])
        elif 'page' in ref:
            data = load_data(logs, ['user_id','count'])
        elif 'users' in ref:
            data = load_data(logs, ['path','count'])
        return send_file(data, as_attachment=True,download_name='download.csv')
    else:
        abort(404)

def load_data(records, fields):
    csv_data=", ".join(fields)+"\n"
    for record in records:
        csv_data += ", ".join([str(getattr(record, field, '')) for field in fields]) + "\n"
    f = io.BytesIO()
    f.write(csv_data.encode('utf-8'))
    f.seek(0)
    return f