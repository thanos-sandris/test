from flask import Blueprint, render_template, redirect, url_for, flash, request, jsonify
from flask_login import login_required, current_user
from src.models.models import db, Quiz, Question, Option, QuizAttempt, Answer
from datetime import datetime

quiz_bp = Blueprint('quiz', __name__, url_prefix='/quiz')

@quiz_bp.route('/')
@login_required
def list():
    if not current_user.is_approved and not current_user.is_admin:
        flash('Your account is pending approval by an administrator', 'warning')
        return redirect(url_for('index'))
        
    quizzes = Quiz.query.filter_by(is_active=True).all()
    return render_template('quiz/list.html', quizzes=quizzes)

@quiz_bp.route('/<int:quiz_id>')
@login_required
def details(quiz_id):
    if not current_user.is_approved and not current_user.is_admin:
        flash('Your account is pending approval by an administrator', 'warning')
        return redirect(url_for('index'))
        
    quiz = Quiz.query.get_or_404(quiz_id)
    return render_template('quiz/details.html', quiz=quiz)

@quiz_bp.route('/<int:quiz_id>/start')
@login_required
def start(quiz_id):
    if not current_user.is_approved and not current_user.is_admin:
        flash('Your account is pending approval by an administrator', 'warning')
        return redirect(url_for('index'))
        
    quiz = Quiz.query.get_or_404(quiz_id)
    
    # Check if there's an incomplete attempt
    existing_attempt = QuizAttempt.query.filter_by(
        user_id=current_user.id,
        quiz_id=quiz_id,
        is_completed=False,
        was_left_early=False
    ).first()
    
    if existing_attempt:
        # Continue existing attempt
        return redirect(url_for('quiz.take', quiz_id=quiz_id, attempt_id=existing_attempt.id))
    
    # Create new attempt
    new_attempt = QuizAttempt(
        user_id=current_user.id,
        quiz_id=quiz_id,
        start_time=datetime.utcnow()
    )
    
    db.session.add(new_attempt)
    db.session.commit()
    
    return redirect(url_for('quiz.take', quiz_id=quiz_id, attempt_id=new_attempt.id))

@quiz_bp.route('/<int:quiz_id>/take/<int:attempt_id>')
@login_required
def take(quiz_id, attempt_id):
    if not current_user.is_approved and not current_user.is_admin:
        flash('Your account is pending approval by an administrator', 'warning')
        return redirect(url_for('index'))
        
    quiz = Quiz.query.get_or_404(quiz_id)
    attempt = QuizAttempt.query.get_or_404(attempt_id)
    
    # Security check - ensure the attempt belongs to the current user
    if attempt.user_id != current_user.id:
        flash('Unauthorized access', 'danger')
        return redirect(url_for('quiz.list'))
    
    # Check if the attempt is already completed or left early
    if attempt.is_completed or attempt.was_left_early:
        flash('This quiz attempt has already been completed or abandoned', 'info')
        return redirect(url_for('quiz.results', quiz_id=quiz_id, attempt_id=attempt_id))
    
    # Get the next unanswered question
    answered_questions = [answer.question_id for answer in attempt.answers]
    next_question = Question.query.filter_by(quiz_id=quiz_id).filter(~Question.id.in_(answered_questions)).order_by(Question.order_num).first()
    
    if not next_question:
        # All questions answered, mark as complete
        attempt.is_completed = True
        attempt.end_time = datetime.utcnow()
        db.session.commit()
        return redirect(url_for('quiz.results', quiz_id=quiz_id, attempt_id=attempt_id))
    
    return render_template('quiz/take.html', quiz=quiz, attempt=attempt, question=next_question)

@quiz_bp.route('/<int:quiz_id>/answer/<int:attempt_id>', methods=['POST'])
@login_required
def answer(quiz_id, attempt_id):
    if not current_user.is_approved and not current_user.is_admin:
        return jsonify({'status': 'error', 'message': 'Account not approved'})
    
    attempt = QuizAttempt.query.get_or_404(attempt_id)
    
    # Security check
    if attempt.user_id != current_user.id:
        return jsonify({'status': 'error', 'message': 'Unauthorized'})
    
    if attempt.is_completed or attempt.was_left_early:
        return jsonify({'status': 'error', 'message': 'Quiz already completed or abandoned'})
    
    data = request.get_json()
    question_id = data.get('question_id')
    option_id = data.get('option_id')  # None if skipped
    time_taken = data.get('time_taken')  # Time taken in seconds
    action = data.get('action', 'answer')  # 'answer', 'skip', or 'leave'
    
    question = Question.query.get_or_404(question_id)
    
    # Check if already answered
    existing_answer = Answer.query.filter_by(attempt_id=attempt_id, question_id=question_id).first()
    if existing_answer:
        return jsonify({'status': 'error', 'message': 'Question already answered'})
    
    if action == 'leave':
        # Mark the attempt as left early
        attempt.was_left_early = True
        attempt.end_time = datetime.utcnow()
        db.session.commit()
        return jsonify({'status': 'success', 'action': 'left', 'redirect': url_for('quiz.list')})
    
    # Create new answer
    is_skipped = (action == 'skip' or option_id is None)
    is_correct = False
    
    if not is_skipped and option_id:
        option = Option.query.get(option_id)
        is_correct = option.is_correct if option else False
    
    new_answer = Answer(
        attempt_id=attempt_id,
        question_id=question_id,
        selected_option_id=option_id if not is_skipped else None,
        is_correct=is_correct if not is_skipped else None,
        is_skipped=is_skipped,
        time_taken_seconds=time_taken
    )
    
    db.session.add(new_answer)
    db.session.commit()
    
    # Check if this was the last question
    total_questions = Question.query.filter_by(quiz_id=quiz_id).count()
    answered_questions = Answer.query.filter_by(attempt_id=attempt_id).count()
    
    if answered_questions >= total_questions:
        attempt.is_completed = True
        attempt.end_time = datetime.utcnow()
        db.session.commit()
        return jsonify({
            'status': 'success', 
            'action': 'completed',
            'redirect': url_for('quiz.results', quiz_id=quiz_id, attempt_id=attempt_id)
        })
    
    return jsonify({
        'status': 'success',
        'action': 'next',
        'redirect': url_for('quiz.take', quiz_id=quiz_id, attempt_id=attempt_id)
    })

@quiz_bp.route('/<int:quiz_id>/results/<int:attempt_id>')
@login_required
def results(quiz_id, attempt_id):
    attempt = QuizAttempt.query.get_or_404(attempt_id)
    
    # Security check
    if attempt.user_id != current_user.id and not current_user.is_admin:
        flash('Unauthorized access', 'danger')
        return redirect(url_for('quiz.list'))
    
    quiz = Quiz.query.get_or_404(quiz_id)
    answers = Answer.query.filter_by(attempt_id=attempt_id).all()
    
    # Calculate statistics
    total_questions = Question.query.filter_by(quiz_id=quiz_id).count()
    answered_questions = len([a for a in answers if not a.is_skipped])
    correct_answers = len([a for a in answers if a.is_correct])
    skipped_questions = len([a for a in answers if a.is_skipped])
    
    return render_template(
        'quiz/results.html',
        quiz=quiz,
        attempt=attempt,
        answers=answers,
        total_questions=total_questions,
        answered_questions=answered_questions,
        correct_answers=correct_answers,
        skipped_questions=skipped_questions
    )
