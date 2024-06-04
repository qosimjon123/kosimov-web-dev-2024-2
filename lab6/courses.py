from flask import Blueprint, render_template, request, flash, redirect, url_for
from flask_login import login_required, current_user
from sqlalchemy import join
from sqlalchemy.exc import IntegrityError
from models import db, Course, Category, User, Review
from tools import CoursesFilter, ImageSaver

bp = Blueprint('courses', __name__, url_prefix='/courses')

COURSE_PARAMS = [
    'author_id', 'name', 'category_id', 'short_desc', 'full_desc'
]

def params():
    return { p: request.form.get(p) or None for p in COURSE_PARAMS }

def search_params():
    return {
        'name': request.args.get('name'),
        'category_ids': [x for x in request.args.getlist('category_ids') if x],
    }

@bp.route('/')
def index():
    courses = CoursesFilter(**search_params()).perform()
    pagination = db.paginate(courses,per_page=1)
    courses = pagination.items
    categories = db.session.execute(db.select(Category)).scalars()
    return render_template('courses/index.html',
                           courses=courses,
                           categories=categories,
                           pagination=pagination,
                           search_params=search_params())

@bp.route('/new')
@login_required
def new():
    course = Course()
    categories = db.session.execute(db.select(Category)).scalars()
    users = db.session.execute(db.select(User)).scalars()
    return render_template('courses/new.html',
                           categories=categories,
                           users=users,
                           course=course)

@bp.route('/create', methods=['POST'])
@login_required
def create():
    f = request.files.get('background_img')
    img = None
    course = Course()
    try:
        if f and f.filename:
            img = ImageSaver(f).save()

        image_id = img.id if img else None
        course = Course(**params(), background_image_id=image_id)
        db.session.add(course)
        db.session.commit()
    except IntegrityError as err:
        flash(f'Возникла ошибка при записи данных в БД. Проверьте корректность введённых данных. ({err})', 'danger')
        db.session.rollback()
        categories = db.session.execute(db.select(Category)).scalars()
        users = db.session.execute(db.select(User)).scalars()
        return render_template('courses/new.html',
                            categories=categories,
                            users=users,
                            course=course)

    flash(f'Курс {course.name} был успешно добавлен!', 'success')

    return redirect(url_for('courses.index'))

ratings = {
    "Отлично" : 5,
    "Хорошо" : 4,
    "Удовлетворительно" : 3,
    "Неудовлетворительно" : 2,
    "Плохо" : 1,
    "Ужасно" : 0
}

@bp.route('/<int:course_id>')
def show(course_id):
    course = db.get_or_404(Course, course_id)
    reviews = join(User, Review, User.id == Review.user_id)
    results = (db.session.query(User.first_name,
                                User.middle_name,
                                User.last_name,
                                Review.created_at,
                                Review.rating,
                                Review.text )
               .select_from(reviews).where(Review.course_id==course_id).order_by(Review.created_at.desc()).limit(5).all())
    # flash(results)
    # review = db.session.execute(db.select(Review).where(Review.course_id == course_id)
    #                             .join(User, Review.user_id == User.id).
    #                             order_by(Review.created_at.desc()).limit(5))
    hasFeedback = False
    users = (db.session.query(
                              Review.rating,
                              Review.text)
             .select_from(Review).where(Review.user_id == current_user.id, Review.course_id==course_id).all())
    comments = None
    if users:
        hasFeedback = True
        comments=users


    return render_template('courses/show.html', course=course, ratings=ratings, reviews=results, hasFeedback=hasFeedback, comments=comments)


# @bp.route('/<int:course_id>/review/')
# def feedbacks(course_id):
#     reviews = join(User, Review, User.id == Review.user_id)
#     results = (db.session.query(User.first_name,
#                                 User.middle_name,
#                                 User.last_name,
#                                 Review.created_at,
#                                 Review.rating,
#                                 Review.text)
#                .select_from(reviews).where(Review.course_id == course_id).order_by(Review.created_at.desc()).all())
#
#     loneReviews = db.select(Review).where(Review.course_id == course_id).order_by(Review.created_at.desc())
#     pagination = db.paginate(loneReviews, per_page=2)  # Убедитесь, что у вас есть аргумент per_page
#
#     return render_template('courses/feedback.html', ratings=ratings, reviews=results,
#                            pagination=pagination,
#                            search_params=search_params(),course_id=course_id)

@bp.route('/<int:course_id>/review/')
def feedbacks(course_id):
    sort_order = request.args.get('sort_order', 'newest')

    # Create a base query to fetch reviews for the given course
    base_query = db.session.query(
        User.first_name,
        User.middle_name,
        User.last_name,
        Review.created_at,
        Review.rating,
        Review.text
    ).join(Review).filter(Review.course_id == course_id)

    # Apply sorting based on the selected order
    if sort_order == 'positive':
        base_query = base_query.order_by(Review.rating.desc(), Review.created_at.desc())
    elif sort_order == 'negative':
        base_query = base_query.order_by(Review.rating.asc(), Review.created_at.desc())
    else:  # Default to sorting by newest
        base_query = base_query.order_by(Review.created_at.desc())

    # Paginate the sorted reviews
    pagination = base_query.paginate(per_page=1)

    # Get the reviews for the current page
    reviews = pagination.items
    return render_template('courses/feedback.html', ratings=ratings, reviews=reviews,
                           pagination=pagination,
                            course_id=course_id,sort_order=sort_order)



@bp.route('/<int:course_id>/rating', methods=['POST'])
def rating(course_id):
    users = (db.session.query(   Review.created_at,
                                Review.rating,
                                Review.text )
               .select_from(Review).where(Review.user_id==current_user.id, Review.course_id==course_id ).all())


    if users:
        flash("Вы уже оставяли свой отзыв")
        return redirect(url_for('courses.show', course_id=course_id))
    #
    if request.method == "POST":
        if request.form.get('category_ids'):

            rating2 = int(request.form.get('category_ids'))
            text = request.form.get('text')


            review = Review(rating=rating2, text=text, user_id=current_user.id, course_id=course_id)


            course = db.session.query(Course).filter_by(id=course_id).first()
            if not course:
                flash("Курс не найден", "danger")
                return redirect(url_for('courses.show', course_id=course_id))


            course.rating_sum += rating2
            course.rating_num += 1

            try:

                db.session.add(review)
                db.session.commit()
                flash("Ваш отзыв был добавлен", "success")
            except Exception as e:
                db.session.rollback()
                flash("Ошибка на стороне сервера, отзыв не сохранен", "danger")
                print(e)
        else:
            flash("Не выбрана оценка", "danger")
    return redirect(url_for('courses.show', course_id=course_id))
