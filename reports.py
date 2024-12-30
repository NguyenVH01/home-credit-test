from sqlalchemy.orm import Session
from sqlalchemy import func, desc
from models import User, Review, ReviewCycle
from typing import List, Dict, Any
from datetime import datetime

def get_department_scores(db: Session, review_cycle_id: int) -> List[Dict[str, Any]]:
    """Lấy điểm trung bình theo phòng ban"""
    results = db.query(
        User.department,
        func.avg(Review.performance_score).label('avg_performance'),
        func.avg(Review.leadership_score).label('avg_leadership'),
        func.avg(Review.teamwork_score).label('avg_teamwork'),
        func.avg(Review.innovation_score).label('avg_innovation'),
        func.count(User.id).label('total_employees')
    ).join(Review, Review.reviewee_id == User.id)\
    .filter(Review.review_cycle_id == review_cycle_id)\
    .group_by(User.department)\
    .all()
    
    return [
        {
            'department': r.department,
            'avg_performance': float(r.avg_performance or 0),
            'avg_leadership': float(r.avg_leadership or 0),
            'avg_teamwork': float(r.avg_teamwork or 0),
            'avg_innovation': float(r.avg_innovation or 0),
            'total_employees': r.total_employees
        }
        for r in results
    ]

def get_top_performers(db: Session, review_cycle_id: int, limit: int = 10) -> List[Dict[str, Any]]:
    """Lấy danh sách nhân viên có điểm cao nhất"""
    results = db.query(
        User.full_name,
        User.department,
        func.avg(Review.performance_score).label('avg_performance'),
        func.avg(Review.leadership_score).label('avg_leadership'),
        func.avg(Review.teamwork_score).label('avg_teamwork'),
        func.avg(Review.innovation_score).label('avg_innovation')
    ).join(Review, Review.reviewee_id == User.id)\
    .filter(Review.review_cycle_id == review_cycle_id)\
    .group_by(User.id, User.full_name, User.department)\
    .order_by(desc(func.avg(Review.performance_score)))\
    .limit(limit)\
    .all()
    
    return [
        {
            'full_name': r.full_name,
            'department': r.department,
            'avg_performance': float(r.avg_performance or 0),
            'avg_leadership': float(r.avg_leadership or 0),
            'avg_teamwork': float(r.avg_teamwork or 0),
            'avg_innovation': float(r.avg_innovation or 0)
        }
        for r in results
    ]

def get_review_completion_status(db: Session, review_cycle_id: int) -> Dict[str, Any]:
    """Lấy thống kê về tiến độ đánh giá"""
    review_cycle = db.query(ReviewCycle).filter_by(id=review_cycle_id).first()
    
    total_reviews = db.query(func.count(Review.id))\
        .filter(Review.review_cycle_id == review_cycle_id)\
        .scalar()
    
    completed_reviews = db.query(func.count(Review.id))\
        .filter(Review.review_cycle_id == review_cycle_id)\
        .filter(Review.status == 'submitted')\
        .scalar()
    
    pending_reviews = total_reviews - completed_reviews
    
    return {
        'cycle_name': review_cycle.name,
        'start_date': review_cycle.start_date,
        'end_date': review_cycle.end_date,
        'total_reviews': total_reviews,
        'completed_reviews': completed_reviews,
        'pending_reviews': pending_reviews,
        'completion_rate': (completed_reviews / total_reviews * 100) if total_reviews > 0 else 0
    }

def get_training_recommendations(db: Session, review_cycle_id: int) -> List[Dict[str, Any]]:
    """Lấy các đề xuất đào tạo phổ biến"""
    reviews = db.query(Review)\
        .filter(Review.review_cycle_id == review_cycle_id)\
        .filter(Review.training_recommendations.isnot(None))\
        .all()
    
    recommendations = {}
    for review in reviews:
        if review.training_recommendations:
            for rec in review.training_recommendations.split(','):
                rec = rec.strip()
                if rec:
                    recommendations[rec] = recommendations.get(rec, 0) + 1
    
    sorted_recommendations = sorted(
        [{'recommendation': k, 'count': v} for k, v in recommendations.items()],
        key=lambda x: x['count'],
        reverse=True
    )
    
    return sorted_recommendations

def get_improvement_areas(db: Session, review_cycle_id: int) -> List[Dict[str, Any]]:
    """Lấy các lĩnh vực cần cải thiện phổ biến"""
    reviews = db.query(Review)\
        .filter(Review.review_cycle_id == review_cycle_id)\
        .filter(Review.areas_for_improvement.isnot(None))\
        .all()
    
    areas = {}
    for review in reviews:
        if review.areas_for_improvement:
            for area in review.areas_for_improvement.split(','):
                area = area.strip()
                if area:
                    areas[area] = areas.get(area, 0) + 1
    
    sorted_areas = sorted(
        [{'area': k, 'count': v} for k, v in areas.items()],
        key=lambda x: x['count'],
        reverse=True
    )
    
    return sorted_areas 