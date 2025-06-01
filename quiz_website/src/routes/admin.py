from flask import Blueprint, render_template, redirect, url_for, flash, request
from flask_login import login_required, current_user
from src.models.models import db, User, Quiz, Question, Option, QuizAttempt, Answer
from datetime import datetime

admin_bp = Blueprint('admin', __name__, url_prefix='/admin')

# Admin access decorator
def admin_required(f):
    def decorated_function(*args, **kwargs):
        if not current_user.is_authenticated or not current_user.is_admin:
            flash('You do not have permission to access this page', 'danger')
            return redirect(url_for('index'))
        return f(*args, **kwargs)
    decorated_function.__name__ = f.__name__
    return decorated_function

@admin_bp.route('/')
@login_required
@admin_required
def dashboard():
    # Get counts for dashboard
    pending_users = User.query.filter_by(is_approved=False, is_admin=False).count()
    total_users = User.query.filter_by(is_admin=False).count()
    total_quizzes = Quiz.query.count()
    total_attempts = QuizAttempt.query.count()
    
    return render_template('admin/dashboard.html', 
                          pending_users=pending_users,
                          total_users=total_users,
                          total_quizzes=total_quizzes,
                          total_attempts=total_attempts)

# User management routes
@admin_bp.route('/users')
@login_required
@admin_required
def users():
    users = User.query.filter_by(is_admin=False).all()
    return render_template('admin/users.html', users=users)

@admin_bp.route('/users/pending')
@login_required
@admin_required
def pending_users():
    users = User.query.filter_by(is_approved=False, is_admin=False).all()
    return render_template('admin/pending_users.html', users=users)

@admin_bp.route('/users/<int:user_id>/approve', methods=['POST'])
@login_required
@admin_required
def approve_user(user_id):
    user = User.query.get_or_404(user_id)
    
    if user.is_admin:
        flash('Cannot modify admin accounts', 'danger')
        return redirect(url_for('admin.users'))
    
    user.is_approved = True
    db.session.commit()
    
    flash(f'User {user.username} has been approved', 'success')
    return redirect(url_for('admin.pending_users'))

@admin_bp.route('/users/<int:user_id>/reject', methods=['POST'])
@login_required
@admin_required
def reject_user(user_id):
    user = User.query.get_or_404(user_id)
    
    if user.is_admin:
        flash('Cannot modify admin accounts', 'danger')
        return redirect(url_for('admin.users'))
    
    db.session.delete(user)
    db.session.commit()
    
    flash(f'User registration has been rejected', 'success')
    return redirect(url_for('admin.pending_users'))

# Quiz management routes
@admin_bp.route('/quizzes')
@login_required
@admin_required
def quizzes():
    quizzes = Quiz.query.all()
    return render_template('admin/quizzes.html', quizzes=quizzes)

@admin_bp.route('/quizzes/new', methods=['GET', 'POST'])
@login_required
@admin_required
def new_quiz():
    if request.method == 'POST':
        title = request.form.get('title')
        description = request.form.get('description')
        
        if not title:
            flash('Quiz title is required', 'danger')
            return render_template('admin/new_quiz.html')
        
        new_quiz = Quiz(
            title=title,
            description=description,
            is_active=True
        )
        
        db.session.add(new_quiz)
        db.session.commit()
        
        flash('Quiz created successfully. Now add questions to it.', 'success')
        return redirect(url_for('admin.edit_quiz', quiz_id=new_quiz.id))
    
    return render_template('admin/new_quiz.html')

@admin_bp.route('/quizzes/<int:quiz_id>/edit', methods=['GET', 'POST'])
@login_required
@admin_required
def edit_quiz(quiz_id):
    quiz = Quiz.query.get_or_404(quiz_id)
    
    if request.method == 'POST':
        title = request.form.get('title')
        description = request.form.get('description')
        is_active = 'is_active' in request.form
        
        if not title:
            flash('Quiz title is required', 'danger')
            return render_template('admin/edit_quiz.html', quiz=quiz)
        
        quiz.title = title
        quiz.description = description
        quiz.is_active = is_active
        
        db.session.commit()
        
        flash('Quiz updated successfully', 'success')
        return redirect(url_for('admin.quizzes'))
    
    return render_template('admin/edit_quiz.html', quiz=quiz)

@admin_bp.route('/quizzes/<int:quiz_id>/delete', methods=['POST'])
@login_required
@admin_required
def delete_quiz(quiz_id):
    quiz = Quiz.query.get_or_404(quiz_id)
    
    db.session.delete(quiz)
    db.session.commit()
    
    flash('Quiz deleted successfully', 'success')
    return redirect(url_for('admin.quizzes'))

# Question management routes
@admin_bp.route('/quizzes/<int:quiz_id>/questions')
@login_required
@admin_required
def questions(quiz_id):
    quiz = Quiz.query.get_or_404(quiz_id)
    questions = Question.query.filter_by(quiz_id=quiz_id).order_by(Question.order_num).all()
    
    return render_template('admin/questions.html', quiz=quiz, questions=questions)

@admin_bp.route('/quizzes/<int:quiz_id>/questions/new', methods=['GET', 'POST'])
@login_required
@admin_required
def new_question(quiz_id):
    quiz = Quiz.query.get_or_404(quiz_id)
    
    if request.method == 'POST':
        question_text = request.form.get('question_text')
        
        if not question_text:
            flash('Question text is required', 'danger')
            return render_template('admin/new_question.html', quiz=quiz)
        
        # Get the next order number
        last_question = Question.query.filter_by(quiz_id=quiz_id).order_by(Question.order_num.desc()).first()
        next_order = 1 if not last_question else last_question.order_num + 1
        
        new_question = Question(
            quiz_id=quiz_id,
            question_text=question_text,
            order_num=next_order
        )
        
        db.session.add(new_question)
        db.session.commit()
        
        # Add options
        for i in range(1, 5):  # Assuming 4 options per question
            option_text = request.form.get(f'option_{i}')
            is_correct = request.form.get('correct_option') == str(i)
            
            if option_text:
                option = Option(
                    question_id=new_question.id,
                    option_text=option_text,
                    is_correct=is_correct
                )
                db.session.add(option)
        
        db.session.commit()
        
        flash('Question added successfully', 'success')
        return redirect(url_for('admin.questions', quiz_id=quiz_id))
    
    return render_template('admin/new_question.html', quiz=quiz)

@admin_bp.route('/questions/<int:question_id>/edit', methods=['GET', 'POST'])
@login_required
@admin_required
def edit_question(question_id):
    question = Question.query.get_or_404(question_id)
    quiz = Quiz.query.get_or_404(question.quiz_id)
    
    if request.method == 'POST':
        question_text = request.form.get('question_text')
        
        if not question_text:
            flash('Question text is required', 'danger')
            return render_template('admin/edit_question.html', quiz=quiz, question=question)
        
        question.question_text = question_text
        
        # Update options
        for option in question.options:
            option_text = request.form.get(f'option_{option.id}')
            is_correct = request.form.get('correct_option') == str(option.id)
            
            if option_text:
                option.option_text = option_text
                option.is_correct = is_correct
        
        db.session.commit()
        
        flash('Question updated successfully', 'success')
        return redirect(url_for('admin.questions', quiz_id=question.quiz_id))
    
    return render_template('admin/edit_question.html', quiz=quiz, question=question)

@admin_bp.route('/questions/<int:question_id>/delete', methods=['POST'])
@login_required
@admin_required
def delete_question(question_id):
    question = Question.query.get_or_404(question_id)
    quiz_id = question.quiz_id
    
    db.session.delete(question)
    db.session.commit()
    
    # Reorder remaining questions
    remaining_questions = Question.query.filter_by(quiz_id=quiz_id).order_by(Question.order_num).all()
    for i, q in enumerate(remaining_questions, 1):
        q.order_num = i
    
    db.session.commit()
    
    flash('Question deleted successfully', 'success')
    return redirect(url_for('admin.questions', quiz_id=quiz_id))

# Quiz results and analytics
@admin_bp.route('/results')
@login_required
@admin_required
def results():
    attempts = QuizAttempt.query.order_by(QuizAttempt.start_time.desc()).all()
    return render_template('admin/results.html', attempts=attempts)

@admin_bp.route('/results/<int:attempt_id>')
@login_required
@admin_required
def attempt_details(attempt_id):
    attempt = QuizAttempt.query.get_or_404(attempt_id)
    answers = Answer.query.filter_by(attempt_id=attempt_id).all()
    
    return render_template('admin/attempt_details.html', attempt=attempt, answers=answers)
